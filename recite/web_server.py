"""Flask web server for recite — browser-based quiz interface."""
import json
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, render_template, request, jsonify, send_from_directory

from .card_generator import generate_cards
from .document_reader import read_document
from .llm_client import chat
from .storage import load_cards, save_cards, list_decks, _cards_dir

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), "templates"))

# In-memory quiz session state: {session_id: {deck_name, history, current_idx, ...}}
_sessions = {}


def _get_llm_config():
    """Extract per-user LLM config from request headers."""
    cfg = {}
    for key in ("x-api-key", "x-base-url", "x-model"):
        val = request.headers.get(key, "")
        if val:
            cfg[key.replace("x-", "").replace("-", "_")] = val
    return cfg

EVAL_SYSTEM_PROMPT = """你是一个严格的知识背诵考官。请用中文评价用户的回答。

评价标准：
1. 指出用户回答中**正确**的部分
2. 指出用户回答中**遗漏**的关键点
3. 指出用户回答中**错误或不准确**的地方
4. 给出 1-5 分的评分

请用以下 Markdown 格式回复：

### 评分：X/5

**✅ 正确的部分**
- ...

**❌ 遗漏的关键点**
- ...

**⚠️ 错误/不准确**
- ...

**📝 参考答案**
（完整参考答案）"""


# ── Page routes ────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── API: upload & generate ─────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Upload a document file, generate cards, return the deck."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Save to temp location
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".md", ".txt", ".pdf", ".docx"):
        return jsonify({"error": f"Unsupported format: {ext}"}), 400

    tmp_path = os.path.join(_cards_dir(), f"_upload_{uuid.uuid4().hex}{ext}")
    os.makedirs(_cards_dir(), exist_ok=True)
    file.save(tmp_path)

    try:
        doc_text = read_document(tmp_path)
        if not doc_text.strip():
            return jsonify({"error": "Document is empty or unreadable"}), 400

        base_name = os.path.splitext(file.filename)[0]
        llm_config = _get_llm_config()
        card_path = generate_cards(tmp_path, llm_config=llm_config)
        deck = load_cards(base_name)

        return jsonify({"success": True, "deck": deck})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ── API: decks ─────────────────────────────────────────────

@app.route("/api/decks", methods=["GET"])
def api_decks():
    decks = list_decks()
    return jsonify({"decks": decks})


@app.route("/api/decks/<name>", methods=["GET"])
def api_deck_detail(name):
    try:
        deck = load_cards(name)
        return jsonify({"deck": deck})
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404


# ── API: quiz session ──────────────────────────────────────

@app.route("/api/quiz/start", methods=["POST"])
def api_quiz_start():
    """Start a new quiz session for a deck."""
    data = request.get_json()
    deck_name = data.get("deck_name", "")
    try:
        deck = load_cards(deck_name)
    except FileNotFoundError:
        return jsonify({"error": "Deck not found"}), 404

    session_id = uuid.uuid4().hex[:12]
    cards = deck["cards"]
    # Ensure each card has a stable id for session tracking
    for i, card in enumerate(cards):
        if "id" not in card:
            card["id"] = i
    _sessions[session_id] = {
        "deck_name": deck_name,
        "cards": cards,
        "attempted": {},
        "history": [],
    }
    return jsonify({"session_id": session_id, "total": len(cards)})


@app.route("/api/quiz/next", methods=["POST"])
def api_quiz_next():
    """Get the next question for the session."""
    data = request.get_json()
    session_id = data.get("session_id", "")
    session = _sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    cards = session["cards"]
    attempted = session["attempted"]

    # Pick unattempted card first, then lowest-scored
    unattempted = [c for c in cards if c["id"] not in attempted]
    if unattempted:
        import random
        card = random.choice(unattempted)
    else:
        scored = sorted(cards, key=lambda c: attempted.get(c["id"], {}).get("score", -1))
        import random
        pool = scored[:max(1, len(scored) // 3)]
        card = random.choice(pool)

    return jsonify({
        "card": card,
        "card_id": card["id"],
        "attempted_count": len(attempted),
        "total": len(cards),
    })


@app.route("/api/quiz/submit", methods=["POST"])
def api_quiz_submit():
    """Submit an answer and get evaluation."""
    data = request.get_json()
    session_id = data.get("session_id", "")
    card_id = data.get("card_id", 0)
    answer = data.get("answer", "").strip()

    session = _sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    # Find the card
    card = None
    for c in session["cards"]:
        if str(c["id"]) == str(card_id):
            card = c
            break
    if not card:
        return jsonify({"error": "Card not found"}), 404

    if not answer:
        return jsonify({"evaluation": "_你什么都没写。跳过此题。_"}), 200

    # Call LLM for evaluation
    messages = [
        {"role": "system", "content": EVAL_SYSTEM_PROMPT},
        {"role": "user", "content": f"""题目：{card['question']}

参考答案：{card['reference_answer']}

关键词：{', '.join(card['keywords'])}

用户的回答：
{answer}

请评价。"""},
    ]
    try:
        llm_config = _get_llm_config()
        evaluation = chat(messages, temperature=0.3, **llm_config)
    except Exception as e:
        evaluation = f"### 评分：-/5\n\n评价出错: {e}"

    # Extract score
    import re
    match = re.search(r"评分[：:]\s*(\d)/5", evaluation)
    score = int(match.group(1)) if match else -1

    # Record in session
    session["attempted"][card_id] = {"score": score, "answer": answer, "ts": datetime.now(timezone.utc).isoformat()}
    session["history"].append({
        "question": card["question"],
        "score": score,
        "answer": answer,
        "evaluation": evaluation,
    })

    # Save history to disk
    _save_session_history(session)

    return jsonify({
        "evaluation": evaluation,
        "score": score,
        "attempted_count": len(session["attempted"]),
        "total": len(session["cards"]),
    })


@app.route("/api/quiz/summary", methods=["POST"])
def api_quiz_summary():
    """Get session summary."""
    data = request.get_json()
    session_id = data.get("session_id", "")
    session = _sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404

    history = session["history"]
    scores = [h["score"] for h in history if h.get("score", -1) >= 0]
    avg = sum(scores) / len(scores) if scores else 0

    return jsonify({
        "history": history,
        "average": round(avg, 1),
        "total_answered": len(history),
        "total_cards": len(session["cards"]),
    })


def _save_session_history(session):
    """Persist session history to a JSON file."""
    deck_name = session["deck_name"]
    history_path = os.path.join(_cards_dir(), f"{deck_name}_history.json")
    records = []
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            records = json.load(f)
    records.extend(session["history"])
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def start_server(host="0.0.0.0", port=5000, debug=False):
    print(f"\n  🧠 recite Web 界面已启动: http://localhost:{port}\n")
    app.run(host=host, port=port, debug=debug)

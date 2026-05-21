import random

from .llm_client import chat
from .storage import load_cards

EVAL_SYSTEM_PROMPT = """你是一个严格的知识背诵考官。用户正在背诵一道题目，你需要对照参考答案和关键词来评价用户的回答。

评价标准：
1. 指出用户回答中**正确**的部分
2. 指出用户回答中**遗漏**的关键点（对照 keywords 和 reference_answer）
3. 指出用户回答中**错误或不准确**的地方（如果有）
4. 给出 1-5 分的评分：
   - 1分：基本不会，或大量错误
   - 2分：说对一小部分，但遗漏很多关键点
   - 3分：说对一半左右，有明显遗漏
   - 4分：大部分正确，只有少量遗漏或小错误
   - 5分：完全正确，覆盖所有关键点

请按以下格式回复：

## 评分：X/5

## 正确的部分
- ...
- ...

## 遗漏的关键点
- ...
- ...

## 错误/不准确的地方
- ...
- ...（如无错误则写"无"）

## 参考答案（供对照）
（这里给出完整参考答案）

评价要具体、有帮助，直接指出问题，不要拐弯抹角。"""


def start_quiz(deck_name):
    deck = load_cards(deck_name)
    cards = deck["cards"]

    if not cards:
        print("题库中没有题目！")
        return

    # 为每道题初始化答题记录
    for card in cards:
        card.setdefault("attempts", 0)
        card.setdefault("last_score", -1)

    print(f"\n{'='*60}")
    print(f"📚 题库: {deck['name']}")
    print(f"📝 共 {len(cards)} 道题目")
    print(f"{'='*60}")
    print("输入你的答案（可以是多行），然后输入空行提交。")
    print("输入 /skip 跳過，输入 /quit 退出。\n")

    session_results = []

    while True:
        card = _pick_card(cards)
        print(f"\n{'─'*60}")
        print(f"📌 [{card['attempts']}次作答] {card['question']}")
        print(f"{'─'*60}")
        print("请作答（输入空行提交）:")

        user_answer = _read_multiline_input()
        if user_answer is None:
            print("\n答题结束。")
            break
        if not user_answer.strip():
            print("答案为空，已跳過。")
            continue

        print("\n正在评价你的回答...\n")

        evaluation = _evaluate(card, user_answer)
        print(evaluation)
        print()

        card["attempts"] += 1

        # 提取评分
        score = _extract_score(evaluation)
        card["last_score"] = score
        session_results.append({
            "question": card["question"],
            "score": score,
        })

        if not _confirm_continue():
            break

    _print_session_summary(session_results, cards)
    print("再见！")


def _pick_card(cards):
    # 优先选未答过的，其次选得分最低的
    unattempted = [c for c in cards if c["attempts"] == 0]
    if unattempted:
        return random.choice(unattempted)
    cards.sort(key=lambda c: c.get("last_score", -1))
    # 从得分最低的 1/3 中随机选
    pool_size = max(1, len(cards) // 3)
    return random.choice(cards[:pool_size])


def _read_multiline_input():
    lines = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            return None
        if line.strip() == "/quit":
            return None
        if line.strip() == "/skip":
            return ""
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def _evaluate(card, user_answer):
    messages = [
        {"role": "system", "content": EVAL_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""题目：{card['question']}

参考答案：{card['reference_answer']}

关键词：{', '.join(card['keywords'])}

用户的回答：
{user_answer}

请评价。""",
        },
    ]
    return chat(messages, temperature=0.3)


def _extract_score(evaluation):
    import re
    match = re.search(r"评分[：:]\s*(\d)/5", evaluation)
    if match:
        return int(match.group(1))
    return -1


def _confirm_continue():
    while True:
        ans = input("继续下一题？[Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("输入 y 或 n")


def _print_session_summary(session_results, cards):
    if not session_results:
        return
    print(f"\n{'='*60}")
    print("📊 本次答题总结")
    print(f"{'='*60}")
    for r in session_results:
        stars = "★" * r["score"] + "☆" * (5 - r["score"])
        print(f"  {stars}  {r['question']}")
    scores = [r["score"] for r in session_results]
    avg = sum(scores) / len(scores)
    print(f"\n平均分: {avg:.1f}/5  |  答题数: {len(session_results)}/{len(cards)}")

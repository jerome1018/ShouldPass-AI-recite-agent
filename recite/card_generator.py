import json
import os
import re

from .llm_client import chat
from .storage import save_cards

SYSTEM_PROMPT = """你是一个知识题库整理助手。用户会提供一份包含题目和参考答案的文档片段，请你：

1. 仔细阅读文档，提取出每一道题目及其参考答案。
2. 为每道题提炼 3-6 个关键词（keywords），覆盖答案的核心要点。
3. 将每道题的参考答案润色整理，使其更条理清晰，但不要丢失任何关键信息。

请严格按照以下 JSON 数组格式输出，不要输出任何其他内容：

```json
[
  {
    "question": "题目内容",
    "reference_answer": "梳理后的参考答案，条理清晰",
    "keywords": ["关键词1", "关键词2", "关键词3"]
  }
]
```

注意：
- 如果文档片段中已经明确划分了题目，就按原题数量输出。
- 如果文档片段中没有明确题目、是纯论述，可以根据内容逻辑拆分为 2-5 道合适的题目，也可以返回空数组 []。
- keywords 必须精准、具体，不要使用过于宽泛的词汇。"""

# 超过此字符数的文档将按标题分片处理
CHUNK_SIZE = 30000


def generate_cards(document_path):
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found: {document_path}")

    with open(document_path, "r", encoding="utf-8") as f:
        doc_text = f.read()

    if not doc_text.strip():
        raise ValueError("Document is empty")

    print(f"正在读取文档: {document_path}")
    print(f"文档长度: {len(doc_text)} 字符")

    # 大文档分片处理
    if len(doc_text) > CHUNK_SIZE:
        print(f"文档较大，按标题分片处理...")
        all_cards = _process_chunked(doc_text)
    else:
        print("正在调用 LLM 梳理题目...")
        response = chat(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": doc_text}],
            temperature=0.3,
            max_tokens=16384,
        )
        all_cards = _parse_llm_response(response, debug_prefix="LLM 返回")

    if not all_cards:
        raise RuntimeError(
            "LLM 未返回有效题目，请检查文档内容或重试。\n"
            "可能原因：文档过大导致输出截断、文档格式混乱、或 LLM 返回异常。"
        )

    base_name = os.path.splitext(os.path.basename(document_path))[0]
    saved_path = save_cards(base_name, all_cards, os.path.abspath(document_path))

    print(f"\n生成了 {len(all_cards)} 道题目")
    print(f"题库已保存至: {saved_path}")
    for i, card in enumerate(all_cards):
        print(f"  [{i}] {card['question']}")

    return saved_path


def _process_chunked(doc_text):
    """Split large document by markdown headers and process each section."""
    chunks = _split_by_headers(doc_text)
    print(f"文档分为 {len(chunks)} 个片段，逐个调用 LLM 处理...")
    all_cards = []
    for idx, chunk in enumerate(chunks):
        title_slug = chunk.strip()[:40].replace("\n", " ")
        print(f"  处理片段 [{idx+1}/{len(chunks)}]: {title_slug}...")
        response = chat(
            [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": chunk}],
            temperature=0.3,
            max_tokens=16384,
        )
        cards = _parse_llm_response(response, debug_prefix=f"片段 {idx+1} LLM 返回")
        if cards:
            all_cards.extend(cards)
            print(f"    -> 提取 {len(cards)} 题")
        else:
            print(f"    -> 未提取到题目，跳过")
    return all_cards


def _split_by_headers(text):
    """Split text by markdown headers (#, ##, ###) into logical sections."""
    # 按 # 标题分片（但保留标题作为上下文）
    sections = re.split(r"\n(?=#{1,3}\s)", text)
    if len(sections) <= 1:
        # 没有标题，按空行粗略分片
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for p in paragraphs:
            if len(current) + len(p) > CHUNK_SIZE and current:
                chunks.append(current)
                current = p
            else:
                current = (current + "\n\n" + p).strip()
        if current:
            chunks.append(current)
        return chunks if len(chunks) > 1 else [text]

    # 将小标题合并成大块
    chunks = []
    current = ""
    for section in sections:
        if len(current) + len(section) > CHUNK_SIZE and current:
            chunks.append(current)
            current = section
        else:
            current = (current + "\n" + section).strip()
    if current:
        chunks.append(current)
    return chunks if chunks else [text]


def _parse_llm_response(response, debug_prefix="LLM 返回"):
    if not response:
        print(f"  ⚠ {debug_prefix}内容为空")
        return []

    errors = []

    # 尝试直接解析整个响应
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        errors.append(f"直接解析: {e}")

    # 尝试从 ```json 代码块中提取
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError as e:
            errors.append(f"代码块提取: {e}")

    # 尝试提取最外层 JSON 数组
    match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            errors.append(f"数组提取: {e}")

    # 解析失败时打印调试信息
    print(f"  ⚠ {debug_prefix}无法解析为 JSON")
    for err in errors:
        print(f"     {err}")
    print(f"  --- 响应开头 200 字 ---")
    print(f"  {response[:200]}")
    print(f"  --- 响应结尾 200 字 ---")
    print(f"  {response[-200:]}")
    print(f"  --- 响应总长度: {len(response)} 字符 ---")
    return []

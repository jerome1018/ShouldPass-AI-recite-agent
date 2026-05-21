import json
import os
import re

from .llm_client import chat
from .storage import save_cards

SYSTEM_PROMPT = """你是一个知识题库整理助手。用户会提供一份包含题目和参考答案的文档（可能格式比较自由），请你：

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
- 如果文档中已经明确划分了题目，就按原题数量输出。
- 如果文档是长篇论述没有明确分题，你可以根据内容逻辑拆分为 3-8 道合适的题目。
- keywords 必须精准、具体，不要使用过于宽泛的词汇。"""


def generate_cards(document_path):
    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Document not found: {document_path}")

    with open(document_path, "r", encoding="utf-8") as f:
        doc_text = f.read()

    if not doc_text.strip():
        raise ValueError("Document is empty")

    print(f"正在读取文档: {document_path}")
    print(f"文档长度: {len(doc_text)} 字符")
    print("正在调用 LLM 梳理题目...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": doc_text},
    ]

    response = chat(messages, temperature=0.3)

    cards = _parse_llm_response(response)
    if not cards:
        raise RuntimeError("LLM 未返回有效题目，请检查文档内容或重试")

    base_name = os.path.splitext(os.path.basename(document_path))[0]
    saved_path = save_cards(base_name, cards, os.path.abspath(document_path))

    print(f"生成了 {len(cards)} 道题目")
    print(f"题库已保存至: {saved_path}")
    for i, card in enumerate(cards):
        print(f"  [{i}] {card['question']}")

    return saved_path


def _parse_llm_response(response):
    # 尝试直接解析整个响应
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # 尝试从 ```json 代码块中提取
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取最外层 JSON 数组
    match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return []

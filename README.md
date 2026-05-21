# 🧠 recite — Your AI Drill Sergeant for Knowledge

> *"You think you know it. The LLM thinks otherwise."*

**recite** turns your messy study notes into a relentless quiz machine. Drop in a document full of Q&A, and it spits out a structured question bank. Then it quizzes you — and judges you. Every correct answer gets a nod. Every missed keyword gets called out. No mercy, no false praise. Just cold, precise feedback until you actually remember what you thought you already knew.

---

## 🚀 Try It Online — No Install Needed

> **[👉 Click here to open the Web version 👈](https://jerome1018.github.io/ShouldPass-AI-recite-agent/)**
>
> No download. No setup. Just bring your own API key and start quizzing in your browser.
> Supports `.md` `.txt` `.pdf` `.docx` — drag, drop, and get grilled by an LLM.

---

## Why recite?

You've read the paper. You've highlighted the slides. You *feel* like you understand it. But can you explain RoPE's long-range decay from scratch, under pressure, with no notes?

That gap — between recognition and recall — is where recite lives.

| Traditional Studying | recite Mode |
|---|---|
| Re-read notes passively | Active recall, forced retrieval |
| "Yeah I get it" | "Prove it. Say it out loud. Now." |
| No feedback loop | LLM grades you on keywords, completeness, accuracy |
| One-size-fits-all | Your own material, your own pace |

---

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure your LLM API key in config.yaml

# 3. Generate cards from your study document (supports .md / .txt / .pdf / .docx)
python -m recite generate documents/my_notes.md

# 4. Get quizzed
python -m recite quiz my_notes
```

---

## Supported Formats

Drop in whatever you have — notes, papers, interview prep docs:

| Format | Extension | Library |
|---|---|---|
| Markdown / Plain text | `.md` `.txt` | built-in |
| PDF | `.pdf` | pymupdf |
| Word | `.docx` | python-docx |

Large documents (132k+ chars) are automatically split by headings and processed in parallel — no manual chunking needed.

---

## How It Works

```
Your messy notes ──▶ LLM structures them ──▶ Structured Q&A cards (JSON)
                                                      │
                                                      ▼
                                              Random pick, you answer
                                                      │
                                                      ▼
                                              LLM evaluates:
                                              ✅ What you got right
                                              ❌ What you missed
                                              ⚡ What you got wrong
                                              📊 Score: 1-5
```

Every session pushes you closer to *actually* knowing your stuff.

---

## Sample Card

```json
{
  "question": "Why does RoPE exhibit long-range decay?",
  "reference_answer": "RoPE's long-range decay stems from...",
  "keywords": ["phase rotation", "high-freq oscillation", "phase cancellation", "cos/sin", "attention decay"]
}
```

When you answer, the LLM cross-checks your response against every keyword — if you skipped "phase cancellation", you'll hear about it.

---

## Pro Tips

- **Throw in any format.** `.md`, `.txt`, `.pdf`, `.docx` — recite parses them all.
- **Make your source docs detailed.** The better the reference answers, the harsher (and more useful) the grading.
- **Don't skip the hard ones.** recite prioritizes questions you've bombed before.
- **Use any LLM.** OpenAI, DeepSeek, Ollama, Groq — anything with an OpenAI-compatible endpoint works.

---

> *Reading is passive. Reciting is active. recite makes sure you can't hide behind "I'll remember it next time."*

---

---

# 🧠 recite — 你的 AI 背诵教官

> *"你以为你懂了。LLM 不这么认为。"*

**recite** 把你的学习笔记变成一台无情的提问机器。丢一份文档进去，它自动整理成结构化题库。然后它考你——还批你。答对的给个点头，漏掉的关键词一个不落地点出来。不手软，不客套，不说"挺不错的"。就是冷冰冰的精准反馈，直到你真正记住你以为已经会了的东西。

---

## 🚀 在线体验 — 无需安装

> **[👉 点这里打开网页版 👈](https://jerome1018.github.io/ShouldPass-AI-recite-agent/)**
>
> 不用下载，不用配置环境。带上你自己的 API Key，浏览器里直接开背。
> 支持 `.md` `.txt` `.pdf` `.docx` — 拖拽上传，LLM 当场拷打。

---

## 为什么需要 recite？

论文看过了。PPT 高亮了。感觉理解了。但关掉所有参考资料，你能从零开始讲清楚 RoPE 的长程衰减机制吗？

从"眼熟"到"能说出来"，中间隔着的那个鸿沟，就是 recite 存在的意义。

| 传统复习 | recite 模式 |
|---|---|
| 被动翻看笔记 | 主动提取，强迫回忆 |
| "嗯，我懂了" | "证明一下。现在。说清楚。" |
| 没有反馈 | LLM 按关键词、完整性、准确性逐项打分 |
| 统一的复习材料 | 你自己的笔记，你自己的节奏 |

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 在 config.yaml 里配置你的 LLM API key

# 3. 从学习文档生成题库（支持 .md / .txt / .pdf / .docx）
python -m recite generate documents/我的笔记.md

# 4. 开始答题
python -m recite quiz 我的笔记
```

---

## 支持格式

什么格式都能扔进来——笔记、论文、面试八股文：

| 格式 | 扩展名 | 依赖库 |
|---|---|---|
| Markdown / 纯文本 | `.md` `.txt` | 无 |
| PDF | `.pdf` | pymupdf |
| Word | `.docx` | python-docx |

大文档（超过 13 万字）会自动按标题分片并行处理，无需手动切割。

---

## 工作流程

```
你凌乱的笔记 ──▶ LLM 梳理结构化 ──▶ 清晰的题库卡片 (JSON)
                                        │
                                        ▼
                                  随机抽题，你来作答
                                        │
                                        ▼
                                  LLM 逐项评价：
                                  ✅ 答对了什么
                                  ❌ 遗漏了什么
                                  ⚡ 哪里说错了
                                  📊 1-5 分打分
```

每一次答题，都让你离"真正掌握"更近一步。

---

## 题库卡片样例

```json
{
  "question": "为什么 RoPE 会长程衰减？",
  "reference_answer": "RoPE 长程衰减的根源在于其旋转机制……",
  "keywords": ["相位旋转", "高频振荡", "相位抵消", "cos/sin", "attention衰减"]
}
```

你作答之后，LLM 会逐一对照每个关键词——漏了"相位抵消"？那它一定会指出来。

---

## 使用技巧

- **什么格式都能扔进来。** `.md`、`.txt`、`.pdf`、`.docx`——recite 全支持。
- **源文档写得越详细，批改越狠（也越有用）。** 参考答案质量决定评价质量。
- **别跳过难题。** recite 会优先抽查你之前翻车过的题目。
- **什么 LLM 都能接。** OpenAI、DeepSeek、Ollama、Groq——只要支持 OpenAI 兼容接口就能用。

---

> *看是输入。说才是输出。recite 让你没法用"下次一定记住"糊弄自己。*

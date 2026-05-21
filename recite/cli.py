#!/usr/bin/env python3
import argparse
import sys

from .card_generator import generate_cards
from .quiz_session import start_quiz
from .storage import list_decks


def main():
    parser = argparse.ArgumentParser(
        prog="recite",
        description="知识背诵自查工具 — 用 LLM 辅助背诵复习",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # generate
    gen_parser = subparsers.add_parser("generate", help="从文档生成结构化题库")
    gen_parser.add_argument("document", help="文档路径（.md / .txt）")

    # quiz
    quiz_parser = subparsers.add_parser("quiz", help="开始答题")
    quiz_parser.add_argument("deck", help="题库名称（不含 .json 后缀）")

    # list
    subparsers.add_parser("list", help="列出已有题库")

    args = parser.parse_args()

    if args.command == "generate":
        try:
            generate_cards(args.document)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "quiz":
        try:
            start_quiz(args.deck)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        decks = list_decks()
        if not decks:
            print("暂无题库。使用 generate 命令从文档生成题库。")
        else:
            for deck in decks:
                n = len(deck.get("cards", []))
                print(f"  {deck['name']} — {n} 题 — 创建于 {deck['created_at']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

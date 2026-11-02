"""第1回: 会話履歴を保ったままLLMに質問するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 既定の質問から対話を始める

質問を続けると、同じチャットに送られるため会話履歴が保持される。
終了するには「終了」「quit」「exit」を入力するか、Ctrl-Dを押す。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def ask(chat, question: str) -> str:
    response = chat.send_message(question)

    usage = response.usage_metadata
    print(
        f"[usage] input_tokens={usage.prompt_token_count} "
        f"output_tokens={usage.candidates_token_count}"
    )

    return response.text


def main() -> None:
    parser = argparse.ArgumentParser(description="会話履歴を保ったままLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    try:
        client = genai.Client(api_key=get_api_key())
        chat = client.chats.create(model=MODEL)

        print(f"[model] {MODEL}")
        question = args.question
        while True:
            print(f"[質問] {question}\n")
            print(ask(chat, question))
            print()
            try:
                question = input("続けて質問してください（終了/quit/exitで終了）: ")
            except EOFError:
                print()
                break
            if question.strip().lower() in {"終了", "quit", "exit"}:
                break
            if not question.strip():
                continue
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()

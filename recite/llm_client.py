from openai import OpenAI
from .config import load_config


def get_client():
    cfg = load_config()
    return OpenAI(
        api_key=cfg["llm"]["api_key"],
        base_url=cfg["llm"]["base_url"],
    )


def chat(messages, temperature=0.7):
    cfg = load_config()
    client = get_client()
    response = client.chat.completions.create(
        model=cfg["llm"]["model"],
        messages=messages,
        temperature=temperature,
        max_tokens=cfg["llm"]["max_tokens"],
    )
    return response.choices[0].message.content

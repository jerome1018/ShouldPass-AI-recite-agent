from openai import OpenAI
from .config import load_config


def get_client(api_key=None, base_url=None):
    cfg = load_config()
    return OpenAI(
        api_key=api_key or cfg["llm"]["api_key"],
        base_url=base_url or cfg["llm"]["base_url"],
    )


def chat(messages, temperature=0.7, max_tokens=None, api_key=None, base_url=None, model=None):
    cfg = load_config()
    client = get_client(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model or cfg["llm"]["model"],
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens or cfg["llm"]["max_tokens"],
    )
    return response.choices[0].message.content

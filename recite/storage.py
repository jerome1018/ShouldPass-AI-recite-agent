import json
import os
from datetime import datetime, timezone

from .config import get_project_root


def _cards_dir():
    return os.path.join(get_project_root(), "cards")


def load_cards(name):
    path = os.path.join(_cards_dir(), f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Card deck not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_cards(name, question_cards, source_document):
    os.makedirs(_cards_dir(), exist_ok=True)
    deck = {
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_document": source_document,
        "cards": question_cards,
    }
    path = os.path.join(_cards_dir(), f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
    return path


def list_decks():
    d = _cards_dir()
    if not os.path.exists(d):
        return []
    decks = []
    for fname in os.listdir(d):
        if fname.endswith(".json"):
            with open(os.path.join(d, fname), "r", encoding="utf-8") as f:
                deck = json.load(f)
            decks.append(deck)
    return decks

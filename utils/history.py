import os
import json

def get_history_path(chat_id):
    return f"data/history_{chat_id}.json"

def load_history(chat_id):
    path = get_history_path(chat_id)
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_history(chat_id, history):
    path = get_history_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

import json
import os
import random

STATE_PATH = "data/letter_state.json"
HISTORY_PATH = "data/letter_history.json"
MAX_HISTORY_PER_SENDER = 9
MAX_ATTEMPTS = 20


def load_letter_state(chat_id):
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(chat_id), {"selected": []})

def save_letter_state(chat_id, state):
    if not os.path.exists(STATE_PATH):
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(STATE_PATH, "r+", encoding="utf-8") as f:
        all_data = json.load(f)
        all_data[str(chat_id)] = state
        f.seek(0)
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        f.truncate()

def load_letter_history(chat_id):
    if not os.path.exists(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(str(chat_id), {})

def save_letter_history(chat_id, history):
    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(HISTORY_PATH, "r+", encoding="utf-8") as f:
        all_data = json.load(f)
        all_data[str(chat_id)] = history
        f.seek(0)
        json.dump(all_data, f, ensure_ascii=False, indent=2)
        f.truncate()


def assign_letter_circle(selected_ids, history):
    if len(selected_ids) < 2:
        return []

    for _ in range(20):
        random.shuffle(selected_ids)
        valid = True
        circle = []

        for i in range(len(selected_ids)):
            sender = selected_ids[i]
            receiver = selected_ids[(i + 1) % len(selected_ids)]

            if receiver in history.get(sender, []):
                valid = False
                break

            circle.append((sender, receiver))

        if valid:
            break
    else:
        circle = []
        for i in range(len(selected_ids)):
            sender = selected_ids[i]
            receiver = selected_ids[(i + 1) % len(selected_ids)]
            circle.append((sender, receiver))

    for sender, receiver in circle:
        if len(history.get(sender, [])) >= 9:
            history[sender] = []
        history.setdefault(sender, []).append(receiver)

    return circle



async def send_letter_assignments(bot, chat_id, members, selected_ids):
    history = load_letter_history(chat_id)
    pairs = assign_letter_circle(selected_ids, history)

    if not pairs:
        return False

    for sender, receiver in pairs:
        sender_name = members[sender]
        receiver_name = members[receiver]
        text = (
            f"💌 Привет, {sender_name}!\n\n"
            f"В этом месяце ты пишешь письмо для {receiver_name} ✨\n"
        )
        try:
            await bot.send_message(int(sender), text)
        except Exception as e:
            print(f"Ошибка отправки {sender_name}: {e}")

    save_letter_history(chat_id, history)
    return True

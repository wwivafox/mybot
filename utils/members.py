import os
import json
import random
import itertools
from utils.history import load_history, save_history
from datetime import datetime


def get_path(chat_id):
    return f"data/members_{chat_id}.json"

def load_members(chat_id):
    path = get_path(chat_id)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_members(chat_id, members):
    path = get_path(chat_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)

def add_member(chat_id, user_id, name=None):
    members = load_members(chat_id)
    if not any(m["telegram_id"] == user_id for m in members):
        members.append({"telegram_id": user_id, "name": name, "active": True})
        save_members(chat_id, members)
        return True
    return False

def update_member_name(chat_id, user_id, new_name):
    members = load_members(chat_id)
    for m in members:
        if m["telegram_id"] == user_id:
            m["name"] = new_name
            save_members(chat_id, members)
            return True
    return False

def make_circle(chat_id):
    members = load_members(chat_id)
    names = [m["name"] for m in members if m["name"] and m.get("active", True)]
    if len(names) < 2:
        return []

    history = load_history(chat_id)

    for attempt in range(20):  
        random.shuffle(names)
        valid = True
        circle = []

        for i in range(len(names)):
            giver = names[i]
            receiver = names[(i + 1) % len(names)]

            if receiver in history.get(giver, []):
                valid = False
                break

            circle.append((giver, receiver))

        if valid:
            break
    else:
        circle = []
        for i in range(len(names)):
            giver = names[i]
            receiver = names[(i + 1) % len(names)]
            circle.append((giver, receiver))

    for giver, receiver in circle:
        if len(history.get(giver, [])) >= 9:
            history[giver] = []
        history.setdefault(giver, []).append(receiver)

    save_history(chat_id, history)
    return circle


def set_active_by_name(chat_id, name, is_active):
    members = load_members(chat_id)
    for m in members:
        if m["name"] and m["name"].lower() == name.lower():
            m["active"] = is_active
            save_members(chat_id, members)
            return True
    return False

def set_active(chat_id, user_id, is_active):
    members = load_members(chat_id)
    for m in members:
        if m["telegram_id"] == user_id:
            m["active"] = is_active
            save_members(chat_id, members)
            return True
    return False

def get_active_mentions(chat_id):
    members = load_members(chat_id)
    mentions = []
    for m in members:
        if m.get("active", True) and m.get("telegram_id"):
            name = m["name"] or "Без имени"
            mention = f'<a href="tg://user?id={m["telegram_id"]}">{name}</a>'
            mentions.append(mention)
    return mentions

def update_member_birthday(chat_id, user_id, birthday):
    members = load_members(chat_id)
    for m in members:
        if m["telegram_id"] == user_id:
            m["birthday"] = birthday
            save_members(chat_id, members)
            return True
    return False


def get_birthdays_today(chat_id):

    today = datetime.now().strftime("%d-%m")
    members = load_members(chat_id)
    return [m for m in members if m.get("birthday") == today]


def list_birthdays(chat_id):
    members = load_members(chat_id)
    result = []
    for m in members:
        if m.get("birthday"):
            result.append(f'{m["name"] or "Без имени"} — {m["birthday"]}')
    return result

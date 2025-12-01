import os

def get_all_chat_ids():

    chat_ids = []
    if not os.path.exists("data"):
        return chat_ids

    for f in os.listdir("data"):
        if f.startswith("members_") and f.endswith(".json"):
            chat_id = f.replace("members_", "").replace(".json", "")
            try:
                chat_ids.append(int(chat_id))
            except ValueError:
                continue
    return chat_ids

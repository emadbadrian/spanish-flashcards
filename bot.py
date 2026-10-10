
import os
import json
import random
import hashlib
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

TIMEZONE = "Asia/Tehran"
START_HOUR = 8
END_HOUR = 20

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

WORDS_FILE = "words.json"
STATE_FILE = "word_state.json"


def load_words():
    with open(WORDS_FILE, "r", encoding="utf-8") as file:
        words = json.load(file)

    # Remove duplicate Spanish entries
    unique_words = []
    seen = set()

    for word in words:
        key = " ".join(word["spanish"].casefold().split())

        if key not in seen:
            seen.add(key)
            unique_words.append(word)

    return unique_words


def load_state(words):
    fingerprint = hashlib.sha256(
        json.dumps(
            [word["spanish"] for word in words],
            ensure_ascii=False
        ).encode("utf-8")
    ).hexdigest()

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            state = json.load(file)

        order = state["order"]
        next_index = state["next_index"]

        valid_order = (
            isinstance(order, list)
            and len(order) == len(words)
            and sorted(order) == list(range(len(words)))
        )

        if (
            state.get("fingerprint") == fingerprint
            and valid_order
            and isinstance(next_index, int)
            and 0 <= next_index <= len(words)
        ):
            return state

    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        pass

    # First run or vocabulary list changed
    order = list(range(len(words)))
    random.shuffle(order)

    return {
        "fingerprint": fingerprint,
        "order": order,
        "next_index": 0
    }


def save_state(state):
    temp_file = STATE_FILE + ".tmp"

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(state, file, ensure_ascii=False, indent=2)

    os.replace(temp_file, STATE_FILE)


def main():
    now = datetime.now(ZoneInfo(TIMEZONE))

    if not (START_HOUR <= now.hour < END_HOUR):
        print("Outside active hours. No message sent.")
        return

    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError("BOT_TOKEN or CHANNEL_ID is missing.")

    words = load_words()

    if not words:
        print("Vocabulary list is empty.")
        return

    state = load_state(words)

    # Start a new cycle only after every word was sent
    if state["next_index"] >= len(words):
        state["order"] = list(range(len(words)))
        random.shuffle(state["order"])
        state["next_index"] = 0

    word = words[state["order"][state["next_index"]]]

    message = (
        f"🇪🇸 {word['spanish']}\n"
        f"🇮🇷 {word['persian']}\n\n"
        f"💬 {word['example']}\n"
        f"{word['example_persian']}"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={"chat_id": CHANNEL_ID, "text": message},
        timeout=20
    )
    response.raise_for_status()

    # Advance only after Telegram confirms the message was sent
    state["next_index"] += 1
    save_state(state)

    print(
        f"Vocabulary message sent successfully: "
        f"{state['next_index']}/{len(words)} in this cycle."
    )


if __name__ == "__main__":
    main()

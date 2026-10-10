
import os
import json
import random
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# ساعات فعالیت ربات
TIMEZONE = "Europe/Berlin"
START_HOUR = 8
END_HOUR = 20

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")


def main():
    now = datetime.now(ZoneInfo(TIMEZONE))

    # در ساعات شب هیچ پیامی ارسال نشود
    if not (START_HOUR <= now.hour < END_HOUR):
        print("Outside active hours. No message sent.")
        return

    if not BOT_TOKEN or not CHANNEL_ID:
        raise RuntimeError("BOT_TOKEN or CHANNEL_ID is missing.")

    # خواندن فهرست لغات
    with open("words.json", "r", encoding="utf-8") as file:
        words = json.load(file)

    if not words:
        print("Vocabulary list is empty.")
        return

    word = random.choice(words)

    message = f"🇪🇸 {word['spanish']}\n"
    message += f"🇮🇷 {word['persian']}"

    if word.get("pronunciation"):
        message += f"\n🔊 {word['pronunciation']}"

    if word.get("example"):
        message += f"\n\n💬 {word['example']}"

    if word.get("example_persian"):
        message += f"\n{word['example_persian']}"

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL_ID,
            "text": message
        },
        timeout=20
    )
    response.raise_for_status()

    print("Vocabulary message sent successfully.")


if __name__ == "__main__":
    main()

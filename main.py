"""
Приложение для получения ответов с GPT.
"""

import configparser
import logging
import os
import sys

from dotenv import load_dotenv

from classes.databases import SqLite
from classes.gpts import Yandex
from classes.messengers import Telegram

load_dotenv()
yandex_oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")
yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=f"{config['DEFAULT']['NAME']}.log",
    filemode="a",
)


if __name__ == "__main__":
    telegram = Telegram(telegram_bot_token, telegram_chat_id)

    # Получаем из базы данных записи с предыдущими ответами.
    # Если они есть, то добавляем их в промпт для исключенияя повторов.
    database = SqLite()
    db_entries_list = database.get_from_db()
    if db_entries_list:
        DB_ENTRIES = ", ".join(
            f'"{db_entry[0]}"' for db_entry in db_entries_list if db_entry[0]
        )
    else:
        DB_ENTRIES = ""

    system_prompt = config["PROMPTS"]["SYSTEM_PROMPT"]
    user_prompt = config["PROMPTS"]["USER_PROMPT"]
    additional_prompt = config["PROMPTS"]["ADDITIONAL_PROMPT"]

    # Если в базе были записи, то добавляем
    # дополнительную строку в промпт для исключенияя повторов.
    if DB_ENTRIES != "":
        user_prompt += f" {additional_prompt} {DB_ENTRIES}."

    # Получаем ответ от GPT.
    yandex_gpt = Yandex(yandex_oauth_token, yandex_folder_id)
    response = yandex_gpt.generate_text(system_prompt, user_prompt)

    if not response or "error" in response:
        telegram.send_message(
            f"Ответ от YandexGPT c ошибкой. Response: `{str(response)}`"
        )
        sys.exit()

    response_text = response["result"]["alternatives"][0]["message"]["text"]

    # Отправляем ответ в Telegram.
    # Если отправка прошла успешно, то сохраняем полученную
    # идею в базу данных чтобы не использовать ее повторно.
    success = telegram.send_message(response_text)

    if success:
        # "Вычленяем" идею из ответа и сохраняем ее в базу данных.
        db_entry = response_text.split(".")[0].split("Идея: ")[1]
        database.write_to_db(db_entry)

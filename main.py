"""
Приложение для получения ответов с GPT.
"""

import configparser
import logging
import os

from dotenv import load_dotenv

from classes.databases import SqLite
from classes.gpts import ProxyAPI
from classes.messengers import Telegram

load_dotenv()
proxy_api_key = os.getenv("PROXY_API_KEY")
yandex_oauth_token = os.getenv("YANDEX_OAUTH_TOKEN")

telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
telegram_admin_chat_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=f"{config['PROJECT']['NAME']}.log",
    filemode="w",
)


if __name__ == "__main__":
    telegram = Telegram(telegram_bot_token)

    # Получаем из базы данных записи с предыдущими ответами.
    # Если они есть, то добавляем их в промпт для исключенияя повторов.
    database = SqLite()
    db_ideas_list = database.get_from_db()

    if db_ideas_list:
        DB_IDEAS = ", ".join(
            f'"{db_entry[0]}"' for db_entry in db_ideas_list if db_entry[0]
        )
    else:
        DB_IDEAS = ""

    additional_prompt = config["PROMPTS"]["ADDITIONAL_PROMPT"]

    # Если в базе были записи, то добавляем
    # дополнительную строку в промпт для исключенияя повторов.
    if DB_IDEAS != "":
        config["PROMPTS"]["USER_PROMPT"] += f" {additional_prompt} {DB_IDEAS}."

    # Получаем ответ от GPT.
    gpt = ProxyAPI(proxy_api_key)
    # gpt = Yandex(yandex_oauth_token)

    response = gpt.openai(
        config["PROMPTS"]["SYSTEM_PROMPT"],
        config["PROMPTS"]["USER_PROMPT"],
        model="gpt-4o",
    )

    if response["status"]:
        response_text = response["text"]

        # Отправляем ответ в Telegram.
        # Если отправка прошла успешно, то сохраняем полученную
        # идею в базу данных чтобы не использовать ее повторно.
        is_sent = telegram.send_message(telegram_chat_id, response_text)

        if is_sent:
            # "Вычленяем" идею из ответа и сохраняем ее в базу данных
            # для последующего использования в ADDITIONAL_PROMPT.
            db_entry = response_text.split("\n")[0].split("Идея: ")[1]
            database.write_to_db(db_entry)
    else:
        telegram.send_message(
            telegram_admin_chat_id, f"Ответ от GPT c ошибкой: {response['text']}"
        )

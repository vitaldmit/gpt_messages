"""
В этом файле хранятся классы для работы с мессенджерами.
Пока только Telegram.
"""

from abc import ABC, abstractmethod

import requests


class Messenger(ABC):
    """
    Абстрактный класс для работы с мессенджерами.
    """

    @abstractmethod
    def send_message(self, message: str) -> bool:
        """
        Отправка сообщения.
        """


# Классы для работы с Telegram.
class Telegram(Messenger):
    """
    Класс для работы с Telegram.
    """

    def __init__(self, bot_token: str | None, chat_id: str | None) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message: str) -> bool:
        """
        Отправка сообщения в Telegram.
        """
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

        data = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

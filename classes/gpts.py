"""
В этом файле хранятся классы для работы с различными GPT.
Пока только YandexGPT.
"""

import configparser
from abc import ABC, abstractmethod

import requests

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

project_name = config["DEFAULT"]["NAME"]


# Классы для работы с GPT.
class GPT(ABC):
    """
    Абстрактный класс для работы с GPT.
    """

    @abstractmethod
    def generate_text(self, system_prompt: str, user_prompt: str) -> dict | None:
        """
        Абстрактный метод для генерации текста.
        """


class Yandex(GPT):
    """
    Класс для работы с API YandexGPT.
    """

    def __init__(self, oauth_token: str | None, folder_id: str | None) -> None:
        self.iam_token = self._get_iam_token(oauth_token)
        self.folder_id = folder_id

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}",
        }

    def _get_iam_token(self, oauth_token: str | None) -> str | None:
        """
        Получение IAM-токена.
        """
        url = config["YANDEX_GPT"]["IAM_TOKEN_URL"]
        data = {"yandexPassportOauthToken": oauth_token}

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()["iamToken"]
        except (requests.exceptions.RequestException, KeyError):
            return None

    def generate_text(self, system_prompt: str, user_prompt: str) -> dict | None:
        """
        Функция для генерации текста с помощью модели YandexGPT.
        """

        url = config["YANDEX_GPT"]["LLM_URL"]

        data = {
            "modelUri": f"gpt://{self.folder_id}/{config['YANDEX_GPT']['LLM_MODEL']}",
            "completionOptions": {
                "stream": config.getboolean("YANDEX_GPT", "STREAM"),
                "temperature": config.getfloat("YANDEX_GPT", "TEMPERATURE"),
                "maxTokens": config["YANDEX_GPT"]["MAXTOKENS"],
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": user_prompt},
            ],
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=10)
        except requests.exceptions.RequestException as e:
            return None

        return resp.json()

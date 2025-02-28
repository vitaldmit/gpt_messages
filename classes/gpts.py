"""
В этом файле хранятся классы для работы с различными GPT.
"""

import configparser
from abc import ABC

import requests

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

project_name = config["PROJECT"]["NAME"]


# Классы для работы с GPT.
class GPT(ABC):
    """
    Абстрактный класс для работы с GPT.
    """

    def __init__(self, api_key):
        self.api_key = api_key

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }


class Yandex(GPT):
    """
    Класс для работы с API YandexGPT.
    """

    def __init__(self, oauth_token, folder_id):
        self.iam_token = self._get_iam_token(oauth_token)
        self.folder_id = folder_id
        super().__init__(self.iam_token)

    def _get_iam_token(self, oauth_token):
        """
        Получение IAM-токена.
        """
        url = config["YANDEX"]["IAM_TOKEN_URL"]
        data = {"yandexPassportOauthToken": oauth_token}

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()["iamToken"]
        except (requests.exceptions.RequestException, KeyError):
            return None

    def generate_text(self, system_prompt, user_prompt):
        """
        Функция для генерации текста с помощью модели YandexGPT.
        """

        url = config["YANDEX"]["MODEL_URL"]

        data = {
            "modelUri": f"gpt://{self.folder_id}/{config['YANDEX']['MODEL']}",
            "completionOptions": {
                "stream": config.getboolean("YANDEX", "STREAM"),
                "temperature": config.getfloat("YANDEX", "TEMPERATURE"),
                "maxTokens": config["YANDEX"]["MAXTOKENS"],
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": user_prompt},
            ],
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)

            response = {
                "status": resp.status_code,
                "text": resp.json()["result"]["alternatives"][0]["message"]["text"],
            }

            return response
        except (requests.exceptions.RequestException, KeyError):
            return None


class ProxyAPI(GPT):
    """
    Класс для работы с API ProxyAPI.
    https://proxyapi.ru/docs
    """

    def __init__(self, api_key):
        self.api_key = api_key
        super().__init__(self.api_key)

    def openai(self, system_prompt, user_prompt, model):
        """
        Метод для генерации текста через ProxyAPI.
        """
        url = config["PROXY_API"]["OPEN_AI_URL"]

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": config.getint("PROXY_API", "MAXTOKENS"),
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)

            response = {
                "status": resp.status_code,
                "text": resp.json()["choices"][0]["message"]["content"],
            }

            return response
        except (requests.exceptions.RequestException, KeyError):
            return None

    def claude(self, system_prompt, user_prompt, model):
        """
        Метод для генерации текста через ProxyAPI.
        """
        url = config["PROXY_API"]["ANTHROPIC_URL"]

        data = {
            "model": model,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": config.getint("PROXY_API", "MAXTOKENS"),
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)

            response = {
                "status": resp.status_code,
                "text": resp.json()["content"][0]["text"],
            }

            return response
        except (requests.exceptions.RequestException, KeyError):
            return None

    def gemini(self, system_prompt, user_prompt, model):
        """
        Метод для генерации текста через ProxyAPI.
        """
        url = config["PROXY_API"]["GOOGLE_URL"] + model + ":generateContent"

        data = {
            "model": model,
            "contents": [
                {"role": "user", "parts": [{"text": system_prompt}]},
                {"role": "user", "parts": [{"text": user_prompt}]},
            ],
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)
            print(f"{resp.json()=}")

            response = {
                "status": resp.status_code,
                "text": resp.json()["candidates"][0]["content"]["parts"][0]["text"],
            }

            return response
        except (requests.exceptions.RequestException, KeyError):
            return None

    def deepseek(self, system_prompt, user_prompt, model):
        """
        Метод для генерации текста через ProxyAPI.
        """
        url = config["PROXY_API"]["DEEPSEEK_URL"]

        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": config.getint("PROXY_API", "MAXTOKENS"),
        }

        try:
            resp = requests.post(url, headers=self.headers, json=data, timeout=30)

            response = {
                "status": resp.status_code,
                "text": resp.json()["choices"][0]["message"]["content"],
            }

            return response
        except (requests.exceptions.RequestException, KeyError):
            return None

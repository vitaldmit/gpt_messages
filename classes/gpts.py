"""
В этом файле хранятся классы для работы с различными GPT.
"""

import configparser
import os
from abc import ABC

import requests
from dotenv import load_dotenv

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

project_name = config["PROJECT"]["NAME"]


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

    def __init__(self, oauth_token):
        load_dotenv()
        self.iam_token = self._get_iam_token(oauth_token)
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.max_tokens = config.getint("YANDEX", "MAX_TOKENS")
        super().__init__(self.iam_token)

    def _get_iam_token(self, oauth_token):
        """
        Получение IAM-токена.
        """
        url = "https://iam.api.cloud.yandex.net/iam/v1/tokens"
        data = {"yandexPassportOauthToken": oauth_token}

        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()["iamToken"]
        except (requests.exceptions.RequestException, KeyError):
            return None

    def yandex(self, system_prompt, user_prompt, model):
        """
        Функция для генерации текста с помощью модели YandexGPT.
        """

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        data = {
            "modelUri": f"gpt://{self.folder_id}/{model}",
            "completionOptions": {
                "stream": config.getboolean("YANDEX", "STREAM"),
                "temperature": config.getfloat("YANDEX", "TEMPERATURE"),
                "maxTokens": config["YANDEX"]["MAX_TOKENS"],
            },
            "messages": [
                {"role": "system", "text": system_prompt},
                {"role": "user", "text": user_prompt},
            ],
        }

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)

            return {
                "status": True,
                "text": response.json()["result"]["alternatives"][0]["message"]["text"],
            }

        except (requests.exceptions.RequestException, KeyError) as e:
            return {
                "status": False,
                "text": f"Yandex API error: {e}",
            }


class ProxyAPI(GPT):
    """
    Класс для работы с API ProxyAPI.
    https://proxyapi.ru/docs
    """

    def __init__(self, api_key):
        self.api_key = api_key
        self.max_tokens = config.getint("PROXY_API", "MAX_TOKENS")
        super().__init__(self.api_key)

    def openai(self, system_prompt, user_prompt, model):
        """
        Функция для генерации текста с помощью модели OpenAI.
        """
        from openai import OpenAI, OpenAIError  # pylint: disable=C

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.proxyapi.ru/openai/v1",
        )

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=self.max_tokens,
            )

            return {
                "status": True,
                "text": completion.choices[0].message.content,
            }

        except OpenAIError as e:
            return {
                "status": False,
                "text": f"OpenAI API error: {e}",
            }

    def claude(self, system_prompt, user_prompt, model):
        """
        Функция для генерации текста с помощью модели Claude.
        """
        from anthropic import Anthropic, AnthropicError  # pylint: disable=C

        client = Anthropic(
            api_key=self.api_key,
            base_url="https://api.proxyapi.ru/anthropic",
        )

        try:
            completion = client.messages.create(
                model=model,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                max_tokens=config.getint("PROXY_API", "MAX_TOKENS"),
            )

            return {
                "status": True,
                "text": completion.content[0].text.strip(),
            }

        except AnthropicError as e:
            return {
                "status": False,
                "text": f"Anthropic API error: {e}",
            }

    def deepseek(self, system_prompt, user_prompt, model):
        """
        Функция для генерации текста с помощью модели DeepSeek.
        """
        from openai import OpenAI, OpenAIError  # pylint: disable=C

        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.proxyapi.ru/deepseek",
        )

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=config.getint("PROXY_API", "MAX_TOKENS"),
            )

            return {
                "status": True,
                "text": completion.choices[0].message.content,
            }

        except OpenAIError as e:
            return {
                "status": False,
                "text": f"Deepseek API error: {e}",
            }

    def gemini(self, system_prompt, user_prompt, model):
        """
        Функция для генерации текста с помощью модели Gemini.
        """
        url = config["PROXY_API"]["GOOGLE_URL"] + model + ":generateContent"

        data = {
            "model": model,
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": system_prompt},
                        {"text": user_prompt},
                    ],
                },
            ],
        }

        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)

            return {
                "status": response.status_code,
                "text": response.json()["candidates"][0]["content"]["parts"][0]["text"],
            }

        except (requests.exceptions.RequestException, KeyError) as e:
            return {
                "status": False,
                "text": f"Gemini API error: {e}",
            }

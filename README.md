# Приложение для работы с GPT моделями

Простое расширяемое Python-приложение, использующее модели для получения информации с GPT. 
На данный момент добавлена модель **`Yandex GPT`**, **но можно добавить любую другую модель**.

## Возможности

- Получение ответа от модели GPT
- Использование модели YandexGPT Lite
- Простая интеграция с API
- Поддержка потоковой передачи (настраиваемая)

## Требования

- Python 3.9+
- Аккаунт Yandex Cloud
- IAM токен
- ID папки из Yandex Cloud

## Установка

1. Настройте виртуальное окружение:
```sh
python -m venv gpt_messages
cd gpt_messages
source bin/activate
mkdir src; cd src
```

2. Клонируйте репозиторий
```sh
git clone https://github.com/vitaldmit/gpt_messages.git .
```

3. Установите зависимости
```sh
pip install -r requirements.txt
```

## Настройка

Создайте файл `.env` с помощью команды:
```sh
mv .env.example .env
```

## Использование

Запустите приложение с помощью команды:
```sh
python main.py
```

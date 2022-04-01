"""Получает данные о статусе домашней работы и отправляет их в телеграм"""


import logging
import os
import time

import requests

import telegram
# from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    ...


def get_api_answer(current_timestamp):
    """Step 2: Получаем данные о статусе домашних работ за месяц."""

    timestamp = current_timestamp or int(time.time())
    month = 2629743
    params = {'from_date': timestamp - month}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        response = response.json()
        return response
    except Exception as error:
        logging.error(error)
        return None


def check_response(response):
    """Step 3: Проверяем ответ API на корректность."""
    
    # if 'homeworks' in response:
    try:
        homeworks = response.get('homeworks')
        return homeworks
    except Exception as error:
        logging.error(error)
        return None


def parse_status(homework):
    """Step 4: Извлекаем статус последней домашней работы"""

    try:
        homework_name = homework.get('lesson_name')
        homework_status = homework.get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(error)
        return None


def check_tokens():
    """Step 1: Проверяем доступность переменных окружения, которые необходимы для работы программы."""
    
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
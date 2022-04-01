"""Получает данные о статусе домашней работы и отправляет их в телеграм."""


import logging
import os
import time

import requests
import telegram
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


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Step 5: Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.info(f'Сообщение: {message} - успешно отправлено')
    except Exception as error:
        logging.error(error)


def get_api_answer(current_timestamp):
    """Step 2: Получает данные о статусе домашних работ за месяц."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        response = response.json()
        logging.info('step 2')
        return response
    except Exception as error:
        logging.error(error)
        return None


def check_response(response):
    """Step 3: Проверяет ответ API на корректность."""
    try:
        homeworks = response.get('homeworks')
        return homeworks
    except Exception as error:
        logging.error(error)
        return None


def parse_status(homework):
    """Step 4: Извлекает статус последней домашней работы."""
    try:
        homework_name = homework.get('lesson_name')
        homework_status = homework.get('status')
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(error)
        return None


def check_tokens():
    """Step 1: Проверяет доступность переменных окружения,
    которые необходимы для работы программы.
    """
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        logging.info('step 1')
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    if check_tokens():
        response = get_api_answer(1)
        homework_list = check_response(response)
        if len(homework_list) > 0:
            message = parse_status(homework_list[0])
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            send_message(bot, message)
#    current_timestamp = int(time.time())
#
#    ...
#
#    while True:
#        try:
#            response = ...
#
#            ...
#
#            current_timestamp = ...
#            time.sleep(RETRY_TIME)
#
#        except Exception as error:
#            message = f'Сбой в работе программы: {error}'
#            ...
#            time.sleep(RETRY_TIME)
#        else:
#            ...


if __name__ == '__main__':
    main()

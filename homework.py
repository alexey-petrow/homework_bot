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

RETRY_TIME = 6
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)


def send_message(bot, message):
    """Step 5: Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info(f'Сообщение: {message} - успешно отправлено')
    except Exception as error:
        logger.error(error)


def get_api_answer(current_timestamp):
    """Step 2: Получает данные о статусе домашних работ за месяц."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        response = response.json()
        logger.info('step 2 - выполнен')
        return response
    except Exception as error:
        logger.error(error)


def check_response(response):
    """Step 3: Проверяет ответ API на корректность."""
    try:
        homeworks = response['homeworks']
        logger.info('step 3 - выполнен')
        return homeworks
    except Exception as error:
        logger.error(error)


def parse_status(homework):
    """Step 4: Извлекает статус последней домашней работы."""
    try:
        homework_name = homework['lesson_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        logger.info('step 4 - выполнен')
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logger.error(error)


def check_tokens():
    """Step 1: Проверяет доступность переменных окружения.

    Которые необходимы для работы программы.
    """
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        logger.info('step 1 - выполнен')
        return True
    else:
        logger.critical('Отсутствуют переменные окружения')
        return False


def main():
    """Основная логика работы бота.

    Проверяет статус последней работы и в случае изменения статуса
    отпрявляет уведомление в телеграм чат.
    """
    # from_date = 01.01.2021 00:00:00
    from_date = 1609448400
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    errors_list = []
    while check_tokens():
        try:
            response = get_api_answer(from_date)
            homework_list = check_response(response)
            if len(homework_list) > 0:
                message = parse_status(homework_list[0])
                time.sleep(RETRY_TIME)
                new_response = get_api_answer(from_date)
                new_homework_list = check_response(new_response)
                if len(new_homework_list) > 0:
                    new_message = parse_status(new_homework_list[0])
                    if message == new_message:
                        send_message(bot, new_message)
                    else:
                        logger.debug('Статус работы не изменился.')
                else:
                    raise TypeError('Переменная не содержит список')
            else:
                raise TypeError('Переменная не содержит список')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

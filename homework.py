"""Получает данные о статусе домашней работы и отправляет их в телеграм."""


import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (
    YandexApiResponseError, UnknownHomeworkStatus, ResponseHasNoHomeworks)

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
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    logger.info(f'step 2 - status code: {response.status_code}')
    status_code = response.status_code
    if status_code != 200:
        raise YandexApiResponseError(
            f'Ошибка ответа от сервера Яндекс. Код ответа: {status_code}')
    response = response.json()
    logger.info('step 2 - выполнен')
    return response


def check_response(response):
    """Step 3: Проверяет ответ API на корректность."""
    if isinstance(response, dict):
        if 'homeworks' in response:
            homeworks = response['homeworks']
            logger.info('step 3 - выполнен')
            if isinstance(homeworks, list):
                return homeworks
            else:
                raise TypeError('Функция возвращает не список')
        else:
            raise ResponseHasNoHomeworks(
                'Проверяемый ответ от сервера не содержит ключ "homeworks"')
    else:
        raise TypeError('Функция получает не словарь')


def parse_status(homework):
    """Step 4: Извлекает статус последней домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    if homework_status not in HOMEWORK_STATUSES:
        raise UnknownHomeworkStatus(
            f'{homework_status} - неизвестный статус домашней работы')

    verdict = HOMEWORK_STATUSES[homework_status]
    logger.info('step 4 - выполнен')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


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
    отпрявляет уведомление в телеграм чат, а в случает ошибки отправляет
    в телеграм чат однократное уведомление об ошибке.
    """
    # from_date = 01.01.2021 00:00:00
    from_date = 1609448400
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    errors_list = []
    last_homework_status = ['has no status yet']
    while check_tokens():
        try:
            response = get_api_answer(from_date)
            homework_list = check_response(response)
            message = parse_status(homework_list[0])
            if message not in last_homework_status:
                send_message(bot, message)
                last_homework_status[0] = message
            else:
                logger.debug('Статус работы не изменился.')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
            if message not in errors_list:
                send_message(bot, message)
                errors_list.append(message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()

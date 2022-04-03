class YandexApiResponseError(Exception):
    """Ошибка ответа от сервера Яндекс.

    Статус ответа не равен 200.
    """

    pass


class UnknownHomeworkStatus(Exception):
    """Неизвестный статус домашней работы.

    Статус домашней работы отсутствует в списке ожидаемых.
    """

    pass


class ResponseHasNoHomeworks(Exception):
    """Принемаемый функцией аргумент не содержит ожидаемого ключа."""

    pass

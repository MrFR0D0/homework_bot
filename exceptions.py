class NoToken(Exception):
    """Обработка исключения отсутствия токена."""

    def __init__(self, *args):
        """Конструктор класса исключения."""
        txt = f'''Отсутствует обязательная переменная окружения: {args}
                    Программа принудительно остановлена.'''
        super().__init__(txt)


class AnswerAPI(Exception):
    """Обработка исключения овета API."""

    def __init__(self):
        """Конструктор класса исключения."""
        txt = 'API домашки возвращает код, отличный от 200'
        super().__init__(txt)


class StatusAPI(Exception):
    """Обработка исключения статуса API."""

    def __init__(self):
        """Конструктор класса исключения."""
        txt = 'Неожиданный статус домашней работы'
        super().__init__(txt)


class NoHWName(Exception):
    """Обработка исключения отсутствия имени ДЗ."""

    def __init__(self):
        """Конструктор класса исключения."""
        txt = 'Отсутсвует имя домашки'
        super().__init__(txt)


class CheckAPI(Exception):
    """Обработка исключения ответа API."""

    def __init__(self, wait_type, fact_type):
        """Конструктор класса исключения."""
        txt = f'''Ответ API не соответствует документации ЯП.
        Тип данны {fact_type} вместо ожидаемого {wait_type}'''
        super().__init__(txt)


class NoKeyAPI(Exception):
    """Обработка исключения ответа API."""

    def __init__(self, key):
        """Конструктор класса исключения."""
        txt = f'''Ответ API не соответствует документации ЯП.
        Отсутствует ключ {key}'''
        super().__init__(txt)


class CantSentTG(Exception):
    """Обработка невозможности отправки TG."""

    def __init__(self):
        """Конструктор класса исключения."""
        txt = 'В этот раз не удалось отправить TG'
        super().__init__(txt)


class EndpointNA(Exception):
    """Обработка исключения статуса API."""

    def __init__(self):
        """Конструктор класса исключения."""
        txt = 'Эндпоинт недоступен'
        super().__init__(txt)

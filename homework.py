import logging
import os
import sys
import requests

import time
from dotenv import load_dotenv
from telebot import TeleBot
import exceptions
from logging import StreamHandler

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN is None:
        logging.critical(
            f'Отсутствует обязательная переменная окружения: {PRACTICUM_TOKEN}'
        )
        raise exceptions.NO_TOKEN('PRACTICUM_TOKEN')
    elif TELEGRAM_TOKEN is None:
        logging.critical(
            f'Отсутствует обязательная переменная окружения: {TELEGRAM_TOKEN}'
        )
        raise exceptions.NO_TOKEN('TELEGRAM_TOKEN')
    elif TELEGRAM_CHAT_ID is None:
        logging.critical(
            f'''Отсутствует обязательная переменная
            окружения: {TELEGRAM_CHAT_ID}'''
        )
        raise exceptions.NO_TOKEN('TELEGRAM_CHAT_ID')


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.debug('Направлено сообщение в TG')
    except Exception:
        logging.error(exceptions.cant_sent_TG())


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException as e:
        logging.error('Эндпоинт недоступен')
        print('Ошибка запроса:', e)
        raise exceptions.endpoint_NA()
    if homework_statuses.status_code != 200:
        logging.error('API домашки возвращает код, отличный от 200')
        raise exceptions.ANSWER_API()
    return homework_statuses.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if type(response) != dict:
        raise TypeError('exceptions.check_API')
    if 'homeworks' not in response.keys():
        logging.error('Отсутствует ожидаемый ключ "homeworks" в ответе API')
        raise exceptions.check_API()
    if type(response['homeworks']) != list:
        raise TypeError(exceptions.check_API())


def parse_status(homework):
    """Получение статуса домашки."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise exceptions.NO_HW_NAME()
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        logging.error('Неожиданный статус домашней работы')
        raise exceptions.status_API()
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    old_message = None
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - 12096000
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s',
        level=logging.DEBUG,
    )
    logger = logging.getLogger(__name__)
    handler = StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    while True:
        try:
            api_answer = get_api_answer(timestamp)
            check_response(api_answer)
            message = parse_status(api_answer['homeworks'][0])
        except Exception as error:
            print(error)
            message = f'Сбой в работе программы: {error}'
        if message == old_message:
            logging.debug('В ответе отсутвует новый статус')
        else:
            send_message(bot, message)
        old_message = message
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

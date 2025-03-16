import logging
import os
import sys
import time
from http import HTTPStatus
from logging import StreamHandler

import requests
import telebot
from dotenv import load_dotenv
from telebot import TeleBot

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

ONE_MONTH = 2629743
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}

logger = logging.getLogger(__name__)
handler = StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    troubles = []
    for token in tokens.items():
        if token[1] is None:
            troubles.append(token)
    if troubles:
        logger.critical(
            'Проблема с обязательными переменными окружения!'
            f'Отсутствует: {troubles}',
        )
        raise exceptions.NoToken(*troubles)


def send_message(bot, message):
    """Отправляет сообщение в Telegram-чат."""
    try:
        logger.debug('Начало отправления сообщения в TG')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение в TG направлено')
        return True
    except (requests.RequestException, telebot.apihelper.ApiException):
        logger.error(exceptions.CantSentTG())
        return False


def get_api_answer(timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    try:
        logger.debug('Начало запроса к API')
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
        )
    except requests.RequestException:
        raise exceptions.EndpointNA()
    if homework_statuses.status_code != HTTPStatus.OK:
        raise exceptions.AnswerAPI()
    return homework_statuses.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError(exceptions.CheckAPI(dict, type(response)))
    if 'homeworks' not in response.keys():
        raise exceptions.NoKeyAPI('homeworks')
    hw_data = response['homeworks']
    if not isinstance(hw_data, list):
        raise TypeError(exceptions.CheckAPI(list, type(hw_data)))
    return hw_data


def parse_status(homework):
    """Получение статуса домашки."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise exceptions.NoHWName()
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise exceptions.StatusAPI()
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - ONE_MONTH
    message_error = None
    while True:
        try:
            api_answer = get_api_answer(timestamp)
            hw_data = check_response(api_answer)
            if hw_data:
                message = parse_status(hw_data[0])
                tg_message_sent = send_message(bot, message)
                if tg_message_sent:
                    timestamp = api_answer.get('current_date', timestamp)
                    message_error = None
            else:
                logger.debug('В ответе отсутвует новый статус')
        except Exception as error:
            logger.error(error)
            if message_error != error:
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                message_error = error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s, %(levelname)s, %(message)s',
        level=logging.DEBUG,
    )
    main()

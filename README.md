# Бот-ассистент

### Описание проекта

Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнаёт статус вашей домашней работы: взята ли ваша домашка в ревью, проверена ли она, а если проверена — то принял её ревьюер или вернул на доработку.

Бот может:
- раз в 10 минут опрашивать API сервиса Практикум.Домашка и проверять статус отправленной на ревью домашней работы;
- при обновлении статуса анализировать ответ API и отправлять вам соответствующее уведомление в Telegram;
- логировать свою работу и сообщать вам о важных проблемах сообщением в Telegram.

### Стек технологий
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=for-the-badge&logo=telegram?logoColor=white)
### Как запустить проект

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:MrFR0D0/homework_bot.git
```
```
cd homework_bot
```

Создать и активировать виртуальную среду:
```
python3 -m venv venv
```
```
source venv/bin/activate
```

Установить зависимости из файла `requirements.txt`:
```
pip install -r requirements.txt
```

Запустить файл `homework.py`:
```
python homework.py
```
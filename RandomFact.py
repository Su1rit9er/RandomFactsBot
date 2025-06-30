import datetime as dt
import logging
import random
import sqlite3
import threading
import time

import pytz
import telebot
from telebot import types

bot = telebot.TeleBot('')

user_states = {}
AWAITING_FACT = 'awaiting_fact'

conn = sqlite3.connect(r"")
cursor = conn.cursor()

cursor.execute("SELECT text FROM fact")
facts = cursor.fetchall()
conn.close()


# старт и кнопка случайного факта
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        logger.info("Получена команда /start от пользователя %s", message.chat.id)

        user_id = message.chat.id
        username = message.from_user.username
        moscow = pytz.timezone('Europe/Moscow')
        created_at = dt.datetime.now(moscow).isoformat()

        with sqlite3.connect(r"") as conn2:
            cursor1 = conn2.cursor()
            cursor1.execute("""
                INSERT INTO ids (user_id, username, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET username=excluded.username
            """, (user_id, username, created_at))
            conn2.commit()

        bot.send_message(message.chat.id, 'Привет! Я отправляю тебе интересный факт каждый день в 20:00 по МСК, '
                                          'также ты можешь сам посмотреть случайный факт с помощью кнопки '
                                          '«🎲 Случайный факт» или предложить свой факт с помощью кнопки '
                                          '«💡 Предложить факт»\n\n/help - команда для обратной связи')

        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        fact_button = types.KeyboardButton('🎲 Случайный факт')
        suggest_button = types.KeyboardButton('💡 Предложить факт')
        keyboard.add(fact_button, suggest_button)

        bot.send_message(message.chat.id, 'Нажми кнопку ниже, чтобы получить случайный факт!', reply_markup=keyboard)

    except telebot.apihelper.ApiException as e:
        logger.error("Ошибка при отправке сообщения: %s", e)
        bot.send_message(message.chat.id, "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.")
    except Exception as e:
        logger.exception("Неизвестная ошибка: %s", e)
        bot.send_message(message.chat.id, "Произошла неизвестная ошибка. Пожалуйста, свяжитесь с поддержкой.")


# команда help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, 'Если возникнут ошибки или баги сразу сообщите мне!\n\nСвязаться с разработчиком - '
                          '@Su1rit9er\n\nФакты могут повторятся.')


# обработка текста
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.chat.id
    username = message.from_user.username
    moscow = pytz.timezone('Europe/Moscow')
    if user_states.get(user_id) == AWAITING_FACT:
        fact_text = message.text.strip()
        if fact_text:
            created_at = dt.datetime.now(moscow).isoformat()

            with sqlite3.connect(r"") as conn3:
                cursor3 = conn3.cursor()
                cursor3.execute("""
                    INSERT INTO suggested_facts (username, fact, created_at)
                    VALUES (?, ?, ?)
                """, (username, fact_text, created_at))
                conn3.commit()

            bot.send_message(user_id, "Спасибо! Твой факт отправлен ✅")
        else:
            bot.send_message(user_id, "Пожалуйста, отправь не пустой текст факта.")

        user_states.pop(user_id, None)
        return

    if message.text == '🎲 Случайный факт':
        bot.send_message(user_id, random.choice(facts)[0])

    elif message.text == '💡 Предложить факт':
        user_states[user_id] = AWAITING_FACT
        bot.send_message(user_id, "Отправь мне интересный факт, и я передам его ✍️")


# функция рассылки

def send_fact():
    try:
        with sqlite3.connect(r"") as conn2:
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT user_id FROM ids")
            user_ids = [row[0] for row in cursor2.fetchall()]

        fact = random.choice(facts)[0]
        for user_id in user_ids:
            try:
                bot.send_message(user_id, fact)
            except Exception as e:
                logger.error(f"Ошибка при отправке пользователю {user_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка в send_fact: {e}")


# функция планировщика
last_sent_date = None


def scheduler():
    global last_sent_date
    moscow = pytz.timezone('Europe/Moscow')
    while True:
        now = dt.datetime.now(moscow)
        if now.strftime("%H:%M") == "20:00" and (last_sent_date != now.date()):
            send_fact()
            last_sent_date = now.date()
            logger.info("Факт успешно отправлен пользователям")
        time.sleep(30)


def send_one_time_message():
    try:
        with sqlite3.connect(r"") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM ids")
            user_ids = [row[0] for row in cursor.fetchall()]

        for user_id in user_ids:
            try:
                bot.send_message(
                    user_id,
                    "Привет! Напомню, что ты можешь предложить предложить свой факт."
                )
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Ошибка при отправке одноразового сообщения пользователю {user_id}: {e}")

        logger.info("Одноразовое сообщение успешно отправлено всем пользователям.")
    except Exception as e:
        logger.exception("Ошибка при выполнении одноразовой рассылки:")


# логгирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

threading.Thread(target=scheduler, daemon=True).start()

# send_one_time_message()

bot.polling(none_stop=True)
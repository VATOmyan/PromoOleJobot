
from config import token
import telebot
from apscheduler.schedulers.blocking import BlockingScheduler
import sqlite3
from datetime import datetime

# Создаем бота и указываем токен
API_TOKEN = token
bot = telebot.TeleBot(API_TOKEN)

# Инициализация базы данных SQLite
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы пользователей, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT
)
''')
conn.commit()

# Функция добавления пользователя в базу данных
def add_user(user_id, username, first_name, last_name):
    try:
        cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Пользователь уже существует в базе данных

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    add_user(user_id, username, first_name, last_name)
    bot.send_message(message.chat.id, "Привет! Вы добавлены в базу данных.")

# Функция отправки сообщения всем пользователям
def send_message_to_all_users():
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    for user in users:
        user_id = user[0]
        try:
            bot.send_message(user_id, "Привет!")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

# Планировщик для ежедневной отправки сообщений в 5 часов вечера
scheduler = BlockingScheduler()
scheduler.add_job(send_message_to_all_users, 'cron', hour=14, minute=0)

# Запуск планировщика в отдельном потоке
import threading
scheduler_thread = threading.Thread(target=scheduler.start)
scheduler_thread.start()

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
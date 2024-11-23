import telebot
import pyautogui
import sqlite3
import os

TOKEN = "TOKEN"
bot = telebot.TeleBot(TOKEN)

def get_app_path(phrase):
    with sqlite3.connect('triggers.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT app_path FROM triggers WHERE phrase=?", (phrase,))
        result = cursor.fetchone()
        return result

def print_text(text):
    pyautogui.typewrite(text)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я ваш помощник.\n"
        "Напишите /help, чтобы получить список доступных команд."
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Вот что я могу:\n"
        "/help - Показать этот список.\n"
        "/list - Показать все триггеры, добавленные в базу.\n"
        "Просто напишите фразу, и я постараюсь открыть нужное приложение или выполнить действие.\n\n"
        "Пример использования:\n"
        "1. Напишите 'Открой браузер', чтобы открыть браузер.\n"
        "2. Напишите 'Напиши привет', чтобы напечатать текст 'привет'."
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['list'])
def show_triggers(message):
    with sqlite3.connect('triggers.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT phrase, app_path FROM triggers")
        triggers = cursor.fetchall()
        
    if triggers:
        trigger_list = "\n".join([f"{trigger[0]} -> {trigger[1]}" for trigger in triggers])
        bot.send_message(message.chat.id, f"Список триггеров:\n{trigger_list}")
    else:
        bot.send_message(message.chat.id, "Триггеров нет.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    if user_id != WRITEYOURID:
        bot.send_message(user_id, "У вас нет доступа к этой функции.")
        return

    command = message.text

    if command.startswith("Напиши"):
        text_to_type = command[len("Напиши "):].strip()
        print_text(text_to_type)
        bot.send_message(user_id, f"Печатаю: {text_to_type}")
        return

    app_path = get_app_path(command)
    if app_path:
        os.startfile(app_path[0]) 
        bot.send_message(user_id, f"Запускаю приложение: {app_path[0]}")
    else:
        bot.send_message(user_id, "Команда не найдена")

bot.polling()

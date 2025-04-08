import telebot
import datetime
import time
import threading
import random
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, ContextTypes, ApplicationBuilder

bot = telebot.TeleBot("8115958836:AAGev4zcxpbL9ObR37RaFAZyTBbBkEuvJ5A")
# Переменная для хранения дистанции
distance = 10
comp_date_str = "2025-05-24"
comp_date = datetime.datetime.strptime(comp_date_str, "%Y-%m-%d").date()
signal_time = "08:00"

# Получаем текущую дату и время
current_datetime = datetime.datetime.now()
# Получаем только текущую дату
current_date = current_datetime.date()
# Определяем номер дня недели (0 - понедельник, 6 - воскресенье)
day_of_week_number = current_date.weekday()
# Определяем название дня недели
day_of_week_name = current_date.strftime("%A")  # Полное название дня недели
# day_of_week_name_short = current_date.strftime("%a")  # Короткое название дня недели
print(f"Текущая дата: {current_date}")
print(f"Номер дня недели: {day_of_week_number}")
print(f"Название дня недели: {day_of_week_name}")

# Получаем от пользователя дату соревнований
@bot.message_handler(commands=['date_of_start'])
def date_of_set(message):
    bot.reply_to(message, "Введите дату соревнований ГГГГ-ММ-ДД. Для отмены введите /cancel.")
    bot.register_next_step_handler(message, date_settings)

def date_settings(message):
    global comp_date
    if message.text == '/cancel':
        bot.reply_to(message, "Настройка отменена.")
        return
    comp_date_str = message.text
    comp_date = datetime.datetime.strptime(comp_date_str, "%Y-%m-%d").date()
    bot.reply_to(message, f"Вы ввели дату: {comp_date}")

# Получаем от пользователя дистанцию соревнований
@bot.message_handler(commands=['distance_of_start'])
def distance_of_set(message):
    bot.reply_to(message, "Введите дистанцию соревнований в километрах в виде числа. Для отмены введите /cancel.")
    bot.register_next_step_handler(message, distance_settings)

def distance_settings(message):
    global distance
    if message.text == '/cancel':
        bot.reply_to(message, "Настройка отменена.")
        return
    distance = message.text
    bot.reply_to(message, f"Вы ввели дистанцию: {distance} км")

# Получаем от пользователя время напоминания
@bot.message_handler(commands=['time_set'])
def time_of_set(message):
    bot.reply_to(message, "Введите время напоминания в формате ЧЧ:ММ. Для отмены введите /cancel.")
    bot.register_next_step_handler(message, time_settings)

def time_settings(message):
    global signal_time
    if message.text == '/cancel':
        bot.reply_to(message, "Настройка отменена.")
        return
    signal_time = message.text
    bot.reply_to(message, f"Вы ввели время напоминания: {signal_time}")
    print(signal_time)
    reminder_thread = threading.Thread(target=send_reminders, args=(message.chat.id,))
    reminder_thread.start()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот - тренер по бегу, и я помогу подготовиться к соревнованиям.")

# Создаем таблицу плана подготовки
plan = []
# Задаем оличество строк и колонок
difference = comp_date - current_date
num_rows = int(difference.days)
print(num_rows)
num_columns = 4
any = (distance - 2) / num_rows
print(any)

# Заполняем список
for i in range(num_rows):
    # Создаем строку из 4-х элементов (например, просто числами от 0 до 3)
    row = [i, current_date + datetime.timedelta(days=i), round(2 + any * i, 1), "Комментарий"]
    plan.append(row)
# Выводим полученный список
#for row in plan:
#   print(row)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.reply_to(message,
        "Привет! Я бот - тренер по бегу, и я помогу подготовиться к соревнованиям.\n"
        "Доступные команды:\n"
        "/start - Начать обработку\n"
        "/fact - Получить интересный факт о беге\n"
        "/info - Получить информацию о настройках бота\n"
        "/date_of_start - Ввести дату соревнований\n"
        "/distance_of_start - Ввести дистанцию соревнований\n"
        "/time_set - Ввести время напоминания\n"
        "/cancel - Отмена\n"
        "/help - Помощь")

@bot.message_handler(commands=['fact'])
def fact_message(message):
    facts = [
        "Бег — один из старейших способов передвижения человека. В древности его использовали для охоты и передвижения с места на место.",
        "Скорость человека теоретически может достигать 60–65 км/ч. Однако максимальная зарегистрированная скорость — 44,7 км/ч, её развил спринтер Усейн Болт из Ямайки.",
        "Бег способствует выработке эндорфинов, так называемых «гормонов счастья». Отсюда идёт чувство эйфории, известное как «беговой кайф».",
        "Существует марафон, участники которого бегут наоборот — задом наперёд. Он проходит в Австралии и называется «Backward Running Championship».",
        "По данным американских учёных, чтобы продлить жизнь на 3 года, достаточно бегать всего 5–10 минут в день в умеренном темпе.",
        "20% населения мира генетически не способны к бегу на длинные дистанции. Учёные из Университета Лафборо (Великобритания) установили, что 1/5 землян не обладает набором генов, отвечающих за выносливость.",
        "27 лет — возраст, в котором быстрее всего бегают марафонцы-мужчины. Женщины — в 29 лет. Как показывают исследования, с каждым последующим годом скорость бега снижается в среднем на 2%."
    ]
    random_fact = random.choice(facts)
    bot.reply_to(message, f'Что мы знаем о беге? {random_fact}')

@bot.message_handler(commands=['cancel'])
def cancel_message(message):
    bot.reply_to(message, "Спасибо за внимание! Заходите ещё! Занимайтесь спортом!")

@bot.message_handler(commands=['info'])
def info_message(message):
    bot.reply_to(message,
        "Бот формирует тренировочный план и напоминания о тренировке\n"
        "Для работы боту нужна информация - дата соревнований, дистанция и время напоминаний\n"
        "Дата соревнований вводится по команде /date_of_start\n"
        "Дистанция вводится по команде /distance_of_start в километрах\n"
        "Время напоминаний вводится по команде /time_set в часах и минутах"
    )
def send_reminders(chat_id):
    while True:
        now = datetime.datetime.now().strftime('%H:%M')
        #print(now)
        #print(signal_time)
        if now == signal_time:
            bot.send_message(chat_id, f"Напоминание: сегодня {current_date}, сейчас {now}, пора тренироваться, дистанция на сегодня {round(2 + any * (num_rows - int((comp_date - current_date).days)), 1)} км.")
            time.sleep(61)
        time.sleep(2)

# Запуск бота
bot.polling(none_stop=True)
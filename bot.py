import telebot
from telebot import types
from datetime import datetime, timedelta
import threading
import time
from flask import Flask
import os

# ВАШ ТОКЕН
API_TOKEN = '8527062785:AAH76mjf7LxxDS8FjW9Q2ENy5B6HCud45xc'

bot = telebot.TeleBot(API_TOKEN)
# ДАТА НАЧАЛА СЕМЕСТРА
START_DATE = datetime(2026, 2, 10) 
app = Flask(__name__)

# ОПРЕДЕЛЯЕМ ПАПКУ, ГДЕ ЛЕЖИТ СКРИПТ (ЧТОБЫ РАБОТАЛО НА СЕРВЕРЕ)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_week_parity(date_obj):
    delta = date_obj - START_DATE
    if delta.days < 0:
         return '1' if date_obj.isocalendar()[1] % 2 != 0 else '2'
    weeks_passed = delta.days // 7
    if weeks_passed % 2 == 0:
        return '1' 
    else:
        return '2' 

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("📅 Текущая неделя"), types.KeyboardButton("➡️ Следующая неделя"))
    bot.send_message(message.chat.id, "Привет! Выбери неделю:", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def send_schedule(message):
    target_date = datetime.now()
    header = "Расписание"
    
    if message.text == "📅 Текущая неделя":
        header += " на ТЕКУЩУЮ неделю"
    elif message.text == "➡️ Следующая неделя":
        target_date += timedelta(days=7)
        header += " на СЛЕДУЮЩУЮ неделю"
    else:
        bot.send_message(message.chat.id, "Используйте кнопки.")
        return

    parity = get_week_parity(target_date)
    week_name = "НЕЧЕТНАЯ (Первая)" if parity == '1' else "ЧЕТНАЯ (Вторая)"
    
    # Ищем файл 1.png или 2.png в папке скрипта
    filename = f"{parity}.png"
    full_path = os.path.join(SCRIPT_DIR, filename)

    try:
        if os.path.exists(full_path):
            with open(full_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f"{header}\nТип: {week_name}")
        else:
            bot.send_message(message.chat.id, f"Ошибка: Файл {filename} не найден на сервере.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# --- ВЕБ-СЕРВЕР (ЧТОБЫ БОТ НЕ ЗАСЫПАЛ) ---
@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render выдаст порт автоматически, или используем 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
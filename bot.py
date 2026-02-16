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
app = Flask(__name__)

# --- НАСТРОЙКИ ВРЕМЕНИ ---
# 1. Дата начала семестра ОБЯЗАТЕЛЬНО должна быть ПОНЕДЕЛЬНИКОМ!
# 9 февраля 2026 - это понедельник.
START_DATE = datetime(2026, 2, 9) 

# 2. Ваш часовой пояс (сдвиг относительно Лондона/UTC)
# Если вы в Москве/Центральной России, ставьте +3. 
# Если в Ульяновске/Самаре, ставьте +4.
TIMEZONE_OFFSET = 3  

# Папка скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_current_time():
    # Получаем время сервера (UTC) и добавляем ваш сдвиг
    return datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)

def get_week_parity(date_obj):
    # Считаем разницу дней от начала семестра
    delta = date_obj - START_DATE
    
    # Если дата меньше старта, используем стандартный календарь
    if delta.days < 0:
         return '1' if date_obj.isocalendar()[1] % 2 != 0 else '2'
    
    # Целочисленное деление на 7 дает количество полных прошедших недель
    weeks_passed = delta.days // 7
    
    # Если прошло 0 недель (первая неделя), 2 недели, 4 недели -> это Нечетная (1)
    # Если прошло 1 неделя, 3 недели -> это Четная (2)
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
    # Берем ВАШЕ правильное время (с учетом часового пояса)
    target_date = get_current_time()
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
    
    filename = f"{parity}.png"
    full_path = os.path.join(SCRIPT_DIR, filename)

    try:
        if os.path.exists(full_path):
            with open(full_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f"{header}\nТип: {week_name}\n(Сегодня: {target_date.strftime('%d.%m')})")
        else:
            bot.send_message(message.chat.id, f"Ошибка: Файл {filename} не найден.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

# --- ВЕБ-СЕРВЕР ---
@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.start()
    bot.infinity_polling()
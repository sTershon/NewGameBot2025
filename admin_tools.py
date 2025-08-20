# admin_tools.py
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players, save_db

def register_admin_handlers(bot: TeleBot, ADMINS: list):
    
    # --- Выдать тег по цвету ---
    @bot.message_handler(func=lambda m: str(m.from_user.id) in ADMINS and m.text == "🎨 Выдать тег по цвету")
    def give_color_tag(message):
        uid = str(message.from_user.id)
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        colors = ["Красный", "Синий", "Зелёный", "Жёлтый", "Фиолетовый"]
        for color in colors:
            markup.add(KeyboardButton(color))
        markup.add(KeyboardButton("⬅️ Назад"))
        bot.send_message(message.chat.id, "Выберите цвет тега для игрока:", reply_markup=markup)
    
    # Обработка выбора цвета
    @bot.message_handler(func=lambda m: str(m.from_user.id) in ADMINS)
    def set_tag_color(message):
        if message.text in ["Красный", "Синий", "Зелёный", "Жёлтый", "Фиолетовый"]:
            # Например, выдаём тег первому игроку (для теста)
            if players:
                player_id = list(players.keys())[0]
                players[player_id]["tag_color"] = message.text
                save_db()
                bot.send_message(message.chat.id, f"✅ Игроку {players[player_id]['name']} выдан тег цвета {message.text}")
            else:
                bot.send_message(message.chat.id, "❌ Нет игроков для выдачи тега")
    
    # --- Изменить статистику игрока ---
    @bot.message_handler(func=lambda m: str(m.from_user.id) in ADMINS and m.text == "📊 Изменить статистику игрока")
    def change_player_stats(message):
        if not players:
            bot.send_message(message.chat.id, "❌ Нет игроков для редактирования")
            return
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for pid, pdata in players.items():
            markup.add(KeyboardButton(f"{pdata['name']} (ID: {pid})"))
        markup.add(KeyboardButton("⬅️ Назад"))
        bot.send_message(message.chat.id, "Выберите игрока для редактирования:", reply_markup=markup)

    # Обработка выбора игрока
    @bot.message_handler(func=lambda m: str(m.from_user.id) in ADMINS)
    def edit_player(message):
        if "(ID:" in message.text:
            pid = message.text.split("ID:")[1].replace(")", "").strip()
            if pid in players:
                markup = ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(KeyboardButton("💰 Изменить золото"))
                markup.add(KeyboardButton("⭐ Изменить уровень"))
                markup.add(KeyboardButton("⬅️ Назад"))
                bot.send_message(message.chat.id, f"Выберите, что изменить для {players[pid]['name']}:", reply_markup=markup)

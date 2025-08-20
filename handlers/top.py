# handlers/top.py
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players

def get_top_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Топ по золоту"), KeyboardButton("🎖 Топ по уровню"))
    kb.add(KeyboardButton("⚔ Топ по победам"), KeyboardButton("🏢 Топ по бизнесу"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def register_top_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "🏆 Топ")
    def show_top_menu(message):
        bot.send_message(message.chat.id, "Выбери категорию топа:", reply_markup=get_top_keyboard())

    # 💰 Топ по золоту
    @bot.message_handler(func=lambda m: m.text == "💰 Топ по золоту")
    def top_gold(message):
        sorted_players = sorted(players.items(), key=lambda x: x[1].get("gold", 0), reverse=True)
        text = "💰 ТОП игроков по золоту:\n\n"
        for i, (uid, p) in enumerate(sorted_players[:10], start=1):
            text += f"{i}. {p['name']} — {p.get('gold', 0)}💰\n"
        bot.send_message(message.chat.id, text)

    # 🎖 Топ по уровню
    @bot.message_handler(func=lambda m: m.text == "🎖 Топ по уровню")
    def top_level(message):
        sorted_players = sorted(players.items(), key=lambda x: x[1].get("level", 1), reverse=True)
        text = "🎖 ТОП игроков по уровню:\n\n"
        for i, (uid, p) in enumerate(sorted_players[:10], start=1):
            text += f"{i}. {p['name']} — {p.get('level', 1)} lvl\n"
        bot.send_message(message.chat.id, text)

    # ⚔ Топ по победам
    @bot.message_handler(func=lambda m: m.text == "⚔ Топ по победам")
    def top_battles(message):
        sorted_players = sorted(players.items(), key=lambda x: x[1].get("wins", 0), reverse=True)
        text = "⚔ ТОП бойцов (по победам):\n\n"
        for i, (uid, p) in enumerate(sorted_players[:10], start=1):
            text += f"{i}. {p['name']} — {p.get('wins', 0)} побед\n"
        bot.send_message(message.chat.id, text)

    # 🏢 Топ по бизнесу
    @bot.message_handler(func=lambda m: m.text == "🏢 Топ по бизнесу")
    def top_business(message):
        sorted_players = sorted(players.items(), key=lambda x: len(x[1].get("businesses", [])), reverse=True)
        text = "🏢 ТОП по бизнесам (кол-во):\n\n"
        for i, (uid, p) in enumerate(sorted_players[:10], start=1):
            text += f"{i}. {p['name']} — {len(p.get('businesses', []))} бизнесов\n"
        bot.send_message(message.chat.id, text)

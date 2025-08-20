from telebot import TeleBot
from database import players, save_db
from keyboards import get_main_keyboard
from config import ADMINS
from mechanics.battle import pve_battle, pvp_battle

def register_player_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start_message(message):
        user_id = str(message.from_user.id)
        if user_id not in players:
            bot.send_message(message.chat.id, "Добро пожаловать в RPG-бот! 🎮\nВведите имя своего персонажа:")
            players[user_id] = {"stage": "register"}
        else:
            kb = get_main_keyboard(user_id in ADMINS)
            bot.send_message(message.chat.id, f"С возвращением, {players[user_id]['name']}! ✨", reply_markup=kb)

    @bot.message_handler(commands=['myid'])
    def get_id(message):
        bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

    @bot.message_handler(func=lambda m: True)
    def player_commands(message):
        user_id = str(message.from_user.id)

        if user_id in players and players[user_id].get("stage") == "register":
            name = message.text.strip()
            players[user_id] = {
                "name": name,
                "level": 1,
                "xp": 0,
                "hp": 100,
                "gold": 50,
                "inventory": []
            }
            save_db()
            kb = get_main_keyboard(user_id in ADMINS)
            bot.send_message(message.chat.id, f"Персонаж {name} создан! 🎉", reply_markup=kb)
            return

        if user_id not in players:
            bot.send_message(message.chat.id, "Ты ещё не зарегистрирован! Напиши /start")
            return

        p = players[user_id]

        if message.text == "📜 Профиль":
            text = (
                f"👤 Имя: {p['name']}\n"
                f"⭐ Уровень: {p['level']}\n"
                f"🔥 Опыт: {p['xp']}\n"
                f"❤️ Здоровье: {p['hp']}\n"
                f"💰 Золото: {p['gold']}"
            )
            bot.send_message(message.chat.id, text)

        elif message.text == "⚒ Работа":
            p["gold"] += 10
            p["xp"] += 5
            save_db()
            bot.send_message(message.chat.id, "Ты поработал и получил +10💰 и +5🔥 опыта!")

        elif message.text == "⚔ Бой":
            p["hp"] -= 10
            p["xp"] += 15
            p["gold"] += 20
            if p["hp"] <= 0:
                p["hp"] = 100
                bot.send_message(message.chat.id, "Ты погиб в бою... но воскрес! HP восстановлено до 100 ❤️")
            save_db()
            bot.send_message(message.chat.id, "Ты сразился с монстром: -10❤️, +15🔥, +20💰")

        elif message.text == "❤️ Лечение":
            if p["gold"] >= 15:
                p["gold"] -= 15
                p["hp"] = min(100, p["hp"] + 30)
                save_db()
                bot.send_message(message.chat.id, "Ты купил зелье и восстановил 30❤️")
            else:
                bot.send_message(message.chat.id, "Недостаточно золота!")

        elif message.text == "🛒 Магазин":
            bot.send_message(message.chat.id, "Магазин пока в разработке 🛠")
        elif message.text == "⚔ Бой":
            result = pve_battle(user_id)
            bot.send_message(message.chat.id, result)

        elif message.text.startswith("/pvp"):
            try:
                _, target_id = message.text.split()
                result = pvp_battle(user_id, target_id)
                bot.send_message(message.chat.id, result)
            except:
                bot.send_message(message.chat.id, "Используй команду так: /pvp ID_игрока")

    @bot.message_handler(commands=['help'])
    def help_message(message):
        text = (
            "📖 Доступные команды и кнопки:\n\n"
            "💡 Основное:\n"
            "/start – начать игру или войти\n"
            "/myid – узнать свой ID\n"
            "/help – показать это меню\n\n"
            "🎮 Игровые кнопки:\n"
            "📜 Профиль – посмотреть характеристики\n"
            "⚒ Работа – заработать золото и опыт\n"
            "⚔ Бой – сразиться с монстром (PvE)\n"
            "❤️ Лечение – восстановить здоровье за золото\n"
            "🛒 Магазин – купить предметы (в разработке)\n\n"
            "⚔ PvP:\n"
            "/pvp <ID> – сразиться с другим игроком\n\n"
            "👑 Админка:\n"
            "⚙️ Админка – вход в панель администратора (только для админов)\n"
        )
        bot.send_message(message.chat.id, text)
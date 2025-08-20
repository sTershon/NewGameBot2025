from telebot import TeleBot
from database import players, save_db
from keyboards import get_travel_dest_keyboard
from data.game_data import DESTINATIONS

def register_travel_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda m: m.text == "✈️ Перелёт")
    def travel_menu(message):
        uid = str(message.from_user.id)
        player = players[uid]

        if player["level"] < 10:
            bot.send_message(message.chat.id, "❌ Перелёты доступны только с 10 уровня!")
            return
        if not player.get("travel_pass", False):
            bot.send_message(message.chat.id, "❌ Нужна карта выезда (купить в магазине перелётов)!")
            return

        current_city = player.get("city", "Москва")
        bot.send_message(message.chat.id, f"🌍 Ты сейчас в {current_city}. Куда полетим?",
                         reply_markup=get_travel_dest_keyboard(current_city))

    @bot.message_handler(func=lambda m: m.text.startswith("Лететь: "))
    def do_travel(message):
        uid = str(message.from_user.id)
        dest_city = message.text.replace("Лететь: ", "")

        if dest_city in DESTINATIONS:
            players[uid]["city"] = dest_city
            save_db()
            bot.send_message(message.chat.id, f"✈️ Ты прилетел в {dest_city}! Добро пожаловать 🙌")
        else:
            bot.send_message(message.chat.id, "❌ Такого города нет.")
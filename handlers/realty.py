from telebot import TeleBot
from database import players, save_db
from keyboards import get_realty_menu_keyboard, get_realty_buy_keyboard, get_main_keyboard
from data.game_data import CITIES

def register_realty_handlers(bot: TeleBot):
    # --- Открытие меню недвижимости ---
    @bot.message_handler(func=lambda m: m.text == "🏘 Недвижимость")
    def open_realty_menu(message):
        user_id = str(message.from_user.id)
        bot.send_message(message.chat.id, "🏘 Меню недвижимости:", reply_markup=get_realty_menu_keyboard())

    # --- Назад в главное меню ---
    @bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
    def back_to_main(message):
        user_id = str(message.from_user.id)
        bot.send_message(message.chat.id, "⬅️ Возврат в меню", reply_markup=get_main_keyboard(user_id))

    # --- Моя недвижимость ---
    @bot.message_handler(func=lambda m: m.text == "🏠 Моя недвижимость")
    def my_realty(message):
        user_id = str(message.from_user.id)
        realties = players[user_id].get("realty", [])
        if not realties:
            bot.send_message(message.chat.id, "У тебя пока нет недвижимости 🏚")
        else:
            text = "🏘 Твоя недвижимость:\n\n"
            for r in realties:
                text += f"🏠 {r['name']} | Цена: {r['price']}💰 | Аренда: {r['rent']}💰\n"
            bot.send_message(message.chat.id, text)

    # --- Купить недвижимость ---
    @bot.message_handler(func=lambda m: m.text == "🛒 Купить недвижимость")
    def buy_realty_menu(message):
        user_id = str(message.from_user.id)
        city = players[user_id].get("city", "Москва")
        bot.send_message(message.chat.id, f"Недвижимость в городе {city}:", 
                         reply_markup=get_realty_buy_keyboard(city))

    @bot.message_handler(func=lambda m: m.text.startswith("Купить дом:"))
    def buy_realty(message):
        user_id = str(message.from_user.id)
        city = players[user_id].get("city", "Москва")
        choice = message.text.replace("Купить дом: ", "").split(" (")[0]

        for r in CITIES[city].get("realty", []):
            if r["name"] == choice:
                if players[user_id]["gold"] >= r["price"]:
                    players[user_id]["gold"] -= r["price"]
                    players[user_id].setdefault("realty", []).append(r)
                    save_db()
                    bot.send_message(message.chat.id, f"Поздравляю! 🎉 Ты купил недвижимость: {r['name']}")
                else:
                    bot.send_message(message.chat.id, "Недостаточно золота ❌")
                return

    # --- Сдать недвижимость в аренду ---
    @bot.message_handler(func=lambda m: m.text == "📑 Сдать в аренду")
    def rent_realty(message):
        user_id = str(message.from_user.id)
        realties = players[user_id].get("realty", [])
        if not realties:
            bot.send_message(message.chat.id, "У тебя нет недвижимости для аренды ❌")
            return

        income = sum([r["rent"] for r in realties])
        players[user_id]["gold"] += income
        save_db()
        bot.send_message(message.chat.id, f"Ты сдал недвижимость в аренду и получил {income}💰!")

        

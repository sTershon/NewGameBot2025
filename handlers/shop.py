from telebot import TeleBot
from database import players, save_db, ensure_defaults
from keyboards import get_shop_root_keyboard, get_city_shop_keyboard, get_travel_shop_keyboard
from data.game_data import CITIES, TRAVEL_PASS_PRICE


def register_shop_handlers(bot: TeleBot):

    # Корневое меню магазина
    @bot.message_handler(func=lambda m: m.text == "🛒 Магазин")
    def shop_root(message):
        bot.send_message(
            message.chat.id,
            "🛍 Добро пожаловать в магазин!",
            reply_markup=get_shop_root_keyboard()
        )

    # Магазин города
    @bot.message_handler(func=lambda m: m.text == "🛍 Товары города")
    def city_shop(message):
        uid = str(message.from_user.id)
        city = players[uid].get("city", "Москва")
        bot.send_message(
            message.chat.id,
            f"🛒 Товары в {city}:",
            reply_markup=get_city_shop_keyboard(city)
        )

    # Покупка предмета
    @bot.message_handler(func=lambda m: m.text.startswith("Купить: "))
    def buy_item(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)

        city = players[uid].get("city")
        shop_items = CITIES.get(city, {}).get("shop", [])

        # убираем "Купить: "
        item_name = message.text.replace("Купить: ", "").split("(")[0].strip()
        item = next((i for i in shop_items if i["name"] == item_name), None)

        if not item:
            bot.send_message(message.chat.id, "❌ Этот предмет не найден в магазине.")
            return

        if players[uid]["gold"] < item["price"]:
            bot.send_message(message.chat.id, "❌ У тебя недостаточно золота.")
            return

        # списываем деньги
        players[uid]["gold"] -= item["price"]

        # добавляем предмет в инвентарь
        inventory = players[uid].setdefault("inventory", [])
        for inv_item in inventory:
            if inv_item["name"] == item["name"]:
                inv_item["count"] += 1
                break
        else:
            inventory.append({
                "name": item["name"],
                "type": item.get("type", "misc"),   # heal / weapon / misc
                "value": item.get("value", 0),      # сила предмета
                "count": 1
            })

        save_db()
        bot.send_message(message.chat.id, f"✅ Ты купил {item['name']} за {item['price']}💰!")

    # Магазин перелётов
    @bot.message_handler(func=lambda m: m.text == "🛫 Магазин перелётов")
    def travel_shop(message):
        bot.send_message(
            message.chat.id,
            "✈️ Магазин перелётов:",
            reply_markup=get_travel_shop_keyboard(TRAVEL_PASS_PRICE)
        )

    # Покупка карты перелёта
    @bot.message_handler(func=lambda m: m.text.startswith("🗺 Карта выезда"))
    def buy_travel_pass(message):
        uid = str(message.from_user.id)
        if players[uid]["gold"] >= TRAVEL_PASS_PRICE:
            players[uid]["gold"] -= TRAVEL_PASS_PRICE
            players[uid]["travel_pass"] = True
            save_db()
            bot.send_message(message.chat.id, f"✅ Куплена карта выезда за {TRAVEL_PASS_PRICE}💰")
        else:
            bot.send_message(message.chat.id, "❌ Недостаточно золота!")

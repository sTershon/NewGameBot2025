# handlers/inventory.py

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import players, ensure_defaults

def get_inventory_keyboard(uid):
    kb = InlineKeyboardMarkup()
    inventory = players[uid].get("inventory", [])

    if not inventory:
        return None

    for item in inventory:
        if item.get("type") == "heal":
            kb.add(InlineKeyboardButton(f"🧪 Использовать {item['name']}", callback_data=f"use_{item['name']}"))
        elif item.get("type") in ("weapon", "armor"):
            kb.add(InlineKeyboardButton(f"⚔ Экипировать {item['name']}", callback_data=f"equip_{item['name']}"))
    return kb


def register_inventory_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "🎒 Инвентарь")
    def inventory(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]

        inv = player.get("inventory", [])
        if not inv:
            bot.send_message(message.chat.id, "🎒 Инвентарь пуст.")
            return

        text = "🎒 Твои предметы:\n" + "\n".join([f"- {i['name']}" for i in inv])
        kb = get_inventory_keyboard(uid)

        if kb:
            bot.send_message(message.chat.id, text, reply_markup=kb)
        else:
            bot.send_message(message.chat.id, text)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("use_"))
    def use_item(call):
        uid = str(call.from_user.id)
        player = players[uid]

        item_name = call.data[4:]
        item = next((i for i in player["inventory"] if i["name"] == item_name), None)

        if not item:
            bot.answer_callback_query(call.id, "❌ Предмет не найден")
            return

        if item["type"] == "heal":
            if player["hp"] >= 100:
                bot.answer_callback_query(call.id, "❤️ У тебя уже полное здоровье")
                return

            player["hp"] = min(100, player["hp"] + item["value"])
            player["inventory"].remove(item)
            bot.answer_callback_query(call.id, f"🧪 Ты использовал {item['name']}! Здоровье восстановлено.")
            bot.edit_message_text("🎒 Инвентарь обновлён.", call.message.chat.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("equip_"))
    def equip_item(call):
        uid = str(call.from_user.id)
        player = players[uid]

        item_name = call.data[6:]
        item = next((i for i in player["inventory"] if i["name"] == item_name), None)

        if not item:
            bot.answer_callback_query(call.id, "❌ Предмет не найден")
            return

        if item["type"] == "weapon":
            player["equipped_weapon"] = f"{item['name']} (+{item['value']})"
            bot.answer_callback_query(call.id, f"⚔ Ты экипировал {item['name']}")
        elif item["type"] == "armor":
            player["equipped_armor"] = f"{item['name']} (+{item['value']})"
            bot.answer_callback_query(call.id, f"🛡 Ты надел {item['name']}")

        bot.edit_message_text("🎒 Инвентарь обновлён.", call.message.chat.id, call.message.message_id)

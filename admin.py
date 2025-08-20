# admin.py
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players, save_db
from config import ADMINS

# --- Клавиатура для админки ---
def get_admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📊 Все игроки"), KeyboardButton("👑 Выдать золото себе"))
    kb.add(KeyboardButton("🔎 Поиск по ID"), KeyboardButton("💰 Выдать золото по ID"))
    kb.add(KeyboardButton("🎨 Выдать тег по цвету"), KeyboardButton("📊 Изменить статистику игрока"))
    kb.add(KeyboardButton("⚡ Очистить достижения"), KeyboardButton("🛡 Выдать админку"))
    kb.add(KeyboardButton("📢 Разослать всем"))

    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def register_admin_handlers(bot: TeleBot):
    def is_admin(message):
        return str(message.from_user.id) in ADMINS

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "📊 Все игроки")
    def show_all_players(message):
        if not players:
            bot.send_message(message.chat.id, "Нет зарегистрированных игроков.")
            return
        text = "📜 Список всех игроков:\n"
        for uid, pdata in players.items():
            text += f"{pdata.get('name', 'Безымянный')} (ID: {uid}) — lvl {pdata.get('level',0)}, {pdata.get('gold',0)}💰\n"
        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "👑 Выдать золото себе")
    def give_gold_self(message):
        uid = str(message.from_user.id)
        players[uid]["gold"] = players.get(uid, {}).get("gold", 0) + 1000
        save_db()
        bot.send_message(message.chat.id, "💰 Тебе выдано 1000 золота.")

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "💰 Выдать золото по ID")
    def give_gold_by_id(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока и количество через пробел (например: 12345 500):")
        bot.register_next_step_handler(msg, process_give_gold)

    def process_give_gold(message):
        try:
            parts = message.text.split()
            target_id = parts[0]
            amount = int(parts[1])
            if target_id not in players:
                bot.send_message(message.chat.id, "❌ Игрок не найден.")
                return
            players[target_id]["gold"] = players.get(target_id, {}).get("gold",0) + amount
            save_db()
            bot.send_message(message.chat.id, f"💰 Игрок {players[target_id]['name']} получил {amount} золота.")
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат. Попробуй снова.")

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "🔎 Поиск по ID")
    def search_player(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока для поиска:")
        bot.register_next_step_handler(msg, process_search_player)

    def process_search_player(message):
        uid = message.text.strip()
        pdata = players.get(uid)
        if not pdata:
            bot.send_message(message.chat.id, "❌ Игрок не найден.")
            return
        text = f"📊 Игрок: {pdata.get('name', 'Безымянный')}\n"
        text += f"💰 Золото: {pdata.get('gold', 0)}\n"
        text += f"⭐ Уровень: {pdata.get('level',0)}\n"
        text += f"🏰 Клан: {pdata.get('clan_id','Нет')}\n"
        bot.send_message(message.chat.id, text)

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "🎨 Выдать тег по цвету")
    def give_color_tag(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока и цвет тега через пробел (например: 12345 красный):")
        bot.register_next_step_handler(msg, process_color_tag)

    def process_color_tag(message):
        try:
            parts = message.text.split()
            target_id = parts[0]
            color = parts[1]
            if target_id not in players:
                bot.send_message(message.chat.id, "❌ Игрок не найден.")
                return
            players[target_id]["tag_color"] = color
            save_db()
            bot.send_message(message.chat.id, f"🎨 Игрок {players[target_id]['name']} получил тег цвета {color}.")
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат. Попробуй снова.")

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "📊 Изменить статистику игрока")
    def change_player_stats(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока и поле:значение через пробел (например: 12345 gold:500 level:3):")
        bot.register_next_step_handler(msg, process_change_stats)

    def process_change_stats(message):
        try:
            parts = message.text.split()
            target_id = parts[0]
            if target_id not in players:
                bot.send_message(message.chat.id, "❌ Игрок не найден.")
                return
            for p in parts[1:]:
                key, value = p.split(":")
                if key in ["gold", "level", "hp", "xp"]:
                    players[target_id][key] = int(value)
            save_db()
            bot.send_message(message.chat.id, f"✅ Статистика игрока {players[target_id]['name']} обновлена.")
        except:
            bot.send_message(message.chat.id, "❌ Ошибка формата. Попробуй снова.")

    # Новые функции админа
    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "⚡ Очистить достижения")
    def reset_player_menu(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока для полной очистки:")
        bot.register_next_step_handler(msg, process_reset_player)

    def process_reset_player(message):
        target_id = message.text.strip()
        if target_id not in players:
            bot.send_message(message.chat.id, "❌ Игрок не найден.")
            return

        player = players[target_id]

        # Обнуляем всё
        player["gold"] = 0
        player["level"] = 0
        player["xp"] = 0
        player["hp"] = 100
        player["attack_bonus"] = 0
        player["hp_bonus"] = 0
        player["equipped_weapon"] = "❌ Нет"
        player["equipped_armor"] = "❌ Нет"
        player["inventory"] = []
        player["clan_id"] = None
        player["tag_color"] = None
        player["achievements"] = []

        save_db()
        bot.send_message(message.chat.id, f"✅ Игрок {player.get('name', 'Безымянный')} полностью очищен.")


    def process_clear_achievements(message):
        uid = message.text.strip()
        if uid not in players:
            bot.send_message(message.chat.id, "❌ Игрок не найден.")
            return
        players[uid]["achievements"] = []
        save_db()
        bot.send_message(message.chat.id, f"✅ Все достижения игрока {players[uid]['name']} были очищены.")

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "🛡 Выдать админку")
    def give_admin(message):
        msg = bot.send_message(message.chat.id, "Введите ID игрока, которому выдать админку:")
        bot.register_next_step_handler(msg, process_give_admin)

    def process_give_admin(message):
        uid = message.text.strip()
        if uid not in players:
            bot.send_message(message.chat.id, "❌ Игрок не найден.")
            return
        if uid not in ADMINS:
            ADMINS.append(uid)
            save_db()  # если у тебя ADMINS хранится в БД/файле
        bot.send_message(message.chat.id, f"🛡 Игрок {players[uid]['name']} теперь администратор.")

    @bot.message_handler(func=lambda m: is_admin(m) and m.text == "📢 Разослать всем")
    def broadcast_to_all(message):
        msg = bot.send_message(message.chat.id, "Введите текст рассылки:")
        bot.register_next_step_handler(msg, process_broadcast_text)

    def process_broadcast_text(message):
        text = message.text
        msg = bot.send_message(message.chat.id, "Введите количество золота для выдачи каждому игроку (0 если без выдачи):")
        bot.register_next_step_handler(msg, process_broadcast_gold, text)

    def process_broadcast_gold(message, text):
        try:
            amount = int(message.text)
        except:
            bot.send_message(message.chat.id, "❌ Неверное число. Попробуйте снова.")
            return
        
        for uid, pdata in players.items():
            if amount > 0:
                pdata["gold"] = pdata.get("gold",0) + amount
            bot.send_message(uid, f"📢 Сообщение от администрации:\n{text}\n💰 Вам выдано: {amount}💰" if amount > 0 else f"📢 Сообщение от администрации:\n{text}")
        
        save_db()
        bot.send_message(message.chat.id, "✅ Рассылка успешно отправлена всем игрокам!")
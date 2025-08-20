from telebot import TeleBot
from database import players, save_db, ensure_defaults
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import random, time

def get_battle_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🗡 Атаковать"))
    kb.add(KeyboardButton("⬅️ Сбежать"))
    return kb

def get_main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("⚔ Бой"))
    kb.add(KeyboardButton("👤 Профиль"))
    kb.add(KeyboardButton("🏪 Магазин"))
    return kb

def register_battle_handlers(bot: TeleBot):
    enemies = [
        {"name": "Орк", "hp": 40, "attack": 8},
        {"name": "Гоблин", "hp": 30, "attack": 5},
        {"name": "Тролль", "hp": 60, "attack": 10},
        {"name": "Разбойник", "hp": 50, "attack": 7}
    ]

    def check_level_up(uid):
        player = players[uid]
        exp_needed = player["level"] * 100
        if player["exp"] >= exp_needed:
            player["exp"] -= exp_needed
            player["level"] += 1
            player["hp"] = 100 + player["level"] * 10  # максимум HP растёт
            return True
        return False

    @bot.message_handler(func=lambda m: m.text == "⚔ Бой")
    def start_battle(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)

        player = players[uid]

        # Проверка: умер ли игрок недавно
        if "last_death" in player and time.time() - player["last_death"] < 300:
            wait = int(300 - (time.time() - player["last_death"]))
            bot.send_message(message.chat.id, f"💀 Ты пал в бою. Отдохни {wait} сек. прежде чем снова сражаться.")
            return

        # Проверка здоровья
        if player["hp"] <= 0:
            bot.send_message(message.chat.id, "💀 Ты слишком слаб. Восстанови здоровье перед боем!")
            return

        # Проверка кулдауна между боями
        if "last_battle" in player and time.time() - player["last_battle"] < 300:
            wait = int(300 - (time.time() - player["last_battle"]))
            bot.send_message(message.chat.id, f"⏳ Ты устал. Отдохни {wait} сек. перед новым боем.")
            return

        enemy = random.choice(enemies).copy()
        player["battle"] = enemy
        save_db()

        bot.send_message(
            message.chat.id,
            f"🐲 На тебя напал {enemy['name']}!\n"
            f"❤️ Твои HP: {player['hp']}\n"
            f"💢 HP врага: {enemy['hp']}",
            reply_markup=get_battle_keyboard()
        )

    @bot.message_handler(func=lambda m: m.text == "🗡 Атаковать")
    def attack(message):
        uid = str(message.from_user.id)
        player = players[uid]
        battle = player.get("battle")
        if not battle:
            bot.send_message(message.chat.id, "⚔ Сейчас ты не в бою.")
            return

        # Игрок атакует (урон зависит от уровня)
        dmg = random.randint(5, 10) + player["level"] * 2
        battle["hp"] -= dmg
        text = f"🗡 Ты ударил врага и нанёс {dmg} урона!\n"

        # Проверка победы
        if battle["hp"] <= 0:
            gold_reward = random.randint(50, 150)
            exp_reward = random.randint(20, 50)
            player["gold"] += gold_reward
            player["exp"] += exp_reward
            if "battle" in player: del player["battle"]
            player["last_battle"] = time.time()

            lvl_up = check_level_up(uid)
            save_db()

            msg = text + f"🎉 Ты победил {battle['name']}!\n"
            msg += f"💰 Получено золота: {gold_reward}\n⭐ Опыт: {exp_reward}\n"

            if lvl_up:
                msg += f"⬆️ Уровень повышен! Теперь твой уровень: {player['level']} 🎉"

            bot.send_message(message.chat.id, msg, reply_markup=get_main_keyboard())
            return

        # Враг атакует
        enemy_dmg = random.randint(1, battle["attack"])
        player["hp"] -= enemy_dmg
        text += f"🐲 {battle['name']} атакует и наносит {enemy_dmg} урона!\n"
        text += f"❤️ Твои HP: {player['hp']}\n💢 HP врага: {battle['hp']}"

        # Проверка поражения
        if player["hp"] <= 0:
            player["hp"] = 0
            if "battle" in player: del player["battle"]
            player["last_death"] = time.time()
            save_db()
            bot.send_message(
                message.chat.id,
                text + "\n💀 Ты пал в бою. Лечение и отдых займут 5 минут.",
                reply_markup=get_main_keyboard()
            )
            return

        save_db()
        bot.send_message(message.chat.id, text, reply_markup=get_battle_keyboard())

    @bot.message_handler(func=lambda m: m.text == "⬅️ Сбежать")
    def run_away(message):
        uid = str(message.from_user.id)
        if players[uid].get("battle"):
            del players[uid]["battle"]
            save_db()
            bot.send_message(message.chat.id, "🏃 Ты сбежал из боя.", reply_markup=get_main_keyboard())
        else:
            bot.send_message(message.chat.id, "⚔ Сейчас ты не в бою.", reply_markup=get_main_keyboard())

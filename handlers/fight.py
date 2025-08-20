# fight.py
import time
import random
from telebot import TeleBot
from database import players, ensure_defaults, save_db

# Возможные враги
ENEMIES = [
    {"name": "Разбойник", "hp": 30, "damage": 10, "reward": 40},
    {"name": "Гоблин", "hp": 25, "damage": 8, "reward": 30},
    {"name": "Орк", "hp": 40, "damage": 15, "reward": 60},
    {"name": "Скелет", "hp": 20, "damage": 6, "reward": 20},
    {"name": "Тролль", "hp": 50, "damage": 18, "reward": 80},
]

def register_fight_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "⚔ Бой")
    def start_fight(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]

        # Проверка, жив ли игрок
        if player.get("hp", 100) <= 0:
            cooldown = player.get("death_cooldown", 0)
            if time.time() < cooldown:
                wait = int(cooldown - time.time())
                bot.send_message(message.chat.id, f"💀 Ты мёртв! Жди ещё {wait // 60} мин {wait % 60} сек.")
                return
            else:
                bot.send_message(message.chat.id, "💀 Ты мёртв! Восстанови HP зельем, потом сможешь снова сражаться.")
                return

        # --- Выбираем случайного врага ---
        enemy = random.choice(ENEMIES)
        enemy_hp = enemy["hp"]
        enemy_name = enemy["name"]
        enemy_damage = enemy["damage"]
        reward = enemy["reward"]

        # Урон игрока
        damage = 10
        if player.get("equipped_weapon") == "Меч воина":
            damage += 5
        if player.get("equipped_weapon") == "Сабля казака":
            damage += 7

        # ⚔ Битва (1 раунд)
        player["hp"] -= enemy_damage
        enemy_hp -= damage

        if player["hp"] <= 0:
            player["hp"] = 0
            player["death_cooldown"] = time.time() + 300  # 5 минут кулдаун
            bot.send_message(message.chat.id, f"💀 {enemy_name} одолел тебя! Подожди 5 минут после восстановления HP.")
        elif enemy_hp <= 0:
            player["gold"] += reward
            bot.send_message(
                message.chat.id,
                f"🏆 Ты победил врага ({enemy_name}) и получил {reward}💰!\n"
                f"❤️ HP осталось: {player['hp']}"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"⚔ Ты сразился с {enemy_name}!\n"
                f"Ты нанёс {damage} урона, враг нанёс {enemy_damage}.\n"
                f"❤️ Твои HP: {player['hp']} | 💢 HP врага: {enemy_hp}"
            )

        save_db()

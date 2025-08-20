# work.py
import random
import time
from telebot import TeleBot
from database import players, save_db, ensure_defaults

WORK_COOLDOWN = 86400  # 24 часа

def register_work_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "⚒ Работа")
    def work_handler(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        p = players[uid]

        now_ts = int(time.time())
        last_work = p.get("last_work", 0)

        if now_ts - last_work < WORK_COOLDOWN:
            remaining = WORK_COOLDOWN - (now_ts - last_work)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            bot.send_message(message.chat.id, f"⏳ Ты уже работал сегодня. Следующая попытка через {hours}ч {minutes}м.")
            return

        earned = random.randint(50, 150)
        p["gold"] += earned
        p["last_work"] = now_ts

        save_db()
        bot.send_message(message.chat.id, f"⚒ Ты поработал и получил {earned}💰!")
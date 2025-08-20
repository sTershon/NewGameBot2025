from telebot import TeleBot, telebot
from config import TOKEN, ADMINS
from database import players, save_db, ensure_defaults
from keyboards import get_main_keyboard, get_admin_keyboard


# хендлеры
from handlers.admin import register_admin_handlers
from handlers.shop import register_shop_handlers
from handlers.business import register_business_handlers
from handlers.travel import register_travel_handlers
from handlers.realty import register_realty_handlers
from handlers.profile import register_profile_handlers
from handlers.work import register_work_handlers
from handlers.fight import register_fight_handlers
from handlers.inventory import register_inventory_handlers
from handlers.top import register_top_handlers
from handlers.clans import register_clan_handlers
from handlers.casino import register_casino_handlers
from handlers.misc import register_misc_handlers

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    ensure_defaults(user_id, message.from_user.first_name)
    bot.send_message(message.chat.id, "Добро пожаловать в RPG!⚔", reply_markup=get_main_keyboard(user_id))

# Открытие админки
@bot.message_handler(func=lambda m: m.text == "⚙️ Админка")
def open_admin_menu(message):
    user_id = str(message.from_user.id)
    if user_id not in ADMINS:
        bot.send_message(message.chat.id, "❌ Только для админов!")
        return
    bot.send_message(message.chat.id, "⚙️ Админка:", reply_markup=get_admin_keyboard())

def register_start_handler(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]

        # Проверяем, есть ли у игрока уже рефералка
        if "referral_code" not in player:
            player["referral_code"] = uid
            player["referrals"] = []

        # Проверяем, передан ли код в команде
        if len(message.text.split()) > 1:
            ref_code = message.text.split()[1]
            if ref_code != uid and ref_code in players:
                referrer = players[ref_code]

                # Если игрок ещё не был добавлен в рефералов
                if uid not in referrer.get("referrals", []):
                    referrer.setdefault("referrals", []).append(uid)

                    # Бонус за приглашение
                    referrer["gold"] = referrer.get("gold", 0) + 500
                    player["gold"] = player.get("gold", 0) + 100

                    save_db()
                    bot.send_message(ref_code, f"🎉 Ты получил 500💰 за приглашённого друга {player['name']}!")
                    bot.send_message(uid, "🎁 Ты получил 100💰 за регистрацию по реферальной ссылке!")

        save_db()
        bot.send_message(uid, f"Привет, {player['name']}! Добро пожаловать в игру!")

# Подключаем все хендлеры
register_admin_handlers(bot)
register_shop_handlers(bot)
register_business_handlers(bot)
register_travel_handlers(bot)
register_realty_handlers(bot)
register_profile_handlers(bot)
register_work_handlers(bot)
register_fight_handlers(bot)
register_inventory_handlers(bot)
register_top_handlers(bot)
register_clan_handlers(bot)
register_casino_handlers(bot)
register_misc_handlers(bot)

print("Бот запущен…")
bot.infinity_polling()

from telebot import TeleBot
from database import players, ensure_defaults

def register_misc_handlers(bot: TeleBot):
    @bot.message_handler(commands=['referrals'])
    def show_referrals(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]
        referrals = player.get("referrals", [])
        if not referrals:
            bot.send_message(message.chat.id, "❌ Ты пока не пригласил ни одного игрока.")
            return
        text = "👥 Твои приглашённые игроки:\n"
        for rid in referrals:
            rplayer = players.get(rid, {})
            text += f"- {rplayer.get('name', 'Безымянный')} (ID: {rid})\n"
        bot.send_message(message.chat.id, text)

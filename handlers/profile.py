from telebot import TeleBot
from database import players,save_db, ensure_defaults
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players, ensure_defaults

def get_profile_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🎒 Инвентарь"))
    kb.add(KeyboardButton("🤝 Пригласить друзей"))  # новая кнопка
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def register_profile_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda m: m.text == "👤 Профиль")
    def profile(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]

        # --- Данные игрока ---
        name = player.get("name", "Безымянный")
        gold = player.get("gold", 0)
        level = player.get("level", 1)
        xp = player.get("xp", 0)
        hp = player.get("hp", 100)

        # Бонусы
        attack_bonus = player.get("attack_bonus", 0)
        hp_bonus = player.get("hp_bonus", 0)

        # Экипировка
        weapon = player.get("equipped_weapon", "❌ Нет")
        armor = player.get("equipped_armor", "❌ Нет")

        # Расчёты
        max_hp = 100 + hp_bonus
        need_xp = 100 * level
        progress_blocks = 10
        filled = int((xp / need_xp) * progress_blocks) if need_xp > 0 else 0
        xp_bar = "▓" * filled + "░" * (progress_blocks - filled)

        # Рейтинг
        sorted_by_level = sorted(players.values(), key=lambda p: p.get("level", 1), reverse=True)
        level_rank = sorted_by_level.index(player) + 1 if player in sorted_by_level else "?"
        sorted_by_gold = sorted(players.values(), key=lambda p: p.get("gold", 0), reverse=True)
        gold_rank = sorted_by_gold.index(player) + 1 if player in sorted_by_gold else "?"
        total_players = len(players)

        text = (
            f"👤 {name}\n"
            f"🏅 Уровень: {level}\n"
            f"⭐ Опыт: {xp}/{need_xp} {xp_bar}\n\n"
            f"❤️ Здоровье: {hp}/{max_hp}\n"
            f"⚔ Атака: {10 + attack_bonus}\n\n"
            f"💰 Золото: {gold}\n\n"
            f"🗡 Оружие: {weapon}\n"
            f"🛡 Броня: {armor}\n\n"
            f"📊 Рейтинг по уровню: {level_rank}/{total_players}\n"
            f"💸 Рейтинг по золоту: {gold_rank}/{total_players}\n"
        )

        bot.send_message(message.chat.id, text, reply_markup=get_profile_keyboard())

    @bot.message_handler(func=lambda m: m.text == "🤝 Пригласить друзей")
    def invite_friends(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        player = players[uid]

        # Устанавливаем уникальный реферальный код, если ещё нет
        if "referral_code" not in player:
            player["referral_code"] = uid
            player["referrals"] = []

        referral_code = player["referral_code"]
        referral_link = f"https://t.me/NewGameBot2025_bot?start={referral_code}"
        bot.send_message(
            message.chat.id,
            f"🤝 Приглашай друзей и получай бонусы!\n\nТвоя уникальная ссылка:\n{referral_link}"
        )

# clans.py
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players, clans, save_db, ensure_defaults
import random, time

# Доступные улучшения и их стоимость
CLAN_UPGRADES = {
    "Улучшение казны (+50💰/час)": 150,
    "Улучшение уровня": 100,
    "Улучшение обороны": 200,
    "Улучшение производства": 250
}

def get_clan_root_keyboard(uid: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    player = players[uid]
    clan_id = player.get("clan_id")
    if clan_id and clan_id in clans:
        kb.add(KeyboardButton("📊 Кланское меню"))
        kb.add(KeyboardButton("⬅️ Выйти из клана"))
    else:
        kb.add(KeyboardButton("🆕 Создать клан"))
        kb.add(KeyboardButton("🔍 Вступить в клан"))
        kb.add(KeyboardButton("🔍 Вступить по ID"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_clan_management_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Внести золото"))
    kb.add(KeyboardButton("⬆️ Улучшить клан"))
    kb.add(KeyboardButton("👥 Список участников"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_clan_upgrade_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for name, cost in CLAN_UPGRADES.items():
        kb.add(KeyboardButton(f"⬆️ {name} ({cost}💰)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def register_clan_handlers(bot: TeleBot):

    @bot.message_handler(func=lambda m: m.text == "🏰 Кланы")
    def open_clan_menu(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        bot.send_message(
            message.chat.id,
            "📜 Клановое меню:",
            reply_markup=get_clan_root_keyboard(uid)
        )

    @bot.message_handler(func=lambda m: m.text == "🆕 Создать клан")
    def create_clan(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        if players[uid].get("clan_id"):
            bot.send_message(message.chat.id, "❌ Ты уже в клане!")
            return
        clan_id = str(int(time.time() * 1000) + random.randint(0, 999))
        clans[clan_id] = {
            "name": f"Клан_{random.randint(100,999)}",
            "owner": uid,
            "deputy": None,
            "members": [uid],
            "level": 1,
            "gold": 0,
            "upgrades": {}
        }
        players[uid]["clan_id"] = clan_id
        save_db()
        bot.send_message(message.chat.id, f"✅ Клан создан! Название: {clans[clan_id]['name']}", reply_markup=get_clan_root_keyboard(uid))

    @bot.message_handler(func=lambda m: m.text == "🔍 Вступить в клан")
    def join_random_clan(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        if players[uid].get("clan_id"):
            bot.send_message(message.chat.id, "❌ Ты уже в клане!")
            return
        if not clans:
            bot.send_message(message.chat.id, "❌ Нет доступных кланов для вступления.")
            return
        clan_id = random.choice(list(clans.keys()))
        clans[clan_id]["members"].append(uid)
        players[uid]["clan_id"] = clan_id
        save_db()
        bot.send_message(message.chat.id, f"✅ Ты вступил в клан {clans[clan_id]['name']}", reply_markup=get_clan_root_keyboard(uid))

    @bot.message_handler(func=lambda m: m.text == "🔍 Вступить по ID")
    def join_clan_by_id(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        msg = bot.send_message(message.chat.id, "Введите ID клана, в который хотите вступить:")
        bot.register_next_step_handler(msg, process_clan_id, uid)

    def process_clan_id(message, uid):
        clan_id = message.text.strip()
        if clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Клан с таким ID не найден!")
            return
        if uid in clans[clan_id]["members"]:
            bot.send_message(message.chat.id, "❌ Ты уже в этом клане!")
            return
        clans[clan_id]["members"].append(uid)
        players[uid]["clan_id"] = clan_id
        save_db()
        bot.send_message(message.chat.id, f"✅ Ты вступил в клан {clans[clan_id]['name']}", reply_markup=get_clan_root_keyboard(uid))

    @bot.message_handler(func=lambda m: m.text == "⬅️ Выйти из клана")
    def leave_clan(message):
        uid = str(message.from_user.id)
        clan_id = players[uid].get("clan_id")
        if not clan_id or clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Ты не в клане!")
            return
        clan = clans[clan_id]
        clan["members"].remove(uid)
        players[uid]["clan_id"] = None
        save_db()
        bot.send_message(message.chat.id, f"✅ Ты покинул клан {clan['name']}", reply_markup=get_clan_root_keyboard(uid))

    @bot.message_handler(func=lambda m: m.text == "📊 Кланское меню")
    def clan_management(message):
        uid = str(message.from_user.id)
        clan_id = players[uid].get("clan_id")
        if not clan_id or clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Ты не в клане!")
            return
        clan = clans[clan_id]
        text = (
            f"🏰 Клан: {clan['name']}\n"
            f"💰 Золото клана: {clan['gold']}\n"
            f"⭐ Уровень: {clan['level']}\n"
            f"👥 Кол-во участников: {len(clan['members'])}\n"
            f"🔧 Улучшения: {', '.join(clan['upgrades'].keys()) if clan['upgrades'] else 'Нет'}"
        )
        bot.send_message(message.chat.id, text, reply_markup=get_clan_management_keyboard())

    @bot.message_handler(func=lambda m: m.text == "💰 Внести золото")
    def deposit_gold(message):
        uid = str(message.from_user.id)
        clan_id = players[uid].get("clan_id")
        if not clan_id or clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Ты не в клане!")
            return
        clan = clans[clan_id]
        gold = players[uid].get("gold", 0)
        if gold <= 0:
            bot.send_message(message.chat.id, "❌ У тебя нет золота для вклада!")
            return
        clan["gold"] += gold
        players[uid]["gold"] = 0
        save_db()
        bot.send_message(message.chat.id, f"💰 Ты внес {gold}💰 в казну клана!", reply_markup=get_clan_management_keyboard())

    @bot.message_handler(func=lambda m: m.text == "⬆️ Улучшить клан")
    def choose_upgrade(message):
        bot.send_message(message.chat.id, "Выбери улучшение:", reply_markup=get_clan_upgrade_keyboard())

    @bot.message_handler(func=lambda m: any(m.text.startswith(f"⬆️ {name}") for name in CLAN_UPGRADES))
    def upgrade_clan(message):
        uid = str(message.from_user.id)
        clan_id = players[uid].get("clan_id")
        if not clan_id or clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Ты не в клане!")
            return
        clan = clans[clan_id]

        selected_upgrade = next((name for name in CLAN_UPGRADES if message.text.startswith(f"⬆️ {name}")), None)
        if not selected_upgrade:
            bot.send_message(message.chat.id, "❌ Неверное улучшение!", reply_markup=get_clan_management_keyboard())
            return

        cost = CLAN_UPGRADES[selected_upgrade]
        if clan["gold"] < cost:
            bot.send_message(message.chat.id, f"❌ Недостаточно золота для улучшения! Нужно {cost}💰", reply_markup=get_clan_management_keyboard())
            return

        clan["gold"] -= cost
        # Применяем улучшение
        if "уровня" in selected_upgrade.lower():
            clan["level"] += 1
        clan["upgrades"][selected_upgrade] = True
        save_db()
        bot.send_message(message.chat.id, f"⬆️ Клан улучшен! Применено: {selected_upgrade}\n💰 Потрачено золота: {cost}", reply_markup=get_clan_management_keyboard())

    @bot.message_handler(func=lambda m: m.text == "👥 Список участников")
    def list_members(message):
        uid = str(message.from_user.id)
        clan_id = players[uid].get("clan_id")
        if not clan_id or clan_id not in clans:
            bot.send_message(message.chat.id, "❌ Ты не в клане!")
            return
        clan = clans[clan_id]
        lines = []
        for member_id in clan["members"]:
            member_name = players.get(member_id, {}).get("name", "Безымянный")
            role = "Владелец" if member_id == clan["owner"] else "Заместитель" if member_id == clan.get("deputy") else "Участник"
            lines.append(f"{member_name} — {role}")
        bot.send_message(message.chat.id, "👥 Участники клана:\n" + "\n".join(lines), reply_markup=get_clan_management_keyboard())

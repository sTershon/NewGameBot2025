# handlers/business.py
from telebot import TeleBot
from database import players, save_db
from keyboards import get_business_menu_keyboard, get_business_buy_keyboard
from data.game_data import CITIES
import time

CITY_TAX = {
    "Москва": 0.05,
    "Париж": 0.10,
    "Лондон": 0.08,
}
MAX_HOURS_WITHOUT_COLLECT = 6     # если копишь больше этого — часть прибыли сгорает
LOSS_RATE = 0.30                  # процент потерь
PROFIT_COOLDOWN = 3600            # 1 час в секундах


# ================= ВСПОМОГАТЕЛЬНЫЕ =================

def _find_business_cfg(city: str, name: str):
    """Находит настройки бизнеса по имени и городу."""
    for b in CITIES.get(city, {}).get("businesses", []):
        if b["name"] == name:
            return b
    # fallback: ищем во всех городах
    for c, data in CITIES.items():
        for b in data.get("businesses", []):
            if b["name"] == name:
                return b | {"city": c}
    return None


def _normalize_owned_business(entry, fallback_city: str):
    """Приводит старый формат бизнеса (строка) к новому формату (dict)."""
    if isinstance(entry, dict):
        name = entry.get("name")
        city = entry.get("city", fallback_city)
        profit = entry.get("profit")
        last_collect = entry.get("last_collect", 0)
        if profit is None:
            cfg = _find_business_cfg(city, name) or {}
            profit = cfg.get("profit", 0)
        return {"name": name, "city": city, "profit": profit, "last_collect": last_collect}
    else:
        name = str(entry)
        city = fallback_city
        cfg = _find_business_cfg(city, name) or {}
        return {"name": name, "city": cfg.get("city", city), "profit": cfg.get("profit", 0), "last_collect": 0}


def _normalize_player_businesses(uid: str):
    """Миграция: приводит все бизнесы игрока к dict-формату."""
    p = players[uid]
    city = p.get("city", "Москва")
    owned = p.get("businesses", [])
    normalized = [_normalize_owned_business(e, city) for e in owned]
    p["businesses"] = normalized
    return normalized


# ================== РЕГИСТРАЦИЯ ХЕНДЛЕРОВ ==================

def register_business_handlers(bot: TeleBot):

    # Главное меню бизнесов
    @bot.message_handler(func=lambda m: m.text == "💼 Бизнес")
    def business_root(message):
        bot.send_message(message.chat.id, "💼 Меню бизнеса:", reply_markup=get_business_menu_keyboard())

    # Мои бизнесы
    @bot.message_handler(func=lambda m: m.text == "📜 Мои бизнесы")
    def my_businesses(message):
        uid = str(message.from_user.id)
        owned = _normalize_player_businesses(uid)
        if not owned:
            bot.send_message(message.chat.id, "❌ У тебя пока нет бизнесов.")
            return

        now_ts = time.time()
        lines = []
        for b in owned:
            remaining = max(0, PROFIT_COOLDOWN - int(now_ts - b.get("last_collect", 0)))
            rem_min = remaining // 60
            lines.append(f"• {b['name']} ({b['city']}) — {b['profit']}💰/час | до сбора: {rem_min} мин")
        save_db()
        bot.send_message(message.chat.id, "📋 Твои бизнесы:\n" + "\n".join(lines))

    # Купить бизнес (меню)
    @bot.message_handler(func=lambda m: m.text == "🏭 Купить бизнес")
    def buy_business_menu(message):
        uid = str(message.from_user.id)
        city = players[uid].get("city", "Москва")
        bot.send_message(message.chat.id, f"🏭 Доступные бизнесы в {city}:", reply_markup=get_business_buy_keyboard(city))

    # Купить конкретный бизнес
    @bot.message_handler(func=lambda m: m.text.startswith("Купить бизнес: "))
    def buy_business(message):
        uid = str(message.from_user.id)
        p = players[uid]
        city = p.get("city", "Москва")
        business_name = message.text.replace("Купить бизнес: ", "").split(" (")[0]

        cfg = _find_business_cfg(city, business_name)
        if not cfg:
            bot.send_message(message.chat.id, "❌ Бизнес не найден.")
            return

        price = cfg["price"]
        if p["gold"] < price:
            bot.send_message(message.chat.id, "❌ Недостаточно золота!")
            return

        p["gold"] -= price
        p.setdefault("businesses", [])
        p["businesses"].append({
            "name": cfg["name"],
            "city": city,
            "profit": cfg["profit"],
            "last_collect": time.time()
        })
        save_db()
        bot.send_message(message.chat.id, f"✅ Куплен бизнес: {cfg['name']} за {price}💰")

    # Собрать прибыль
    @bot.message_handler(func=lambda m: m.text == "💰 Собрать прибыль")
    def collect_profit(message):
        uid = str(message.from_user.id)
        p = players[uid]
        owned = _normalize_player_businesses(uid)  # твоя функция, нормализует список бизнесов
        if not owned:
            bot.send_message(message.chat.id, "❌ У тебя нет бизнесов для прибыли.")
            return

        now_ts = time.time()
        total = 0
        collected_any = False
        details = []

        for b in owned:
            last_collect = b.get("last_collect", 0)
            elapsed = now_ts - last_collect

            if elapsed >= PROFIT_COOLDOWN and b["profit"] > 0:
                earned = b["profit"]  # прибыль за день
                tax_rate = CITY_TAX.get(b["city"], 0.05)  # налог города
                tax = int(earned * tax_rate)
                earned -= tax

                details.append(f"{b['name']} ({b['city']}) — прибыль {earned}💰 (налог {tax}💰)")
                total += earned

                b["last_collect"] = now_ts
                collected_any = True
            else:
                remaining = int((PROFIT_COOLDOWN - elapsed) // 3600)
                details.append(f"{b['name']} ({b['city']}) — ждать ещё {remaining}ч")

        if not collected_any:
            bot.send_message(message.chat.id, "⏳ Пока нечего собирать.\n\n" + "\n".join(details))
            return

        p["gold"] += total
        p["businesses"] = owned
        save_db()

        text = f"💰 Собрано прибыли: {total}💰\n\n" + "\n".join(details)
        bot.send_message(message.chat.id, text)
 
    @bot.message_handler(func=lambda m: m.text == "📑 Собрать аренду")
    def collect_rent(message):
        uid = str(message.from_user.id)
        p = players[uid]
        owned = p.get("realty", [])
        if not owned:
            bot.send_message(message.chat.id, "❌ У тебя нет недвижимости.")
            return

        now_ts = time.time()
        total = 0
        collected_any = False
        details = []

        for r in owned:
            last_collect = r.get("last_collect", 0)
            elapsed = now_ts - last_collect

            if elapsed >= PROFIT_COOLDOWN and r["rent"] > 0:
                earned = r["rent"]  # аренда за день
                details.append(f"{r['name']} — аренда {earned}💰")
                total += earned
                r["last_collect"] = now_ts
                collected_any = True
            else:
                remaining = int((PROFIT_COOLDOWN - elapsed) // 3600)
                details.append(f"{r['name']} — ждать ещё {remaining}ч")

        if not collected_any:
            bot.send_message(message.chat.id, "⏳ Пока нечего собирать.\n\n" + "\n".join(details))
            return

        p["gold"] += total
        p["realty"] = owned
        save_db()

        text = f"🏘 Собрано аренды: {total}💰\n\n" + "\n".join(details)
        bot.send_message(message.chat.id, text)
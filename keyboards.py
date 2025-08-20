# keyboards.py
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import ADMINS
from database import players, clans
from data.game_data import CITIES, DESTINATIONS

# --- Основное меню ---
def get_main_keyboard(user_id: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("👤 Профиль"), KeyboardButton("⚒ Работа"))
    kb.add(KeyboardButton("⚔ Бой"), KeyboardButton("❤️ Лечение"))
    kb.add(KeyboardButton("🛒 Магазин"), KeyboardButton("💼 Бизнес"))
    kb.add(KeyboardButton("🎒 Инвентарь"))
    kb.add(KeyboardButton("🎰 Казино"))
    kb.add(KeyboardButton("🏰 Кланы")) 
    kb.add(KeyboardButton("🏘 Недвижимость"))
    kb.add(KeyboardButton("✈️ Перелёт"))
    if str(user_id) in ADMINS:
        kb.add(KeyboardButton("⚙️ Админка"))
    return kb

# --- Админка ---
def get_admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📊 Все игроки"), KeyboardButton("👑 Выдать золото себе"))
    kb.add(KeyboardButton("🔎 Поиск по ID"), KeyboardButton("💰 Выдать золото по ID"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Магазины ---
def get_shop_root_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Товары города"))
    kb.add(KeyboardButton("🛫 Магазин перелётов"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_city_shop_keyboard(city: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in CITIES.get(city, {}).get("shop", []):
        kb.add(KeyboardButton(f"Купить: {item['name']} ({item['price']}💰)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_travel_shop_keyboard(travel_pass_price: int):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton(f"🗺 Карта выезда ({travel_pass_price}💰)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Перелёты ---
def get_travel_dest_keyboard(current_city: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for city in DESTINATIONS:
        if city != current_city:
            kb.add(KeyboardButton(f"Лететь: {city}"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Бизнесы ---
def get_business_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📜 Мои бизнесы"))
    kb.add(KeyboardButton("🏭 Купить бизнес"))
    kb.add(KeyboardButton("💰 Собрать прибыль"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_business_buy_keyboard(city: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for b in CITIES.get(city, {}).get("businesses", []):
        kb.add(KeyboardButton(f"Купить бизнес: {b['name']} ({b['price']}💰 / {b['profit']}💰/час)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Недвижимость ---
def get_realty_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🏠 Моя недвижимость"))
    kb.add(KeyboardButton("🛒 Купить недвижимость"))
    kb.add(KeyboardButton("📑 Сдать в аренду"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_realty_buy_keyboard(city: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for r in CITIES.get(city, {}).get("realty", []):
        kb.add(KeyboardButton(f"Купить дом: {r['name']} ({r['price']}💰 / аренда {r['rent']}💰)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Клан ---
def get_clan_root_keyboard(uid: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    player = players.get(uid)
    clan_id = player.get("clan_id") if player else None
    if clan_id and clan_id in clans:
        kb.add(KeyboardButton("📊 Кланское меню"))
        kb.add(KeyboardButton("⬅️ Выйти из клана"))
    else:
        kb.add(KeyboardButton("🆕 Создать клан"))
        kb.add(KeyboardButton("🔍 Вступить в клан"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_clan_management_keyboard(clan_id: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💰 Внести золото"))
    kb.add(KeyboardButton("⬆️ Улучшить клан"))
    kb.add(KeyboardButton("👥 Список участников"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_upgrade_keyboard(clan_id: str):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    clan = clans[clan_id]
    upgrades = {
        "Улучшение казны (+50💰/час)": 150,
        "Улучшение армии (+10 атаки)": 200,
        "Улучшение крепости (+50 HP)": 250
    }
    for name, cost in upgrades.items():
        if name not in clan["upgrades"]:
            kb.add(KeyboardButton(f"{name} ({cost}💰)"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Пример других клавиатур (магазин, недвижимость и т.д.) ---
def get_shop_root_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Товары города"))
    kb.add(KeyboardButton("🛫 Магазин перелётов"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

def get_realty_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🏠 Моя недвижимость"))
    kb.add(KeyboardButton("🛒 Купить недвижимость"))
    kb.add(KeyboardButton("📑 Сдать в аренду"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb

# --- Админская клавиатура ---
def get_admin_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📊 Все игроки"), KeyboardButton("👑 Выдать золото себе"))
    kb.add(KeyboardButton("🔎 Поиск по ID"), KeyboardButton("💰 Выдать золото по ID"))
    kb.add(KeyboardButton("🎨 Выдать тег по цвету"), KeyboardButton("📊 Изменить статистику игрока"))
    kb.add(KeyboardButton("⚡ Очистить достижения"), KeyboardButton("🛡 Выдать админку"))
    kb.add(KeyboardButton("📢 Разослать всем"))
    kb.add(KeyboardButton("⬅️ Назад"))
    return kb
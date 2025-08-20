import json
from time import time
from config import DB_FILE, CLANS_FILE

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        players = json.load(f)
except FileNotFoundError:
    players = {}

try:
    with open(CLANS_FILE, "r", encoding="utf-8") as f:
        clans = json.load(f)
except FileNotFoundError:
    clans = {}

def ensure_defaults(user_id: str, name: str):
    p = players.setdefault(user_id, {})
    p.setdefault("name", name or "Безымянный")
    p.setdefault("gold", 100)
    p.setdefault("level", 1)
    p.setdefault("xp", 0)
    p.setdefault("hp", 100)
    p.setdefault("city", "Начальный")
    p.setdefault("exit_pass", False)
    p.setdefault("inventory", [])
    p.setdefault("businesses", [])  # [{name, city, profit, last_collect}]
    p.setdefault("stage", None)
    p.setdefault("clan_id", None)   # ссылка на клан
    return p

def now():
    return int(time())

def save_db():
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
    with open(CLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(clans, f, ensure_ascii=False, indent=2)
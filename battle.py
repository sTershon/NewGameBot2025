import random
from database import players, save_db

# Список монстров
MONSTERS = [
    {"name": "🐺 Волк", "hp": 30, "damage": (5, 10), "reward": (10, 20)},
    {"name": "🦇 Летучая мышь", "hp": 20, "damage": (3, 8), "reward": (5, 15)},
    {"name": "🦂 Скорпион", "hp": 40, "damage": (7, 12), "reward": (15, 25)},
    {"name": "🐉 Дракон", "hp": 100, "damage": (15, 30), "reward": (50, 100)},
]

def pve_battle(user_id: str):
    """PvE сражение против монстра"""
    player = players[user_id]
    monster = random.choice(MONSTERS)
    
    log = [f"⚔ Ты встретил монстра: {monster['name']} (HP: {monster['hp']})"]

    player_attack = random.randint(10, 20)
    monster_attack = random.randint(*monster["damage"])

    # Игрок атакует
    monster["hp"] -= player_attack
    log.append(f"Ты ударил и нанёс {player_attack} урона! {monster['name']} осталось {max(monster['hp'], 0)} HP")

    # Если монстр жив — он атакует
    if monster["hp"] > 0:
        player["hp"] -= monster_attack
        log.append(f"{monster['name']} атакует! Ты получил {monster_attack} урона. У тебя {player['hp']} HP.")
    else:
        reward_gold = random.randint(*monster["reward"])
        reward_xp = reward_gold // 2
        player["gold"] += reward_gold
        player["xp"] += reward_xp
        log.append(f"🎉 Ты победил {monster['name']}! Получено {reward_gold}💰 и {reward_xp}🔥 XP.")

    # Проверяем, не умер ли игрок
    if player["hp"] <= 0:
        player["hp"] = 100
        log.append("☠️ Ты погиб в бою... но воскрес с 100 HP.")

    save_db()
    return "\n".join(log)


def pvp_battle(attacker_id: str, defender_id: str):
    """PvP битва между игроками"""
    if defender_id not in players or "name" not in players[defender_id]:
        return "❌ Игрок для боя не найден!"

    attacker = players[attacker_id]
    defender = players[defender_id]

    log = [f"⚔ Бой между {attacker['name']} и {defender['name']}!"]

    attack_power = random.randint(10, 20)
    defender["hp"] -= attack_power
    log.append(f"{attacker['name']} ударил {defender['name']} на {attack_power} урона! У {defender['name']} {max(defender['hp'], 0)} HP.")

    if defender["hp"] <= 0:
        defender["hp"] = 100
        reward = 50
        attacker["gold"] += reward
        attacker["xp"] += reward // 2
        log.append(f"💀 {defender['name']} пал в бою. {attacker['name']} получает {reward}💰 и {reward//2}🔥 XP. {defender['name']} воскрес с 100 HP.")

    save_db()
    return "\n".join(log)

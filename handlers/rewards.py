# handlers/rewards.py
import datetime
from database import players, save_db

# Награды (можно настроить)
WEEKLY_REWARDS = {
    1: {"gold": 5000, "item": "Корона чемпиона"},
    2: {"gold": 3000},
    3: {"gold": 1500},
}

def give_weekly_rewards(bot):
    # Сортировка игроков по золоту (можно заменить на уровень/победы)
    sorted_players = sorted(players.items(), key=lambda x: x[1].get("gold", 0), reverse=True)

    rewards_given = []
    for place, (uid, player) in enumerate(sorted_players[:3], start=1):
        reward = WEEKLY_REWARDS.get(place)
        if not reward:
            continue

        # Добавляем золото
        if "gold" in reward:
            player["gold"] = player.get("gold", 0) + reward["gold"]

        # Добавляем предмет
        if "item" in reward:
            inventory = player.setdefault("inventory", [])
            found = next((i for i in inventory if i["name"] == reward["item"]), None)
            if found:
                found["count"] += 1
            else:
                inventory.append({
                    "name": reward["item"],
                    "type": "misc",
                    "value": 0,
                    "count": 1
                })

        rewards_given.append((player["name"], place, reward))
    
    save_db()

    # Уведомляем всех, что награды выданы
    for name, place, reward in rewards_given:
        text = f"🏆 {name} занял {place} место и получил:\n"
        if "gold" in reward:
            text += f"💰 {reward['gold']} золота\n"
        if "item" in reward:
            text += f"🎁 предмет: {reward['item']}\n"
        bot.send_message(123456789, text)  # 🔴 сюда можно список админов или канал

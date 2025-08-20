# data/game_data.py

CITIES = {
    "Москва": {
        "shop": [
            {"name": "Зелье лечения", "price": 100, "type": "heal", "value": 30},
            {"name": "Меч воина", "price": 500, "type": "weapon", "value": 10},
            {"name": "Броня новичка", "price": 800, "type": "armor", "value": 5},

            # дорогие вещи
            {"name": "Меч героя", "price": 10000, "type": "weapon", "value": 25},
            {"name": "Легендарная броня", "price": 15000, "type": "armor", "value": 20},
        ],
        "businesses": [
            {"name": "Ларёк с шаурмой", "price": 2000, "profit": 200},
            {"name": "Магазин одежды", "price": 8000, "profit": 900},
            {"name": "Завод", "price": 50000, "profit": 6000},
        ],
        "realty": [
            {"name": "Хрущёвка", "price": 5000, "rent": 200},
            {"name": "Элитная квартира", "price": 20000, "rent": 1000},
            {"name": "Вилла", "price": 100000, "rent": 5000},
        ]
    },

    "Питер": {
        "shop": [
            {"name": "Зелье энергии", "price": 150, "type": "heal", "value": 40},
            {"name": "Сабля казака", "price": 700, "type": "weapon", "value": 15},
            {"name": "Стальная броня", "price": 18000, "type": "armor", "value": 25},
            {"name": "Меч северного воина", "price": 12000, "type": "weapon", "value": 30},
        ],
        "businesses": [
            {"name": "Киоск у Невы", "price": 2500, "profit": 250},
            {"name": "Бар", "price": 12000, "profit": 1300},
            {"name": "Фабрика", "price": 60000, "profit": 7500},
        ],
        "realty": [
            {"name": "Коммуналка", "price": 3000, "rent": 150},
            {"name": "Квартира у Невы", "price": 15000, "rent": 800},
            {"name": "Особняк на Васильевском", "price": 75000, "rent": 4000},
        ]
    },

    "Казань": {
        "shop": [
            {"name": "Татарский пирог", "price": 80, "type": "heal", "value": 20},
            {"name": "Боевой лук", "price": 600, "type": "weapon", "value": 12},
            {"name": "Кожаная броня", "price": 2000, "type": "armor", "value": 8},
            {"name": "Эпический лук", "price": 14000, "type": "weapon", "value": 28},
        ],
        "businesses": [
            {"name": "Чайхана", "price": 1800, "profit": 150},
            {"name": "Ресторан", "price": 15000, "profit": 1600},
            {"name": "Торговый центр", "price": 70000, "profit": 9000},
        ],
        "realty": [
            {"name": "Маленькая квартира", "price": 4000, "rent": 180},
            {"name": "Дом у Кремля", "price": 25000, "rent": 1200},
            {"name": "Элитный коттедж", "price": 120000, "rent": 6500},
        ]
    }
}

# Города, доступные для путешествий
DESTINATIONS = list(CITIES.keys())

# Стоимость карты для перелёта
TRAVEL_PASS_PRICE = 5000

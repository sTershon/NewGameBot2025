# casino.py
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from database import players, save_db, ensure_defaults
from random import randint, choice

def register_casino_handlers(bot: TeleBot):
    # Главное меню казино
    @bot.message_handler(func=lambda m: m.text == "🎰 Казино")
    def open_casino_menu(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(KeyboardButton("🎲 Кубик"))
        kb.add(KeyboardButton("🎰 Слот-машина"))
        kb.add(KeyboardButton("🎯 Угадай число"))
        kb.add(KeyboardButton("⬅️ Назад"))
        bot.send_message(message.chat.id, "🎰 Выберите игру:", reply_markup=kb)

    # ---------------- Кубик ----------------
    @bot.message_handler(func=lambda m: m.text == "🎲 Кубик")
    def play_dice(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        msg = bot.send_message(message.chat.id, "Введите ставку (💰):")
        bot.register_next_step_handler(msg, process_dice_bet)

    def process_dice_bet(message):
        uid = str(message.from_user.id)
        try:
            bet = int(message.text)
            if bet <= 0:
                raise ValueError
            if players[uid]["gold"] < bet:
                bot.send_message(message.chat.id, "❌ Недостаточно золота!")
                return
            roll = randint(1, 6)
            win = roll >= 4  # выигрывает при 4,5,6
            if win:
                players[uid]["gold"] += bet
                bot.send_message(message.chat.id, f"🎲 Выпало {roll}! Вы выиграли {bet}💰")
            else:
                players[uid]["gold"] -= bet
                bot.send_message(message.chat.id, f"🎲 Выпало {roll}! Вы проиграли {bet}💰")
            save_db()
        except:
            bot.send_message(message.chat.id, "❌ Неверная ставка!")

    # ---------------- Слот-машина ----------------
    @bot.message_handler(func=lambda m: m.text == "🎰 Слот-машина")
    def play_slot(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        msg = bot.send_message(message.chat.id, "Введите ставку (💰):")
        bot.register_next_step_handler(msg, process_slot_bet)

    def process_slot_bet(message):
        uid = str(message.from_user.id)
        try:
            bet = int(message.text)
            if bet <= 0:
                raise ValueError
            if players[uid]["gold"] < bet:
                bot.send_message(message.chat.id, "❌ Недостаточно золота!")
                return
            symbols = ["🍒", "🍋", "🔔", "⭐", "7️⃣"]
            result = [choice(symbols) for _ in range(3)]
            bot.send_message(message.chat.id, " | ".join(result))
            if result[0] == result[1] == result[2]:
                win_amount = bet * 5
                players[uid]["gold"] += win_amount
                bot.send_message(message.chat.id, f"🎉 Три одинаковых! Вы выиграли {win_amount}💰")
            else:
                players[uid]["gold"] -= bet
                bot.send_message(message.chat.id, f"❌ Вы проиграли {bet}💰")
            save_db()
        except:
            bot.send_message(message.chat.id, "❌ Неверная ставка!")

    # ---------------- Угадай число ----------------
    @bot.message_handler(func=lambda m: m.text == "🎯 Угадай число")
    def play_guess_number(message):
        uid = str(message.from_user.id)
        ensure_defaults(uid, message.from_user.first_name)
        msg = bot.send_message(message.chat.id, "Введите ставку (💰):")
        bot.register_next_step_handler(msg, start_guess_number)

    def start_guess_number(message):
        uid = str(message.from_user.id)
        try:
            bet = int(message.text)
            if bet <= 0:
                raise ValueError
            if players[uid]["gold"] < bet:
                bot.send_message(message.chat.id, "❌ Недостаточно золота!")
                return
            number = randint(1, 10)
            msg = bot.send_message(message.chat.id, "Угадай число от 1 до 10:")
            bot.register_next_step_handler(msg, lambda m: process_guess_number(m, number, bet))
        except:
            bot.send_message(message.chat.id, "❌ Неверная ставка!")

    def process_guess_number(message, number, bet):
        uid = str(message.from_user.id)
        try:
            guess = int(message.text)
            if guess == number:
                players[uid]["gold"] += bet * 5
                bot.send_message(message.chat.id, f"🎯 Верно! Вы выиграли {bet*5}💰")
            else:
                players[uid]["gold"] -= bet
                bot.send_message(message.chat.id, f"❌ Неверно! Выпало {number}. Вы проиграли {bet}💰")
            save_db()
        except:
            bot.send_message(message.chat.id, "❌ Введите число от 1 до 10!")

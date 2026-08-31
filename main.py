#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули
import telebot
import socket
import time
import os
from dotenv import find_dotenv, load_dotenv
from telebot import types

from src.class_game import Game

# Обход блокировки по SNI/DNS для api.telegram.org:
# оставляем URL как api.telegram.org (корректный SNI, Host и проверка сертификата),
# но заставляем DNS-резолв этого домена возвращать рабочий IP-адрес Telegram,
# чтобы TCP-подключение шло напрямую по IP, минуя блокировку имени.
TELEGRAM_API_IP = "149.154.167.221"
_original_getaddrinfo = socket.getaddrinfo


def _telegram_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "api.telegram.org":
        host = TELEGRAM_API_IP
    return _original_getaddrinfo(host, port, family, type, proto, flags)


socket.getaddrinfo = _telegram_getaddrinfo
 
# Константы и настройки
game_sessions = {}

# Запускаем бота
load_dotenv(find_dotenv())
token = os.getenv('TelegramGameToken')
bot = telebot.TeleBot(token)

#Функции бота

@bot.message_handler(commands=['start', 'старт', 's'])
def welcome(message):
    chat_id = message.chat.id
    game = game_sessions.get(chat_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Новая игра')
    itembtn2 = types.KeyboardButton('Отмена')
    if game:
        if game.game_is_on:
            markup.add(itembtn1, itembtn2)
            bot.reply_to(message, "Игра уже запущена.\nТы точно хочешь начать новую игру?\n", reply_markup=markup)
        else:
            markup.add(itembtn1)
            bot.reply_to(message, "Привет!\nХочешь начать игру?\n", reply_markup=markup)
    else:
        markup.add(itembtn1)
        bot.reply_to(message, "Привет!\nХочешь начать игру?\n", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def all_commands(message):
    global game_sessions
    text = message.text
    chat_id = message.chat.id
    game = game_sessions.get(chat_id)
    command = message.text.lower().split(' ')[0]
    if text.lower() == "новая игра":
        new_game = Game(chat_id, bot)
        game_sessions[chat_id] = new_game
        player = new_game.player
        new_game.game_is_on = True
        player.current_position.show(player)
        player.current_position.map()
        return True
    if not game:
        bot.reply_to(message, 'В этом чате нет активной игры, начните новую игру командой "Новая игра".')
        return False
    game.navigate_action(command, text)
    return True


if __name__ == "__main__":
    # Сеть нестабильна: укорачиваем таймауты запросов и long-polling,
    # чтобы соединение не успевало оборваться по read-timeout.
    telebot.apihelper.CONNECT_TIMEOUT = 10
    telebot.apihelper.READ_TIMEOUT = 10
    LONG_POLLING_TIMEOUT = 3  # короткий опрос вместо длинного (20c) соединения

    # Поллинг оборачиваем в цикл с переподключением: кратковременные
    # сетевые сбои/таймауты не должны ронять весь процесс.
    while True:
        try:
            bot.polling(
                non_stop=True,
                interval=0,
                timeout=10,
                long_polling_timeout=LONG_POLLING_TIMEOUT,
            )
        except Exception as e:
            print(f"[bot] polling crashed ({type(e).__name__}: {e}), restarting in 3s...")
            time.sleep(3)
        else:
            break

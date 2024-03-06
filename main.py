#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули
import telebot
import os
from dotenv import find_dotenv, load_dotenv
from telebot import types

from class_game import Game
 
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
    if text == "Новая игра":
        new_game = Game(chat_id, bot)
        game_sessions[chat_id] = new_game
        player = new_game.player
        new_game.game_is_on = True
        player.current_position.show(player)
        player.current_position.map()
    if game:
        game.action(command, text)
    return True

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)

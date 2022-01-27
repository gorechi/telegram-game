#!/usr/bin/python
# -*- coding: utf-8 -*-
# Импортируем необходимые модули
import telebot
from telebot import types
from functions import tprint
from constants import TOKEN
from class_game import Game
from class_items import Rune

# Константы и настройки
game_sessions = {}

# Запускаем бота
bot = telebot.TeleBot(TOKEN)

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
    common_commands = ['?',
                       'осмотреть',
                       'идти',
                       'атаковать',
                       'напасть',
                       'взять',
                       'забрать',
                       'подобрать',
                       'обыскать',
                       'открыть',
                       'использовать',
                       'применить',
                       'читать',
                       'прочитать',
                       'чинить',
                       'починить',
                       'убрать',
                       'улучшить',
                       'отдохнуть',
                       'отдыхать',
                       'бросить',
                       'сменить',
                       'поменять',
                       'выбросить']
    level_up_commands = ['здоровье',
                       '?',
                       'силу',
                       'ловкость',
                       'интеллект']
    fight_commands = ['ударить',
                      '?',
                      'защититься',
                      'бежать',
                      'сменить оружие',
                      'сменить',
                      'поменять',
                      'использовать']
    text = message.text
    chat_id = message.chat.id
    game = game_sessions.get(chat_id)
    command = message.text.lower().split(' ')[0]
    if text == "Новая игра":
        new_game = Game(chat_id, bot)
        game_sessions[chat_id] = new_game
        player = new_game.player
        new_game.game_is_on = True
        new_game.new_castle.plan[player.current_position].show(player)
        new_game.new_castle.plan[player.current_position].map()
    if game:
        if command in common_commands and game.state == 0:
            chat_id = message.chat.id
            game = game_sessions[chat_id]
            if not game.player.game_over('killall'):
                game.player.do(message.text.lower())
        elif command in level_up_commands and game.state == 3:
            if command == 'здоровье':
                game.player.health += 3
                game.player.start_health += 3
                tprint(game, game.player.name + ' получает 3 единицы здоровья.', 'off')
                game.state = 0
            elif command == 'силу':
                game.player.stren += 1
                game.player.start_stren += 1
                tprint(game, game.player.name + ' увеличивает свою силу на 1.', 'off')
                game.state = 0
            elif command == 'ловкость':
                game.player.dext += 1
                game.player.start_dext += 1
                tprint(game, game.player.name + ' увеличивает свою ловкость на 1.', 'off')
                game.state = 0
            elif command == 'интеллект':
                game.player.intel += 1
                game.player.start_intel += 1
                tprint(game, game.player.name + ' увеличивает свой интеллект на 1.', 'off')
                game.state = 0
        elif command and game.state ==2:
            answer = text.lower()
            rune_list = game.player.inpockets(Rune)
            if answer == 'отмена':
                game.state = 0
                return True
            elif answer.isdigit() and int(answer) - 1 < len(rune_list):
                if game.selected_item.enchant(rune_list[int(answer) - 1]):
                    tprint(game, game.player.name + ' улучшает ' + game.selected_item.name1 + ' новой руной.', 'off')
                    game.player.pockets.remove(rune_list[int(answer) - 1])
                    game.state = 0
                    return True
                else:
                    tprint(game, 'Похоже, что ' +
                           game.player.name +
                           'не может вставить руну в ' +
                           game.selected_item.name1 +
                           '.', 'off')
                    game.state = 0
                    return False
            else:
                tprint(game, game.player.name + ' не находит такую руну у себя в карманах.', 'off')
        elif command in fight_commands and game.state == 1:
            enemy = game.new_castle.plan[game.player.current_position].center
            tprint(game, game.player.attack(enemy, message.text))
            if game.state == 1:
                if enemy.run:
                    game.state = 0
                elif enemy.health > 0:
                    enemy.attack(game.player)
                else:
                    tprint(game, game.player.name + ' побеждает в бою!', 'off')
                    game.state = 0
                    game.player.win(enemy)
                    enemy.lose(game.player)
    return True

bot.polling(none_stop=True, interval=0)

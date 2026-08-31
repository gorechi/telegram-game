#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Оффлайн-отладка игры в консоли (без Telegram).

Заменяет бота фейковой заглушкой, которая печатает сообщения в терминал
вместо отправки в Telegram, и даёт REPL для ввода игровых команд.

Запуск:
    python debug.py

Игровые команды вводятся точно так же, как текстом в чате с ботом
(например: "новая игра", "осмотреться", "идти на север", "открыть дверь"...).
Команды-выхода REPL: exit, quit, q
"""
import sys

from src.class_game import Game


def _force_utf8():
    """Перенастроить потоки ввода/вывода на UTF-8 под Windows-консоль."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except Exception:
                pass


class FakeBot:
    """Заглушка вместо telebot.TeleBot - печатает вывод в консоль."""

    def send_message(self, chat_id, text, reply_markup=None):
        print("\n=== message ===")
        print(text)
        print("===============")
        return None

    def send_photo(self, chat_id, pic, caption=None):
        print("\n=== photo ===")
        print(f"(изображение {pic.size[0]}x{pic.size[1]})")
        if caption:
            print(caption)
        print("=============")
        return None


def run_repl():
    bot = FakeBot()
    game = None

    print("Оффлайн-отладка игры (без Telegram).", file=sys.stderr)
    print("Начните игру командой: новая игра", file=sys.stderr)
    print("Выход: exit / quit / q", file=sys.stderr)

    while True:
        try:
            line = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДо свидания!")
            break

        if not line:
            continue

        command = line.lower().split(' ')[0]

        if command in ('exit', 'quit', 'q'):
            print("До свидания!")
            break

        if line.lower() == "новая игра":
            game = Game("debug_console", bot)
            game.game_is_on = True
            player = game.player
            player.current_position.show(player)
            player.current_position.map()
            continue

        if game is None:
            print('В чате нет активной игры, начните новую игру командой "Новая игра".')
            continue

        game.navigate_action(command, line)


if __name__ == "__main__":
    _force_utf8()
    run_repl()

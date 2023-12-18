#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-
"""
    2023-12-18
    Телеграм-бот с шуточной анкетой с сохранением данных
    Fil FC Math test
    fil_fc_math_test_bot
    6935069653:AAG9ml7xd6ldG9TMyu2wc8lVoCgosJz3nRo
    https://t.me/fil_fc_math_test_bot
"""

from lists import *

import time
import random

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, Message

random.seed(time.time())

TOKEN = "6935069653:AAG9ml7xd6ldG9TMyu2wc8lVoCgosJz3nRo"
bot = TeleBot(TOKEN)

# Меню с предложением тестирования
markup = ReplyKeyboardMarkup(
    row_width=2)
NEW_TEST_COMMAND = "new_test"
NEW_TEST_MENU = "♨️ Новый тест"
RESUME_COMMAND = "resume"
RESUME_MENU = "♨️ Продолжить"
markup.add(
    * [NEW_TEST_MENU, RESUME_MENU])

# Меню с вариантами ответа (от 0 до 9)
markupNumbers = ReplyKeyboardMarkup(
    row_width=10)
digits = {
    1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
    6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 0: "0️⃣",
}
markupNumbers.add(* digits.values())

# Меню с предложением посмотреть свои и чужие результаты
markupStat = ReplyKeyboardMarkup(
    row_width=2)
MY_STAT_COMMAND = "my_stat"
MY_STAT_MENU = "〽️ Мой результат"
BEST_COMMAND = "best"
BEST_MENU = "🏆 Чемпионы"
markupStat.add(* [MY_STAT_MENU, BEST_MENU])


Settings = {
    "this_hour": -1,
    "record_table": []
}


def generate_record_table() -> None:
    if Settings["this_hour"] != int(time.strftime("%H")):
        Settings["this_hour"] = int(time.strftime("%H"))
        Settings["record_table"] = []
        for i in range(1, 6):
            Settings["record_table"].append(
                f"<b>{i}</b>. Telegram user "
                f"#{random.randint(2124501689-1000000,
                                   2124501689+1000000)}: "
                f" <b>{100 - i * 6 - random.randint(-3, 3)}</b>%"
            )


Users = {}
# Количество вопросов в тесте. С формой "вопросов"
Q_MAX = 10
ANSWER_NOTE = "<i>если результат многозначный, дайте ответ по модулю 10</i>"
math_person = ["Колмановскому", "Карлу Гауссу", "Леонарду Эйлеру", "Евклиду",
               "Пифагору", "Архимеду", "Менелаю", "Фалесу", "Птолемею",
               "Фибоначчи", "Вейерштрассу",]


# Здороваемся, говорим кратко о возможностях бота
@bot.message_handler(
    func=lambda message:
    any(word in message.text.lower()
        for word in ['старт', 'start', 'cnfhn', 'ыефке',
                     'помощ', 'help', 'gjvjo', 'рудз', ]),
    content_types=["text"])
@bot.message_handler(
    commands=["start", "help"])
def handle_start(message: Message):
    """ Функция с подсказками """
    generate_record_table()
    ave = math_person[random.randint(0, len(math_person) - 1)]
    bot.send_message(
        message.chat.id,
        f"Слава {ave}, к нам пришёл {message.chat.first_name}!\n\n"
        f"Мир полон слухов, что ты великий математик.\n"
        f"Штош, это можно легко проверить.\n"
        f"<b>Всего {Q_MAX + 1} вопросов!</b>\n\n"
        f"Начать новый тест /new_test\n"
        f"Продолжить уже начатый /resume\n"
        f"Посмотреть свою статистику /my_stat\n"
        f"Таблица чемпионов /best\n\n"
        f"Вспомнить список команд: /help",
        parse_mode="HTML",
        reply_markup=markup
    )


# Новый тест
@bot.message_handler(
    func=lambda message: message.text in [NEW_TEST_MENU, RESUME_MENU],
    content_types=["text"])
@bot.message_handler(
    commands=[NEW_TEST_COMMAND, RESUME_COMMAND])
def handle_new_test(message: Message):
    """ Новый тест, если не было. Продолжение, если было """
    # print(message)
    user_id = message.from_user.id

    if user_id not in Users.keys():
        q_id = get_new_question_id(but_id=-1)
        Users[user_id] = {
            "attempts": 1,  # какая по счёту попытка
            "time_first": time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_last": time.strftime("%Y-%m-%d %H:%M:%S"),
            "q_num_now": 1,  # текущий вопрос по счёту для пользователя
            "q_id_now": q_id,  # текущий вопрос, id в базе вопросов
            "q_correct": 0,  # правильных ответов
            "test_started": True,  # тест начат
            "test_finished": False,  # тест пройден до конца?
        }
        bot.send_message(
            message.chat.id,
            "Начинаем тестирование!"
            )
    else:
        Users[user_id]['test_finished'] = False
        q_id = Users[user_id]['q_id_now']
        bot.send_message(
            message.chat.id,
            f"Вы прервали тестирование {Users[user_id]['time_last']}\n"
            f"на вопросе №{Users[user_id]['q_num_now']}.\n"
            f"Продолжаем тестирование.",
        )

    bot.send_message(
        message.chat.id,
        f"<b>Вопрос №{Users[user_id]['q_num_now']} "
        f"из {Q_MAX + 1}</b>\n\n"
        f"{questions[q_id]}\n\n"
        f"{ANSWER_NOTE}",
        parse_mode="HTML",
        reply_markup=markupNumbers)


# Обработка ответов
@bot.message_handler(
    content_types=["text"],
    func=lambda message: message.text in digits.values()
)
def handle_answer(message: Message):
    """ Ответ пользователя? """
    user_id = message.from_user.id
    # если не начинал
    if user_id not in Users.keys():
        bot.reply_to(
            message,
            f"Не понимаю. Возможно, опечатка? Попробуйте /help",
            parse_mode="HTML",
            reply_markup=markup)
    elif Users[user_id]["test_started"] and not Users[user_id]["test_finished"]:
        answer = [k for k, v in digits.items() if v == message.text][0]
        bot.reply_to(
            message,
            f"<b>Ваш ответ на вопрос №{Users[user_id]['q_num_now']}</b>: "
            f"{answer}\n\n"
            f"😲 {bad_comment[random.randint(0, len(bad_comment) - 1)]}",
            parse_mode="HTML")

        Users[user_id]["time_last"] = time.strftime("%Y-%m-%d %H:%M:%S")
        Users[user_id]['q_num_now'] += 1
        if Users[user_id]['q_num_now'] > Q_MAX:
            Users[user_id]["test_finished"] = True
            Users[user_id]['q_num_now'] = 1
            Users[user_id]['attempts'] += 1

            bot.send_message(
                message.chat.id,
                f"В тесте {Q_MAX + 1} вопросов, но результат очевиден... "
                f"Не буду вас больше мучить.\n\n"
                f"Можете посмотреть свой результат /my_stat\n"
                f"и таблицу чемпионов этого часа /best",
                parse_mode="HTML",
                reply_markup=markupStat)
        else:
            q_id = get_new_question_id(but_id=-1)
            Users[user_id]['q_id_now'] = q_id
            bot.send_message(
                message.chat.id,
                f"<b>Вопрос №{Users[user_id]['q_num_now']} "
                f"из {Q_MAX + 1}</b>\n\n"
                f"{questions[q_id]}\n\n"
                f"{ANSWER_NOTE}",
                parse_mode="HTML",
                reply_markup=markupNumbers)


# Просмотр своего результата и таблицы чемпионов
@bot.message_handler(
    func=lambda message: message.text in [MY_STAT_MENU, BEST_MENU],
    content_types=["text"])
@bot.message_handler(
    commands=[MY_STAT_COMMAND, BEST_COMMAND])
def handle_my_stat(message: Message):
    """ Одновременно выводим результат и таблицу """
    generate_record_table()
    user_id = message.from_user.id
    if user_id in Users.keys():
        if Users[user_id]["test_finished"]:
            bot.send_message(
                message.chat.id,
                f"Мой друг <b>{message.chat.first_name}</b>!\n\n"
                f"Попытка №<b>{Users[user_id]['attempts'] - 1}</b>\n"
                f"Результат так себе: <b>0</b> из <b>{Q_MAX}</b>\n"
                f"Диагноз: <b>вы - гуманитарий!</b>"
                f"😂 🤣 😆\n\n",
                parse_mode="HTML")
        else:
            bot.send_message(
                message.chat.id,
                f"Вы ещё не завершили тест! /resume\n\n",
                parse_mode="HTML")
    else:
        bot.send_message(
            message.chat.id,
            f"Вы ещё не начинали тест! /new_test\n\n",
            parse_mode="HTML")
    bot.send_message(
        message.chat.id,
        f"<b>TOP-5 рекордов этого часа:</b>\n\n"
        f"{"\n".join(Settings['record_table'])}",
        parse_mode="HTML",
        reply_markup=markup)


# Обработка невыясненных команд
@bot.message_handler(content_types=["text"])
def handle_error(message: Message):
    """ Функция с ответом на абсолютно непонятные фразы пользователя """
    bot.reply_to(
        message,
        f"Не понимаю. Возможно, опечатка? Попробуйте /help",
        parse_mode="HTML",
        reply_markup=markup)


print(time.strftime("%H:%M:%S"))
print(TOKEN)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as ex:
        print(ex)
        time.sleep(10)

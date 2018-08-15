import telebot
from telebot import types
import const
import random
import keyboard_defs
import index
from index import get_db_connection, DBNAME, queries

bot = telebot.TeleBot(const.token2)

global rating

def end_path(call, e, battle):
    # максимальное количество вопросов достигнута
    if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
        bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                   battle[0].get_score(e.from_user.id)), call.from_user.id,
                              call.message.message_id)
        #bot.answer_callback_query(call.id, text="")

        # отправить следующий вопрос соперникy

        bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                   battle[0].get_score(call.from_user.id)), e.from_user.id,
                              e.message.message_id)
        #bot.answer_callback_query(e.id, text="")
    elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
        bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                   battle[0].get_score(e.from_user.id)), call.from_user.id,
                              call.message.message_id)
        #bot.answer_callback_query(call.id, text="")

        # отправить следующий вопрос соперникy

        bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                   battle[0].get_score(call.from_user.id)), e.from_user.id,
                              e.message.message_id)
        #bot.answer_callback_query(e.id, text="")
    else:
        bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                   battle[0].get_score(e.from_user.id)), call.from_user.id,
                              call.message.message_id)
        #bot.answer_callback_query(call.id, text="")

        # отправить следующий вопрос соперникy

        bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                   battle[0].get_score(call.from_user.id)), e.from_user.id,
                              e.message.message_id)
        #bot.answer_callback_query(e.id, text="")

    try:
        const.battle_array.pop(call.message.chat.id)
        const.battle_array.pop(e.message.chat.id)
    except:
        pass

    keyboard_defs.paymenu_keyboard(call.message)
    keyboard_defs.paymenu_keyboard(e.message)

def answer(call, num):
    # объект класса битвы [0]
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][2+num] == battle[0].nine_questions[battle[1]][7]:
        # добавляем очков
        battle[0].inc_score(call.message.chat.id)
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        # показать правильный ответ
        pass

    curr = const.battle_array.get(call.message.chat.id)[1]
    print(curr)
    e = battle[0].get_another(call.from_user.id)

    if (curr == 4):
        end_path(call, e, battle)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            battle[0].inc_quest_count()
            if const.battle_array.get(call.message.chat.id)[1] == 4:
                end_path(call, e, battle)
            # отправить следующий вопрос себе
            markup = index.create_question(battle[0].nine_questions, battle[1])
            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            #bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперника

            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], e.from_user.id, e.message.message_id,
                                  reply_markup=markup)
            #bot.answer_callback_query(e.id, text="")
        else:
            # вывести сообщение, что ждём соперника
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            #bot.answer_callback_query(call.id, text="")

def random_user(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['max_id'])
    max_id = cursor.fetchone()[0]


    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    while True:
        x = random.randrange(1, max_id + 1, 1)
        cursor.execute(queries['random_usname_chat_id'], (x, message.chat.id))
        z = cursor.fetchone()

        if z != None:
            return z
def ques_9():
    mass = []

    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    mass.append(random_ques())
    return mass



def random_ques():
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['max_ques_id'])
    max_ques_id = cursor.fetchone()[0]
    x = random.randrange(1, max_ques_id + 1, 1)
    cursor.execute(queries['random_question'], (x,))
    return cursor.fetchone()


def upd_rating(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['rating_update'], (rate, message.chat.id))
    connection.commit()

def upd_money(message, money, earn):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cash = money + earn
    cursor.execute(queries['money_update'], (cash, message.chat.id))
    connection.commit()

def get_reting(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['rating_get'], (message.chat.id,))
    print(get_money(message))
    return cursor.fetchone()[0]

def get_money(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['money_get'], (message.chat.id,))
    return cursor.fetchone()[0]

def ref_get(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['referal_get'], (message.chat.id,))
    return cursor.fetchone()[0]

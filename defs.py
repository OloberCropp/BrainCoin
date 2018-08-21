import telebot
from telebot import types
import const
import random
import index

import time
import threading
from index import get_db_connection, DBNAME, queries

bot = telebot.TeleBot(const.API_TOKEN)

global rating


def ques_9():
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['Rand_q'])
    return cursor.fetchall()

"""
def pquest(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['pquest_num_get'], (message.chat.id,))
    q_id = cursor.fetchone()[0]
    cursor.execute(queries['random_question'], (q_id,q_id+5))
    x = cursor.fetchall()
    cursor.execute(queries['pquest_num_upd'], (q_id,))
    connection.commit()
    return x

def fquest(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['fquest_num_get'],(message.chat.id,))
    q_id = cursor.fetchone()[0]
    cursor.execute(queries['random_question'], (q_id,q_id+5))
    x = cursor.fetchall()
    cursor.execute(queries['fquest_num_upd'], (q_id,))
    connection.commit()
    return x
"""

def create_question(cur_quests, num):
    print(num)
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton(cur_quests[num][2], callback_data="answer1"))
    row.append(types.InlineKeyboardButton(cur_quests[num][3], callback_data="answer2"))
    markup.row(*row)

    row = []
    row.append(types.InlineKeyboardButton(cur_quests[num][4], callback_data="answer3"))
    row.append(types.InlineKeyboardButton(cur_quests[num][5], callback_data="answer4"))
    markup.row(*row)
    return markup

def counter_time(call):
    try:
        battle = const.battle_array.get(call.from_user.id)
    except:
        return

    markup = create_question(battle[0].nine_questions, const.battle_array.get(call.message.chat.id)[1])
    second = const.seconds

    while second > 0 and const.users_time.get(call.from_user.id) == 1:
        try:
            bot.edit_message_text(const.time.format(second) + battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        except:
            pass

        second -= 1
        time.sleep(1)

    if const.users_time.get(call.from_user.id) == 1 and second == 0:    # если время вышло, то
        const.users_time.update({call.from_user.id: 2})
        try:
            bot.edit_message_text("Ввремя вышло, правильный ответ - '" + battle[0].nine_questions[battle[1]][6] + "'.",
                                  call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")
        except:
            pass
        time.sleep(2)
        const.users_time.update({call.from_user.id: 0})

        curr = const.battle_array.get(call.message.chat.id)[1]
        e = battle[0].get_another(call.from_user.id)
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            battle[0].inc_quest_count()

            if (curr == const.count_questions):

                const.users_time.update({call.from_user.id: 3})
                end_path(call, e, battle)

            else:
                # отправить следующий вопрос себе
                const.users_time.update({call.from_user.id: 1})
                my_thread1 = threading.Thread(
                    target=counter_time, args=(call,))
                my_thread1.start()

                # отправить следующий вопрос сопернику
                const.users_time.update({e.from_user.id: 1})
                my_thread2 = threading.Thread(target=counter_time, args=(e,))
                my_thread2.start()
        else:
            const.users_time.update({call.from_user.id: 0})
            try:
                bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass




def end_path(call, e, battle):
    # максимальное количество вопросов достигнута
    # удаляем ник противника и глём гифку
    #bot.delete_message(call.message.chat.id, call.message.message_id)
    #bot.delete_message(e.message.chat.id, e.message.message_id)
    if battle[0].cur_bet == 0:
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('before', Ra, Rb)

            upd_rating(call.message, count_new_rating(Ra, Rb, 1))
            upd_rating(e.message, count_new_rating(Rb, Ra, 0))

            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('after', Ra, Rb)

            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), get_rating(call.message)), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id), get_rating(call.message)),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass



            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), get_rating(e.message)), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), get_rating(e.message)),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('before', Ra, Rb)

            upd_rating(call.message, count_new_rating(Ra, Rb, 0))
            upd_rating(e.message, count_new_rating(Rb, Ra, 1))

            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('after', Ra, Rb)


            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), get_rating(call.message)), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id), get_rating(call.message)),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass
            # отправить следующий вопрос соперникy

            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), get_rating(e.message)), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), get_rating(e.message)),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
        else:
            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('before', Ra, Rb)

            upd_rating(call.message, count_new_rating(Ra, Rb, 0.5))
            upd_rating(e.message, count_new_rating(Rb, Ra, 0.5))

            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))

            print('after', Ra, Rb)

            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), get_rating(call.message)), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(
                        const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                             battle[0].get_score(e.from_user.id), get_rating(call.message)), call.from_user.id,
                        call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass

            # отправить следующий вопрос соперникy
            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), get_rating(e.message)), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), get_rating(e.message)),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
    else:
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            upd_money(call.message, get_money(call.message), battle[0].cur_bet)

            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))
            upd_rating(call.message, count_new_rating(Ra, Rb, 1))
            upd_rating(e.message, count_new_rating(Rb, Ra, 0))

            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(call.message))),
                                      call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id),
                                                               "Теперь ваш баланс - {} Braincoins".format(
                                                                   get_money(call.message))),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass
            # отправить следующий вопрос соперникy
            upd_money(e.message, get_money(e.message), -1 * battle[0].cur_bet)
            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(e.message))),
                                      e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id),
                                                               "Теперь ваш баланс - {} Braincoins".format(
                                                                   get_money(e.message))),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):

            upd_money(call.message, get_money(call.message), -1 * battle[0].cur_bet)

            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))
            upd_rating(call.message, count_new_rating(Ra, Rb, 0))
            upd_rating(e.message, count_new_rating(Rb, Ra, 1))

            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(call.message))),
                                      call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id),
                                                               "Теперь ваш баланс - {} Braincoins".format(
                                                                   get_money(call.message))),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass
            # отправить следующий вопрос соперникy

            upd_money(e.message, get_money(e.message), battle[0].cur_bet)

            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(e.message))),
                                      e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id),
                                                               "Теперь ваш баланс - {} Braincoins".format(
                                                                   get_money(e.message))),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass

        else:
            Ra = int(get_rating(call.message))
            Rb = int(get_rating(e.message))
            upd_rating(call.message, count_new_rating(Ra, Rb, 0.5))
            upd_rating(e.message, count_new_rating(Rb, Ra, 0.5))
            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(call.message))),
                                      call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(
                        const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                             battle[0].get_score(e.from_user.id),
                                             "Теперь ваш баланс - {} Braincoins".format(
                                                 get_money(call.message))),
                        call.from_user.id,
                        call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass
            # отправить следующий вопрос соперникy
            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id),
                                                           "Теперь ваш баланс - {} Braincoins".format(
                                                               get_money(e.message))),
                                      e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id),
                                                               "Теперь ваш баланс - {} Braincoins".format(
                                                                   get_money(e.message))),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass

    try:
        const.battle_array.pop(call.message.chat.id)
        const.battle_array.pop(e.message.chat.id)
    except:
        pass

    try:
        const.in_game.pop(call.message.chat.id)
        const.in_game.pop(e.message.chat.id)
    except:
        pass

    try:
        const.users_time.pop(call.from_user.id)
        const.users_time.pop(e.from_user.id)
    except:
        pass

def answer(call, num):
    # объект класса битвы [0]
    #const.users_time.update({call.from_user.id: 0}) уже установлено
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][1+num] == battle[0].nine_questions[battle[1]][6]:
        # добавляем очков

        battle[0].inc_score(call.message.chat.id)
        try:
            bot.edit_message_text("Вы выбрали правильный ответ.", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")
        except:
            try:
                bot.edit_message_text("Вы выбрали правильный ответ.", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                pass
        time.sleep(2)
        const.users_time.update({call.from_user.id: 0})
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        try:
            bot.edit_message_text("Вы ошиблись, правильный ответ - '" + battle[0].nine_questions[battle[1]][6] + "'.", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")
        except:
            try:
                bot.edit_message_text(
                    "Вы ошиблись, правильный ответ - '" + battle[0].nine_questions[battle[1]][6] + "'.",
                    call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                pass
        time.sleep(2)
        const.users_time.update({call.from_user.id: 0})
        # показать правильный ответ

    e = battle[0].get_another(call.from_user.id)
    battle[0].set_ready(call.message.chat.id)


    if battle[0].is_two_ready():
        battle[0].inc_quest_count()

        if const.battle_array.get(call.message.chat.id)[1] == const.count_questions:
            const.users_time.update({call.from_user.id: 3})
            end_path(call, e, battle)
        else:
            # отправить следующий вопрос себе
            const.users_time.update({call.from_user.id: 1})
            my_thread1 = threading.Thread(target=counter_time, args=(call,))
            my_thread1.start()

            # отправить следующий вопрос сопернику
            const.users_time.update({e.from_user.id: 1})
            my_thread2 = threading.Thread(target=counter_time, args=(e,))
            my_thread2.start()

    else:  # вывести сообщение, что ждём соперник
        try:
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")
        except:
            try:
                bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                pass


def count_new_rating(ra, rb, sa):
    ea = (1/(1 + (10 ** ((rb - ra)/400))))
    na = ra + 15 * (sa - ea)
    return int(na)

def random_ques():
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['max_ques_id'])
    max_ques_id = cursor.fetchone()[0]
    x = random.randrange(1, max_ques_id + 1, 1)
    cursor.execute(queries['random_question'], (x,))
    return cursor.fetchone()


def upd_rating(message, rate):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['rating_update'], (rate, message.chat.id))
    connection.commit()


def gl_rate():
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['gl_rate'])
    return cursor.fetchall()


def max_id():
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['max_id'])
    return cursor.fetchone()[0]


def upd_money(message, money, earn):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cash = money + earn
    cursor.execute(queries['money_update'], (cash, message.chat.id))
    connection.commit()


def get_rating(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['rating_get'], (message.chat.id,))
    return cursor.fetchone()[0]


def get_money(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['money_get'], (message.chat.id,))
    return cursor.fetchone()[0]


def ref_get(ref_chid):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['referal_get'], (ref_chid,))
    return cursor.fetchone()[0]
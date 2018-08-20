import telebot
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


def counter_time(call):
    battle = const.battle_array.get(call.message.chat.id)
    markup = index.create_question(battle[0].nine_questions, battle[1])
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

    if const.users_time.get(call.from_user.id) == 1 or const.users_time.get(call.from_user.id) == 3:
        if second == 0:
            const.users_time.update({call.from_user.id: 2})
            try:
                bot.edit_message_text("Ввремя вышло, праильный ответ - '" + battle[0].nine_questions[battle[1]][6] + "'.",
                                      call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                pass
            time.sleep(2)
            const.users_time.update({call.from_user.id: 0})

            curr = const.battle_array.get(call.message.chat.id)[1]
            e = battle[0].get_another(call.from_user.id)

            if (curr == const.count_questions):
                end_path(call, e, battle)
            else:
                battle[0].set_ready(call.message.chat.id)

                if battle[0].is_two_ready():
                    battle[0].inc_quest_count()
                    if const.battle_array.get(call.message.chat.id)[1] == const.count_questions:
                        end_path(call, e, battle)
                    # отправить следующий вопрос себе
                    const.users_time.update({call.from_user.id: 1})
                    my_thread1 = threading.Thread(
                        target=counter_time, args=(call,))
                    my_thread1.start()

                    # отправить следующий вопрос сопернику
                    const.users_time.update({e.from_user.id: 1})
                    my_thread2 = threading.Thread(target=counter_time, args=(e,))
                    my_thread2.start()
    elif const.users_time.get(call.from_user.id) == 0:
        try:
            battle[0].set_ready(call.message.chat.id)
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
            upd_money(call.message, get_money(call.message), battle[0].cur_bet)
            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), ""), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id), ""),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass

            # отправить следующий вопрос соперникy
            upd_money(e.message, get_money(e.message), -1 * battle[0].cur_bet)
            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), ""), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), ""),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):

            upd_money(call.message, get_money(call.message), -1 * battle[0].cur_bet)
            try:
                bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), ""), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                               battle[0].get_score(e.from_user.id), ""),
                                          call.from_user.id,
                                          call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass
            # отправить следующий вопрос соперникy

            upd_money(e.message, get_money(e.message), battle[0].cur_bet)
            try:
                bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), ""), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), ""),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass

        else:
            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                           battle[0].get_score(e.from_user.id), ""), call.from_user.id,
                                      call.message.message_id)
                bot.answer_callback_query(call.id, text="")
            except:
                try:
                    bot.edit_message_text(
                        const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                             battle[0].get_score(e.from_user.id), ""), call.from_user.id,
                        call.message.message_id)
                    bot.answer_callback_query(call.id, text="")
                except:
                    pass

            # отправить следующий вопрос соперникy
            try:
                bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                           battle[0].get_score(call.from_user.id), ""), e.from_user.id,
                                      e.message.message_id)
                bot.answer_callback_query(e.id, text="")
            except:
                try:
                    bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                               battle[0].get_score(call.from_user.id), ""),
                                          e.from_user.id,
                                          e.message.message_id)
                    bot.answer_callback_query(e.id, text="")
                except:
                    pass
    else:
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            upd_money(call.message, get_money(call.message), battle[0].cur_bet)
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
        print("crush1")

    try:
        const.in_game.pop(call.message.chat.id)
        const.in_game.pop(e.message.chat.id)
    except:
        print("crush2")

    try:
        const.users_time.pop(call.from_user.id)
        const.users_time.pop(e.from_user.id)
    except:
        print("crush3")

def answer(call, num):
    # объект класса битвы [0]
    #const.users_time.update({call.from_user.id: 0}) уже установлено
    battle = const.battle_array.get(call.message.chat.id)
    battle[0].set_ready(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][1+num] == battle[0].nine_questions[battle[1]][6]:
        # добавляем очков

        battle[0].inc_score(call.message.chat.id)
        bot.edit_message_text("Вы выбрали правильный ответ.", call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")
        const.users_time.update({call.from_user.id: 2})
        time.sleep(2)
        const.users_time.update({call.from_user.id: 0})
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        bot.edit_message_text("Вы ошиблись, правильный ответ - '" + battle[0].nine_questions[battle[1]][6] + "'.", call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")
        const.users_time.update({call.from_user.id: 2})
        time.sleep(2)
        const.users_time.update({call.from_user.id: 0})
        # показать правильный ответ

    curr = const.battle_array.get(call.message.chat.id)[1]
    e = battle[0].get_another(call.from_user.id)

    if (curr == const.count_questions):
        end_path(call, e, battle)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():

            battle[0].inc_quest_count()
            if const.battle_array.get(call.message.chat.id)[1] == const.count_questions:
                end_path(call, e, battle)
            # отправить следующий вопрос себе
            const.users_time.update({call.from_user.id: 1})
            my_thread1 = threading.Thread(target=counter_time, args=(call,))
            my_thread1.start()

            # отправить следующий вопрос соперника
            const.users_time.update({e.from_user.id: 1})
            my_thread2 = threading.Thread(target=counter_time, args=(e,))
            my_thread2.start()

        else:
            # вывести сообщение, что ждём соперника
            const.users_time.update({call.from_user.id: 3})
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")



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

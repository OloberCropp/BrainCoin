import telebot
import keyboard_defs
import const
import defs
import texts
import sqlite3
import threading
from telebot import types
from classes import Battle
#import flask
import requests
#from flask import request
import time

# Запросы
queries = {
    'table_users_create': "CREATE TABLE IF NOT EXISTS users (id INTEGER, chat_id INTEGER, username INTEGER, money INTEGER, referal INTEGER, rating INTEGER, payedquest INTEGER, freequest INTEGER)",
    'table_question_create': "CREATE TABLE IF NOT EXISTS questions (id INTEGER, category VARCHAR(32), question VARCHAR(128), ans1 VARCHAR, ans2 VARCHAR, ans3 VARCHAR, ans4 VARCHAR, right_ansver VARCHAR)",
    'rating_update': "UPDATE users SET rating = ? WHERE chat_id = ?",
    'money_update': "UPDATE users SET money = ? WHERE chat_id = ?",
    'referal_insert': "UPDATE users SET referal = ? WHERE chat_id = ?",
    'rating_get': "SELECT rating FROM users WHERE chat_id =?",
    'money_get': "SELECT money FROM users WHERE chat_id =?",
    'referal_get': "SELECT referal FROM users WHERE chat_id =?",
    'user_insert': "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
    'user_get': "SELECT * FROM users WHERE chat_id = ?",
    'my_chat_id': "SELECT id FROM users WHERE chat_id = ?",
    'max_id': "SELECT max(id) FROM users",
    'max_ques_id': "SELECT max(id) FROM questions",
    'random_question': "SELECT * FROM questions WHERE id >= ? AND id < ?",
    'Rand_q': "SELECT * FROM questions WHERE id IN (SELECT id FROM questions ORDER BY RANDOM() LIMIT 5)",
    'inc_ref': "UPDATE users SET referal=referal+1 WHERE chat_id=?",
    'gl_rate': "SELECT username, rating FROM users ORDER BY rating DESC",
    'pquest_num_get': "SELECT payedquest FROM users WHERE chat_id=?",
    'fquest_num_get': "SELECT freequest FROM users WHERE chat_id=?",
    'pquest_num_upd': "UPDATE users SET payedquest+=5 WHERE chat_id=?",
    'fquest_num_upd': "UPDATE users SET freequest+=5 WHERE chat_id=?",
}


DBNAME = 'main.db'


def get_db_connection(dbname):
    """
    :param dbname: <str> name of database (like test.db)
    :return: <sqlite3.connection>
    """
    return sqlite3.connect(dbname)

bot = telebot.TeleBot(const.API_TOKEN)
#app = flask.Flask(__name__)

"""
def exit_loop():
    word = ''
    while word != 'stop':
        word = input()
    exit(0)
"""

connection = get_db_connection('main.db')
connection.execute(queries['table_users_create'])
connection.execute(queries['table_question_create'])
connection.commit()
connection.close()

welcome_text = """Ваш противник: {}"""
your_bet_is = """Ваша ставка: {} Braincoin-ов"""
bet = 0


def create_question(cur_quests, num):
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

@bot.callback_query_handler(func=lambda call: call.data == 'answer1')
def answer1(call):
    const.users_time.update({call.from_user.id: 0})
    defs.answer(call, 1)

@bot.callback_query_handler(func=lambda call: call.data == 'answer2')
def answer2(call):
    const.users_time.update({call.from_user.id: 0})
    defs.answer(call, 2)

@bot.callback_query_handler(func=lambda call: call.data == 'answer3')
def answer3(call):
    const.users_time.update({call.from_user.id: 0})
    defs.answer(call, 3)

@bot.callback_query_handler(func=lambda call: call.data == 'answer4')
def answer4(call):
    const.users_time.update({call.from_user.id: 0})
    defs.answer(call, 4)



@bot.callback_query_handler(func=lambda call: call.data == 'accept')
def accept_bet(call):
    #начaло самой игры
    print("user started the game")
    try:
        bet = const.in_game[call.message.chat.id]
    except:
        bet = 25

    if bet == 25:
        if defs.get_money(call.message) >= 25:
            const.users_time.update({call.from_user.id: 0})
            if len(const.map_25) == 0:
                const.map_25.append([call.message.chat.id, call.message.chat.first_name, call])

                #изменение текста на "Поиск соперника"
                bot.edit_message_text("Поиск соперника", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
                return
            elif const.map_25[0][0] != call.message.chat.id:

                x = Battle(call.message, const.map_25[0], 25)
                const.battle_array.update({call.message.chat.id: [x, 0]})
                const.battle_array.update({const.map_25[0][0]: [x, 0]})

                battle = const.battle_array.get(call.message.chat.id)
                battle[0].set_id(call)
                battle[0].set_id(const.map_25[0][2])

                try:
                    const.map_25.remove(const.map_25[0])
                except:
                    pass

                # отправка сообщения сопернику

                e = battle[0].get_another(call.from_user.id)

                const.users_time.update({call.from_user.id: 1})
                my_thread1 = threading.Thread(target=defs.counter_time, args=(call,))
                my_thread1.start()
                # print("ya tut")
                # bot.edit_message_text(battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
                #                      reply_markup=markup)
                # bot.answer_callback_query(call.id, text="")

                # отправить следующий вопрос соперника
                const.users_time.update({e.from_user.id: 1})
                my_thread2 = threading.Thread(target=defs.counter_time, args=(e,))
                my_thread2.start()
        else:
            bot.edit_message_text("Маловато у тебя Braincoin, для такой ставки, выбери меньше.", call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")
            time.sleep(3)
            markup = create_choice()
            bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

    elif bet == 50:
        if defs.get_money(call.message) >= 50:
            const.users_time.update({call.from_user.id: 0})
            if len(const.map_50) == 0:
                const.map_50.append([call.message.chat.id, call.message.chat.first_name, call])

                # изменение текста на "Поиск соперника"
                bot.edit_message_text("Поиск соперника", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
                return
            elif const.map_50[0][0] != call.message.chat.id:

                x = Battle(call.message, const.map_50[0], 50)
                const.battle_array.update({call.message.chat.id: [x, 0]})
                const.battle_array.update({const.map_50[0][0]: [x, 0]})

                battle = const.battle_array.get(call.message.chat.id)
                battle[0].set_id(call)
                battle[0].set_id(const.map_50[0][2])

                try:
                    const.map_50.remove(const.map_50[0])
                except:
                    pass

                # отправка сообщения сопернику

                e = battle[0].get_another(call.from_user.id)

                const.users_time.update({call.from_user.id: 1})
                my_thread1 = threading.Thread(target=defs.counter_time, args=(call,))
                my_thread1.start()
                # print("ya tut")
                # bot.edit_message_text(battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
                #                      reply_markup=markup)
                # bot.answer_callback_query(call.id, text="")

                # отправить следующий вопрос соперника
                const.users_time.update({e.from_user.id: 1})
                my_thread2 = threading.Thread(target=defs.counter_time, args=(e,))
                my_thread2.start()
        else:
            bot.edit_message_text("Маловато у тебя Braincoin, для такой ставки, выбери меньше.", call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")
            time.sleep(3)
            markup = create_choice()
            bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

    elif bet == 100:
        if defs.get_money(call.message) >= 100:
            const.users_time.update({call.from_user.id: 0})
            if len(const.map_100) == 0:
                const.map_100.append([call.message.chat.id, call.message.chat.first_name, call])

                # изменение текста на "Поиск соперника"
                bot.edit_message_text("Поиск соперника", call.from_user.id, call.message.message_id)
                bot.answer_callback_query(call.id, text="")
                return
            elif const.map_100[0][0] != call.message.chat.id:

                x = Battle(call.message, const.map_100[0], 100)
                const.battle_array.update({call.message.chat.id: [x, 0]})
                const.battle_array.update({const.map_100[0][0]: [x, 0]})

                battle = const.battle_array.get(call.message.chat.id)
                battle[0].set_id(call)
                battle[0].set_id(const.map_100[0][2])

                try:
                    const.map_100.remove(const.map_100[0])
                except:
                    pass

                # отправка сообщения сопернику

                e = battle[0].get_another(call.from_user.id)

                const.users_time.update({call.from_user.id: 1})
                my_thread1 = threading.Thread(target=defs.counter_time, args=(call,))
                my_thread1.start()
                # print("ya tut")
                # bot.edit_message_text(battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
                #                      reply_markup=markup)
                # bot.answer_callback_query(call.id, text="")

                # отправить следующий вопрос соперника
                const.users_time.update({e.from_user.id: 1})
                my_thread2 = threading.Thread(target=defs.counter_time, args=(e,))
                my_thread2.start()
        else:
            bot.edit_message_text("Маловато у тебя Braincoin, для такой ставки, выбери меньше.", call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")
            time.sleep(3)
            markup = create_choice()
            bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

    elif bet == 200:
        if defs.get_money(call.message) >= 200:
            const.users_time.update({call.from_user.id: 0})
            if len(const.map_200) == 0:
                const.map_200.append([call.message.chat.id, call.message.chat.first_name, call])



                # изменение текста на "Поиск соперника"
                bot.edit_message_text("Поиск соперника", call.from_user.id, call.message.message_id, reply_markup=markup)
                bot.answer_callback_query(call.id, text="")
                return
            elif const.map_200[0][0] != call.message.chat.id:

                x = Battle(call.message, const.map_200[0], 200)
                const.battle_array.update({call.message.chat.id: [x, 0]})
                const.battle_array.update({const.map_200[0][0]: [x, 0]})

                battle = const.battle_array.get(call.message.chat.id)
                battle[0].set_id(call)
                battle[0].set_id(const.map_200[0][2])

                try:
                    const.map_200.remove(const.map_200[0])
                except:
                    pass

                # отправка сообщения сопернику

                e = battle[0].get_another(call.from_user.id)

                const.users_time.update({call.from_user.id: 1})
                my_thread1 = threading.Thread(target=defs.counter_time, args=(bet, call))
                my_thread1.start()
                # print("ya tut")
                # bot.edit_message_text(battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
                #                      reply_markup=markup)
                # bot.answer_callback_query(call.id, text="")

                # отправить следующий вопрос соперника
                const.users_time.update({e.from_user.id: 1})
                my_thread2 = threading.Thread(target=defs.counter_time, args=(bet, e))
                my_thread2.start()
        else:
            bot.edit_message_text("Маловато у тебя Braincoin, для такой ставки, выбери меньше.", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")
            time.sleep(3)
            markup = create_choice()
            bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == "cancel_free_search")
def cancel_search(call):
    const.map_free.remove(const.map_free[0])
    markup = create_choice()
    bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_25_search")
def cancel_25_search(call):
    const.map_25.remove(const.map_25[0])
    markup = create_choice()
    bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_50_search")
def cancel_50_search(call):
    const.map_50.remove(const.map_50[0])
    markup = create_choice()
    bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_100_search")
def cancel_100_search(call):
    const.map_100.remove(const.map_100[0])
    markup = create_choice()
    bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_200_search")
def cancel_200_search(call):
    const.map_200.remove(const.map_200[0])
    markup = create_choice()
    bot.edit_message_text("Выбери свою ставку чтобы начать ⚔️", call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == 'accept_free')
def accept_bet(call):
    #начaло самой игры
    print("user started the free game")

    if len(const.map_free) == 0:
        const.map_free.append([call.message.chat.id, call.message.chat.first_name, call])

        markup = types.InlineKeyboardMarkup()
        row = []
        row.append(types.InlineKeyboardButton("Отмена поиска", callback_data="cancel_free_search"))
        markup.row(*row)

        #изменение текста на "Поиск соперника"
        bot.edit_message_text("Поиск соперника", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
        return
    elif const.map_free[0][0] != call.message.chat.id:

        x = Battle(call.message, const.map_free[0], 0)
        const.battle_array.update({call.message.chat.id: [x, 0]})
        const.battle_array.update({const.map_free[0][0]: [x, 0]})

        battle = const.battle_array.get(call.message.chat.id)
        battle[0].set_id(call)
        battle[0].set_id(const.map_free[0][2])

        try:
            const.map_free.remove(const.map_free[0])
        except:
            pass

        # отправка сообщения сопернику

        e = battle[0].get_another(call.from_user.id)

        const.users_time.update({call.from_user.id: 1})
        my_thread1 = threading.Thread(target=defs.counter_time, args=(call,))
        my_thread1.start()
        # print("ya tut")
        # bot.edit_message_text(battle[0].nine_questions[battle[1]][1], call.from_user.id, call.message.message_id,
        #                      reply_markup=markup)
        # bot.answer_callback_query(call.id, text="")

        # отправить следующий вопрос соперника
        const.users_time.update({e.from_user.id: 1})
        my_thread2 = threading.Thread(target=defs.counter_time, args=(e,))
        my_thread2.start()

def create_choice():

    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton("0 (На интерес)", callback_data="accept_free"))
    markup.row(*row)
    row = []
    row.append(types.InlineKeyboardButton("25", callback_data="bet_25"))
    row.append(types.InlineKeyboardButton("50", callback_data="bet_50"))
    row.append(types.InlineKeyboardButton("100", callback_data="bet_100"))
    row.append(types.InlineKeyboardButton("200", callback_data="bet_200"))
    markup.row(*row)
    row = []
    row.append(types.InlineKeyboardButton("Подтвердить и начать", callback_data="accept"))
    markup.row(*row)

    return markup


@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_25')
def change_bet_25(curr_bet):
    const.in_game.update({curr_bet.message.chat.id: 25})
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(25), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_50')
def change_bet_50(curr_bet):
    const.in_game.update({curr_bet.message.chat.id: 50})
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(50), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_100')
def change_bet_100(curr_bet):
    const.in_game.update({curr_bet.message.chat.id: 100})
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(100), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_200')
def change_bet_200(curr_bet):
    const.in_game.update({curr_bet.message.chat.id: 200})
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(200), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.message_handler(commands=['start'])
def start(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['user_get'], (message.chat.id,))
    if cursor.fetchone() is None:
        x = message.text[7:]
        if x != '':
            y = int(defs.ref_get(x))+1
            cursor.execute(queries['inc_ref'], (y, x))
            bot.send_message(x, "Привет, твой друг: "+message.chat.first_name+""" перешёл по твоей ссылке! 
теперь у тебя: """+str(y)+""" приглашений, ещё:
"""+str(5-y)+""" до очистки рекламы, и
"""+str(13-y)+""" до снятия комиссии""")
            connection.commit()
        # Создание нумерации пользователей
        connection = get_db_connection(DBNAME)
        cursor = connection.cursor()
        cursor.execute('SELECT max(id) FROM users')
        max_id = cursor.fetchone()[0]
        try:
            if max_id is None:
                max_id = 0
        except:
            pass


        # Запись пользователя в базу
        money = 0
        rating = 2000
        referal = 0
        payedquest = 1
        freequest = 1

        cursor.execute(queries['user_insert'], (max_id+1, message.chat.id, message.chat.first_name, money, referal, rating, payedquest, freequest))
        connection.commit()

        print(message.chat.id, 'started the bot.')
        bot.send_message(message.chat.id, 'Привет, ' + message.chat.first_name + texts.Start_text )

    else:
        bot.send_message(message.chat.id, 'С возвращением, '+message.chat.first_name+"\n\n"+'Загружаю твой прогресс...')
        cursor.close()
        connection.close()
        print(message.chat.id, 'started the bot')
    keyboard_defs.start_keyboard(message)

def send_pay(message, call):
    if call == 0:
        r = requests.post(const.BOT_GET_WALLET,
                          data={'k': const.TRADE_TOKEN, 'tgid': message.chat.id})

        js = r.json()
        if js["ok"] == 1:
            markup = types.InlineKeyboardMarkup()
            row = []
            row.append(types.InlineKeyboardButton("Я оплатил", callback_data="cp_%s" % js['wi']))
            row.append(types.InlineKeyboardButton("Отмена", callback_data="cancel"))
            markup.row(*row)

            bot.send_message(message.chat.id, 'Ваш реквизит готов:' + "\n\n" + js["r"]
                             + "\n\n" + "Пополните карту на нужное количество средств и нажмите кнопку \"Я оплатил\""
                             + "\n\nЕсли передумали, освободите реквизит, нажав на кнопку \"Отмена\""
                             + "\n\nРеквизит выдаётся на 30 минут. По всем вопросам к админу ебаному.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Свободного реквизита нет, повторите попытку через 15 минут.")
    else:
        r = requests.post(const.BOT_GET_WALLET,
                          data={'k': const.TRADE_TOKEN, 'tgid': message.chat.id})

        js = r.json()
        if js["ok"] == 1:
            markup = types.InlineKeyboardMarkup()
            row = []
            row.append(types.InlineKeyboardButton("Я оплатил", callback_data="cp_%s" % js['wi']))
            row.append(types.InlineKeyboardButton("Отмена", callback_data="cancel"))
            markup.row(*row)

            bot.edit_message_text('💳 перевод по номеру карты VISA' + "\n\n" + js["r"]
                             + "\n\n" + "Пополните карту на нужное количество средств и нажмите кнопку \"Я оплатил\""
                             + "\n\nЕсли передумали, освободите реквизит, нажав на кнопку \"Отмена\""
                             + "\n\nРеквизит выдаётся на 30 минут. По всем вопросам к админу ебаному.",
                                  call.from_user.id, call.message.message_id, reply_markup=markup)
            bot.answer_callback_query(call.id, text="")
        else:
            bot.send_message(message.chat.id, "Свободного реквизита нет, повторите попытку через 15 минут.")

@bot.callback_query_handler(func=lambda call: call.data == 'cancel')
def cancel_button(call):
    keyboard_defs.wallet_keyboard(call.message)
    bot.send_message(call.message.chat.id, 'На твоём счету   ' + str(defs.get_money(call.message)) + ' BrainCoin-ов')

@bot.callback_query_handler(func=lambda call: call.data[:3] == 'cp_')
def check_pay(call):
    r = requests.post(const.BOT_CHECK_PAY,
                      data={'k': const.TRADE_TOKEN, 'wi': call.data[3:]})
    js = r.json()

    if js['a'] == 0:
        bot.edit_message_text("Средства ещё не поступили на счёт.", call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")
        time.sleep(3)
        send_pay(call.message, call)
    else:
        earn = int(js['a'])
        money = defs.get_money(call.message)
        defs.upd_money(call.message, money, earn)
        bot.send_message(call.message.chat.id, 'Ты пополнил кошелёк на %s' % js['a'] + "\n\n"
                         + 'Теперь на твоём счету: ' + str(defs.get_money(call.message)) + ' BrainCoin-ов!')


def pay_out(message):
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton("Я ввёл реквизит", callback_data="out_1"))
    markup.row(*row)

    bot.send_message(message.chat.id, 'Введите ваш номер кошелька киви в формате 79991112233 и нажмите на кнопку \"Я ввёл реквизит\"\n\n'
                     + 'Порядок действий:\nОтправить боту сообщение с вашим номером QIWI кошелька -> Нажать на кнопку', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'out_1')
def out(call):
    if len(const.last_sended_message.get(call.from_user.id)) == 11:

        const.pay_req.update({call.from_user.id : const.last_sended_message.get(call.from_user.id)})

        markup = types.InlineKeyboardMarkup()
        row = []
        row.append(types.InlineKeyboardButton("Я ввёл сумму вывода", callback_data="out_2"))
        markup.row(*row)

        bot.edit_message_text('Введите сумму вывода не превышающую ваш баланс и нажмите на кнопку'
                              + '"Я ввёл сумму вывода\"\n\nУ вас на счету: '
                              + str(defs.get_money(call.message)) + ' BrainCoin-ов.',
                              call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        bot.edit_message_text("Вы ввели не корректный номер️", call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == "out_2")
def out2(call):
    if int(const.last_sended_message.get(call.from_user.id)) <= defs.get_money(call.message):
        r = requests.post(const.BOT_PAY_OUT,
                          data={'k': const.TRADE_TOKEN, 'd': const.pay_req.get(call.from_user.id),
                                'a': int(const.last_sended_message.get(call.from_user.id))})
        js = r.json()

        earn = -1 * int(const.last_sended_message.get(call.from_user.id))
        defs.upd_money(call.message, defs.get_money(call.message), earn)
        bot.edit_message_text('Ты вывел %s' % const.last_sended_message.get(call.from_user.id)
                         + " BrainCoin-ов.\n\n" + 'Теперь на твоём счету: ' + str(defs.get_money(call.message))
                         + ' BrainCoin-ов.', call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")
    else:
        bot.edit_message_text('Маловато у тебя BrainCoin-ов для такого вывода!', call.from_user.id, call.message.message_id)
        bot.answer_callback_query(call.id, text="")

@bot.message_handler(content_types='text')
def start_handler(message):
    if message.text == 'Рейтинг':
        f = defs.gl_rate()
        global i
        i = 0
        while message.chat.first_name != f[i][0]:
            i += 1
        stri = '1 место: '+f[0][0] + ' с рейтингом: ' + str(f[0][1]) + "\n" + '2 место: '\
               + f[1][0] + ' с рейтингом: ' + str(f[1][1]) + "\n" +   '3 место: ' + f[2][0]\
               + ' с рейтингом: ' + str(f[2][1]) + "\n" + '4 место: ' + f[3][0] + ' с рейтингом: ' \
               + str(f[3][1]) + "\n"+ '5 место: '+f[4][0]+ ' с рейтингом: '+str(f[4][1])
        bot.send_message(message.chat.id, stri)
        bot.send_message(message.chat.id, 'Твой рейтинг: ' + str(defs.get_rating(message))
+ '\n' + 'Позиция в рейтинге: ' + str(i+1))
    elif message.text == 'About':
        keyboard_defs.about_keyboard(message)
    elif message.text == 'Назад':
        keyboard_defs.start_keyboard(message)
    elif message.text == '🏆💯💍   Играть   💍💯🏆':
        if const.in_game.get(message.chat.id) is None:
            markup = create_choice()
            bot.send_message(message.chat.id, "Выбери свою ставку чтобы начать ⚔️", reply_markup=markup)
        else:
            pass
    elif message.text == '💳 Cчёт 💳':
        keyboard_defs.wallet_keyboard(message)
        bot.send_message(message.chat.id, 'На твоём счету   ' + str(defs.get_money(message)) + ' BrainCoin-ов')
    elif message.text == 'Ввести':
        send_pay(message, 0)
    elif message.text == 'Вывести':
        pay_out(message)
    elif message.text == 'Хочешь больше?':
        keyboard_defs.freecoins_menu(message)
    elif message.text == 'Написать о проблеме':
        bot.send_message(message.chat.id, """Напиши нашему менеджеру о своей проблеме.
Это может быть как баг, так и ошибка перевода средств.""")
    elif message.text == 'Пригласить друга':
        bot.send_message(message.chat.id, """Твоя персональная ссылка:
https://telegram.me/Crypto_Shit_Fucking_bot?start="""+str(message.chat.id))
    else:
        const.last_sended_message.update({message.chat.id: message.text})
        bot.send_message(680328648, 'Сообщение от: ' + message.chat.first_name + """
         Следующего содержания: """ + message.text)

"""@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''

@app.route(const.WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


if __name__ == '__main__':
    print('launching bot')

    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=const.WEBHOOK_URL_BASE + const.WEBHOOK_URL_PATH,
                    certificate=open(const.WEBHOOK_SSL_CERT, 'rb'))
    app.run(host=const.WEBHOOK_LISTEN,
            port=const.WEBHOOK_PORT,
            ssl_context=(const.WEBHOOK_SSL_CERT, const.WEBHOOK_SSL_PRIV),
            debug=True)"""





if __name__ == '__main__':
    bot.polling(none_stop=True)
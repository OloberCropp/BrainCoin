import telebot
import keyboard_defs
import const
import defs
import texts
import sqlite3
import random
from telebot import types
from classes import Battle

# Запросы
queries = {
    'table_users_create': "CREATE TABLE IF NOT EXISTS users (id INTEGER, chat_id INTEGER, username INTEGER, money INTEGER, referal VARCHAR(16), rating INTEGER)",
    'table_question_create': "CREATE TABLE IF NOT EXISTS questions (id INTEGER, category VARCHAR(32), question VARCHAR(128), ans1 VARCHAR, ans2 VARCHAR, ans3 VARCHAR, ans4 VARCHAR, right_ansver VARCHAR)",
    'rating_update': "UPDATE users SET rating = ? WHERE chat_id = ?",
    'money_update': "UPDATE users SET money = ? WHERE chat_id = ?",
    'referal_insert': "INSERT INTO users WHERE chat_id = ? VALUE rating = ?",
    'rating_get': "SELECT rating FROM users WHERE chat_id =?",
    'money_get': "SELECT money FROM users WHERE chat_id =?",
    'referal_get': "SELECT referal FROM users WHERE chat_id =?",
    'user_insert': "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
    'user_delete': "DELETE FROM users WHERE chat_id = ?",
    'user_get': "SELECT * FROM users WHERE chat_id = ?",
    'users_get': "SELECT * FROM users",
    'chat_id_get': "SELECT chat_id FROM users",
    'random_usname_chat_id': "SELECT chat_id, username FROM users WHERE id = ? AND NOT chat_id = ?",
    'my_chat_id': "SELECT id FROM users WHERE chat_id = ?",
    'max_id': "SELECT max(id) FROM users",
    'max_ques_id': "SELECT max(id) FROM questions",
    'random_question': "SELECT * FROM questions WHERE id = ?"
}

DBNAME = 'main.db'


def get_db_connection(dbname):
    """
    :param dbname: <str> name of database (like test.db)
    :return: <sqlite3.connection>
    """
    return sqlite3.connect(dbname)

bot = telebot.TeleBot(const.token)

connection = get_db_connection('main.db')
connection.execute(queries['table_users_create'])
connection.execute(queries['table_question_create'])
connection.commit()
connection.close()


welcome_text = """Ваш противник: {}"""
your_bet_is = """Ваша ставка: {}"""
bet = 0


def create_question(cur_quests, num):
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton(cur_quests[num][3], callback_data="answer1"))
    row.append(types.InlineKeyboardButton(cur_quests[num][4], callback_data="answer2"))
    markup.row(*row)

    row = []
    row.append(types.InlineKeyboardButton(cur_quests[num][5], callback_data="answer3"))
    row.append(types.InlineKeyboardButton(cur_quests[num][6], callback_data="answer4"))
    markup.row(*row)
    return markup

@bot.callback_query_handler(func=lambda call: call.data == 'answer1')
def answer1(call):
    # объект класса битвы [0]
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][3] == battle[0].nine_questions[battle[1]][7]:
        # добавляем очков
        battle[0].inc_score(call.message.chat.id)
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        # показать правильный ответ
        pass

    curr = const.battle_array.get(battle[0].first_player)[1]
    battle[0].inc_quest_count()
    e = battle[0].get_another(call.from_user.id)

    if (curr >= 5):
        # максимальное количество вопросов достигнута
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        else:
            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")

        keyboard_defs.paymenu_keyboard(call.message)
        keyboard_defs.paymenu_keyboard(e.message)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            # отправить следующий вопрос себе
            markup = create_question(battle[0].nine_questions, battle[1])
            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперника

            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], e.from_user.id, e.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(e.id, text="")
        else:
            # вывести сообщение, что ждём соперника
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")


@bot.callback_query_handler(func=lambda call: call.data == 'answer2')
def answer2(call):
    # объект класса битвы [0]
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][4] == battle[0].nine_questions[battle[1]][7]:
        # добавляем очков
        battle[0].inc_score(call.message.chat.id)
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        # показать правильный ответ
        pass

    curr = const.battle_array.get(battle[0].first_player)[1]
    battle[0].inc_quest_count()
    e = battle[0].get_another(call.from_user.id)

    if (curr >= 5):
        # максимальное количество вопросов достигнута
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        else:
            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")

        keyboard_defs.paymenu_keyboard(call.message)
        keyboard_defs.paymenu_keyboard(e.message)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            # отправить следующий вопрос себе
            markup = create_question(battle[0].nine_questions, battle[1])
            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперника

            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], e.from_user.id, e.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(e.id, text="")
        else:
            # вывести сообщение, что ждём соперника
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == 'answer3')
def answer3(call):
    # объект класса битвы [0]
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][5] == battle[0].nine_questions[battle[1]][7]:
        # добавляем очков
        battle[0].inc_score(call.message.chat.id)
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        # показать правильный ответ
        pass

    curr = const.battle_array.get(battle[0].first_player)[1]
    battle[0].inc_quest_count()
    e = battle[0].get_another(call.from_user.id)

    if (curr >= 5):
        # максимальное количество вопросов достигнута
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        else:
            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")

        keyboard_defs.paymenu_keyboard(call.message)
        keyboard_defs.paymenu_keyboard(e.message)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            # отправить следующий вопрос себе
            markup = create_question(battle[0].nine_questions, battle[1])
            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперника

            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], e.from_user.id, e.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(e.id, text="")
        else:
            # вывести сообщение, что ждём соперника
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == 'answer4')
def answer4(call):
    # объект класса битвы [0]
    battle = const.battle_array.get(call.message.chat.id)

    if battle[0].nine_questions[battle[1]][6] == battle[0].nine_questions[battle[1]][7]:
        # добавляем очков
        battle[0].inc_score(call.message.chat.id)
        # поставить таймер и отсчитывать 3 секунды, показывая сообщение "Правильно"
    else:
        # показать правильный ответ
        pass

    curr = const.battle_array.get(battle[0].first_player)[1]
    battle[0].inc_quest_count()
    e = battle[0].get_another(call.from_user.id)

    if(curr >= 5):
        # максимальное количество вопросов достигнута
        if battle[0].get_score(call.from_user.id) > battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(call.from_user.id), battle[0].get_score(e.from_user.id)), call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(e.from_user.id), battle[0].get_score(call.from_user.id)), e.from_user.id, e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        elif battle[0].get_score(call.from_user.id) < battle[0].get_score(e.from_user.id):
            bot.edit_message_text(const.end_str.format(const.lose, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.win, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")
        else:
            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(call.from_user.id),
                                                       battle[0].get_score(e.from_user.id)), call.from_user.id,
                                  call.message.message_id)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперникy

            bot.edit_message_text(const.end_str.format(const.ne_vam_ne_nam, battle[0].get_score(e.from_user.id),
                                                       battle[0].get_score(call.from_user.id)), e.from_user.id,
                                  e.message.message_id)
            bot.answer_callback_query(e.id, text="")

        keyboard_defs.paymenu_keyboard(call.message)
        keyboard_defs.paymenu_keyboard(e.message)
    else:
        battle[0].set_ready(call.message.chat.id)

        if battle[0].is_two_ready():
            # отправить следующий вопрос себе
            markup = create_question(battle[0].nine_questions, battle[1])
            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], call.from_user.id, call.message.message_id,
                                  reply_markup=markup)
            bot.answer_callback_query(call.id, text="")

            # отправить следующий вопрос соперника


            bot.edit_message_text(battle[0].nine_questions[battle[1]][2], e.from_user.id, e.message.message_id, reply_markup=markup)
            bot.answer_callback_query(e.id, text="")
        else:
            # вывести сообщение, что ждём соперника
            bot.edit_message_text("Ждём соперника", call.from_user.id, call.message.message_id)
            bot.answer_callback_query(call.id, text="")

@bot.callback_query_handler(func=lambda call: call.data == 'accept')
def accept_bet(call):
    #начaло самой игры
    print("user started the game")

    if len(const.map) == 0:
        const.map.append([call.message.chat.id, call.message.chat.username, call])

        #изменение текста на "Поиск соперника"
        return
    else:
        x = Battle(call.message, const.map[0])
        const.battle_array.update({call.message.chat.id: [x, 0]})

    markup = create_question(const.battle_array.get(call.message.chat.id)[0].nine_questions,
                             const.battle_array.get(call.message.chat.id)[1])
    bat = const.battle_array.get(call.message.chat.id)

    bat[0].set_id(call)

    bot.edit_message_text(bat[0].nine_questions[bat[1]][2], call.from_user.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id, text="")

    #отправка сообщения сопернику

    e = bat[0].get_another(call.from_user.id)

    bot.edit_message_text(bat[0].nine_questions[bat[1]][2], e.from_user.id, e.message.message_id,
                          reply_markup=markup)
    bot.answer_callback_query(e.id, text="")


##################################    bet


def create_choice():
    markup = types.InlineKeyboardMarkup()
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
    bet = 25
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_50')
def change_bet_50(curr_bet):
    bet = 50
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_100')
def change_bet_100(curr_bet):
    bet = 100
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_200')
def change_bet_200(curr_bet):
    bet = 200
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")


##################################


@bot.message_handler(commands=['start'])
def start(message):
    connection = get_db_connection(DBNAME)
    cursor = connection.cursor()
    cursor.execute(queries['user_get'], (message.chat.id,))
    if cursor.fetchone() is None:
        # Создание нумерации пользователей
        cursor.execute('SELECT max(id) FROM users')
        max_id = cursor.fetchone()[0]
        print(max_id)
        try:
            if max_id is None:
                max_id = 0
        except:
            pass


        # Запись пользователя в базу
        money = 0
        rating = 0
        referal = "0000000000"
        cursor.execute(queries['user_insert'], (max_id+1, message.chat.id, message.chat.username, money, referal, rating))
        connection.commit()

        print(message.chat.username, ' начал(-ла) игру')
        bot.send_message(message.chat.id, 'Привет, ' + message.chat.username + texts.Start_text )

    else:
        bot.send_message(message.chat.id, 'Загружаю твой прогресс...')
        cursor.close()
        connection.close()
        print(message.chat.username, 'Запустил(-ла ) бота')
    keyboard_defs.start_keyboard(message)

@bot.message_handler(content_types='text')
def start_handler(message):
    if message.text == 'Заработать':
        keyboard_defs.paymenu_keyboard(message)
    elif message.text == 'На интерес':
        keyboard_defs.freemenu_keyboard(message)
    elif message.text == 'Рейтинг':
        keyboard_defs.rating_keyboard(message)
    elif message.text == 'About':
        keyboard_defs.about_keyboard(message)
    elif message.text == 'Назад':
        keyboard_defs.start_keyboard(message)
    elif message.text == 'Играть':
        markup = create_choice()
        bot.send_message(message.chat.id, your_bet_is.format(str(bet)), reply_markup=markup)
    elif message.text == 'Кошелёк':
        keyboard_defs.wallet_keyboard(message)
        money = str(defs.get_money(message))
        bot.send_message(message.chat.id, 'На твоём счету   ' + money + '   BrainCoin-ов')
    elif message.text == 'Ввести':
        earn = 100
        money = defs.get_money(message)
        defs.upd_money(message, money, earn)
        bot.send_message(message.chat.id, 'Ты пополнил кошелёк на 100')
    elif message.text == 'Вывести':
        bot.send_message(message.chat.id, 'Упс... Кажется эта функция пока не доступна.')
    else:
        bot.send_message(message.chat.id, "Ты ввёл что-то не то =( =( =(")

    print(defs.random_user(message))
    print(defs.ques_9())




"""x = time.time()
if x == 120:
    c = 0
    x = 0
Принцип работы таймеров
"""

if __name__ == '__main__':
    bot.polling(none_stop=True)
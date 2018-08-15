import telebot
from telebot import types
import const
import random
from index import get_db_connection, DBNAME, queries

bot = telebot.TeleBot(const.token)

global rating


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
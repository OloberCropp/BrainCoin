import time
import telebot
import const
import defs
import keyboard_defs
from telebot import types

bot = telebot.TeleBot(const.token)

# const for battle

welcome_text = """Ваш противник {}"""
your_bet_is = """Ваша ставка - {}"""
bet = 0


def create_choice():
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton("50", callback_data="bet_50"))
    row.append(types.InlineKeyboardButton("100", callback_data="bet_100"))
    row.append(types.InlineKeyboardButton("200", callback_data="bet_200"))
    markup.row(*row)
    return markup

class battle:

    def __init__(self, message):
        self.first_player = message.chat.id
        self.name_fp = message.chat.username
        get_user = defs.random_user(message)
        self.second_player = get_user[0] #get id
        self.name_sp = get_user[1] #get username

        bot.send_message(self.first_player, welcome_text.format(self.second_player))
        bot.send_message(self.second_player, welcome_text.format(self.name_sp))

    def start_battle(self):
        # выводим выбор категорий
        # выводим кнопк
        pass

@bot.message_handler(commands=['start'])
def start(message):
    keyboard_defs.start_keyboard(message)

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_50')
def change_bet_50(curr_bet):
    bet = 50
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_100')
def change_bet_50(curr_bet):
    bet = 100
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_200')
def change_bet_50(curr_bet):
    bet = 200
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.message_handler(content_types='text')
def start_handler(message):
    if message.text == 'Заработать':
        markup = create_choice()
        bot.send_message(message.chat.id, your_bet_is.format(str(bet)), reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=True)
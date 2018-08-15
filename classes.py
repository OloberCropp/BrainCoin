import random
import telebot
import const
import defs
import keyboard_defs
from telebot import types

bot = telebot.TeleBot(const.token)

# const for battle

welcome_text = """Ваш противник {}"""
your_bet_is = """Ваша ставка - {}"""



def create_choice():
    markup = types.InlineKeyboardMarkup()
    row = []
    row.append(types.InlineKeyboardButton("50", callback_data="bet_50"))
    row.append(types.InlineKeyboardButton("100", callback_data="bet_100"))
    row.append(types.InlineKeyboardButton("200", callback_data="bet_200"))
    markup.row(*row)
    return markup

def create_table_vote(num):
    markup = types.InlineKeyboardMarkup()

    if num == 0:
        row = []
        row.append(types.InlineKeyboardButton("1 theme", callback_data="set_1_t" + "1 theme"))
        row.append(types.InlineKeyboardButton("2 theme", callback_data="set_1_t" + "2 theme"))
        row.append(types.InlineKeyboardButton("3 theme", callback_data="set_1_t" + "3 theme"))

        markup.row(*row)
        row = []

        row.append(types.InlineKeyboardButton("1 theme", callback_data="set_3_t" + "1 theme"))
        row.append(types.InlineKeyboardButton("2 theme", callback_data="set_3_t" + "2 theme"))
        row.append(types.InlineKeyboardButton("3 theme", callback_data="set_3_t" + "3 theme"))
        markup.row(*row)
    else:
        row = []
        row.append(types.InlineKeyboardButton("1 theme", callback_data="set_2_t" + "1 theme"))
        row.append(types.InlineKeyboardButton("2 theme", callback_data="set_2_t" + "2 theme"))
        row.append(types.InlineKeyboardButton("3 theme", callback_data="set_2_t" + "3 theme"))
        markup.row(*row)

    return markup


class battle:

    def __init__(self, message, s_id, s_usrn):
        # убрать пользователя из базы ищущих игру

        const.battle_array.update({s_id: self})

        try:
            const.map.extend([s_id, s_usrn, 1])
        except:
            pass

        self.first_player = message.chat.id
        self.name_fp = message.chat.username
        #get_user = defs.random_user(message)
        self.second_player = s_id#get_user[0] #get id
        self.name_sp = s_usrn#get_user[1] #get username

        bot.send_message(self.first_player, welcome_text.format(self.name_sp))
        bot.send_message(self.second_player, welcome_text.format(self.name_fp))

        #self.fp_ready = 0
        #self.sp_ready = 0

        #self.tema1 = "Не выбрана"
        #self.tema2 = "Не выбрана"
        #self.tema3 = "Не выбрана"
        #self.temaN = "Её выбирает соперник"

        self.start_battle()

    def set_fp_theme_id(self, id):
        self.fp_theme_id = id

    def set_sp_theme_id(self, id):
        self.sp_theme_id = id

    def set_ready_fp(self):
        self.fp_ready = 1

    def set_ready_sp(self):
        self.sp_ready = 1

    def is_ready(self):

        if (self.fp_ready == 1) and (self.sp_ready == 1):
            pass
            # начинать игру
        pass

    def start_battle(self):
        # выводим выбор категорий
        x = random.randrange(0, 2, 1)

        print(x)

        if x == 0:
            markup1 = create_table_vote(0)
            markup2 = create_table_vote(1)

            self.fp_num = 0
            self.sp_num = 1

            bot.send_message(self.first_player,
                             "Первая тема - {}\nВторая тема - {}\nТретья тема - {}".format(self.tema1, self.temaN, self.tema3),
                             reply_markup=markup1)
            bot.send_message(self.second_player,
                             "Первая тема - {}\nВторая тема - {}\nТретья тема - {}".format(self.temaN, self.tema2, self.temaN),
                             reply_markup=markup2)
        else:
            markup1 = create_table_vote(0)
            markup2 = create_table_vote(1)

            self.fp_num = 1
            self.sp_num = 0

            bot.send_message(self.second_player,
                             "Первая тема - {}\nВторая тема - {}\nТретья тема - {}".format(self.tema1, self.temaN, self.tema3),
                             reply_markup=markup1)
            bot.send_message(self.first_player,
                             "Первая тема - {}\nВторая тема - {}\nТретья тема - {}".format(self.temaN, self.tema2, self.temaN),
                             reply_markup=markup2)

        # выводим кнопк

@bot.message_handler(commands=['start'])
def start(message):
    #const.map[message] = [message.chat.username, 0]
    keyboard_defs.start_keyboard(message)

############################################

def sender(u_id, message_id, num, t_id):
    markup = create_table_vote(num)
    bot.edit_message_text(const.theme.format(const.battle_array.get(u_id).tema1,
                                             const.battle_array.get(u_id).tema2,
                                             const.battle_array.get(u_id).tema3),
                          u_id, message_id, reply_markup=markup)
    bot.answer_callback_query(t_id, text="")

@bot.callback_query_handler(func=lambda theme: theme.data[0:7] == 'set_1_t')
def change_1_theme(theme):
    const.battle_array.get(theme.from_user.id).tema1 = theme.data[7:]
    markup = create_table_vote(0)
    bot.edit_message_text(const.theme.format(const.battle_array.get(theme.from_user.id).tema1,
                                             const.battle_array.get(theme.from_user.id).tema2,
                                             const.battle_array.get(theme.from_user.id).tema3),
                          theme.from_user.id, theme.message.message_id, reply_markup=markup)
    bot.answer_callback_query(theme.id, text="")
    #sender(theme.from_user.id, theme.message.message_id, 1, theme.id)

@bot.callback_query_handler(func=lambda theme: theme.data[0:7] == 'set_2_t')
def change_2_theme(theme):
    const.battle_array.get(theme.from_user.id).tema2 = theme.data[7:]
    markup = create_table_vote(1)
    bot.edit_message_text(const.theme.format(const.battle_array.get(theme.from_user.id).tema1,
                                             const.battle_array.get(theme.from_user.id).tema2,
                                             const.battle_array.get(theme.from_user.id).tema3),
                          theme.from_user.id, theme.message.message_id, reply_markup=markup)
    bot.answer_callback_query(theme.id, text="")
    #sender(theme.from_user.id, theme.message.message_id, 0, theme.id)

@bot.callback_query_handler(func=lambda theme: theme.data[0:7] == 'set_3_t')
def change_3_theme(theme):
    const.battle_array.get(theme.from_user.id).tema3 = theme.data[7:]
    markup = create_table_vote(0)
    bot.edit_message_text(const.theme.format(const.battle_array.get(theme.from_user.id).tema1,
                                             const.battle_array.get(theme.from_user.id).tema2,
                                             const.battle_array.get(theme.from_user.id).tema3),
                          theme.from_user.id, theme.message.message_id, reply_markup=markup)
    bot.answer_callback_query(theme.id, text="")
    #sender(theme.from_user.id, theme.message.message_id, 1, theme.id)

##############################################

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_50')
def change_bet_50(curr_bet):
    const.bet = 50
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(const.bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_100')
def change_bet_50(curr_bet):
    const.bet = 100
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(const.bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.callback_query_handler(func=lambda curr_bet: curr_bet.data == 'bet_200')
def change_bet_50(curr_bet):
    const.bet = 200
    markup = create_choice()
    bot.edit_message_text(your_bet_is.format(str(const.bet)), curr_bet.from_user.id, curr_bet.message.message_id, reply_markup=markup)
    bot.answer_callback_query(curr_bet.id, text="")

@bot.message_handler(content_types='text')
def start_handler(message):
    if message.text == 'Заработать':
        markup = create_choice()
        bot.send_message(message.chat.id, your_bet_is.format(str(const.bet)), reply_markup=markup)
        keyboard_defs.paygame_keyboard(message)
    elif message.text == 'Поиск':
        if len(const.map) == 0:
            const.map.append([message.chat.id, message.chat.username, 1])
        else:
            x = battle(message, const.map[0][0], const.map[0][1])
            const.battle_array.update({message.chat.id: x})
            #const.battle_array[-1].start_battle
    elif message.text == 'Назад':
        try:
            const.map.extend([message.chat.id, message.chat.username, 1])
        except:
            pass
        keyboard_defs.start_keyboard(message)




if __name__ == '__main__':
    bot.polling(none_stop=True)


import telebot
from telebot import types
import const
import texts
import html

bot = telebot.TeleBot(const.API_TOKEN)

#Главные клавиатуры

def start_keyboard(message):
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('🏆💯💍   Играть   💍💯🏆')
    murkup.row('Рейтинг', 'Мой счёт', 'About')
    bot.send_message(message.chat.id, '<strong>Играй.  Разивайся.  Зарабатывай.</strong>', parse_mode="HTML", reply_markup=murkup)

def about_keyboard(message):
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('Пригласить друга')
    murkup.row('Что-то не так?', 'Назад')
    bot.send_message(message.chat.id, texts.about_text, parse_mode="HTML", reply_markup=murkup)

def wallet_keyboard(message):
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('Ввести', 'Вывести')
    murkup.row('Хочешь больше?')
    murkup.row('Назад')
    bot.send_message(message.chat.id, 'Загружаю...', reply_markup=murkup)

def freecoins_menu(message):                                        #Меню реферов
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('Пригласить друга')
    murkup.row('Назад')
    bot.send_message(message.chat.id, texts.free_coins, reply_markup=murkup)

def hide(message):
    reply_markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Я вернуcь",reply_markup=reply_markup)
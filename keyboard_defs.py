import telebot
from telebot import types
import const
import texts

bot = telebot.TeleBot(const.API_TOKEN)

#Главные клавиатуры

def start_keyboard(message):
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('🏆💯💍   Играть   💍💯🏆')
    murkup.row('Рейтинг', '💳 Счёт 💳', 'About')
    bot.send_message(message.chat.id, 'Сделай свой выбор...', reply_markup=murkup)

def about_keyboard(message):
    murkup = types.ReplyKeyboardMarkup(True, False)
    murkup.row('Пригласить друга')
    murkup.row('Что-то не так?', 'Назад')
    bot.send_message(message.chat.id, texts.about_text, reply_markup=murkup)

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
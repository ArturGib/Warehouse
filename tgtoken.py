import telebot

class Bot:
    token = ''
    with open('token.txt') as f:
        token = f.read()
    bot = telebot.TeleBot(token)
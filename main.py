import telebot
import requests
from tgtoken import Bot
import messages
from States import State
import time
#from config import Token, Mongo
import logging

bot = Bot.bot
logging.basicConfig(level=logging.INFO, filename="logs/main_log.log", filemode='a',
                    format="%(asctime)s %(levelname)s %(message)s")

# Регистрация Пользователя #####
@bot.message_handler(commands = ['start'])
def handle_start_bot(message):
    messages.start(message, bot)


@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_status)
def take_status(message):
    messages.status(message, bot)
    #Выбрасывает в главное меню

    
#Принятие действия
@bot.callback_query_handler(func=lambda call: messages.get_STATE(user_id=call.message.chat.id) == State.STATE_wait_action)
def take_action(call):
    messages.take_action(call, bot)
    logging.info(f"Action by {messages.get_user_name(call.message.chat.id)}")

################################################################################
# Редактирование прибора
# меню редактирования
@bot.message_handler(content_types=['photo'], func=lambda message:
										messages.get_STATE(user_id=message.from_user.id) == State.STATE_edit_device)
def edit_device_in(message):
    messages.edit_device(message, bot)


#Выбор позиции редактирования
@bot.callback_query_handler(func=lambda call: messages.get_STATE(user_id=call.message.chat.id) == State.STATE_wait_edit)
def update_button_choice(call):
    messages.update_button_choice(call, bot)

    
#Редактирование
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) in [State.STATE_edit_type,
                                                                                               State.STATE_edit_name,
                                                                                               State.STATE_edit_inventory,
                                                                                               State.STATE_edit_notes,
                                                                                               State.STATE_edit_options,
                                                                                               State.STATE_edit_serial_number])
def editing(message):
    messages.editing(message, bot)

##############################################################################
# Взять устройство в использование
@bot.message_handler(content_types=['photo'],func=lambda message:
											messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_device_in_use)
def take_device_in_use(message):
    messages.take_device(message, bot)

# Смана комнаты
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_update_room)
def update_room(message):
	messages.update_room(message, bot)


# Заметка и переход в меню ожидания команды
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_update_notes)
def update_notes(message):
	messages.update_notes(message, bot)


##############################################################################
#Добавление прибора
@bot.message_handler(content_types=['photo'],func=lambda message:
											messages.get_STATE(user_id=message.from_user.id) == State.STATE_add_device)
def add_device(message):
    messages.add_device(message, bot)


# Внести тип устройства
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_type)
def get_type(message):
    messages.get_type(message, bot)


# Внести название прибора
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_dev_name)
def get_dev_name(message):
    messages.get_dev_name(message, bot)


# Внести инвентарный номер прибора
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_inventory)
def get_inventory(message):
    messages.get_inventory(message, bot)


#  Внести опции
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_opt)
def get_opt(message):
    messages.get_opt(message, bot)


# Записать комнату
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_get_room)
def get_room(message):
    messages.get_room(message, bot)


# Записать серийный номер
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_serial_number)
def get_serial_number(message):
    messages.get_serial_number(message, bot)


# Добавить пометки
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) == State.STATE_notes)
def get_notes(message):
    messages.get_notes(message, bot)


#####################################################################

# Поиск
@bot.callback_query_handler(func=lambda call: messages.get_STATE(user_id=call.message.chat.id) == State.STATE_search)
def search(call):
	messages.search(call, bot)

# Результат в зависимости от типа поиска
@bot.message_handler(func=lambda message: messages.get_STATE(user_id=message.from_user.id) in [State.STATE_searching_type, 
                                                                                               State.STATE_searching_inventory, 
                                                                                               State.STATE_searching_name,
                                                                                               State.STATE_searching_room,
                                                                                               State.STATE_searching_serial_number])
def searching_type(message):
    messages.searching(message, bot)
    
######################################################################

# Сведения о приборе
@bot.message_handler(content_types=['photo'], func=lambda message:
											messages.get_STATE(user_id=message.from_user.id) == State.STATE_view_device)
def get_view_device(message):
    messages.get_view_device(message, bot)
    

#@bot.message_handler(content_types=['text'])
#def get_greeting_messages(message):
#	if message.text == "Пилвет":
#		bot.send_message(message.from_user.id, "Пилвет, мевкий!")
#	else:
#		bot.send_message(message.from_user.id, "Привет, зарегистрируйтесь с помощью команды '/start' или перейди в меню с помощью команды '/help' ")
  
  
@bot.message_handler(content_types=['text'])
def get_greeting_messages(message):
	if message.text == "Пилвет":
		bot.send_message(message.from_user.id, "Пилвет, мевкий!")
	elif messages.str_convert(message.text, "l") == "/help":
		if messages.users.count_documents({"_id": message.from_user.id}) == 0:
			bot.send_message(message.from_user.id, "Привет, зарегистрируйтесь с помощью команды '/start' ")
		else:
			messages.waiting(user_id=message.from_user.id, bot = bot, message_id = message.message_id)
	else:
		bot.send_message(message.from_user.id, "Привет, зарегистрируйтесь с помощью команды '/start' или перейди в меню с помощью команды '/help' ")

while True:
	try:
		bot.polling(none_stop=True, interval=2)
		# Предполагаю, что бот может мирно завершить работу, поэтому
        # даем выйти из цикла
		logging.info("In progress")
		break
	except telebot.apihelper.ApiException as e:
		bot.stop_polling()
		time.sleep(5)
		logging.error("ApiException")
	except KeyboardInterrupt:
		print('\n! Received keyboard interrupt\n')
		logging.error("User stop")
		break
	except requests.exceptions.ConnectionError:
		bot.stop_polling()
		time.sleep(60)
		logging.error("Connection Error")
	except requests.exceptions.ReadTimeout:
		bot.stop_polling()
		time.sleep(60)
		logging.error("ReadTimeout Error")
	except:
		logging.error("Unexpected Error")
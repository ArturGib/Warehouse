from pymongo import MongoClient
from tgtoken import Bot
from telebot import types
from States import State
from qr_detector import qr_data
import time

cluster = MongoClient("mongodb://127.0.0.1:27017") # пользуемся локальной БД
db = cluster.newdb
users = db.users
devices = db.devices
tconv = lambda x: time.strftime("(%H:%M:%S) - %d.%m.%Y", time.localtime(x)) #Конвертация даты в читабельный вид


class My_Text:
    T_search = "ПОИСК"
    T_replace_device = "ВЗЯТЬ/ПЕРЕМЕСТИТЬ"
    T_add_device = "НОВОЕ устройство"
    T_about_device = "СВЕДЕНИЯ о устройстве"
    T_edit_device = "РЕДАКТИРОВАТЬ устройство"
    
    
def get_status(user_id=0):
	data = users.find({"_id":user_id})
	for obj in data:
		return obj['status']


def start(message, bot):
    if users.count_documents({"_id": message.from_user.id}) == 0:
        users.insert_one({"_id": message.from_user.id, "first_name": message.from_user.first_name,
						 "last_name": message.from_user.last_name, "STATE": State.STATE_status})
        bot.send_message(message.from_user.id, "Введите свой статус")
    else:
        bot.send_message(message.from_user.id, "Вы уже зарегистрированы")
        users.update_one({"_id": message.from_user.id},
							{"$set": {"STATE": "2"}})
        
 
def status(message, bot):
    if message.text == 'admin':
        users.update_one({"_id": message.from_user.id}, {"$set": {"status": message.text}})
        bot.send_message(message.from_user.id, "Вы зарегистрированы")
        waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
    elif message.text == 'user':
        users.update_one({"_id": message.from_user.id}, {"$set": {"status": message.text}})
        bot.send_message(message.from_user.id, "Вы зарегистрированы")
        waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
    else:
        bot.send_message(message.from_user.id, "Введите свой статус")
  

def waiting(user_id, bot, message_id):
    users.update_one({"_id": user_id}, {"$set": {"STATE": State.STATE_wait_action}})
    result = get_status(user_id=user_id)
    if result == 'admin':
        keyboard = types.InlineKeyboardMarkup()
        callback_search = types.InlineKeyboardButton(text=My_Text.T_search, callback_data="1")
        callback_take_device = types.InlineKeyboardButton(text=My_Text.T_replace_device, callback_data="2")
        callback_make_device = types.InlineKeyboardButton(text=My_Text.T_add_device, callback_data="3")
        callback_view = types.InlineKeyboardButton(text=My_Text.T_about_device, callback_data="4")
        callback_update_device = types.InlineKeyboardButton(text=My_Text.T_edit_device, callback_data="5")
        keyboard.add(callback_search)
        keyboard.add(callback_take_device)
        keyboard.add(callback_view)
        keyboard.add(callback_make_device)
        keyboard.add(callback_update_device)
        try:
            bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Выберите действие", reply_markup=keyboard)
        except:
            bot.send_message(user_id, "Выберите категорию", reply_markup=keyboard)
    if result == 'user':
        keyboard = types.InlineKeyboardMarkup()
        callback_search = types.InlineKeyboardButton(text="ПОИСК", callback_data="1")
        callback_take_device = types.InlineKeyboardButton(text="ВЗЯТЬ/ПЕРЕМЕСТИТЬ", callback_data="2")
        callback_view = types.InlineKeyboardButton(text="СВЕДЕНИЯ о устройстве", callback_data="4")
        keyboard.add(callback_search)
        keyboard.add(callback_take_device)
        keyboard.add(callback_view)
        bot.send_message(user_id, "Выберите категорию", reply_markup=keyboard)
        

def take_action(call, bot):
	keyboard = types.InlineKeyboardMarkup()
	callback_type = types.InlineKeyboardButton(text="ТИП", callback_data="1")
	callback_name = types.InlineKeyboardButton(text="НАЗВАНИЕ", callback_data="2")
	callback_room = types.InlineKeyboardButton(text="КОМНАТА", callback_data="3")
	callback_inventory = types.InlineKeyboardButton(text="ИНВЕНТАРНЫЙ НОМЕР", callback_data="4")
	callback_serial_number = types.InlineKeyboardButton(text="ЗАВОДСКОЙ НОМЕР", callback_data="5")
	keyboard.add(callback_type)
	keyboard.add(callback_name)
	keyboard.add(callback_room)
	keyboard.add(callback_inventory)
	keyboard.add(callback_serial_number)
	if call.data == '1':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_search}})
		bot.send_message(call.message.chat.id, "Выберите категорию поиска", reply_markup=keyboard)
	elif call.data == '2':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_get_device_in_use}})
		bot.send_message(call.message.chat.id, "Отправьте фото QR-кода прибора, который хотите взять в использование")
	elif call.data == '3':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_add_device}})
		bot.send_message(call.message.chat.id, "Отправьте фото QR-кода, установленного на прибор")
	elif call.data == '4':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_view_device}})
		bot.send_message(call.message.chat.id, "Отправьте фото QR-кода, чтобы узнать сведения о приборе")
	elif call.data == '5':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_device}})
		bot.send_message(call.message.chat.id, "Отправьте фото QR-кода для редактирования")




def edit_device(message, bot):
	file_info = bot.get_file(message.photo[2].file_id) #message.json['photo'][2]['file_id']
	file = bot.download_file(file_info.file_path)

	with open('photo.png', 'wb') as new_file:
		new_file.write(file)
	"""
	inpt_im = cv2.imread("photo.png")
	inpt_im = cv2.cvtColor(inpt_im, cv2.COLOR_RGB2GRAY)
	detector = cv2.QRCodeDetector()
	"""
	data = qr_data()

	if data:
		if devices.count_documents({"_id": data}) == 0:
			bot.send_message(message.from_user.id,"Прибора нет в базе") #data[1][0]
			waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
		else:
			users.update_one({"_id": message.from_user.id}, {"$set": {"current_dev_id": data}})	
			users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_wait_edit}})
			keyboard = types.InlineKeyboardMarkup()
			result = devices.find({"_id":data})
			print_search_result(result=result, bot=bot, user_id=message.from_user.id)
			callback_type = types.InlineKeyboardButton(text="ТИП", callback_data="1")
			callback_name = types.InlineKeyboardButton(text="НАЗВАНИЕ", callback_data="2")
			callback_room = types.InlineKeyboardButton(text="КОМНАТА", callback_data="3")
			callback_inventory = types.InlineKeyboardButton(text="ИНВЕНТАРНЫЙ НОМЕР", callback_data="4")
			callback_serial_number = types.InlineKeyboardButton(text="ЗАВОДСКОЙ НОМЕР", callback_data="5")
			callback_options = types.InlineKeyboardButton(text="ОПЦИИ", callback_data="6")
			callback_notes = types.InlineKeyboardButton(text="ПОМЕТКИ", callback_data="7")
			callback_back = types.InlineKeyboardButton(text="ЗАКОНЧИТЬ РЕДАКТИРОВАНИЕ", callback_data="8")
			keyboard.add(callback_type)
			keyboard.add(callback_name)
			keyboard.add(callback_room)
			keyboard.add(callback_inventory)
			keyboard.add(callback_serial_number)
			keyboard.add(callback_options)
			keyboard.add(callback_notes)
			keyboard.add(callback_back)
			bot.send_message(message.from_user.id, "Что редактируем?", reply_markup=keyboard)		
	else:
		bot.send_message(message.from_user.id, 'Не смог разобрать :(')
	# добавление редактируемых категорий


def editing(message, bot):
    match get_STATE(user_id=message.from_user.id):
        case State.STATE_edit_name:
            devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Device_name": str_convert(message.text, "u")}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)
        case State.STATE_edit_inventory:
            devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Inventory": str_convert(message.text, "u")}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)
        case State.STATE_edit_notes:
            devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Note": message.text.strip()}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)
        case State.STATE_edit_options:
            devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Options": message.text.strip()}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)
        case State.STATE_edit_serial_number:
            devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Serial_number": str_convert(message.text,"u")}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)
        case State.STATE_edit_type:
            type_list = convert_type_str_to_list(message.text)
            qr_id = get_current_dev_id(user_id=message.from_user.id)
            for obj in type_list:
                devices.update_one({"_id": qr_id}, {"$push":{"Type": obj}})
            to_edit_menu(user_id=message.from_user.id, bot=bot, message_id=message.message_id)



# Сведения о приборе

def get_view_device(message, bot):
	#file_info = bot.get_file(message.json['photo'][2]['file_id'])
	file_info = bot.get_file(message.photo[2].file_id)
	file = bot.download_file(file_info.file_path)

	with open('photo.png', 'wb') as new_file:
		new_file.write(file)

	data = qr_data()
	if data:
		if devices.count_documents({"_id": data}) > 0:
			result = devices.find({"_id": data})
			print_search_result(result=result, bot=bot, user_id=message.from_user.id)
			get_users_list(QR_id = data, bot = bot, user_id=message.from_user.id)
			waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
		else:
			bot.send_message(message.from_user.id, 'Устройства нет в базе или у меня не получилось разобрать')
			waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
	else:
		bot.send_message(message.from_user.id, 'Не смог разобрать :(')
		waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)   


# Поиск
def search(call, bot):
	if call.data == '1':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_searching_type}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите интересующий тип \n(Например: генератор)")
	elif call.data == '2':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_searching_name}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите интересующее название\n(Например: SMF100A)")
	elif call.data == '3':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_searching_room}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите номер комнаты в которой ищете приборы\n(Например: 528)")
	elif call.data == '4':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_searching_inventory}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите искомый инвентарник\n (Например: П-1-1010)")
	elif call.data == '5':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_searching_serial_number}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите искомый заводской номер\n (Например: MY92837535)")

def searching(message, bot):
    match get_STATE(user_id=message.from_user.id):
        case State.STATE_searching_name:
            if devices.count_documents({"Device_name": str_convert(message.text, "u")}) > 0:
                result = devices.find({"Device_name": str_convert(message.text, "u")})
                print_search_result(result=result, bot=bot, user_id=message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Устройств не найдено')
            waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
        
        case State.STATE_searching_inventory:
            if devices.count_documents({"Inventory": str_convert(message.text, "u")}) > 0:
                result = devices.find({"Inventory": str_convert(message.text, "u")})
                bot.send_message(message.from_user.id, "Устройство с заданным инвентарником")
                print_search_result(result=result, bot=bot, user_id=message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Устройств не найдено')
            waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
        
        case State.STATE_searching_room:
            if devices.count_documents({"Room": str_convert(message.text, "u")}) > 0:
                result = devices.find({"Room": str_convert(message.text, "u")})
                bot.send_message(message.from_user.id, "Устройства в комнате")
                print_search_result(result=result, bot=bot, user_id=message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Устройств не найдено')
            waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
        
        case State.STATE_searching_serial_number:
            if devices.count_documents({"Serial_number": str_convert(message.text, "u")}) > 0:
                result = devices.find({"Serial_number": str_convert(message.text, "u")})
                bot.send_message(message.from_user.id, "Устройство с заданным заводским номером")
                print_search_result(result=result, bot=bot, user_id=message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Устройств не найдено')
            waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
        
        case State.STATE_searching_type:
            type_list = convert_type_str_to_list(str_type=message.text)
            if devices.count_documents({"Type": {"$in": type_list}})>0:
                result = devices.find({"Type": {"$in": type_list}})
                print_search_result(result=result, bot=bot, user_id = message.from_user.id)
            else:
                bot.send_message(message.from_user.id, 'Устройств не найдено')
            waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
            


# Взять устройство
def take_device(message, bot):
	file_info = bot.get_file(message.photo[2].file_id)
	file = bot.download_file(file_info.file_path)
	with open('photo.png', 'wb') as new_file:
		new_file.write(file)

	data = qr_data()
	add_time = tconv(message.date)
	if data:
		if devices.count_documents({"_id": data}) > 0:
			users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_update_room}})
			users.update_one({"_id": message.from_user.id}, {"$set": {"current_dev_id": data}})
			result = devices.find({"_id":data})
			print_search_result(result=result, bot=bot, user_id=message.from_user.id)
			if len(devices.find_one({"_id": data})["owner"]) < 5:
				devices.update_one({"_id": data}, {"$push": {"owner": (message.from_user.id, add_time)}})
			else:
				devices.update_one({"_id": data}, {"$pop": {"owner": -1}})
				devices.update_one({"_id": data}, {"$push": {"owner": (message.from_user.id, add_time)}})
			bot.send_message(message.from_user.id, 'В какую комнату отправляется?')
		else:
			bot.send_message(message.from_user.id, 'Устройства нет в базе или у меня не получилось разобрать')
			waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
	else:
		bot.send_message(message.from_user.id, 'Не смог разобрать :(')
		waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)


# Обновление комнаты
def update_room(message, bot):
    devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)}, {"$set": {"Room": str_convert(message.text, "u")}}) #исправление 
    users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_update_notes}})
    bot.send_message(message.from_user.id, 'Пометки')
    

# Обновление заметки и выход в меню ожидания команды
def update_notes(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)}, {"$set": {"Note": message.text.strip()}})
	waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)


def update_button_choice(call, bot):
	if call.data == '1':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_type}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите тип \n(Например: генератор)")
	elif call.data == '2':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_name}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите название\n(Например: SMF100A)")
	elif call.data == '3':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_room}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите номер комнаты")
	elif call.data == '4':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_inventory}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите инвентарник\n (Например: П-1-1010)")
	elif call.data == '5':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_serial_number}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите заводской номер\n (Например: MY92837535)")
	elif call.data == '6':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_options}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите опции")
	elif call.data == '7':
		users.update_one({"_id": call.message.chat.id}, {"$set": {"STATE": State.STATE_edit_notes}})
		bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Введите пометку\n (Например: П-1-1010)")
	elif call.data == '8':
		waiting(user_id=call.message.chat.id, bot=bot, message_id=call.message.message_id)
  
# Добавление устройства в базу
# По QR инициируем устройство, переходим к типу устройства
def add_device(message, bot):
	file_info = bot.get_file(message.photo[2].file_id)
	file = bot.download_file(file_info.file_path)
	
	with open('photo.png', 'wb') as new_file:
		new_file.write(file)

	data = qr_data()
	if data:
		if devices.count_documents({"_id": data}) == 0:
			#bot.send_message(message.from_user.id, data) #data[1][0] # вывод прочитанного QR кода
			add_time = tconv(message.date)
			load_dev_todb(QR_id=data, user_id=message.from_user.id, add_time=add_time, bot=bot)  # проверять на непустые значения
		else:
			bot.send_message(message.from_user.id, "Прибор уже в базе")
			waiting(user_id=message.from_user.id, bot=bot, message_id = message.message_id)
	else:
		bot.send_message(message.from_user.id, 'Не смог разобрать :(')
	      
      
def get_type(message, bot):
    qr_id=get_current_dev_id(user_id=message.from_user.id)
    type_list = convert_type_str_to_list(message.text)
    for obj in type_list: 
        devices.update_one({"_id": qr_id}, {"$push":{"Type": obj}})
	#db.Devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id,db=db)},
	#					  {"$push":{"Type":str_convert(message.text, ''}})
    users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_get_dev_name}})
    bot.send_message(message.from_user.id, "Введите название устройства:")


def get_dev_name(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Device_name": str_convert(message.text, "u")}})
	users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_get_inventory}})
	bot.send_message(message.from_user.id, "Введите инвентарник устройства:")


def get_inventory(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Inventory": str_convert(message.text, "u")}})
	users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_get_opt}})
	bot.send_message(message.from_user.id, "Введите опции устройства:")


def get_opt(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Options": message.text.strip()}})
	users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_get_room}})
	bot.send_message(message.from_user.id, "Введите номер комнаты, в которой будет находиться устройство:")


def get_room(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Room": str_convert(message.text, "u")}})
	users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_serial_number}})
	bot.send_message(message.from_user.id, "Введите заводской номер:")
 
 
def get_serial_number(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Serial_number": str_convert(message.text,"u")}})
	users.update_one({"_id": message.from_user.id}, {"$set": {"STATE": State.STATE_notes}})
	bot.send_message(message.from_user.id, "Введите необходимые пометки:")
 
 
def get_notes(message, bot):
	devices.update_one({"_id": get_current_dev_id(user_id=message.from_user.id)},
						  {"$set": {"Note": message.text.strip()}})
	waiting(user_id=message.from_user.id, bot=bot, message_id=message.message_id)




def get_user_name(owner=0):
	data = users.find({"_id": owner})
	for obj in data:
		return str(obj['first_name']) + " " + str(obj['last_name'])


def str_convert(c_str, r=0):
    if r == 'l':
        return c_str.replace(" ", "").lower()
    elif r == "u":
        return c_str.replace(" ", "").upper()
    
    
def get_STATE(user_id=0):
	data = users.find({"_id":user_id})
	for obj in data:
		return obj['STATE']


def convert_type_str_to_list(str_type=""):
    str_list = str_type.strip(" ").split(" ")
    my_list = []
    for obj_s in str_list:
        if len(obj_s):
            my_list.append(obj_s.lower())
    return my_list
    

def get_users_list(QR_id=0, bot=0, user_id=0):
    owners_list = devices.find_one({"_id":QR_id})["owner"]
    for person in owners_list:
        bot.send_message(user_id, "В распоряжении " + get_user_name(person[0]) + "\n" +
                         "c " + str(person[1]))


def get_current_dev_id(user_id=0):
    data = users.find({"_id": user_id})
    for obj in data:
        return obj['current_dev_id']
    
    
def get_type_str(obj=0):
    try:
        my_list = obj["Type"]
        type_str = ""
        for st in my_list:
            type_str += st + " "
        type_str = type_str.strip()
        return type_str
    except:
        return "нет типа"
        
        
# Первичная загрузка в базу
def load_dev_todb(QR_id=0,  user_id=0,  add_time=0,  bot=0):
    post = {"_id": QR_id}
    if devices.count_documents({"_id": QR_id}) == 0:
        devices.insert_one(post)
        users.update_one({"_id": user_id}, {"$set": {"STATE": State.STATE_get_type}})
        users.update_one({"_id": user_id}, {"$set": {"current_dev_id": QR_id}}) # по хорошему нужно удалять после того как взял кто-то другой
        devices.update_one({"_id": QR_id}, {"$push": {"owner": (user_id, add_time)}})
        bot.send_message(user_id, "Введите тип устройства:")
    else:
        users.update_one({"_id": user_id}, {"$set": {"STATE": State.STATE_get_type}})
        users.update_one({"_id": user_id}, {"$set": {"current_dev_id": QR_id}})
        if len(devices.find_one({"_id": QR_id})["owner"])<5:
            devices.update_one({"_id": QR_id}, {"$push": {"owner": (user_id, add_time)}})
        else:
            devices.update_one({"_id": QR_id}, {"$pop": {"owner": -1}})
            devices.update_one({"_id": QR_id}, {"$push": {"owner": (user_id, add_time)}})
        bot.send_message(user_id, "Введите тип устройства:")
    
        
# Формирователь отчета о поиске
def print_search_result(result=[], bot=0, user_id=0):
    counter = 1 #номер устройства в списке выдачи
    for obj in result:
        owners_list = obj["owner"]
        owner_id = owners_list[-1][0]
        owner_time = owners_list[-1][1]
        type_str = get_type_str(obj=obj)
        bot.send_message(user_id, "Устройство №" + str(counter) + "\n" +
						 type_str + " " + str(obj['Device_name']) + "\n" +
						 "В распоряжении " + get_user_name(owner=owner_id) + "\n" +
                         "Взят " + str(owner_time) + "\n" +
						 "В комнате: " + str(obj['Room']) + "\n" +
						 "Инвентарник: " + str(obj['Inventory']) + "\n" +
						 "Опции: " + str(obj['Options']) + "\n" +
                         "Заводской номер: " + str(obj['Serial_number']) + "\n" +
						 "Пометка: " + str(obj['Note']))
        counter = counter + 1
        
        
def to_edit_menu(user_id=0, bot=0, message_id=0):
    users.update_one({"_id": user_id}, {"$set": {"STATE": State.STATE_wait_edit}})

    keyboard = types.InlineKeyboardMarkup()
    callback_type = types.InlineKeyboardButton(text="ТИП", callback_data="1")
    callback_name = types.InlineKeyboardButton(text="НАЗВАНИЕ", callback_data="2")
    callback_room = types.InlineKeyboardButton(text="КОМНАТА", callback_data="3")
    callback_inventory = types.InlineKeyboardButton(text="ИНВЕНТАРНЫЙ НОМЕР", callback_data="4")
    callback_serial_number = types.InlineKeyboardButton(text="ЗАВОДСКОЙ НОМЕР", callback_data="5")
    callback_options = types.InlineKeyboardButton(text="ОПЦИИ", callback_data="6")
    callback_notes = types.InlineKeyboardButton(text="ПОМЕТКИ", callback_data="7")
    callback_back = types.InlineKeyboardButton(text="ЗАКОНЧИТЬ РЕДАКТИРОВАНИЕ", callback_data="8")
    keyboard.add(callback_type)
    keyboard.add(callback_name)
    keyboard.add(callback_room)
    keyboard.add(callback_inventory)
    keyboard.add(callback_serial_number)
    keyboard.add(callback_options)
    keyboard.add(callback_notes)
    keyboard.add(callback_back)
    try:
        bot.edit_message_text(chat_id=user_id, message_id=message_id, text="Что редактируем?", reply_markup=keyboard)
    except:
        bot.send_message(user_id, "Что редактируем?", reply_markup=keyboard)
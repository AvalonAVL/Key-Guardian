from telebot import TeleBot, types
from sqlite3 import connect
from config import token

bot = TeleBot(str(token))

connection = connect('storage.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute('PRAGMA foreign_keys = ON')
connection.commit()


def user_menu_markup():
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text='Получить новый ключ', callback_data='get_new_key')
    button2 = types.InlineKeyboardButton(text='Посмотреть мои ключи', callback_data='view_my_keys')
    button3 = types.InlineKeyboardButton(text='Моя динамическая ссылка', callback_data='my_dynamic_link')
    markup.add(button1, button2, button3)
    return markup

def admin_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Список пользователей', callback_data='view_users')
    button2 = types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user')
    button3 = types.InlineKeyboardButton(text='Получить новый ключ', callback_data='get_new_key')
    button4 = types.InlineKeyboardButton(text='Посмотреть мои ключи', callback_data='view_my_keys')
    button5 = types.InlineKeyboardButton(text='Посмотреть все ключи', callback_data='view_all_keys')
    button6 = types.InlineKeyboardButton(text='Моя динамическая ссылка', callback_data='my_dynamic_link')
    button7 = types.InlineKeyboardButton(text='Посмотреть все ссылки', callback_data='view_all_links')
    markup.add(button1, button2, button3, button4, button5, button6, button7)
    return markup


@bot.message_handler(commands=['start', 'auth'])
def start(message):
    id = message.from_user.id
    cursor.execute('SELECT is_admin FROM Users WHERE telegram_id=?', (id,))
    res = cursor.fetchall()
    if not len(res):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text='/auth')
        markup.add(button)
        bot.send_message(id, text='Вы не обнаружены в списке разрешенных пользователей. ' \
        'Если Вы считаете, что произошла ошибка, обратитесь к администратору сервиса. Ваш идентификатор: <code>%s</code>\nЧтобы ' \
        'авторизоваться снова, нажмите кнопку внизу сообщения или введите команду <code>/auth</code>' % (id), 
        parse_mode='HTML', reply_markup=markup)
        return
    elif res[0][0]:
        markup = admin_menu_markup()
        bot.send_message(id, text='All hail Lord Avalon! Что желаете совершить сегодня?', reply_markup=markup, protect_content=True)
    else:
        markup = user_menu_markup()
        bot.send_message(id, text='Вы успешно авторизовались! Выберите, что хотите сделать', reply_markup=markup, protect_content=True)
    data = (message.from_user.username, message.from_user.first_name, message.from_user.last_name, id)
    cursor.execute('UPDATE Users SET username=?, first_name=?, last_name=? WHERE telegram_id=?', data)


@bot.callback_query_handler(func=lambda f: f.data == 'menu')
def menu(query):
    id = query.from_user.id
    cursor.execute('SELECT is_admin FROM Users WHERE telegram_id=?', (id,))
    res = cursor.fetchall()
    if res[0][0]:
        markup = admin_menu_markup()
    else:
        markup = user_menu_markup()
    bot.delete_message(chat_id=id, message_id=query.message.id)
    bot.send_message(chat_id=id, text='С возвращением в меню! Выберите действие:', reply_markup=markup, protect_content=True)


@bot.callback_query_handler(func=lambda f: f.data == 'add_user')
def add_user(query):
    id = query.from_user.id
    

@bot.callback_query_handler(func=lambda f: f.data == 'my_dynamic_link')
def view_my_links(query):
    markup = types.InlineKeyboardMarkup(row_width=1)
    id = query.from_user.id
    cursor.execute('SELECT link, key_id FROM Links WHERE user_id=?', (id,))
    data = cursor.fetchall()
    if not len(data):
        text = 'У вас нет динамической ссылки для подключения'
    else:
        text = 'Ваша динамическая ссылка для подключения:\n'
        link = data[0][0]
        internal_id = data[0][1]
        text += '`' + link + '`\n'
        if internal_id is not None:
            text += 'Сейчас ссылка привязана к ключу с id: `' + str(internal_id) + '`'
        else:
            cursor.execute('SELECT COUNT (key_id) FROM Ownership WHERE user_id=?', (id,))
            res = cursor.fetchall()[0][0]
            text += 'Сейчас ссылка не привязана ни к одному из ваших ключей'
            if res:
                button = types.InlineKeyboardButton(text='Привязать к ключу', callback_data='connect_my_link')
                markup.add(button)
    button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    markup.add(button)
    bot.delete_message(chat_id=id, message_id=query.message.id)
    bot.send_message(chat_id=id, text=text, parse_mode='MarkdownV2', reply_markup=markup, protect_content=True)


@bot.callback_query_handler(func=lambda f: f.data == 'view_users')
def view_users(query):
    markup = types.InlineKeyboardMarkup()
    cursor.execute('SELECT * FROM Users')
    data = cursor.fetchall()
    text = 'Список пользователей:\n'
    for i in range(len(data)):
        id = data[i][0]
        name = str(data[i][2])
        if data[i][3] is not None:
            name += ' ' + data[i][3]
        text += f'• {name}, id: `' + id + '`'
        if data[i][1] is not None:
            username = '@' + data[i][1]
            text += ', username: `' + username + '` Админ: `'
        else:
            text += ' Админ: `'
        if data[i][4]:
            is_admin = 'Да'
        else:
            is_admin = 'Нет'
        text += is_admin + '`\n'
    if len(data) > 1:
        button = types.InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user')
        markup.add(button)
    button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    markup.add(button)
    id = query.from_user.id
    bot.delete_message(chat_id=id, message_id=query.message.id)
    chunk_size = 4096
    if len(text) <= chunk_size:
        bot.send_message(chat_id=id, text=text, parse_mode='MarkdownV2', reply_markup=markup, protect_content=True)
    else:
        new_text = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        for i in range(len(new_text)-1):
            bot.send_message(chat_id=id, text=new_text[i], parse_mode='MarkdownV2', protect_content=True)
        bot.send_message(chat_id=id, text=new_text[-1], parse_mode='MarkdownV2', reply_markup=markup, protect_content=True)


bot.polling(non_stop=True)
connection.close()

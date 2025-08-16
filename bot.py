from telebot import TeleBot, types
from telebot.util import split_string, quick_markup
from telebot.apihelper import ApiTelegramException
from sqlite3 import connect
from config import token, key_limit, create_dynamic_link

bot = TeleBot(str(token))

connection = connect('storage.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute('PRAGMA foreign_keys = ON')
connection.commit()


def user_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Получить новый ключ', callback_data='get_new_key')
    button2 = types.InlineKeyboardButton(text='Посмотреть мои ключи', callback_data='view_my_keys')
    button3 = types.InlineKeyboardButton(text='Моя динамическая ссылка', callback_data='my_dynamic_link')
    button4 = types.InlineKeyboardButton(text='Настроить префикс', callback_data='set_prefix')
    markup.add(button1, button2, button3, button4)
    return markup

def admin_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    button1 = types.InlineKeyboardButton(text='Список пользователей', callback_data='view_users')
    button2 = types.InlineKeyboardButton(text='Владение ключами', callback_data='view_key_ownership')
    button3 = types.InlineKeyboardButton(text='Получить новый ключ', callback_data='get_new_key')
    button4 = types.InlineKeyboardButton(text='Посмотреть мои ключи', callback_data='view_my_keys')
    button5 = types.InlineKeyboardButton(text='Посмотреть все ключи', callback_data='view_all_keys')
    button6 = types.InlineKeyboardButton(text='Моя динамическая ссылка', callback_data='my_dynamic_link')
    button7 = types.InlineKeyboardButton(text='Посмотреть все ссылки', callback_data='view_all_links')
    button8 = types.InlineKeyboardButton(text='Настроить префикс', callback_data='set_prefix')
    markup.add(button1, button2, button3, button4, button5, button6, button7, button8)
    return markup

def choose_prefix_markup(exclusion: str):
    markup = types.InlineKeyboardMarkup(row_width=2)
    no_prefix = types.InlineKeyboardButton(text='Не использовать префикс', callback_data='set_prefix None')
    http_request = types.InlineKeyboardButton(text='HTTP-запрос', callback_data='set_prefix HTTP-req')
    http_response = types.InlineKeyboardButton(text='HTTP-ответ', callback_data='set_prefix HTTP-res')
    dns = types.InlineKeyboardButton(text='DNS-over-TCP-запрос', callback_data='set_prefix dns')
    tls_client = types.InlineKeyboardButton(text='TLS ClientHello', callback_data='set_prefix tls_client')
    tls_application_data = types.InlineKeyboardButton(text='TLS Application Data', callback_data='set_prefix tls_application')
    tls_server = types.InlineKeyboardButton(text='TLS ServerHello', callback_data='set_prefix tls_server')
    ssh = types.InlineKeyboardButton(text='SSH', callback_data='set_prefix ssh')
    prefixes = {'None': no_prefix, 'HTTP-запрос': http_request, 'HTTP-ответ': http_response, 'DNS-over-TCP-запрос': dns,
                'TLS ClientHello': tls_client, 'TLS Application Data': tls_application_data, 'TLS ServerHello': tls_server,
                'SSH': ssh}
    prefixes.pop(exclusion, None)
    what_button = types.InlineKeyboardButton(text='Что такое префикс?', callback_data='wtf_is_prefix')
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    values = list(prefixes.values())
    values.append(what_button)
    values.append(menu_button)
    buttons = [values[i:i+2] for i in range(0, len(values), 2)]
    for row in buttons:
        markup.add(*row)
    return markup

def add_user_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    add_button = types.InlineKeyboardButton(text='Попробовать снова', callback_data='add_user')
    markup.add(add_button, menu_button)
    return markup


def add_user_via_id(message):
    id = message.from_user.id
    user_id = message.text
    try:
        new_user = bot.get_chat_member(chat_id=user_id, user_id=user_id)
        user_data = (new_user.user.id, new_user.user.username, new_user.user.first_name, new_user.user.last_name)
        user_available = True
    except ApiTelegramException:
        user_available = False
        user_data = ()
    if len(user_id) > 52 or not str(user_id).isdigit():
        text = 'К сожалению, Telegram ID пользователя не выглядит валидным. Мы не можем добавить такого пользователя'
        bot.send_message(chat_id=id, text=text, reply_markup=add_user_markup(), protect_content=True)
        return 
    cursor.execute('SELECT telegram_id FROM Users WHERE telegram_id=?', (user_id,))
    data = cursor.fetchall()
    if len(data):
        text = 'Пользователь с данным Telegram ID уже есть в базе'
        bot.send_message(chat_id=id, text=text, reply_markup=add_user_markup(), protect_content=True)
        return
    markup = types.InlineKeyboardMarkup()
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    markup.add(menu_button)
    if not user_available:
        text = 'Успешно добавлен пользователь с id: <code>' + user_id + '</code>'
        cursor.execute('INSERT INTO Users (telegram_id) VALUES (?)', (user_id,))
    else:
        text = 'Успешно добавлен пользователь с id: <code>' + user_id + '</code> и его данные'
        cursor.execute('INSERT INTO Users (telegram_id, username, first_name, last_name) VALUES (?, ?, ?, ?)', user_data)
    cursor.execute('INSERT INTO Links (user_id, link) VALUES (?, ?)', (user_id, create_dynamic_link(user_id)))
    connection.commit()
    bot.send_message(chat_id=id, text=text, reply_markup=markup, parse_mode='HTML', protect_content=True)


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
    connection.commit()


@bot.callback_query_handler(func=lambda f: f.data == 'menu')
def menu(query):
    id = query.from_user.id
    cursor.execute('SELECT is_admin FROM Users WHERE telegram_id=?', (id,))
    res = cursor.fetchall()
    if res[0][0]:
        markup = admin_menu_markup()
    else:
        markup = user_menu_markup()
    bot.edit_message_text(chat_id=id, message_id=query.message.id, text='С возвращением в меню! Выберите действие:', reply_markup=markup)


@bot.callback_query_handler(func=lambda f: f.data == 'add_user')
def add_user_menu(query):
    id = query.from_user.id
    message = bot.send_message(chat_id=id, text='Введите Telegram ID пользователя, которого хотите добавить', protect_content=True)
    bot.delete_message(chat_id=id, message_id=query.message.id)
    bot.register_next_step_handler(message, add_user_via_id)


@bot.callback_query_handler(func=lambda f: f.data == 'my_dynamic_link')
def view_my_links(query):
    markup = types.InlineKeyboardMarkup(row_width=2)
    id = query.from_user.id
    cursor.execute('SELECT link, key_id, prefix FROM Links WHERE user_id=?', (id,))
    data = cursor.fetchall()
    cursor.execute('SELECT COUNT (key_id) FROM Ownership WHERE user_id=?', (id,))
    keys = cursor.fetchall()[0][0]
    text = 'Ваша динамическая ссылка для подключения:\n'
    link = data[0][0]
    key_id = data[0][1]
    text += '<code>' + link + '</code>\n'
    if key_id is not None:
        text += 'Сейчас ссылка привязана к ключу с id: <code>' + str(key_id) + '</code>\n'
    elif not keys:
        text += 'У вас нет ключей <i>(ссылка не работает без привязки к ключу)</i>\n'
    else:
        text += 'Сейчас ссылка не привязана ни к одному из ваших ключей <i>(cсылка не работает без привязки к ключу)</i>\n'
    prefix = data[0][2]
    if prefix is not None:
        text += 'Используется префикс вида <code>' + prefix + '</code>'
    else:
        text += 'Префикс не используется'
    what_button = types.InlineKeyboardButton(text='Что такое префикс?', callback_data='wtf_is_prefix')
    prefix_button = types.InlineKeyboardButton(text='Настроить префикс', callback_data='set_prefix')
    markup.add(prefix_button, what_button)
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    if keys > 1 or keys == 1 and key_id is None:
        link_button = types.InlineKeyboardButton(text='Привязать ссылку к ключу', callback_data='connect_my_link')
        markup.add(link_button, menu_button)
    elif not keys:
        key_button = types.InlineKeyboardButton(text='Получить ключ', callback_data='get_new_key')
        markup.add(key_button, menu_button)
    else:
        markup.add(menu_button)
    bot.edit_message_text(chat_id=id, message_id=query.message.id, text=text, parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda f: 'connect_my_link' in f.data)
def connect_my_link(query):
    id = query.from_user.id
    cursor.execute('SELECT key_id FROM Ownership WHERE user_id=?', (id,))
    keys = [key[0] for key in cursor.fetchall()]
    if len(query.data.split()) > 1:
        link_key = int(query.data.split()[1])
        data = (link_key, id)
        cursor.execute('UPDATE Links SET key_id=? WHERE user_id=?', data)
        connection.commit()
    else:
        cursor.execute('SELECT key_id FROM Links WHERE user_id=?', (id,))
        link_key = cursor.fetchall()[0][0]
    if link_key in keys:
        keys.remove(link_key)
    buttons = [types.InlineKeyboardButton(text=str(keys[i]), callback_data='connect_my_link '+str(keys[i])) for i in range(len(keys))]
    markup = types.InlineKeyboardMarkup(row_width=3)
    if link_key is None:
        text = 'Динамическая ссылка не привязана к ключу\n'
    else:
        text = 'Динамическая ссылка привязана к ключу с id: <code>' + str(link_key) + '</code>\n'
    text += 'Вы можете привязать ссылку к ключу, выбрав нужную кнопку'
    rowed_buttons = [buttons[i:i+3] for i in range(0, len(buttons), 3)]
    for row in rowed_buttons:
        markup.add(*row)
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    link_button = types.InlineKeyboardButton(text='Посмотреть ссылку', callback_data='my_dynamic_link')
    markup.add(link_button, menu_button)
    bot.edit_message_text(chat_id=id, message_id=query.message.id, text=text, parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda f: f.data == 'wtf_is_prefix')
def wtf_is_prefix(query):
    id = query.from_user.id
    markup = types.InlineKeyboardMarkup(row_width=2)
    text = 'Префикс — это список байтов, благодаря которым подключение выглядит как протокол, разрешенный в сети, ' \
    'и обходит брандмауэры, которые блокируют нераспознанные протоколы. ' \
    'Вы можете поменять префикс в настройках, если испытываете проблемы с подключением.\n' \
    '<a href="https://developers.google.com/outline/docs/guides/service-providers/prefixing?hl=ru">Подробнее</a>'
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    prefix_button = types.InlineKeyboardButton(text='Настроить префикс', callback_data='set_prefix')
    markup.add(prefix_button, menu_button)
    bot.edit_message_text(chat_id=id, message_id=query.message.id, text=text, parse_mode='HTML', reply_markup=markup)


@bot.callback_query_handler(func=lambda f: 'set_prefix' in f.data)
def set_prefix(query):
    id = query.from_user.id
    if len(query.data.split()) > 1:
        prefix = query.data.split()[1]
        prefixes = {'None': None, 'HTTP-req': 'HTTP-запрос', 'HTTP-res': 'HTTP-ответ', 'dns': 'DNS-over-TCP-запрос', 
                    'tls_client': 'TLS ClientHello', 'tls_application': 'TLS Application Data', 'tls_server': 'TLS ServerHello',
                    'ssh': 'SSH'}
        prefix = prefixes[prefix]
        data = (prefix, id)
        cursor.execute('UPDATE Links SET prefix=? WHERE user_id=?', data)
        connection.commit()
    else:
        cursor.execute('SELECT prefix FROM Links WHERE user_id=?', (id,))
        prefix = cursor.fetchall()[0][0]
    if prefix is None:
        text = 'Сейчас префикс не используется\n'
    else:
        text = 'Ваш текущий вид префикса: `' + prefix + '`\n'
    text += 'Вы можете изменить префикс, выбрав соответствующую кнопку'
    markup = choose_prefix_markup(str(prefix))
    bot.edit_message_text(chat_id=id, message_id=query.message.id, text=text, parse_mode='MarkdownV2', reply_markup=markup)


@bot.callback_query_handler(func=lambda f: f.data == 'view_users')
def view_users(query):
    data = (query.from_user.username, query.from_user.first_name, query.from_user.last_name, query.from_user.id)
    cursor.execute('UPDATE Users SET username=?, first_name=?, last_name=? WHERE telegram_id=?', data)
    connection.commit()
    markup = types.InlineKeyboardMarkup(row_width=1)
    cursor.execute('SELECT telegram_id, username, first_name, last_name, is_admin FROM Users')
    data = cursor.fetchall()
    text = 'Список пользователей:\n'
    for i in range(len(data)):
        id = data[i][0]
        name = str(data[i][2])
        if data[i][3] is not None:
            name += ' ' + data[i][3]
        if data[i][4]:
            name = '<b><i>' + name + '</i></b>'
        text += f'• {name}, id: <code>' + id + '</code>'
        if data[i][1] is not None:
            username = '@' + data[i][1]
            text += ', username: <code>' + username + '</code>'
        cursor.execute('SELECT key_id FROM Ownership WHERE user_id=?', (id,))
        keys = cursor.fetchall()
        keys_len = len(keys)
        if keys_len:
            text += ', ключи:'
            for i in range(len(keys)):
                text += ' <code>' + str(keys[i][0]) + '</code>'
                if i != keys_len - 1:
                    text += ','
        text += '\n'
    if len(data) > 1:
        button = types.InlineKeyboardButton(text='Удалить пользователя', callback_data='delete_user')
        markup.add(button)
    add_button = types.InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user')
    menu_button = types.InlineKeyboardButton(text='Вернуться в меню', callback_data='menu')
    markup.add(add_button, menu_button)
    id = query.from_user.id
    bot.delete_message(chat_id=id, message_id=query.message.id)
    chunk_size = 4096
    if len(text) <= chunk_size:
        bot.send_message(chat_id=id, text=text, parse_mode='HTML', reply_markup=markup, protect_content=True)
    else:
        new_text = split_string(text=text, chars_per_string=chunk_size)
        for i in range(len(new_text)-1):
            bot.send_message(chat_id=id, text=new_text[i], parse_mode='HTML', protect_content=True)
        bot.send_message(chat_id=id, text=new_text[-1], parse_mode='HTML', reply_markup=markup, protect_content=True)


# bot.infinity_polling()
bot.polling(non_stop=True)
connection.close()

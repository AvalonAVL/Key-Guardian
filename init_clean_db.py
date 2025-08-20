from sqlite3 import connect
from config import get_keys, get_service_info, create_dynamic_link, admin_id


connection = connect('storage.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute('PRAGMA foreign_keys = ON')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
telegram_id TEXT PRIMARY KEY NOT NULL,
username TEXT,
first_name TEXT,
last_name TEXT,
is_admin BOOL NOT NULL DEFAULT 0
)
''')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Keys (
internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
key_id TEXT,
server TEXT,
name TEXT,
password TEXT,
server_port TEXT,
method TEXT,
access_url TEXT
)
''')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Links (
internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT NOT NULL,
key_id INTEGER,
link TEXT,
prefix TEXT,
FOREIGN KEY (user_id) REFERENCES Users (telegram_id) ON DELETE CASCADE,
FOREIGN KEY (key_id) REFERENCES Keys (internal_id) ON DELETE CASCADE
)
''')
connection.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Ownership (
user_id TEXT,
key_id INTEGER,
PRIMARY KEY (user_id, key_id),
FOREIGN KEY (user_id) REFERENCES Users (telegram_id) ON DELETE CASCADE,
FOREIGN KEY (key_id) REFERENCES Keys (internal_id) ON DELETE CASCADE
)       
''')
connection.commit()

cursor.execute('INSERT INTO Users (telegram_id, is_admin) VALUES (?, ?)', (admin_id, 1))
cursor.execute('INSERT INTO Links (user_id, link) VALUES (?, ?)', (admin_id, create_dynamic_link(admin_id)))
connection.commit()

keys = get_keys()
server = get_service_info()['hostnameForAccessKeys']
key_req = 'INSERT INTO Keys (key_id, server, name, password, server_port, method, access_url) VALUES (?, ?, ?, ?, ?, ?, ?)'
for key in keys:
    key_data = (key.key_id, server, key.name, key.password, key.port, key.method, key.access_url)
    cursor.execute(key_req, key_data)
connection.commit()

cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()[0]
cursor.execute('SELECT * FROM Links')
links = cursor.fetchall()[0]
cursor.execute('SELECT * FROM Keys')
keys = cursor.fetchall()

print('База данных инициализирована с ADMIN_ID=', admin_id, sep='')
print('Таблица Users:\n', users)
print('Таблица Links:\n', links)
print('Таблица Keys:')
for i in range(len(keys)):
    print(keys[i])

cursor.close()
connection.close()

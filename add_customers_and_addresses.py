import sqlite3
from datetime import datetime

conn = sqlite3.connect('cafe.db')
cursor = conn.cursor()

# Додаємо декілька персон
persons = [
    ('Іван', 'Петренко', 'Іванович'),
    ('Олена', 'Коваль', 'Петрівна'),
    ('Сергій', 'Мельник', 'Сергійович'),
    ('Марія', 'Шевченко', 'Олександрівна'),
]

for first, last, patr in persons:
    cursor.execute("INSERT INTO person (FirstName, LastName, Patronymic) VALUES (?, ?, ?)", (first, last, patr))

# Додаємо декілька юнітів (квартир/приміщень)
units = [
    (1, 1, '101'),  # BuildingID, RoomTypeID, UnitNumber
    (1, 1, '102'),
    (1, 1, '103'),
    (1, 1, '104'),
]
for building_id, room_type_id, unit_number in units:
    cursor.execute("INSERT INTO unit (BuildingID, RoomTypeID, UnitNumber) VALUES (?, ?, ?)", (building_id, room_type_id, unit_number))

# Додаємо адреси
addresses = [
    (1, 'Квартира 1'),
    (2, 'Квартира 2'),
    (3, 'Квартира 3'),
    (4, 'Квартира 4'),
]
for unit_id, comment in addresses:
    cursor.execute("INSERT INTO address (UnitID, Comment) VALUES (?, ?)", (unit_id, comment))

# Додаємо клієнтів (PersonID має відповідати доданим person)
person_ids = [row[0] for row in cursor.execute('SELECT PersonID FROM person ORDER BY PersonID DESC LIMIT 4').fetchall()][::-1]
for person_id in person_ids:
    cursor.execute("INSERT INTO customer (PersonID, IsActive) VALUES (?, 1)", (person_id,))

conn.commit()
conn.close()
print('Клієнти та адреси додані.') 
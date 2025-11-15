import sqlite3

conn = sqlite3.connect('cafe.db')
cursor = conn.cursor()

# Додаємо типи вулиць
street_types = [
    ('вул.',),  # Вулиця
    ('просп.',),  # Проспект
    ('пл.',),  # Площа
    ('бул.',),  # Бульвар
]
for name in street_types:
    cursor.execute("INSERT INTO street_type (TypeName) VALUES (?)", name)

# Додаємо вулиці (StreetTypeID має відповідати доданим типам)
streets = [
    ('Шевченка', 1),
    ('Грушевського', 1),
    ('Перемоги', 2),
    ('Свободи', 3),
    ('Миру', 4),
]
for name, type_id in streets:
    cursor.execute("INSERT INTO street (StreetName, StreetTypeID) VALUES (?, ?)", (name, type_id))

conn.commit()
conn.close()
print('Типи вулиць та вулиці додані.') 
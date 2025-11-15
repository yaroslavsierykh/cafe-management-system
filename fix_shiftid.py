import sqlite3

conn = sqlite3.connect('cafe.db')
cursor = conn.cursor()

# Перевіряємо, чи є стовпець ShiftID
cursor.execute("PRAGMA table_info('order')")
columns = [row[1] for row in cursor.fetchall()]
if 'ShiftID' not in columns:
    cursor.execute("ALTER TABLE 'order' ADD COLUMN ShiftID INTEGER NOT NULL DEFAULT 1;")
    print("Стовпець ShiftID додано.")
else:
    print("Стовпець ShiftID вже існує.")

conn.commit()
conn.close() 
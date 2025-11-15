import sqlite3
from datetime import datetime, date

conn = sqlite3.connect('cafe.db')
cursor = conn.cursor()

# Додаємо постачальників
suppliers = [
    ('ТОВ "Продукти+"', 'Іван Іванович', '+380501234567', 'prodplus@email.com', 'м. Київ, вул. Шевченка, 1', '12345678', 1),
    ('ФОП Коваль', 'Олена Коваль', '+380671112233', 'koval@email.com', 'м. Київ, просп. Перемоги, 10', '87654321', 1),
]
for name, contact, phone, email, address, tax, active in suppliers:
    cursor.execute("INSERT INTO suppliers (CompanyName, ContactPerson, Phone, Email, Address, TaxNumber, IsActive, CreatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, contact, phone, email, address, tax, active, datetime.now()))

# Додаємо продукти
products = [
    ('Картопля', 1, 1, 'Свіжа картопля'),
    ('Молоко', 2, 1, 'Молоко 2.5%'),
    ('Яйце куряче', 3, 1, 'Яйце відбірне'),
    ('Олія соняшникова', 2, 1, 'Рафінована'),
]
for name, unit_id, is_avail, desc in products:
    cursor.execute("INSERT INTO product (ProductName, MeasurementUnitID, IsAvailable, Description) VALUES (?, ?, ?, ?)",
                   (name, unit_id, is_avail, desc))

# Додаємо контракти
contracts = [
    (1, 'C-2024-01', date(2024, 1, 1), date(2024, 12, 31), 'Поставка овочів', 'active', 50000, '30 днів', 'Доставка раз на тиждень'),
    (2, 'C-2024-02', date(2024, 2, 1), date(2024, 12, 31), 'Поставка молочних продуктів', 'active', 30000, '15 днів', 'Доставка двічі на місяць'),
]
for supplier_id, number, start, end, desc, status, value, pay, delivery in contracts:
    cursor.execute("INSERT INTO contracts (SupplierID, ContractNumber, StartDate, EndDate, Description, Status, TotalValue, PaymentTerms, DeliveryTerms, CreatedAt) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (supplier_id, number, start, end, desc, status, value, pay, delivery, datetime.now()))

# Додаємо поставки
deliveries = [
    (1, 1, datetime(2024, 3, 1, 10, 0), 'delivered', 12000, 'Поставка за березень'),
    (2, 2, datetime(2024, 3, 5, 11, 0), 'delivered', 8000, 'Поставка молока'),
]
for contract_id, supplier_id, ddate, status, total, notes in deliveries:
    cursor.execute("INSERT INTO deliveries (ContractID, SupplierID, DeliveryDate, Status, TotalAmount, Notes, CreatedAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (contract_id, supplier_id, ddate, status, total, notes, datetime.now()))

# Додаємо позиції поставок
items = [
    (1, 1, 100.0, 10.0, 1000.0, 'Картопля'),
    (1, 4, 50.0, 40.0, 2000.0, 'Олія'),
    (2, 2, 200.0, 20.0, 4000.0, 'Молоко'),
    (2, 3, 300.0, 10.0, 3000.0, 'Яйця'),
]
for delivery_id, product_id, qty, price, total, notes in items:
    cursor.execute("INSERT INTO delivery_items (DeliveryID, ProductID, Quantity, UnitPrice, TotalPrice, Notes) VALUES (?, ?, ?, ?, ?, ?)",
                   (delivery_id, product_id, qty, price, total, notes))

conn.commit()
conn.close()
print('Дані по постачальниках, продуктах, контрактах і поставках додано.') 
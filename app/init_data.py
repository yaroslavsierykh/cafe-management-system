from app import db
from app.models import (
    Person, Contact, Role, Employee, Hall, TableStatus, CafeTable, SeatStatus, Seat,
    MeasurementUnit, DishCategory, Dish, Product, DishIngredient, OrderStatus,
    OrderType, RoomType
)
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_sample_data():
    """Initialize the database with sample data"""
    
    # Add initial roles if they don't exist
    roles = ['Адміністратор', 'Бармен', 'Офіціант', 'Кухар']
    for role_name in roles:
        if not Role.query.filter_by(RoleName=role_name).first():
            role = Role(RoleName=role_name)
            db.session.add(role)
    
    # Add initial table statuses if they don't exist
    table_statuses = ['Вільний', 'Зайнятий', 'Резерв']
    for status_name in table_statuses:
        if not TableStatus.query.filter_by(StatusName=status_name).first():
            status = TableStatus(StatusName=status_name)
            db.session.add(status)
    
    # Add initial seat statuses if they don't exist
    seat_statuses = ['Вільне', 'Зайняте']
    for status_name in seat_statuses:
        if not SeatStatus.query.filter_by(StatusName=status_name).first():
            status = SeatStatus(StatusName=status_name)
            db.session.add(status)
    
    # Add initial order statuses if they don't exist
    order_statuses = ['Нове', 'Готується', 'Готове', 'Доставлено', 'Скасовано']
    for status_name in order_statuses:
        if not OrderStatus.query.filter_by(StatusName=status_name).first():
            status = OrderStatus(StatusName=status_name)
            db.session.add(status)
    
    # Add initial order types if they don't exist
    order_types = ['За столом', 'З собою', 'Доставка']
    for type_name in order_types:
        if not OrderType.query.filter_by(TypeName=type_name).first():
            order_type = OrderType(TypeName=type_name)
            db.session.add(order_type)
    
    # Add initial measurement units if they don't exist
    units = ['грам', 'мілілітр', 'штука', 'порція']
    for unit_name in units:
        if not MeasurementUnit.query.filter_by(UnitName=unit_name).first():
            unit = MeasurementUnit(UnitName=unit_name)
            db.session.add(unit)
    
    # Add initial room types if they don't exist
    room_types = ['Квартира', 'Офіс']
    for type_name in room_types:
        if not RoomType.query.filter_by(TypeName=type_name).first():
            room_type = RoomType(TypeName=type_name)
            db.session.add(room_type)
    
    db.session.commit()
    
    # Add test users if they don't exist
    test_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'Адміністратор',
            'first_name': 'Іван',
            'last_name': 'Петренко',
            'patronymic': 'Михайлович'
        },
        {
            'username': 'barman',
            'password': 'bar123',
            'role': 'Бармен',
            'first_name': 'Марія',
            'last_name': 'Коваленко',
            'patronymic': 'Олександрівна'
        },
        {
            'username': 'waiter',
            'password': 'waiter123',
            'role': 'Офіціант',
            'first_name': 'Олександр',
            'last_name': 'Сидоренко',
            'patronymic': 'Петрович'
        },
        {
            'username': 'cook',
            'password': 'cook123',
            'role': 'Кухар',
            'first_name': 'Тетяна',
            'last_name': 'Мельник',
            'patronymic': 'Василівна'
        }
    ]
    
    for user in test_users:
        if not Employee.query.filter_by(UserName=user['username']).first():
            # Create person
            person = Person(
                FirstName=user['first_name'],
                LastName=user['last_name'],
                Patronymic=user['patronymic']
            )
            db.session.add(person)
            db.session.flush()  # To get PersonID
            
            # Create employee
            role = Role.query.filter_by(RoleName=user['role']).first()
            employee = Employee(
                PersonID=person.PersonID,
                UserName=user['username'],
                RoleID=role.RoleID,
                IsActive=True
            )
            employee.set_password(user['password'])
            db.session.add(employee)
    
    # Add sample dish categories if they don't exist
    categories = [
        ('Гарячі напої', 'мілілітр'),
        ('Холодні напої', 'мілілітр'),
        ('Закуски', 'порція'),
        ('Салати', 'порція'),
        ('Перші страви', 'порція'),
        ('Основні страви', 'порція'),
        ('Гарніри', 'порція'),
        ('Десерти', 'порція')
    ]
    
    for cat_name, unit_name in categories:
        if not DishCategory.query.filter_by(CategoryName=cat_name).first():
            unit = MeasurementUnit.query.filter_by(UnitName=unit_name).first()
            category = DishCategory(
                CategoryName=cat_name,
                MeasurementUnitID=unit.UnitID
            )
            db.session.add(category)
    
    # Add sample products if they don't exist
    products = [
        ('Кава в зернах', 'грам'),
        ('Чай чорний', 'грам'),
        ('Молоко', 'мілілітр'),
        ('Цукор', 'грам'),
        ('Картопля', 'грам'),
        ('Морква', 'грам'),
        ('Цибуля', 'грам'),
        ('Томати', 'грам'),
        ('Огірки', 'грам'),
        ('Куряче філе', 'грам'),
        ('Свинина', 'грам'),
        ('Рис', 'грам'),
        ('Гречка', 'грам'),
        ('Олія соняшникова', 'мілілітр')
    ]
    
    for prod_name, unit_name in products:
        if not Product.query.filter_by(ProductName=prod_name).first():
            unit = MeasurementUnit.query.filter_by(UnitName=unit_name).first()
            product = Product(
                ProductName=prod_name,
                MeasurementUnitID=unit.UnitID,
                IsAvailable=True
            )
            db.session.add(product)
    
    # Add sample dishes if they don't exist
    dishes = [
        ('Еспресо', 'Гарячі напої', 35.00),
        ('Американо', 'Гарячі напої', 40.00),
        ('Капучино', 'Гарячі напої', 55.00),
        ('Лате', 'Гарячі напої', 60.00),
        ('Чай чорний', 'Гарячі напої', 30.00),
        ('Чай зелений', 'Гарячі напої', 30.00),
        ('Кока-кола', 'Холодні напої', 35.00),
        ('Спрайт', 'Холодні напої', 35.00),
        ('Фанта', 'Холодні напої', 35.00),
        ('Мінеральна вода', 'Холодні напої', 25.00),
        ('Картопля фрі', 'Закуски', 65.00),
        ('Нагетси', 'Закуски', 85.00),
        ('Грецький салат', 'Салати', 95.00),
        ('Цезар з куркою', 'Салати', 125.00),
        ('Борщ український', 'Перші страви', 85.00),
        ('Суп грибний', 'Перші страви', 75.00),
        ('Стейк зі свинини', 'Основні страви', 165.00),
        ('Куряче філе на грилі', 'Основні страви', 145.00),
        ('Картопляне пюре', 'Гарніри', 45.00),
        ('Рис з овочами', 'Гарніри', 55.00),
        ('Тірамісу', 'Десерти', 85.00),
        ('Чізкейк', 'Десерти', 95.00)
    ]
    
    for dish_name, category_name, price in dishes:
        if not Dish.query.filter_by(DishName=dish_name, ValidTo=None).first():
            category = DishCategory.query.filter_by(CategoryName=category_name).first()
            dish = Dish(
                DishName=dish_name,
                CategoryID=category.CategoryID,
                Price=price,
                IsAvailable=True,
                ValidFrom=datetime.now()
            )
            db.session.add(dish)
    
    db.session.commit()

    print("Sample data has been initialized successfully!") 
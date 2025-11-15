from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .contracts import Supplier, Contract, Delivery, DeliveryItem

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))

def init_db():
    """Initialize database schema"""
    db.create_all()

class Person(db.Model):
    __tablename__ = 'person'
    PersonID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Patronymic = db.Column(db.String(50))
    contacts = db.relationship('Contact', backref='person', lazy=True)
    employees = db.relationship('Employee', backref='person', lazy=True)

    @property
    def FullName(self):
        parts = [self.LastName, self.FirstName, self.Patronymic]
        return ' '.join([p for p in parts if p])

class Contact(db.Model):
    __tablename__ = 'contact'
    ContactID = db.Column(db.Integer, primary_key=True)
    PersonID = db.Column(db.Integer, db.ForeignKey('person.PersonID'), nullable=False)
    ContactType = db.Column(db.String(10), nullable=False)  # Phone, Email
    ContactValue = db.Column(db.String(100), nullable=False)

class Role(db.Model):
    __tablename__ = 'role'
    RoleID = db.Column(db.Integer, primary_key=True)
    RoleName = db.Column(db.String(50), nullable=False)
    employees = db.relationship('Employee', backref='role', lazy=True)

class Employee(db.Model, UserMixin):
    __tablename__ = 'employee'
    EmployeeID = db.Column(db.Integer, primary_key=True)
    PersonID = db.Column(db.Integer, db.ForeignKey('person.PersonID'), nullable=False)
    UserName = db.Column(db.String(50), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(64), nullable=False)
    RoleID = db.Column(db.Integer, db.ForeignKey('role.RoleID'), nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    shifts = db.relationship('Shift', backref='employee', lazy=True)

    def get_id(self):
        return str(self.EmployeeID)

    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)

    @property
    def current_shift(self):
        """Get the current open shift for this employee"""
        return Shift.query.filter_by(
            EmployeeID=self.EmployeeID,
            CloseDateTime=None
        ).first()

class Shift(db.Model):
    __tablename__ = 'shift'
    ShiftID = db.Column(db.Integer, primary_key=True)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('employee.EmployeeID'), nullable=False)
    OpenDateTime = db.Column(db.DateTime, nullable=False)
    CloseDateTime = db.Column(db.DateTime)
    TotalRevenue = db.Column(db.Numeric(12, 2))
    TotalDishesSold = db.Column(db.Integer)
    Notes = db.Column(db.String(250))
    orders = db.relationship('Order', backref='shift', lazy=True)

class Hall(db.Model):
    __tablename__ = 'hall'
    HallID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    Notes = db.Column(db.String(250))
    tables = db.relationship('CafeTable', backref='hall', lazy=True)

class TableStatus(db.Model):
    __tablename__ = 'table_status'
    TableStatusID = db.Column(db.Integer, primary_key=True)
    StatusName = db.Column(db.String(20), nullable=False)
    tables = db.relationship('CafeTable', backref='status', lazy=True)

class CafeTable(db.Model):
    __tablename__ = 'cafe_table'
    TableID = db.Column(db.Integer, primary_key=True)
    TableName = db.Column(db.String(20), nullable=False)
    HallID = db.Column(db.Integer, db.ForeignKey('hall.HallID'), nullable=False)
    TableStatusID = db.Column(db.Integer, db.ForeignKey('table_status.TableStatusID'), nullable=False)
    SeatsCount = db.Column(db.Integer, nullable=False)
    seats = db.relationship('Seat', backref='table', lazy=True)
    orders = db.relationship('Order', backref='table', lazy=True)

class SeatStatus(db.Model):
    __tablename__ = 'seat_status'
    SeatStatusID = db.Column(db.Integer, primary_key=True)
    StatusName = db.Column(db.String(20), nullable=False)
    seats = db.relationship('Seat', backref='status', lazy=True)

class Seat(db.Model):
    __tablename__ = 'seat'
    SeatID = db.Column(db.Integer, primary_key=True)
    TableID = db.Column(db.Integer, db.ForeignKey('cafe_table.TableID'), nullable=False)
    SeatNumber = db.Column(db.Integer, nullable=False)
    SeatStatusID = db.Column(db.Integer, db.ForeignKey('seat_status.SeatStatusID'), nullable=False)

class MeasurementUnit(db.Model):
    __tablename__ = 'measurement_unit'
    UnitID = db.Column(db.Integer, primary_key=True)
    UnitName = db.Column(db.String(20), nullable=False)

class DishCategory(db.Model):
    __tablename__ = 'dish_category'
    CategoryID = db.Column(db.Integer, primary_key=True)
    CategoryName = db.Column(db.String(50), nullable=False)
    MeasurementUnitID = db.Column(db.Integer, db.ForeignKey('measurement_unit.UnitID'), nullable=False)
    measurement_unit = db.relationship('MeasurementUnit', backref='categories', lazy=True)
    dishes = db.relationship('Dish', backref='category', lazy=True)

class Dish(db.Model):
    __tablename__ = 'dish'
    DishID = db.Column(db.Integer, primary_key=True)
    DishName = db.Column(db.String(100), nullable=False)
    CategoryID = db.Column(db.Integer, db.ForeignKey('dish_category.CategoryID'), nullable=False)
    Price = db.Column(db.Numeric(10, 2), nullable=False)
    Description = db.Column(db.String(250))
    IsAvailable = db.Column(db.Boolean, nullable=False, default=True)
    ValidFrom = db.Column(db.DateTime, nullable=False)
    ValidTo = db.Column(db.DateTime)
    ingredients = db.relationship('DishIngredient', backref='dish', lazy=True)
    order_dishes = db.relationship('OrderDish', backref='dish', lazy=True)

class Product(db.Model):
    __tablename__ = 'product'
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName = db.Column(db.String(100), nullable=False)
    MeasurementUnitID = db.Column(db.Integer, db.ForeignKey('measurement_unit.UnitID'), nullable=False)
    IsAvailable = db.Column(db.Boolean, nullable=False, default=True)
    Description = db.Column(db.String(250))
    Quantity = db.Column(db.Numeric(10, 3), nullable=False, default=0)
    measurement_unit = db.relationship('MeasurementUnit', backref='products', lazy=True)

class DishIngredient(db.Model):
    __tablename__ = 'dish_ingredient'
    DishIngredientID = db.Column(db.Integer, primary_key=True)
    DishID = db.Column(db.Integer, db.ForeignKey('dish.DishID'), nullable=False)
    ProductID = db.Column(db.Integer, db.ForeignKey('product.ProductID'), nullable=False)
    Quantity = db.Column(db.Numeric(10, 3), nullable=False)
    product = db.relationship('Product', backref='dish_ingredients', lazy=True)

class OrderStatus(db.Model):
    __tablename__ = 'order_status'
    OrderStatusID = db.Column(db.Integer, primary_key=True)
    StatusName = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='status', lazy=True)

class OrderType(db.Model):
    __tablename__ = 'order_type'
    OrderTypeID = db.Column(db.Integer, primary_key=True)
    TypeName = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='type', lazy=True)

class Order(db.Model):
    __tablename__ = 'order'
    OrderID = db.Column(db.Integer, primary_key=True)
    OrderDateTime = db.Column(db.DateTime, nullable=False, default=datetime.now)
    TableID = db.Column(db.Integer, db.ForeignKey('cafe_table.TableID'))
    EmployeeID = db.Column(db.Integer, db.ForeignKey('employee.EmployeeID'), nullable=False)
    OrderStatusID = db.Column(db.Integer, db.ForeignKey('order_status.OrderStatusID'), nullable=False)
    OrderTypeID = db.Column(db.Integer, db.ForeignKey('order_type.OrderTypeID'), nullable=False)
    AddressID = db.Column(db.Integer, db.ForeignKey('address.AddressID'))
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'))
    PaymentMethodID = db.Column(db.Integer, db.ForeignKey('payment_method.PaymentMethodID'))
    TotalAmount = db.Column(db.Numeric(10, 2), nullable=False)
    Notes = db.Column(db.String(250))
    PaidDateTime = db.Column(db.DateTime)
    ShiftID = db.Column(db.Integer, db.ForeignKey('shift.ShiftID'), nullable=False, default=1)
    dishes = db.relationship('OrderDish', backref='order', lazy=True)

class OrderDish(db.Model):
    __tablename__ = 'order_dish'
    OrderDishID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('order.OrderID'), nullable=False)
    DishID = db.Column(db.Integer, db.ForeignKey('dish.DishID'), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    PriceAtTime = db.Column(db.Numeric(10, 2), nullable=False)
    Notes = db.Column(db.String(250))

class StreetType(db.Model):
    __tablename__ = 'street_type'
    StreetTypeID = db.Column(db.Integer, primary_key=True)
    TypeName = db.Column(db.String(20), nullable=False)
    streets = db.relationship('Street', backref='type', lazy=True)

class Street(db.Model):
    __tablename__ = 'street'
    StreetID = db.Column(db.Integer, primary_key=True)
    StreetName = db.Column(db.String(100), nullable=False)
    StreetTypeID = db.Column(db.Integer, db.ForeignKey('street_type.StreetTypeID'), nullable=False)
    buildings = db.relationship('Building', backref='street', lazy=True)

class Building(db.Model):
    __tablename__ = 'building'
    BuildingID = db.Column(db.Integer, primary_key=True)
    BuildingNumber = db.Column(db.String(10), nullable=False)
    StreetID = db.Column(db.Integer, db.ForeignKey('street.StreetID'), nullable=False)
    units = db.relationship('Unit', backref='building', lazy=True)

class RoomType(db.Model):
    __tablename__ = 'room_type'
    RoomTypeID = db.Column(db.Integer, primary_key=True)
    TypeName = db.Column(db.String(20), nullable=False)
    units = db.relationship('Unit', backref='room_type', lazy=True)

class Unit(db.Model):
    __tablename__ = 'unit'
    UnitID = db.Column(db.Integer, primary_key=True)
    BuildingID = db.Column(db.Integer, db.ForeignKey('building.BuildingID'), nullable=False)
    RoomTypeID = db.Column(db.Integer, db.ForeignKey('room_type.RoomTypeID'), nullable=False)
    UnitNumber = db.Column(db.String(10), nullable=False)
    addresses = db.relationship('Address', backref='unit', lazy=True)

class Address(db.Model):
    __tablename__ = 'address'
    AddressID = db.Column(db.Integer, primary_key=True)
    UnitID = db.Column(db.Integer, db.ForeignKey('unit.UnitID'))
    Comment = db.Column(db.String(250))
    orders = db.relationship('Order', backref='address', lazy=True)

class PaymentMethod(db.Model):
    __tablename__ = 'payment_method'
    PaymentMethodID = db.Column(db.Integer, primary_key=True)
    MethodName = db.Column(db.String(50), nullable=False)
    orders = db.relationship('Order', backref='payment_method', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customer'
    CustomerID = db.Column(db.Integer, primary_key=True)
    PersonID = db.Column(db.Integer, db.ForeignKey('person.PersonID'), nullable=False)
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    person = db.relationship('Person', backref='customers', lazy=True)

class Payment(db.Model):
    __tablename__ = 'payment'
    PaymentID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('order.OrderID'), nullable=False)
    PaymentMethodID = db.Column(db.Integer, db.ForeignKey('payment_method.PaymentMethodID'), nullable=False)
    Amount = db.Column(db.Numeric(12, 2), nullable=False)
    PaymentDateTime = db.Column(db.DateTime, nullable=False)

    order = db.relationship('Order', backref='payments', lazy=True)
    payment_method = db.relationship('PaymentMethod', backref='payments', lazy=True) 
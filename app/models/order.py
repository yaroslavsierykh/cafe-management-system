from app import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    OrderID = db.Column(db.Integer, primary_key=True)
    TableID = db.Column(db.Integer, db.ForeignKey('cafe_table.TableID'))
    EmployeeID = db.Column(db.Integer, db.ForeignKey('employee.EmployeeID'), nullable=False)
    ShiftID = db.Column(db.Integer, db.ForeignKey('shift.ShiftID'), nullable=False)
    OrderDateTime = db.Column(db.DateTime, default=datetime.utcnow)
    OrderStatusID = db.Column(db.Integer, db.ForeignKey('order_status.OrderStatusID'), nullable=False)
    OrderTypeID = db.Column(db.Integer, db.ForeignKey('order_type.OrderTypeID'), nullable=False)
    CustomerID = db.Column(db.Integer, db.ForeignKey('customer.CustomerID'))
    AddressID = db.Column(db.Integer, db.ForeignKey('address.AddressID'))
    PaymentMethodID = db.Column(db.Integer, db.ForeignKey('payment_method.PaymentMethodID'))
    TotalAmount = db.Column(db.Numeric(10, 2), default=0)
    Notes = db.Column(db.Text)
    PaidDateTime = db.Column(db.DateTime)
    
    # Relationships
    table = db.relationship('CafeTable', backref='orders', lazy=True)
    employee = db.relationship('Employee', backref='orders', lazy=True)
    shift = db.relationship('Shift', backref='orders', lazy=True)
    status = db.relationship('OrderStatus', backref='orders', lazy=True)
    type = db.relationship('OrderType', backref='orders', lazy=True)
    customer = db.relationship('Customer', backref='orders', lazy=True)
    address = db.relationship('Address', backref='orders', lazy=True)
    payment_method = db.relationship('PaymentMethod', backref='orders', lazy=True)
    dishes = db.relationship('OrderDish', backref='order', lazy=True)

class OrderDish(db.Model):
    __tablename__ = 'order_dish'
    
    OrderDishID = db.Column(db.Integer, primary_key=True)
    OrderID = db.Column(db.Integer, db.ForeignKey('orders.OrderID'), nullable=False)
    DishID = db.Column(db.Integer, db.ForeignKey('dish.DishID'), nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)
    PriceAtTime = db.Column(db.Numeric(10, 2), nullable=False)
    Notes = db.Column(db.Text)
    
    # Relationships
    dish = db.relationship('Dish', backref='order_dishes', lazy=True) 
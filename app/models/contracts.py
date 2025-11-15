from app import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'supplier'
    
    SupplierID = db.Column(db.Integer, primary_key=True)
    SupplierType = db.Column(db.String(10), nullable=False)  # 'FOP' або 'TOV'
    CompanyName = db.Column(db.String(100), nullable=False)
    ContactPerson = db.Column(db.String(100))
    Phone = db.Column(db.String(20))
    Email = db.Column(db.String(100))
    Address = db.Column(db.String(200))
    TaxNumber = db.Column(db.String(20))
    
    # Поля для ФОП
    FOPNumber = db.Column(db.String(20))  # Номер свідоцтва ФОП
    FOPRegistrationDate = db.Column(db.Date)  # Дата реєстрації ФОП
    
    # Поля для ТОВ
    EDRPOU = db.Column(db.String(10))  # Код ЄДРПОУ
    LegalForm = db.Column(db.String(50))  # Організаційно-правова форма
    DirectorName = db.Column(db.String(100))  # ПІБ директора
    
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contracts = db.relationship('Contract', backref='supplier', lazy=True)
    deliveries = db.relationship('Delivery', backref='supplier', lazy=True)

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    ContractID = db.Column(db.Integer, primary_key=True)
    SupplierID = db.Column(db.Integer, db.ForeignKey('supplier.SupplierID'), nullable=False)
    ContractNumber = db.Column(db.String(50), nullable=False, unique=True)
    StartDate = db.Column(db.Date, nullable=False)
    EndDate = db.Column(db.Date)
    Description = db.Column(db.Text)
    Status = db.Column(db.String(20), default='active')  # active, expired, terminated
    TotalValue = db.Column(db.Numeric(10, 2))
    PaymentTerms = db.Column(db.String(200))
    DeliveryTerms = db.Column(db.String(200))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    deliveries = db.relationship('Delivery', backref='contract', lazy=True)

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    DeliveryID = db.Column(db.Integer, primary_key=True)
    ContractID = db.Column(db.Integer, db.ForeignKey('contracts.ContractID'), nullable=False)
    SupplierID = db.Column(db.Integer, db.ForeignKey('supplier.SupplierID'), nullable=False)
    DeliveryDate = db.Column(db.DateTime, nullable=False)
    Status = db.Column(db.String(20), default='pending')  # pending, delivered, rejected
    TotalAmount = db.Column(db.Numeric(10, 2))
    Notes = db.Column(db.Text)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('DeliveryItem', backref='delivery', lazy=True)

class DeliveryItem(db.Model):
    __tablename__ = 'delivery_items'
    
    DeliveryItemID = db.Column(db.Integer, primary_key=True)
    DeliveryID = db.Column(db.Integer, db.ForeignKey('deliveries.DeliveryID'), nullable=False)
    ProductID = db.Column(db.Integer, db.ForeignKey('product.ProductID'), nullable=False)
    Quantity = db.Column(db.Numeric(10, 3), nullable=False)
    UnitPrice = db.Column(db.Numeric(10, 2), nullable=False)
    TotalPrice = db.Column(db.Numeric(10, 2), nullable=False)
    Notes = db.Column(db.Text)
    
    # Relationships
    product = db.relationship('Product', backref='delivery_items', lazy=True) 
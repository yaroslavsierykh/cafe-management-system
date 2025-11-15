from app import db
from datetime import datetime

class Hall(db.Model):
    __tablename__ = 'halls'
    
    HallID = db.Column(db.Integer, primary_key=True)
    HallName = db.Column(db.String(50), nullable=False)
    Description = db.Column(db.String(200))
    IsActive = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tables = db.relationship('Table', backref='hall', lazy=True)

class Table(db.Model):
    __tablename__ = 'tables'
    
    TableID = db.Column(db.Integer, primary_key=True)
    HallID = db.Column(db.Integer, db.ForeignKey('halls.HallID'), nullable=False)
    TableNumber = db.Column(db.String(10), nullable=False)
    Capacity = db.Column(db.Integer, nullable=False)
    IsActive = db.Column(db.Boolean, default=True)
    Status = db.Column(db.String(20), default='available')  # available, occupied, reserved
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='table', lazy=True) 
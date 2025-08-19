from .db import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    is_budgeted = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Category {self.name}>'

class PaymentType(db.Model):
    __tablename__ = 'payment_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PaymentType {self.name}>'

class Expense(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    name = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_types.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref=db.backref('expenses', lazy=True))
    payment_type = db.relationship('PaymentType', backref=db.backref('expenses', lazy=True))

    def __repr__(self):
        return f'<Expense {self.name}>'

# models.py

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'RETAIL_CUSTOMERS'
    
    recid = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(100), nullable=False)
    sms_d_1 = db.Column(db.String(20), nullable=True)
    email_d_1 = db.Column(db.String(100), nullable=True)
    customer_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1)  # 1=Not Yet, 2=Sent, 3=Failed

    def __repr__(self):
        return f"<Customer {self.short_name}>"

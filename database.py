from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    agm = db.Column(db.Float, nullable=True, default= 0.0) # new column for agm
    dp = db.Column(db.Float, nullable=False)
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) # Hashed Password
    phone = db.Column(db.String(15),unique = True,  nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    role = db.Column(db.Enum('owner', 'employee'), nullable=False)
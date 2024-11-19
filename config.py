# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kazaneza')  # Replace with a strong secret key in production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///customers.db'  # Using SQLite for simplicity; switch to PostgreSQL/MySQL for production
    SQLALCHEMY_TRACK_MODIFICATIONS = False

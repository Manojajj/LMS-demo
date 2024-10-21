import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///your_database.db')  # Replace with your DB URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

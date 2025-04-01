import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_KEY = os.getenv("JWT_KEY")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOD_ROUTE = os.getenv("GOD_ROUTE")

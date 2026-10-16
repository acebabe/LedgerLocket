import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ledgerlocket.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    JWT_SECRET = os.getenv('JWT_SECRET', 'jwt-secret')
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    PLAYWRIGHT_BROWSERS_PATH = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/ms-playwright')
    PLAYWRIGHT_HEADLESS = os.getenv('PLAYWRIGHT_HEADLESS', '1')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp')
    # Add more config as needed

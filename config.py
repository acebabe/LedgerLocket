import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///./ledgerlocket.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Web3 / wallet settings
    WEB3_PROVIDER_URL = os.getenv('WEB3_PROVIDER_URL')
    WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
    TEST_API_KEY = os.getenv('TEST_API_KEY', 'change_me')
    ALLOWED_CHAIN_IDS = [int(x.strip()) for x in os.getenv('ALLOWED_CHAIN_IDS', '11155111').split(',') if x.strip()]
    DEFAULT_CHAIN_ID = int(os.getenv('DEFAULT_CHAIN_ID', '11155111'))
    TEST_MAX_AMOUNT_ETHER = float(os.getenv('TEST_MAX_AMOUNT_ETHER', '0.1'))
    GAS_PRICE_GWEI = float(os.getenv('GAS_PRICE_GWEI', '20'))
    BROADCAST_TX = os.getenv('BROADCAST_TX', 'false').lower() in ('1','true','yes')

    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() in ('1','true')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@ledgerlocket.test')

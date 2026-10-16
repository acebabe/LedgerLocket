import os
from cryptography.fernet import Fernet

_DEFAULT_KEY = os.getenv("LOCAL_MASTER_KEY") or Fernet.generate_key().decode()
FERNET = Fernet(_DEFAULT_KEY.encode())


def encrypt_text(plaintext: str) -> str:
    return FERNET.encrypt(plaintext.encode()).decode()


def decrypt_text(ciphertext: str) -> str:
    return FERNET.decrypt(ciphertext.encode()).decode()

import os
import base64
from cryptography.fernet import Fernet

# AWS KMS envelope encryption when AWS_KMS_KEY_ID is configured
AWS_KMS_KEY_ID = os.getenv("AWS_KMS_KEY_ID")

if AWS_KMS_KEY_ID:
    import boto3
    kms = boto3.client('kms')

LOCAL_MASTER_KEY = os.getenv("LOCAL_MASTER_KEY")


def _local_fernet():
    key = LOCAL_MASTER_KEY
    if not key:
        # generate a key but DO NOT commit it; in dev this is OK but in prod use KMS
        key = Fernet.generate_key().decode()
    return Fernet(key.encode())


def encrypt_text(plaintext: str) -> str:
    if AWS_KMS_KEY_ID:
        # Envelope: generate data key, encrypt data with it, and store encrypted data key + ciphertext
        resp = kms.generate_data_key(KeyId=AWS_KMS_KEY_ID, KeySpec='AES_256')
        plaintext_key = resp['Plaintext']  # bytes
        encrypted_key = resp['CiphertextBlob']  # bytes
        # use plaintext_key as a Fernet key (needs 32 url-safe base64 bytes)
        fernet_key = base64.urlsafe_b64encode(plaintext_key)
        f = Fernet(fernet_key)
        ciphertext = f.encrypt(plaintext.encode())
        return base64.b64encode(encrypted_key).decode() + '::' + ciphertext.decode()
    else:
        f = _local_fernet()
        return f.encrypt(plaintext.encode()).decode()


def decrypt_text(token: str) -> str:
    if AWS_KMS_KEY_ID and '::' in token:
        enc_key_b64, ciphertext = token.split('::', 1)
        encrypted_key = base64.b64decode(enc_key_b64)
        resp = kms.decrypt(CiphertextBlob=encrypted_key)
        plaintext_key = resp['Plaintext']
        fernet_key = base64.urlsafe_b64encode(plaintext_key)
        f = Fernet(fernet_key)
        return f.decrypt(ciphertext.encode()).decode()
    else:
        f = _local_fernet()
        return f.decrypt(token.encode()).decode()

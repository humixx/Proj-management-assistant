"""Encryption utilities for storing sensitive data like API keys."""
import base64
import hashlib

from cryptography.fernet import Fernet

from app.config import settings


def _derive_key() -> bytes:
    """Derive a Fernet-compatible key from JWT_SECRET_KEY."""
    raw = settings.JWT_SECRET_KEY.encode()
    digest = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_derive_key())


def encrypt_api_key(plain_key: str) -> str:
    """Encrypt an API key for database storage."""
    return _fernet.encrypt(plain_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from database storage."""
    return _fernet.decrypt(encrypted_key.encode()).decode()

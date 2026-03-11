"""Encryption utilities for sensitive data like API keys."""
import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings


def get_cipher() -> Fernet:
    """Get or create a Fernet cipher instance.
    
    Uses a key derived from the ENCRYPTION_KEY setting.
    """
    encryption_key = settings.ENCRYPTION_KEY
    if not encryption_key:
        # Generate a new key if not configured (for development)
        # In production, this should always be set via environment variable
        return None
    
    # Derive a 32-byte key for Fernet using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"project_management_salt",  # In production, use a unique salt per installation
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
    return Fernet(key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key.
    
    Args:
        api_key: The plain text API key to encrypt
        
    Returns:
        Base64 encoded encrypted string
    """
    if not api_key:
        return api_key
    
    cipher = get_cipher()
    if cipher is None:
        # If no encryption key configured, return as-is (development mode)
        return api_key
    
    encrypted = cipher.encrypt(api_key.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key.
    
    Args:
        encrypted_key: The encrypted API key to decrypt
        
    Returns:
        Plain text API key
    """
    if not encrypted_key:
        return encrypted_key
    
    cipher = get_cipher()
    if cipher is None:
        # If no encryption key configured, return as-is (development mode)
        return encrypted_key
    
    try:
        decoded = base64.urlsafe_b64decode(encrypted_key.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        # If decryption fails, assume it's a non-encrypted key (backward compatibility)
        return encrypted_key

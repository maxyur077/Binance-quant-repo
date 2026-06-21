from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from app.settings import get_settings

_HKDF_INFO = b"azalyst-broker-key-v1"
_NONCE_SIZE = 12


def _derive_key() -> bytes | None:
    raw = get_settings().ENCRYPTION_KEY
    if not raw:
        return None
    key_bytes = raw.encode() if isinstance(raw, str) else raw
    return HKDF(
        algorithm=SHA256(),
        length=32,
        salt=None,
        info=_HKDF_INFO,
    ).derive(key_bytes)


def encrypt(plaintext: str) -> str:
    key = _derive_key()
    if key is None:
        return plaintext
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.urlsafe_b64encode(nonce + ciphertext).decode()


def decrypt(token: str) -> str:
    key = _derive_key()
    if key is None:
        return token
    raw = base64.urlsafe_b64decode(token)
    nonce = raw[:_NONCE_SIZE]
    ciphertext = raw[_NONCE_SIZE:]
    return AESGCM(key).decrypt(nonce, ciphertext, None).decode()

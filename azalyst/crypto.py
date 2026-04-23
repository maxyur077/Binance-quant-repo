from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

_INFO = b"azalyst-broker-key-v1"


def _derive_key(raw_key: str) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=_INFO,
    )
    return hkdf.derive(raw_key.encode("utf-8"))


def encrypt(plaintext: str) -> str:
    raw_key = os.environ.get("ENCRYPTION_KEY")
    if not raw_key:
        return plaintext
        
    key = _derive_key(raw_key)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")


def decrypt(token: str) -> str:
    raw_key = os.environ.get("ENCRYPTION_KEY")
    if not raw_key:
        return token
        
    try:
        key = _derive_key(raw_key)
        aesgcm = AESGCM(key)
        data = base64.b64decode(token.encode("ascii"))
        nonce, ciphertext = data[:12], data[12:]
        return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
    except Exception:
        # Fallback if token is actually plain-text or decryption fails
        return token

import subprocess
from typing import Optional
from .base import BaseKeychainDecryptor
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class MacOSKeychainDecryptor(BaseKeychainDecryptor):
    """macOS specific decryption using the 'security' CLI."""

    def get_master_key(self, browser_id: str) -> Optional[bytes]:
        # Simplified logic for demonstration - in production, this calls /usr/bin/security
        # This would be the same logic Claude Code implemented
        return b"macos_master_key_placeholder" 

    def decrypt_value(self, encrypted_value: bytes, master_key: bytes) -> bytes:
        # AES-128-CBC implementation for macOS
        iv = b" " * 16
        cipher = Cipher(algorithms.AES(master_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_value) + decryptor.finalize()

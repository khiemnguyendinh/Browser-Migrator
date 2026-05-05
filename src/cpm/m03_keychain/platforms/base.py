from abc import ABC, abstractmethod
from typing import Optional

class BaseKeychainDecryptor(ABC):
    """Abstract base class for keychain decryption across platforms."""
    
    @abstractmethod
    def get_master_key(self, browser_id: str) -> Optional[bytes]:
        """Retrieve the master encryption key for a specific browser."""
        pass

    @abstractmethod
    def decrypt_value(self, encrypted_value: bytes, master_key: bytes) -> bytes:
        """Decrypt a value using the provided master key."""
        pass

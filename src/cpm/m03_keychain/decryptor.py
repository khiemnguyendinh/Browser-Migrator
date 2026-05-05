from cpm.core.platform import CURRENT_PLATFORM, Platform
from .platforms.macos import MacOSKeychainDecryptor
from .platforms.windows import WindowsKeychainDecryptor

class KeychainDecryptor:
    """M03 - Factory for Platform-specific Keychain Decryptors."""
    
    _instance = None

    @classmethod
    def get_decryptor(cls):
        if cls._instance is None:
            if CURRENT_PLATFORM == Platform.MACOS:
                cls._instance = MacOSKeychainDecryptor()
            elif CURRENT_PLATFORM == Platform.WINDOWS:
                cls._instance = WindowsKeychainDecryptor()
            else:
                raise RuntimeError(f"Unsupported platform for decryption: {CURRENT_PLATFORM}")
        return cls._instance

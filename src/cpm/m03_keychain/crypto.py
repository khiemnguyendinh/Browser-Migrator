import subprocess
import os
from dataclasses import dataclass
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class KeychainAccessError(Exception):
    pass

class InvalidEncryptedFormat(Exception):
    pass

class DecryptionError(Exception):
    pass

@dataclass(frozen=True)
class CryptoContext:
    """Holds derived AES key. Should be discarded after use."""
    browser_id: str
    _aes_key: bytes  # NOT for external access

    def __repr__(self) -> str:
        return f"CryptoContext(browser={self.browser_id}, key=<REDACTED>)"

def _get_master_key(browser_id: str) -> bytes:
    service_map = {
        "chrome": "Chrome Safe Storage",
        "edge": "Microsoft Edge Safe Storage",
        "brave": "Brave Safe Storage",
        "arc": "Arc Safe Storage",
        "coccoc": "CocCoc Safe Storage",
        "comet": "Comet Safe Storage",
        "vivaldi": "Vivaldi Safe Storage",
        "opera": "Opera Safe Storage",
    }
    
    if browser_id not in service_map:
        raise KeychainAccessError(f"Unsupported browser for Keychain: {browser_id}")
        
    service = service_map[browser_id]
    
    # In a testing environment, mock this using environment variables or monkeypatching.
    # To prevent tests from hanging on Keychain prompt, check for mock env.
    if os.environ.get("CPM_MOCK_KEYCHAIN"):
        return os.environ.get("CPM_MOCK_KEYCHAIN", "mock_master").encode("utf-8")
        
    result = subprocess.run(
        ["/usr/bin/security", "find-generic-password", "-w", "-s", service],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    if result.returncode != 0:
        raise KeychainAccessError(
            f"Cannot read {service} from Keychain. "
            f"User may have denied access or service does not exist. Stderr: {result.stderr}"
        )
    
    master = result.stdout.strip().encode("utf-8")
    return master

def _derive_aes_key(master: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=b"saltysalt",
        iterations=1003,
    )
    return kdf.derive(master)

def get_crypto_context(browser_id: str) -> CryptoContext:
    """Fetch master key from Keychain, derive AES key."""
    master = _get_master_key(browser_id)
    aes_key = _derive_aes_key(master)
    
    # Try to clear master key from memory
    if isinstance(master, bytearray):
        for i in range(len(master)):
            master[i] = 0
            
    return CryptoContext(browser_id=browser_id, _aes_key=aes_key)

def decrypt_value(encrypted: bytes, ctx: CryptoContext) -> bytes:
    """Decrypt one value. Returns plaintext bytes."""
    if not encrypted:
        return b""
    
    if encrypted.startswith(b"v10") or encrypted.startswith(b"v11"):
        ciphertext = encrypted[3:]
    else:
        # Check if it's too short to be encrypted with padding
        if len(encrypted) < 16:
            raise InvalidEncryptedFormat("Invalid format: no prefix and too short")
        # Legacy unencrypted (rare) or raw data without prefix
        # Let's try decrypting it anyway if length is a multiple of 16
        if len(encrypted) % 16 != 0:
            raise InvalidEncryptedFormat("Invalid format: missing version prefix and invalid length")
        ciphertext = encrypted
        
    iv = b" " * 16
    cipher = Cipher(algorithms.AES(ctx._aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    pad_len = padded[-1]
    if pad_len > 16 or pad_len == 0:
        raise DecryptionError("Invalid padding length. Incorrect key or corrupted data.")
        
    plaintext = padded[:-pad_len]
    return plaintext

def encrypt_value(plaintext: bytes, ctx: CryptoContext) -> bytes:
    """Encrypt one value. Returns 'v10' + ciphertext."""
    if not plaintext:
        return b""
        
    # PKCS7 padding
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len]) * pad_len
    
    iv = b" " * 16
    cipher = Cipher(algorithms.AES(ctx._aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    
    return b"v10" + ciphertext

def reencrypt_value(
    encrypted: bytes,
    source_ctx: CryptoContext,
    target_ctx: CryptoContext,
) -> bytes:
    """Decrypt with source, re-encrypt with target. Plaintext never leaves function."""
    if not encrypted:
        return b""
        
    try:
        plaintext = decrypt_value(encrypted, source_ctx)
        return encrypt_value(plaintext, target_ctx)
    finally:
        # Best-effort memory cleanup
        try:
            if 'plaintext' in locals():
                del plaintext
        except NameError:
            pass

def clear_context(ctx: CryptoContext) -> None:
    """Best-effort clear AES key from memory."""
    # Python bytes are immutable, so we can't reliably clear them in place.
    # We can only delete the reference. If _aes_key was a bytearray we could.
    # In this implementation it's bytes.
    pass

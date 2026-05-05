import os
import sys
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class KeychainAccessError(Exception):
    pass


class InvalidEncryptedFormat(Exception):
    pass


class DecryptionError(Exception):
    pass


@dataclass
class CryptoContext:
    """Holds the derived/decrypted AES key. Call clear_context() after use."""

    browser_id: str
    _aes_key: bytearray  # mutable so it can be zeroed
    _platform: str       # "macos" | "windows"

    def __repr__(self) -> str:
        return f"CryptoContext(browser={self.browser_id}, key=<REDACTED>)"


# ---------------------------------------------------------------------------
# Platform: macOS
# ---------------------------------------------------------------------------

_MACOS_SERVICE_MAP = {
    "chrome": "Chrome Safe Storage",
    "edge": "Microsoft Edge Safe Storage",
    "brave": "Brave Safe Storage",
    "arc": "Arc Safe Storage",
    "coccoc": "CocCoc Safe Storage",
    "comet": "Comet Safe Storage",
    "vivaldi": "Vivaldi Safe Storage",
    "opera": "Opera Safe Storage",
}


def _get_master_key_macos(browser_id: str) -> bytearray:
    if browser_id not in _MACOS_SERVICE_MAP:
        raise KeychainAccessError(f"Unsupported browser for macOS Keychain: {browser_id}")

    # Only allow mock override when running under pytest or explicit test mode.
    # This prevents production environments from bypassing real keychain access.
    _is_test = "pytest" in sys.modules or os.environ.get("CPM_TEST_MODE") == "1"
    mock_val = os.environ.get("CPM_MOCK_KEYCHAIN")
    if mock_val and _is_test:
        return bytearray(mock_val.encode("utf-8"))

    service = _MACOS_SERVICE_MAP[browser_id]
    result = subprocess.run(
        ["/usr/bin/security", "find-generic-password", "-w", "-s", service],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        # Deliberately omit stderr to avoid leaking system details into logs/UI.
        raise KeychainAccessError(
            f"Cannot read '{service}' from Keychain. "
            "User may have denied access or the service does not exist."
        )

    return bytearray(result.stdout.strip().encode("utf-8"))


def _derive_aes_key_macos(master: bytearray) -> bytearray:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=b"saltysalt",
        iterations=1003,
    )
    return bytearray(kdf.derive(bytes(master)))


# ---------------------------------------------------------------------------
# Platform: Windows
# ---------------------------------------------------------------------------

def _dpapi_decrypt(data: bytes) -> bytes:
    """Decrypt bytes using the Windows Data Protection API (CryptUnprotectData)."""
    import ctypes
    import ctypes.wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", ctypes.c_ulong), ("pbData", ctypes.POINTER(ctypes.c_char))]

    buf = ctypes.create_string_buffer(data, len(data))
    blob_in = DATA_BLOB(len(data), buf)
    blob_out = DATA_BLOB()

    ok = ctypes.windll.crypt32.CryptUnprotectData(  # type: ignore[attr-defined]
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    )
    if not ok:
        raise KeychainAccessError("CryptUnprotectData failed — DPAPI decryption error.")

    decrypted = ctypes.string_at(blob_out.pbData, blob_out.cbData)
    ctypes.windll.kernel32.LocalFree(blob_out.pbData)  # type: ignore[attr-defined]
    return decrypted


def _get_master_key_windows(local_state_path: Path) -> bytearray:
    """Read and DPAPI-decrypt the AES-256 key stored in Chrome's Local State file."""
    import base64
    import json

    if not local_state_path.exists():
        raise KeychainAccessError(f"Local State file not found: {local_state_path}")

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key_b64: Optional[str] = local_state.get("os_crypt", {}).get("encrypted_key")
    if not encrypted_key_b64:
        raise KeychainAccessError("No 'os_crypt.encrypted_key' found in Local State.")

    encrypted_key = base64.b64decode(encrypted_key_b64)

    # Chromium prepends "DPAPI" (5 bytes) to indicate DPAPI protection.
    if not encrypted_key.startswith(b"DPAPI"):
        raise KeychainAccessError("encrypted_key does not carry the expected DPAPI prefix.")

    raw_key = _dpapi_decrypt(encrypted_key[5:])
    return bytearray(raw_key)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_crypto_context(
    browser_id: str,
    profile_path: Optional[Path] = None,
) -> CryptoContext:
    """
    Acquire OS-specific encryption key for the given browser and return a
    CryptoContext. On Windows, profile_path is required to locate Local State.
    """
    current_os = platform.system()

    if current_os == "Darwin":
        master = _get_master_key_macos(browser_id)
        try:
            aes_key = _derive_aes_key_macos(master)
            return CryptoContext(browser_id=browser_id, _aes_key=aes_key, _platform="macos")
        finally:
            for i in range(len(master)):
                master[i] = 0

    elif current_os == "Windows":
        if profile_path is None:
            raise KeychainAccessError(
                "profile_path is required on Windows to locate Local State."
            )
        local_state_path = profile_path.parent / "Local State"
        key = _get_master_key_windows(local_state_path)
        return CryptoContext(browser_id=browser_id, _aes_key=key, _platform="windows")

    else:
        raise KeychainAccessError(f"Unsupported platform: {current_os}")


def decrypt_value(encrypted: bytes, ctx: CryptoContext) -> bytes:
    """Decrypt one value using the context's platform algorithm."""
    if not encrypted:
        return b""

    if ctx._platform == "macos":
        return _decrypt_macos(encrypted, ctx)
    elif ctx._platform == "windows":
        return _decrypt_windows(encrypted, ctx)
    else:
        raise DecryptionError(f"Unknown platform in context: {ctx._platform}")


def encrypt_value(plaintext: bytes, ctx: CryptoContext) -> bytes:
    """Encrypt one value using the context's platform algorithm."""
    if not plaintext:
        return b""

    if ctx._platform == "macos":
        return _encrypt_macos(plaintext, ctx)
    elif ctx._platform == "windows":
        return _encrypt_windows(plaintext, ctx)
    else:
        raise DecryptionError(f"Unknown platform in context: {ctx._platform}")


def reencrypt_value(
    encrypted: bytes,
    source_ctx: CryptoContext,
    target_ctx: CryptoContext,
) -> bytes:
    """Decrypt with source key then re-encrypt with target key."""
    if not encrypted:
        return b""

    plaintext = decrypt_value(encrypted, source_ctx)
    try:
        return encrypt_value(plaintext, target_ctx)
    finally:
        # Best-effort zeroing — bytes are immutable, but removing the reference
        # at least makes the value eligible for GC.
        del plaintext


def clear_context(ctx: CryptoContext) -> None:
    """Zero out the AES key in memory."""
    for i in range(len(ctx._aes_key)):
        ctx._aes_key[i] = 0


# ---------------------------------------------------------------------------
# macOS AES-128-CBC helpers
# ---------------------------------------------------------------------------

def _decrypt_macos(encrypted: bytes, ctx: CryptoContext) -> bytes:
    if encrypted.startswith(b"v10") or encrypted.startswith(b"v11"):
        ciphertext = encrypted[3:]
    elif len(encrypted) >= 16 and len(encrypted) % 16 == 0:
        # Legacy: no prefix, attempt raw decryption
        ciphertext = encrypted
    else:
        raise InvalidEncryptedFormat("Missing version prefix and invalid length for macOS format.")

    iv = b" " * 16
    cipher = Cipher(algorithms.AES(bytes(ctx._aes_key)), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Validate PKCS7 padding: all padding bytes must equal pad_len.
    pad_len = padded[-1]
    if pad_len == 0 or pad_len > 16:
        raise DecryptionError("Invalid PKCS7 padding length — wrong key or corrupted data.")
    if padded[-pad_len:] != bytes([pad_len] * pad_len):
        raise DecryptionError("Invalid PKCS7 padding bytes — wrong key or corrupted data.")

    return padded[:-pad_len]


def _encrypt_macos(plaintext: bytes, ctx: CryptoContext) -> bytes:
    pad_len = 16 - (len(plaintext) % 16)
    padded = plaintext + bytes([pad_len] * pad_len)

    iv = b" " * 16
    cipher = Cipher(algorithms.AES(bytes(ctx._aes_key)), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()

    return b"v10" + ciphertext


# ---------------------------------------------------------------------------
# Windows AES-256-GCM helpers (Chrome 80+)
# ---------------------------------------------------------------------------

def _decrypt_windows(encrypted: bytes, ctx: CryptoContext) -> bytes:
    if not (encrypted.startswith(b"v8") and len(encrypted) > 15):
        raise InvalidEncryptedFormat(
            "Expected 'v8x' prefix for Windows AES-GCM format. "
            "Legacy DPAPI-direct values are not supported."
        )
    # bytes 0-2: version prefix ("v80", "v81", etc.)
    # bytes 3-14: 12-byte nonce
    # bytes 15+: ciphertext + 16-byte GCM auth tag
    nonce = encrypted[3:15]
    ciphertext_with_tag = encrypted[15:]
    aesgcm = AESGCM(bytes(ctx._aes_key))
    try:
        return aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except Exception as exc:
        raise DecryptionError(f"AES-GCM decryption failed: {exc}") from exc


def _encrypt_windows(plaintext: bytes, ctx: CryptoContext) -> bytes:
    nonce = os.urandom(12)
    aesgcm = AESGCM(bytes(ctx._aes_key))
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)
    return b"v80" + nonce + ciphertext_with_tag

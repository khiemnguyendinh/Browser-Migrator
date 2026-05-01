# M03 — Keychain Decryptor

**Owner:** Claude Code (SOLE — security critical)
**Reviewer:** Khiêm + Claude Code
**Priority:** P0 — BLOCKING
**Estimated Effort:** 16 hours

> **WARNING:** Module này xử lý mật khẩu và session tokens của user. Sai một bug có thể leak credentials. Antigravity KHÔNG được modify. Mọi thay đổi phải qua Claude Code.

## 1. Mục đích

- Lấy master encryption key từ macOS Keychain.
- Decrypt cookies + passwords từ profile nguồn.
- Re-encrypt với key của profile đích.
- Đảm bảo memory hygiene: clear plaintext khỏi RAM ngay sau khi dùng.

## 2. Cryptography Background

### Chromium Encryption Scheme (macOS)

```
Step 1: Browser stores random 16-byte master key in macOS Keychain
        Service: "Chrome Safe Storage" (hoặc "Edge Safe Storage", etc.)
        Account: "Chrome" (hoặc browser name)
        Value: base64-encoded 16 random bytes

Step 2: When encrypting a cookie/password:
        - Derive AES key from master:
            key = PBKDF2-SHA1(master, salt="saltysalt", iter=1003, len=16)
        - IV = b" " * 16  (16 spaces)
        - Encrypt: AES-128-CBC(plaintext, key, IV)
        - Prefix with version: b"v10" + ciphertext

Step 3: Stored in SQLite as BLOB.
```

## 3. Public API

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class CryptoContext:
    """Holds derived AES key. Should be discarded after use."""
    browser_id: str
    _aes_key: bytes              # NOT for external access
    
    def __repr__(self) -> str:
        return f"CryptoContext(browser={self.browser_id}, key=<REDACTED>)"

def get_crypto_context(browser_id: str) -> CryptoContext:
    """Fetch master key from Keychain, derive AES key. Triggers user auth."""
    ...

def decrypt_value(encrypted: bytes, ctx: CryptoContext) -> bytes:
    """Decrypt one value. Returns plaintext bytes."""
    ...

def encrypt_value(plaintext: bytes, ctx: CryptoContext) -> bytes:
    """Encrypt one value. Returns 'v10' + ciphertext."""
    ...

def reencrypt_value(
    encrypted: bytes,
    source_ctx: CryptoContext,
    target_ctx: CryptoContext,
) -> bytes:
    """Decrypt với source, re-encrypt với target. Plaintext never leaves function."""
    ...

def clear_context(ctx: CryptoContext) -> None:
    """Best-effort clear AES key from memory."""
    ...
```

## 4. Implementation

### 4.1 Keychain Access

```python
import subprocess

def _get_master_key(browser_id: str) -> bytes:
    service_map = {
        "chrome": "Chrome Safe Storage",
        "edge": "Microsoft Edge Safe Storage",
        "brave": "Brave Safe Storage",
        "arc": "Arc Safe Storage",
        "coccoc": "CocCoc Safe Storage",
    }
    service = service_map[browser_id]
    
    result = subprocess.run(
        ["/usr/bin/security", "find-generic-password", "-w", "-s", service],
        capture_output=True,
        text=True,
        timeout=30,
    )
    
    if result.returncode != 0:
        raise KeychainAccessError(
            f"Cannot read {service} from Keychain. "
            f"User may have denied access. Stderr: {result.stderr}"
        )
    
    master = result.stdout.strip().encode("utf-8")
    return master
```

**Note:** `-w` flag prints password to stdout. macOS will prompt user GUI for authentication.

### 4.2 Key Derivation

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def _derive_aes_key(master: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA1(),
        length=16,
        salt=b"saltysalt",
        iterations=1003,
    )
    return kdf.derive(master)
```

### 4.3 Decrypt

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def decrypt_value(encrypted: bytes, ctx: CryptoContext) -> bytes:
    if not encrypted:
        return b""
    
    # Strip version prefix
    if encrypted.startswith(b"v10") or encrypted.startswith(b"v11"):
        ciphertext = encrypted[3:]
    else:
        # Legacy unencrypted (rare)
        return encrypted
    
    iv = b" " * 16
    cipher = Cipher(algorithms.AES(ctx._aes_key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    pad_len = padded[-1]
    plaintext = padded[:-pad_len]
    
    return plaintext
```

### 4.4 Memory Hygiene

```python
def clear_context(ctx: CryptoContext) -> None:
    """Best-effort. Python doesn't guarantee memory clear, but we try."""
    if isinstance(ctx._aes_key, bytearray):
        for i in range(len(ctx._aes_key)):
            ctx._aes_key[i] = 0
```

**Pattern for re-encryption:**
```python
def reencrypt_value(encrypted, src, dst):
    plaintext = decrypt_value(encrypted, src)
    try:
        return encrypt_value(plaintext, dst)
    finally:
        # Plaintext should be garbage collected ASAP
        del plaintext
```

## 5. Security Requirements (MANDATORY)

1. **No logging of plaintext values, ever.** Even DEBUG level.
2. **No persisting plaintext to disk.** Memory only.
3. **CryptoContext is opaque.** External code cannot access `_aes_key`.
4. **Re-encryption is atomic from caller's perspective.** Decrypt and re-encrypt in same function call, plaintext never leaves M03.
5. **Test với fake keys, không dùng real Keychain trong CI.**

## 6. Error Cases

| Error | Cause | Handling |
|---|---|---|
| `KeychainAccessError` | User denied access | Prompt user grant permission, retry |
| `InvalidEncryptedFormat` | Blob không có v10/v11 prefix và quá ngắn | Skip với warning log |
| `DecryptionError` | Wrong key, corrupted data | Skip individual value, continue |
| `KeychainNotFoundError` | Browser not installed hoặc never run | Raise with helpful message |

## 7. Tests

```python
def test_derive_key_deterministic():
    key1 = _derive_aes_key(b"test_master")
    key2 = _derive_aes_key(b"test_master")
    assert key1 == key2
    assert len(key1) == 16

def test_encrypt_decrypt_roundtrip():
    ctx = CryptoContext("test", _derive_aes_key(b"master"))
    plaintext = b"my secret password"
    encrypted = encrypt_value(plaintext, ctx)
    assert encrypted.startswith(b"v10")
    decrypted = decrypt_value(encrypted, ctx)
    assert decrypted == plaintext

def test_reencrypt_uses_target_key():
    src = CryptoContext("a", _derive_aes_key(b"key_a"))
    dst = CryptoContext("b", _derive_aes_key(b"key_b"))
    
    enc_a = encrypt_value(b"secret", src)
    enc_b = reencrypt_value(enc_a, src, dst)
    
    # Decrypt with dst should give original
    assert decrypt_value(enc_b, dst) == b"secret"
    # Decrypt with src should NOT work
    with pytest.raises(Exception):
        decrypt_value(enc_b, src)

def test_logging_does_not_contain_plaintext(caplog):
    # Run encrypt/decrypt operations
    # Assert no "secret" string in any log message
    ...

def test_invalid_format_handled():
    ctx = CryptoContext("test", _derive_aes_key(b"master"))
    with pytest.raises(InvalidEncryptedFormat):
        decrypt_value(b"xx", ctx)  # Too short

def test_empty_input_returns_empty():
    ctx = CryptoContext("test", _derive_aes_key(b"master"))
    assert decrypt_value(b"", ctx) == b""
```

Coverage target: ≥ 95% (security critical).

## 8. Audit Checklist (before merge)

- [ ] No `print()` statements in module.
- [ ] No `logger.debug(plaintext)` patterns.
- [ ] All public functions có type hints.
- [ ] CryptoContext không bị serialize qua repr/str.
- [ ] Tests pass với coverage > 95%.
- [ ] Manual test trên real Chrome → Edge thành công.
- [ ] grep module cho `password|secret|cookie_value` → chỉ trong test fixtures.

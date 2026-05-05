import pytest
from cpm.m03_keychain.crypto import (
    _derive_aes_key_macos,
    get_crypto_context,
    encrypt_value,
    decrypt_value,
    reencrypt_value,
    CryptoContext,
    InvalidEncryptedFormat,
    DecryptionError,
)


def test_derive_key_deterministic():
    """PBKDF2 derivation must be deterministic for the same input."""
    key1 = _derive_aes_key_macos(bytearray(b"test_master"))
    key2 = _derive_aes_key_macos(bytearray(b"test_master"))
    assert key1 == key2
    assert len(key1) == 16


def test_encrypt_decrypt_roundtrip(monkeypatch):
    monkeypatch.setenv("CPM_MOCK_KEYCHAIN", "mock_master")
    ctx = get_crypto_context("chrome")

    plaintext = b"my secret password"
    encrypted = encrypt_value(plaintext, ctx)
    assert encrypted.startswith(b"v10")

    decrypted = decrypt_value(encrypted, ctx)
    assert decrypted == plaintext


def test_reencrypt_uses_target_key(monkeypatch):
    monkeypatch.setenv("CPM_MOCK_KEYCHAIN", "key_aaaaaaaaaa")
    src = get_crypto_context("chrome")

    monkeypatch.setenv("CPM_MOCK_KEYCHAIN", "key_bbbbbbbbbb")
    dst = get_crypto_context("edge")

    enc_a = encrypt_value(b"secret", src)
    enc_b = reencrypt_value(enc_a, src, dst)

    assert decrypt_value(enc_b, dst) == b"secret"
    with pytest.raises(DecryptionError):
        decrypt_value(enc_b, src)


def test_invalid_format_handled(monkeypatch):
    monkeypatch.setenv("CPM_MOCK_KEYCHAIN", "mock_master")
    ctx = get_crypto_context("chrome")
    with pytest.raises((InvalidEncryptedFormat, DecryptionError)):
        decrypt_value(b"xx", ctx)  # Too short


def test_empty_input_returns_empty(monkeypatch):
    monkeypatch.setenv("CPM_MOCK_KEYCHAIN", "mock_master")
    ctx = get_crypto_context("chrome")
    assert decrypt_value(b"", ctx) == b""
    assert encrypt_value(b"", ctx) == b""

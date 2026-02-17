import pytest
from security.crypto import AESCipher


def test_key_derivation_sha256():
    """
    Verifica que la clave interna sea siempre de 32 bytes (SHA-256),
    sin importar la longitud de la entrada.
    """
    # Clave corta
    cipher = AESCipher("short")
    assert len(cipher.key) == 32

    # Clave larga
    cipher = AESCipher("very_long_secret_key_that_exceeds_32_bytes_limit")
    assert len(cipher.key) == 32


def test_encrypt_returns_iv_and_ciphertext():
    """
    Verifica que encrypt retorne iv y ciphertext en base64.
    """
    cipher = AESCipher("test_secret")

    data = {"test": "value"}
    encrypted = cipher.encrypt(data)

    assert "iv" in encrypted
    assert "ciphertext" in encrypted


def test_encrypt_decrypt_cycle():
    """
    Test crítico:
    Verifica que al cifrar y luego descifrar,
    el resultado sea exactamente igual al original.
    """
    cipher = AESCipher("test_secret_cycle")

    original = {"metric": 123}
    encrypted = cipher.encrypt(original)
    decrypted = cipher.decrypt(encrypted)

    assert decrypted == original

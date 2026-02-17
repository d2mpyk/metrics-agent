# security/crypto.py

import os
import json
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class AESCipher:

    def __init__(self, key):
        """
        Inicializa el cifrador.
        Deriva una clave AES-256 (32 bytes) usando SHA256 sobre la entrada.
        Acepta la clave como string o bytes.
        """
        if isinstance(key, str):
            key = key.encode("utf-8")

        # Derivación de clave SHA256 según requisito
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, data: dict) -> dict:
        # Generar IV aleatorio de 16 bytes
        iv = os.urandom(16)

        # Configurar Cipher AES-CBC
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        plaintext = json.dumps(data).encode("utf-8")

        # Aplicar Padding PKCS7 (bloque de 128 bits)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return {
            "iv": base64.b64encode(iv).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        }

    def decrypt(self, encrypted_data: dict) -> dict:
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Remover Padding PKCS7
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return json.loads(plaintext.decode("utf-8"))

import base64
import pytest
from config.settings import Settings
from pydantic import ValidationError


def test_settings_load_valid_env(monkeypatch):
    """
    Verifica que Settings pueda cargar variables de entorno válidas.
    """

    # Generamos una clave válida de 32 bytes
    valid_key = base64.b64encode(b"a" * 32).decode()

    monkeypatch.setenv("INTERVAL_SECONDS", "10")
    monkeypatch.setenv("AES_SECRET_KEY", valid_key)
    monkeypatch.setenv("API_BASE_URL", "http://test-api.com")
    monkeypatch.setenv("SERVICE_TYPE", "Asterisk-DB")

    settings = Settings()

    assert settings.INTERVAL_SECONDS == 10
    assert settings.AES_SECRET_KEY.get_secret_value() == valid_key
    assert settings.API_BASE_URL == "http://test-api.com"
    assert settings.SERVICE_TYPE == "Asterisk-DB"


def test_get_aes_key_bytes_valid(monkeypatch):
    """
    Verifica que la clave AES se decodifique correctamente
    y tenga exactamente 32 bytes.
    """

    valid_raw = b"x" * 32
    valid_key = base64.b64encode(valid_raw).decode()

    monkeypatch.setenv("INTERVAL_SECONDS", "5")
    monkeypatch.setenv("AES_SECRET_KEY", valid_key)

    settings = Settings()

    key_bytes = settings.get_aes_key_bytes()

    assert isinstance(key_bytes, bytes)
    assert len(key_bytes) == 32
    assert key_bytes == valid_raw


def test_get_aes_key_bytes_invalid_length(monkeypatch):
    """
    Si la clave no tiene 32 bytes reales
    debe lanzar ValueError.
    """

    invalid_raw = b"x" * 16  # incorrecto
    invalid_key = base64.b64encode(invalid_raw).decode()

    monkeypatch.setenv("INTERVAL_SECONDS", "5")
    monkeypatch.setenv("AES_SECRET_KEY", invalid_key)

    settings = Settings()

    with pytest.raises(ValueError):
        settings.get_aes_key_bytes()


def test_interval_is_integer(monkeypatch):
    """
    INTERVAL_SECONDS debe ser convertido a int automáticamente
    por Pydantic.
    """

    valid_key = base64.b64encode(b"a" * 32).decode()

    monkeypatch.setenv("INTERVAL_SECONDS", "15")
    monkeypatch.setenv("AES_SECRET_KEY", valid_key)

    settings = Settings()

    assert isinstance(settings.INTERVAL_SECONDS, int)
    assert settings.INTERVAL_SECONDS == 15


def test_aes_key_is_optional(monkeypatch):
    """
    AES_SECRET_KEY ahora es opcional. Si falta, debe ser None
    y no lanzar ValidationError.
    """

    monkeypatch.delenv("INTERVAL_SECONDS", raising=False)
    monkeypatch.delenv("AES_SECRET_KEY", raising=False)

    settings = Settings(_env_file=None)
    assert settings.AES_SECRET_KEY is None


def test_get_aes_key_bytes_none(monkeypatch):
    """
    Verifica que get_aes_key_bytes lance ValueError si AES_SECRET_KEY es None.
    """
    monkeypatch.delenv("AES_SECRET_KEY", raising=False)
    settings = Settings(_env_file=None)

    with pytest.raises(ValueError, match="AES_SECRET_KEY is not set"):
        settings.get_aes_key_bytes()

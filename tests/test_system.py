from core.system import get_system_info


def test_get_system_info_structure():
    """
    Verifica que el diccionario tenga las claves esperadas.
    """
    info = get_system_info()

    assert "hostname" in info
    assert "ip_address" in info
    assert "os" in info
    assert "os_version" in info
    assert "timestamp" in info


def test_ip_address_returns_string():
    """
    Verifica que la IP sea un string no vacío.
    """
    info = get_system_info()
    assert isinstance(info["ip_address"], str)
    assert len(info["ip_address"]) > 0

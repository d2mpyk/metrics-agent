from unittest.mock import MagicMock, patch

from core.system import get_service_status, get_system_info


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


def _mock_systemctl(stdout):
    result = MagicMock()
    result.stdout = stdout
    return result


def test_asterisk_status_ok_when_service_is_active():
    with patch("core.system.subprocess.run", return_value=_mock_systemctl("active\n")):
        status = get_service_status("Asterisk")

    assert status == {"servicio": "Asterisk", "status": "ok"}


def test_db_status_ok_when_service_is_active():
    with patch("core.system.subprocess.run", return_value=_mock_systemctl("active\n")) as run:
        status = get_service_status("DB")

    run.assert_called_once()
    assert run.call_args[0][0] == ["systemctl", "is-active", "mysqld.service"]
    assert status == {"servicio": "DB", "status": "ok"}


def test_asterisk_db_status_ok_only_when_both_services_are_active():
    with patch("core.system.subprocess.run", return_value=_mock_systemctl("active\n")) as run:
        status = get_service_status("Asterisk-DB")

    assert run.call_count == 2
    assert status == {"servicio": "Asterisk-DB", "status": "ok"}


def test_asterisk_db_status_error_when_one_service_is_inactive():
    responses = [_mock_systemctl("active\n"), _mock_systemctl("inactive\n")]

    with patch("core.system.subprocess.run", side_effect=responses) as run:
        status = get_service_status("Asterisk-DB")

    assert run.call_count == 2
    assert status == {"servicio": "Asterisk-DB", "status": "error"}


def test_web_status_uses_httpd_service():
    with patch("core.system.subprocess.run", return_value=_mock_systemctl("active\n")) as run:
        status = get_service_status("Web")

    run.assert_called_once()
    assert run.call_args[0][0] == ["systemctl", "is-active", "httpd"]
    assert status == {"servicio": "Web", "status": "ok"}


def test_unknown_service_type_returns_error():
    status = get_service_status("Redis")

    assert status == {"servicio": "Redis", "status": "error"}

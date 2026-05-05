# core/system.py

import socket
import platform
import subprocess
from datetime import datetime, timezone

SERVICE_UNITS = {
    "asterisk": ("Asterisk", ["asterisk.service"]),
    "db": ("DB", ["mysqld.service"]),
    "asterisk-db": ("Asterisk-DB", ["asterisk.service", "mysqld.service"]),
    "web": ("Web", ["httpd"]),
}


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "ip_address": get_ip_address(),
        "os": platform.system(),
        "os_version": platform.version(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def _normalize_service_type(service_type: str) -> str:
    return service_type.strip().lower()


def is_systemd_unit_active(unit_name: str) -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "is-active", unit_name],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

    return result.stdout.strip() == "active"


def get_service_status(service_type: str) -> dict:
    normalized = _normalize_service_type(service_type)
    service_config = SERVICE_UNITS.get(normalized)

    if service_config is None:
        return {
            "servicio": service_type,
            "status": "error",
        }

    service_name, unit_names = service_config
    unit_statuses = [is_systemd_unit_active(unit) for unit in unit_names]

    return {
        "servicio": service_name,
        "status": "ok" if all(unit_statuses) else "error",
    }

# core/system.py

import socket
import platform
from datetime import datetime, timezone


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

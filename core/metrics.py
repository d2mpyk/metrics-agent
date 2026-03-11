# core/metrics.py

import psutil
from .system import get_system_info


def bytes_to_human_readable(bytes_value: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} PB"


def get_cpu_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_count_logical": psutil.cpu_count(logical=True),
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "load_average": psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
    }


def get_memory_metrics():
    memory = psutil.virtual_memory()
    return {
        "total_bytes": memory.total,
        "total": bytes_to_human_readable(memory.total),
        "available_bytes": memory.available,
        "available": bytes_to_human_readable(memory.available),
        "used_bytes": memory.used,
        "used": bytes_to_human_readable(memory.used),
        "percent": memory.percent
    }


def get_disk_metrics(path="/"):
    disk = psutil.disk_usage(path)
    return {
        "total_bytes": disk.total,
        "used_bytes": disk.used,
        "free_bytes": disk.free,
        "percent": disk.percent
    }


def collect_metrics():
    return {
        "system": get_system_info(),
        "cpu": get_cpu_metrics(),
        "memory": get_memory_metrics(),
        "disk": get_disk_metrics()
    }

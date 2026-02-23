# s:\WISE\Management\AGENTS\core\collector.py
import psutil


def get_system_metrics() -> dict:
    """
    Recolecta métricas reales del sistema para enviar al servidor.
    Las claves deben coincidir con lo que espera el modelo ServerMetric.
    """
    # CPU: Porcentaje de uso total
    cpu_usage = psutil.cpu_percent(interval=1)

    # RAM: Porcentaje de uso
    ram = psutil.virtual_memory()
    ram_usage = ram.percent

    # DISK: Porcentaje de uso de la partición principal
    disk = psutil.disk_usage("/")
    disk_usage = disk.percent

    # RED: Estadísticas de E/S de red (acumulativo)
    # pernic=False para obtener el total combinado de todas las interfaces
    net = psutil.net_io_counters(pernic=False)

    return {
        "cpu": cpu_usage,
        "ram": ram_usage,
        "disk": disk_usage,
        "net_sent": net.bytes_sent,
        "net_recv": net.bytes_recv,
    }

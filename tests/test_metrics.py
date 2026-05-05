from core.metrics import collect_metrics


def test_collect_metrics_structure():
    """
    Verifica que collect_metrics contenga
    system, cpu, memory y disk.
    """
    metrics = collect_metrics()

    assert "system" in metrics
    assert "cpu" in metrics
    assert "memory" in metrics
    assert "disk" in metrics
    assert "servicio" in metrics
    assert "status" in metrics


def test_cpu_metrics_keys():
    metrics = collect_metrics()
    cpu = metrics["cpu"]

    assert "cpu_percent" in cpu
    assert "cpu_count_logical" in cpu
    assert "cpu_count_physical" in cpu


def test_memory_metrics_keys():
    metrics = collect_metrics()
    memory = metrics["memory"]

    assert "total_bytes" in memory
    assert "used_bytes" in memory
    assert "percent" in memory


def test_disk_metrics_keys():
    metrics = collect_metrics()
    disk = metrics["disk"]

    assert "total_bytes" in disk
    assert "percent" in disk


def test_collect_metrics_includes_service_status(monkeypatch):
    monkeypatch.setattr(
        "core.metrics.get_service_status",
        lambda service_type: {"servicio": service_type, "status": "ok"},
    )

    metrics = collect_metrics("Asterisk")

    assert metrics["servicio"] == "Asterisk"
    assert metrics["status"] == "ok"

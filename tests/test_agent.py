import pytest, requests, threading, time
import logging
from unittest.mock import patch, MagicMock
from agent import MetricsAgent


@pytest.fixture
def mock_settings():
    m = MagicMock()
    m.INTERVAL_SECONDS = 60
    m.get_aes_key_bytes.return_value = b"0" * 32
    m.API_BASE_URL = "http://mock-api"
    m.API_TIMEOUT = 10
    return m


@pytest.fixture
def mock_credentials():
    return {"access_token": "fake_token_123", "client_secret_key": "fake_secret_key"}


def test_agent_initialization(mock_settings, mock_credentials):
    """
    Verifica que el agente se inicialice correctamente.
    """
    agent = MetricsAgent(mock_settings, mock_credentials)
    assert agent.interval == 60
    assert not agent.shutdown_event.is_set()
    assert agent.cipher is not None


def test_agent_stop_sets_shutdown_event(mock_settings, mock_credentials):
    """
    Verifica que stop() active el evento de apagado.
    """
    agent = MetricsAgent(mock_settings, mock_credentials)
    assert not agent.shutdown_event.is_set()

    agent.stop()

    assert agent.shutdown_event.is_set()


def test_send_to_api_success(mock_settings, mock_credentials, caplog):
    """
    Verifica que _send_to_api realice la petición POST correctamente.
    """
    agent = MetricsAgent(mock_settings, mock_credentials)
    payload = {"ciphertext": "dummy", "nonce": "123"}

    with patch("agent.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        with caplog.at_level(logging.INFO):
            agent._send_to_api(payload)

        mock_post.assert_called_once()
        assert "Metrics sent successfully" in caplog.text

        # Verificar headers de autorización
        args, kwargs = mock_post.call_args
        assert args[0] == "http://mock-api/clients/metrics"
        assert kwargs["headers"]["Authorization"] == "Bearer fake_token_123"


def test_agent_runs_and_stops_cleanly(mock_settings, mock_credentials):
    """
    Test de integración: verifica que el agente se inicie en un hilo,
    se ejecute y se detenga limpiamente.
    """
    mock_settings.INTERVAL_SECONDS = 0.1
    agent = MetricsAgent(mock_settings, mock_credentials)

    # Evitamos llamadas de red reales durante el test
    with patch("agent.requests.post"):
        agent_thread = threading.Thread(target=agent.run, daemon=True)
        agent_thread.start()

        # Damos tiempo al agente para que se ejecute al menos un ciclo
        time.sleep(0.5)

        # Verificamos que el hilo está vivo
        assert agent_thread.is_alive()

        # Enviamos la señal de detención
        agent.stop()

        # Esperamos a que el hilo termine (con un timeout de seguridad)
        agent_thread.join(timeout=2)

        # Verificamos que el hilo haya terminado
        assert not agent_thread.is_alive()


def test_send_to_api_handles_error(mock_settings, mock_credentials, caplog):
    """
    Verifica que el agente capture excepciones de requests sin detenerse.
    """
    agent = MetricsAgent(mock_settings, mock_credentials)
    payload = {"data": "test"}

    with patch("agent.requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException(
            "Connection refused"
        )

        with caplog.at_level(logging.ERROR):
            # No debe lanzar excepción, el agente debe capturarla y loguearla
            agent._send_to_api(payload)

        mock_post.assert_called_once()
        assert "Failed to send metrics to API" in caplog.text

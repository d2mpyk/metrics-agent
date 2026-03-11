import pytest
from unittest.mock import patch, MagicMock
from core.auth_flow import authenticate_device


@pytest.fixture
def mock_settings():
    m = MagicMock()
    m.API_BASE_URL = "http://test-api.com/api/v1"
    m.API_TIMEOUT = 5
    return m


def test_authenticate_device_flow_success(mock_settings):
    """
    Test de integración simulado:
    Verifica el flujo completo de autenticación:
    1. Solicitud de código exitosa.
    2. Polling con estado 'authorization_pending'.
    3. Polling exitoso con obtención de credenciales.
    """

    # 1. Respuesta para solicitud de código
    resp_code = MagicMock()
    resp_code.status_code = 200
    resp_code.json.return_value = {
        "device_code": "device_123",
        "user_code": "USER-123",
        "verification_uri": "http://verify.me",
        "interval": 1,
    }

    # 2. Respuesta para polling (pendiente)
    resp_pending = MagicMock()
    resp_pending.status_code = 400
    resp_pending.json.return_value = {"error": "authorization_pending"}

    # 3. Respuesta para polling (éxito)
    resp_success = MagicMock()
    resp_success.status_code = 200
    resp_success.json.return_value = {
        "access_token": "token_secret_123",
        "client_secret_key": "key_secret_123",
    }

    # Patcheamos requests.post y time.sleep (para no esperar realmente)
    with patch("core.auth_flow.requests.post") as mock_post, patch(
        "core.auth_flow.time.sleep"
    ) as mock_sleep:

        # Configuramos la secuencia de respuestas
        mock_post.side_effect = [resp_code, resp_pending, resp_success]

        # Ejecutamos la función
        creds = authenticate_device(mock_settings)

        # Verificaciones
        assert creds["access_token"] == "token_secret_123"
        assert creds["client_secret_key"] == "key_secret_123"

        # Verificamos que se hicieron 3 llamadas
        assert mock_post.call_count == 3

        # Verificamos URLs y datos
        # Llamada 1: /code
        args1, _ = mock_post.call_args_list[0]
        assert args1[0] == "http://test-api.com/api/v1/auth/device/code"

        # Llamada 2: /token (pendiente)
        args2, kwargs2 = mock_post.call_args_list[1]
        assert args2[0] == "http://test-api.com/api/v1/auth/device/token"
        assert kwargs2["data"]["device_code"] == "device_123"

        # Verificamos que se llamó a sleep con el intervalo correcto
        mock_sleep.assert_called_with(1)

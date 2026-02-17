# core/auth_flow.py

import time
import logging
import requests
from config.settings import Settings

logger = logging.getLogger("AuthFlow")


def authenticate_device(settings: Settings) -> dict:
    """
    Ejecuta el flujo de autorización de dispositivo (Device Flow).
    1. Solicita un código de dispositivo.
    2. Muestra instrucciones al usuario.
    3. Realiza polling hasta obtener el token.

    Retorna:
        dict: Respuesta JSON con 'access_token' y 'client_secret_key'.
    """
    base_url = settings.API_BASE_URL.rstrip("/")
    code_url = f"{base_url}/auth/device/code"
    token_url = f"{base_url}/auth/device/token"

    # Paso 1: Solicitar código de dispositivo
    try:
        logger.info(f"Iniciando autenticación con {code_url}")
        response = requests.post(code_url, timeout=settings.API_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error(f"Error al solicitar código de dispositivo: {e}")
        raise

    device_code = data["device_code"]
    user_code = data["user_code"]
    verification_uri = data["verification_uri"]
    interval = data.get("interval", 5)

    # Paso 2: Interacción con el usuario
    print(f"\n{'='*40}")
    print(f"REQUIERE AUTORIZACIÓN DE DISPOSITIVO")
    print(f"{'='*40}")
    print(f"1. Visite: {verification_uri}")
    print(f"2. Ingrese el código: {user_code}")
    print(f"{'='*40}\n")

    logger.info(f"Esperando autorización. Código de usuario: {user_code}")

    # Paso 3: Polling por el token
    while True:
        time.sleep(interval)
        try:
            payload = {
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            }
            response = requests.post(
                token_url, data=payload, timeout=settings.API_TIMEOUT
            )

            if response.status_code == 200:
                logger.info("¡Dispositivo autorizado exitosamente!")
                return response.json()

            # Manejo de errores esperados en OAuth Device Flow
            if response.status_code in (400, 403):
                error_resp = response.json()
                error = error_resp.get("detail") or error_resp.get("error")

                if error == "authorization_pending":
                    continue
                elif error == "slow_down":
                    interval += 5
                    continue
                elif error == "expired_token":
                    raise TimeoutError("El código de dispositivo ha expirado.")
                elif error == "access_denied":
                    raise PermissionError("Acceso denegado por el usuario.")

            if response.status_code != 200:
                logger.error(
                    f"Respuesta del servidor ({response.status_code}): {response.text}"
                )

            response.raise_for_status()

        except requests.exceptions.ConnectionError:
            logger.warning("Error de conexión durante el polling, reintentando...")
            continue

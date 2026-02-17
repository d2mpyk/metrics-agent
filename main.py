# main.py

from agent import MetricsAgent
from config.settings import get_settings
from core.credentials import CredentialManager
from core.auth_flow import authenticate_device
import logging

if __name__ == "__main__":
    settings = get_settings()
    cred_manager = CredentialManager()

    if not cred_manager.exists():
        logging.info(
            "Credenciales no encontradas. Iniciando registro de dispositivo..."
        )
        creds = authenticate_device(settings)
        cred_manager.save(creds)
        logging.info("Credenciales guardadas exitosamente.")

    credentials = cred_manager.load()
    if not credentials:
        raise RuntimeError("No se pudieron cargar las credenciales.")

    agent = MetricsAgent(settings, credentials)
    try:
        agent.run()
    except KeyboardInterrupt:
        logging.info("Shutdown signal received, stopping agent...")
    finally:
        agent.stop()

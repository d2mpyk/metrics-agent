# main.py

import os
import signal
import sys
from agent import MetricsAgent
from config.settings import get_settings
from core.credentials import CredentialManager
from core.auth_flow import authenticate_device
import logging


def main():
    settings = get_settings()

    # Asegurar ruta absoluta para las credenciales
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cred_path = os.path.join(base_dir, "credentials.json")

    cred_manager = CredentialManager(filepath=cred_path)

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

    # --- Inicio de la lógica del agente ---
    agent = MetricsAgent(settings, credentials)

    # Manejador para un apagado limpio (Ctrl+C o systemctl stop)
    def shutdown_handler(signum, frame):
        logging.info(f"Señal de apagado {signum} recibida, deteniendo el agente...")
        agent.stop()

    # Registrar los manejadores para las señales SIGINT (Ctrl+C) y SIGTERM (systemd)
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # El agente se ejecuta y bloquea aquí hasta que agent.stop() es llamado
    agent.run()
    logging.info("El agente se ha detenido limpiamente. Saliendo.")


if __name__ == "__main__":
    main()

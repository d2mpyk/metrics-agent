# agent.py

import os
import time
import threading
import json
import logging
from logging.handlers import RotatingFileHandler
import requests

from config.settings import Settings
from security.crypto import AESCipher
from core.collector import get_system_metrics

# Configuración del Logger
logger = logging.getLogger("MetricsAgent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # 1. Handler de Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Determinar ruta absoluta para el log
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(base_dir, "agent.log")

    # 2. Handler de Archivo Rotativo (5 MB por archivo, max 3 backups)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class MetricsAgent:

    def __init__(self, settings: Settings, credentials: dict):
        self.settings = settings
        self.credentials = credentials
        self.interval = settings.INTERVAL_SECONDS
        self.shutdown_event = threading.Event()
        self.cipher = AESCipher(credentials["client_secret_key"])

    def run(self):
        logger.info("Metrics Agent started")

        while not self.shutdown_event.is_set():
            try:
                metrics = get_system_metrics()

                encrypted = self.cipher.encrypt(metrics)

                # El servidor espera 'nonce', pero la librería de criptografía retorna 'iv'
                if "iv" in encrypted:
                    encrypted["nonce"] = encrypted.pop("iv")

                logger.info("Metrics encrypted successfully")
                logger.debug("Payload: %s", json.dumps(encrypted))
                self._send_to_api(encrypted)

            except Exception as e:
                logger.error(f"Error: {str(e)}")

            # Wait for the next interval or a shutdown signal
            self.shutdown_event.wait(self.interval)

    def _send_to_api(self, payload: dict):
        try:
            headers = {"Authorization": f"Bearer {self.credentials['access_token']}"}
            url = f"{self.settings.API_BASE_URL.rstrip('/')}/clients/metrics"
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.settings.API_TIMEOUT,
            )
            response.raise_for_status()
            logger.info(f"Metrics sent successfully. Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                logger.error(f"API Error Response: {e.response.text}")
            logger.error(f"Failed to send metrics to API: {e}")

    def stop(self):
        logger.info("Metrics Agent stopped")
        self.shutdown_event.set()

# core/credentials.py

import json
import os
from typing import Optional, Dict


class CredentialManager:
    def __init__(self, filepath: str = "credentials.json"):
        self.filepath = filepath

    def save(self, credentials: Dict[str, str]) -> None:
        """Guarda las credenciales en un archivo JSON."""
        with open(self.filepath, "w") as f:
            json.dump(credentials, f, indent=4)

    def load(self) -> Optional[Dict[str, str]]:
        """Carga las credenciales desde el archivo JSON."""
        if not os.path.exists(self.filepath):
            return None
        try:
            with open(self.filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def exists(self) -> bool:
        """Verifica si el archivo de credenciales existe."""
        return os.path.exists(self.filepath)

#!/bin/bash

# Configuración (Debe coincidir con install.sh)
APP_DIR="/opt/metrics"
SERVICE_NAME="metrics-agent"
SERVICE_FILE="/etc/systemd/system/metrics-agent.service"
USER_NAME="wiseagent"

# Verificación de Root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Error: Este script debe ejecutarse como root (usa sudo)."
  exit 1
fi

echo "=================================================="
echo "   Desinstalador de WISE Metrics Agent            "
echo "=================================================="

# 1. Detener y eliminar el servicio Systemd
echo "🛑 [1/4] Deteniendo y eliminando servicio..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME"; then
    systemctl disable "$SERVICE_NAME"
fi

if [ -f "$SERVICE_FILE" ]; then
    rm "$SERVICE_FILE"
    systemctl daemon-reload
    echo "      Servicio eliminado de systemd."
else
    echo "      El archivo de servicio no existía."
fi

# 2. Eliminar Usuario
echo "👤 [2/4] Eliminando usuario de servicio '$USER_NAME'..."
if id "$USER_NAME" &>/dev/null; then
    userdel "$USER_NAME"
    echo "      Usuario eliminado."
else
    echo "      El usuario no existe."
fi

# 3. Eliminar Directorios
echo "cX [3/4] Eliminando archivos de la aplicación..."
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
    echo "      Directorio $APP_DIR eliminado."
fi

echo "✅ Desinstalación completada."
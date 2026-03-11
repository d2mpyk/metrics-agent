#!/bin/bash
set -e  # Detener script si ocurre cualquier error

# Configuración
APP_DIR="/opt/metrics"
SERVICE_NAME="metrics-agent"
SERVICE_FILE="metrics-agent.service"
USER_NAME="wiseagent"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Verificación de Root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Error: Este script debe ejecutarse como root (usa sudo)."
  exit 1
fi

echo "=================================================="
echo "   Instalador de WISE Metrics Agent (CentOS 10)   "
echo "=================================================="

# 1. Dependencias del Sistema
echo "📦 [1/6] Instalando dependencias del sistema..."
dnf install -y python3 python3-pip rsync

# 2. Usuario de Servicio
echo "👤 [2/6] Configurando usuario de servicio '$USER_NAME'..."
if id "$USER_NAME" &>/dev/null; then
    echo "      El usuario ya existe."
else
    useradd --system --shell /sbin/nologin --home-dir "$APP_DIR" "$USER_NAME"
    echo "      Usuario creado correctamente."
fi

# 3. Copia de Archivos
echo "cX [3/6] Copiando archivos a $APP_DIR..."
if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
fi

# Usamos rsync para excluir archivos innecesarios como entornos virtuales antiguos o git
rsync -av --exclude='venv' --exclude='__pycache__' --exclude='.git' --exclude='install.sh' "$SCRIPT_DIR/" "$APP_DIR/" > /dev/null

# 4. Entorno Python
echo "🐍 [4/6] Configurando entorno virtual Python..."
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi

echo "      Instalando librerías desde requirements.txt..."
"$APP_DIR/venv/bin/pip" install --upgrade pip > /dev/null
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# 5. Permisos
echo "🔒 [5/6] Aplicando permisos de seguridad..."
chown -R "$USER_NAME:$USER_NAME" "$APP_DIR"
chmod 750 "$APP_DIR"
# Asegurar que systemd pueda leer el archivo .service antes de moverlo/linkearlo
chmod 644 "$APP_DIR/$SERVICE_FILE"

# 6. Configuración Systemd
echo "⚙️  [6/6] Instalando servicio Systemd..."
if [ -f "$APP_DIR/$SERVICE_FILE" ]; then
    cp "$APP_DIR/$SERVICE_FILE" "/etc/systemd/system/$SERVICE_FILE"
    
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    
    echo ""
    echo "✅ Instalación completada exitosamente."
    echo "Estado del servicio:"
    systemctl status "$SERVICE_NAME" --no-pager | head -n 10
else
    echo "❌ Error: No se encontró $SERVICE_FILE en el directorio de instalación."
    exit 1
fi

exit 0
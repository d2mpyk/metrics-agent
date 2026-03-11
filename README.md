# WISE Metrics Agent

Este es un agente de monitoreo ligero y seguro diseñado para recolectar métricas de sistema y enviarlas a una API centralizada.

## 📋 Funcionalidades

1.  **Recolección de Métricas:**
    *   **CPU:** Uso porcentual total.
    *   **RAM:** Uso porcentual de memoria virtual.
    *   **Disco:** Uso porcentual de la partición raíz (`/`).
    *   **Red:** Bytes enviados y recibidos (acumulativo).

2.  **Seguridad y Cifrado:**
    *   Todos los datos se cifran localmente antes de enviarse usando **AES-256 (CBC Mode)**.
    *   Utiliza un esquema de **clave simétrica** derivada de las credenciales del cliente.
    *   Implementa rotación de vectores de inicialización (IV/Nonce) por cada mensaje.

3.  **Autenticación:**
    *   Implementa el flujo **OAuth 2.0 Device Flow**.
    *   Si no existen credenciales, el agente inicia un proceso de registro y espera autorización.
    *   Gestiona automáticamente el almacenamiento seguro de tokens en `credentials.json`.

---

## 🐧 Instalación en Linux (CentOS 10 Stream)

Para facilitar el despliegue, se incluyen scripts que automatizan todo el proceso.

### 🚀 Instalación Automática (Recomendada)
1.  Sube la carpeta del agente al servidor.
2.  Ejecuta el script de instalación:
    ```bash
    chmod +x install.sh
    sudo ./install.sh
    ```
    Esto instalará dependencias, creará el usuario `wiseagent`, configurará el entorno en `/opt/metrics` y activará el servicio systemd automáticamente.

### 🗑️ Desinstalación
Para detener el servicio y eliminar todos los archivos y usuarios creados por el agente:
```bash
sudo ./uninstall.sh
```

### 🛠️ Instalación Manual (Detallada)
Si prefieres no usar los scripts, sigue estos pasos manuales:

#### 1. Preparar el Sistema
Instala Python 3 y las herramientas de desarrollo necesarias:
```bash
sudo dnf update -y
sudo dnf install python3 python3-pip -y
```

### 2. Crear Usuario y Directorio
Por seguridad, no ejecutaremos el agente como `root`.
```bash
# Crear usuario de sistema sin acceso a shell
sudo useradd --system --shell /sbin/nologin --home-dir /opt/metrics wiseagent

# Crear directorio de la aplicación
sudo mkdir -p /opt/metrics
```

### 3. Copiar Archivos e Instalar Dependencias
Copia los archivos de la carpeta `AGENTS` a `/opt/metrics` en el servidor. Luego:

```bash
cd /opt/metrics

# Crear entorno virtual
sudo python3 -m venv venv

# Instalar dependencias
sudo ./venv/bin/pip install requests psutil cryptography pydantic-settings

# Asignar permisos al usuario wiseagent
sudo chown -R wiseagent:wiseagent /opt/metrics
sudo chmod 750 /opt/metrics
```

### 4. Configurar Systemd
Crea el archivo de servicio `/etc/systemd/system/metrics-agent.service`.

*Nota: Si no has empaquetado la app con `setup.py`, asegúrate de que tu `ExecStart` en el archivo .service apunte directamente al script `main.py` así:*
`ExecStart=/opt/metrics/venv/bin/python /opt/metrics/main.py`

```bash
# Recargar demonios
sudo systemctl daemon-reload

# Habilitar e iniciar
sudo systemctl enable metrics-agent
sudo systemctl start metrics-agent

# Ver estado
sudo systemctl status metrics-agent
```

---

## 🪟 Instalación en Windows

### 1. Requisitos Previos
*   Tener instalado Python 3.9+.
*   Asegurarse de marcar "Add Python to PATH" durante la instalación.

### 2. Preparación
Abre **PowerShell** como Administrador y navega a la carpeta donde alojarás el agente (ej. `C:\WISE\Agents`).

```powershell
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno
.\venv\Scripts\Activate

# 3. Instalar dependencias
pip install requests psutil cryptography pydantic-settings
```

### 3. Ejecución Manual
Para probar el agente:
```powershell
python main.py
```

### 4. Ejecución en Segundo Plano (Opcional)
Para que se ejecute siempre al iniciar Windows, puedes usar el **Programador de Tareas (Task Scheduler)**:
1.  Crear una tarea básica que se inicie "Al arrancar el sistema".
2.  **Acción:** Iniciar programa.
3.  **Programa/Script:** `C:\WISE\Agents\venv\Scripts\python.exe` (Ruta absoluta al python del venv).
4.  **Argumentos:** `C:\WISE\Agents\main.py` (Ruta absoluta al script).
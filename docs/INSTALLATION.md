# 🛠️ Manual de Instalación - X Media Downloader

## 📋 Requisitos del Sistema

- **macOS** (El sistema está optimizado para macOS)
- **Python 3.12** (instalado via Homebrew)
- **Microsoft Edge** (para navegación automatizada)
- **Conexión a Internet** estable

---

## 🐍 Configuración del Entorno Python

### 1. Verificar la instalación de Python 3.12

Si ya tienes Python 3.12 instalado via Homebrew, verifica la ruta:

```bash
which python
# Debería mostrar: /opt/homebrew/opt/python@3.12/libexec/bin/python
```

Si no tienes Python 3.12, instálalo con Homebrew:

```bash
# Instalar Python 3.12 con Homebrew
brew install python@3.12

# Verificar la instalación
/opt/homebrew/opt/python@3.12/libexec/bin/python --version
```

### 2. Crear el Entorno Virtual

Navega al directorio del proyecto y crea el entorno virtual:

```bash
# Navegar al directorio del proyecto
cd /Volumes/SSDWD2T/projects/x_backup

# Crear el entorno virtual usando Python 3.12
/opt/homebrew/opt/python@3.12/libexec/bin/python -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Verificar que estás usando el Python correcto
which python
python --version  # Debería mostrar Python 3.12.x
```

### 3. Instalar las Dependencias

Con el entorno virtual activado, instala las dependencias:

```bash
# Actualizar pip a la última versión
pip install --upgrade pip

# Instalar las dependencias del proyecto
pip install -r requirements.txt

# Instalar los navegadores de Playwright
playwright install chromium
```

---

## 📦 Dependencias del Proyecto

### Dependencias Principales

- **`playwright>=1.40.0`**: Automatización del navegador para navegar X.com
- **`requests>=2.31.0`**: Descarga de archivos HTTP/HTTPS
- **`yt-dlp`**: Para descarga de videos (usado por `video_selector.py` y otros scripts de video)

### Dependencias Opcionales

- **`pytest>=7.4.0`**: Para ejecutar tests (solo para desarrollo)

---

## 🔧 Configuración Inicial

### 1. Configurar Microsoft Edge

El sistema requiere que tengas una sesión activa en X.com en Microsoft Edge:

1. Abre **Microsoft Edge**
2. Navega a [x.com](https://x.com)
3. **Inicia sesión** con tu cuenta
4. **Mantén la sesión abierta** (no cierres Edge)

### 2. Verificar la Instalación

Ejecuta este comando para verificar que todo está configurado correctamente:

```bash
# Verificar que los scripts funcionan
python edge_x_downloader_clean.py --help
python x_video_url_extractor.py --help
```

---

## 🚀 Comandos de Instalación Rápida

```bash
# 1. Clonar o navegar al directorio del proyecto
cd /Volumes/SSDWD2T/projects/x_backup

# 2. Crear entorno virtual con Python 3.12
/opt/homebrew/opt/python@3.12/libexec/bin/python -m venv .venv

# 3. Activar entorno virtual
source .venv/bin/activate

# 4. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 5. Instalar navegadores de Playwright
playwright install chromium

# 6. Verificar instalación
python edge_x_downloader_clean.py --help
```

---

## 🔄 Uso Diario

### Activar el Entorno Virtual

Cada vez que quieras usar los scripts, primero activa el entorno virtual:

```bash
cd /Volumes/SSDWD2T/projects/x_backup
source .venv/bin/activate
```

### Desactivar el Entorno Virtual

Cuando termines de usar los scripts:

```bash
deactivate
```

---

## 📁 Estructura del Proyecto

```
x_backup/
├── .venv/                          # Entorno virtual (creado tras la instalación)
├── requirements.txt                # Dependencias del proyecto
├── INSTALLATION.md                 # Este archivo
├── edge_x_downloader_clean.py      # Script principal de descarga de imágenes
├── manage_users.py                 # Gestión de usuarios configurables
├── video_selector.py               # Selector interactivo de videos desde caché
├── x_video_url_extractor.py        # Extractor de URLs de videos
├── manage_users.py                 # Gestión de usuarios configurables
├── simple_video_extractor.py       # Extractor simple de videos
├── quick_x_downloader.py           # Descargador rápido
├── x_media_automation.py           # Automatización completa
├── config_files/
│   └── x_usernames.json            # Configuración de usuarios
├── docs/
│   ├── MANUAL_COMPLETO.md          # Manual completo del sistema
│   ├── README_X_MEDIA_DOWNLOADER.md
│   └── TODO.md                     # Lista de mejoras futuras
└── test_files/                     # Archivos de prueba
```

---

## 🔧 Solución de Problemas

### Error: "playwright not found"

```bash
# Reinstalar playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

### Error: "Permission denied"

```bash
# Dar permisos de ejecución a los scripts
chmod +x *.py
```

### Error: "Microsoft Edge not found"

1. Asegúrate de que Microsoft Edge esté instalado
2. Verifica que tengas una sesión activa en X.com
3. No cierres Edge mientras ejecutas los scripts

### Error: "Module not found"

```bash
# Verificar que el entorno virtual esté activado
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

---

## 📊 Verificación de la Instalación

### Test Básico

```bash
# Activar entorno virtual
source .venv/bin/activate

# Verificar Python
python --version

# Verificar dependencias
python -c "import playwright; print('Playwright OK')"
python -c "import requests; print('Requests OK')"

# Verificar scripts
python edge_x_downloader_clean.py --list-users
```

### Test de Navegador

```bash
# Test de Playwright con navegador
python -c "
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        print('✅ Playwright y navegador funcionando correctamente')
        await browser.close()

asyncio.run(test())
"
```

---

## 🎯 Próximos Pasos

Una vez completada la instalación:

1. **Lee el manual completo**: `docs/MANUAL_COMPLETO.md`
2. **Configura usuarios**: `python manage_users.py`
3. **Prueba el sistema**: `python edge_x_downloader_clean.py --help`

---

## 📞 Soporte

### Errores Comunes

- **Error de permisos**: Usar `chmod +x *.py`
- **Entorno virtual no activo**: Ejecutar `source .venv/bin/activate`
- **Dependencias faltantes**: Ejecutar `pip install -r requirements.txt`
- **Navegador no encontrado**: Ejecutar `playwright install chromium`

### Logs de Debug

Para obtener información detallada de errores, ejecuta los scripts con output verbose:

```bash
python edge_x_downloader_clean.py --auto --temporal > debug.log 2>&1
```

---

**✅ ¡Instalación Completa!**

*Última actualización: 13 de junio de 2025*
*Versión: X Media Downloader v2.0*

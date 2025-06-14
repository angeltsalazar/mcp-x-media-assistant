#!/bin/bash

# Instalación del MCP Server para X Media Downloader
# Este script configura el servidor MCP y sus dependencias

echo "🚀 Instalando X Media Downloader MCP Server..."
echo "=" * 50

# Verificar que estamos en el directorio correcto
if [ ! -f "edge_x_downloader_clean.py" ]; then
    echo "❌ Error: No se encontró edge_x_downloader_clean.py"
    echo "   Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

# Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

# Verificar instalación de MCP
echo "🔍 Verificando instalación MCP..."
if python3 -c "import mcp" 2>/dev/null; then
    echo "✅ MCP SDK instalado correctamente"
else
    echo "⚠️ Instalando MCP SDK..."
    pip install mcp
fi

# Verificar Playwright
echo "🔍 Verificando Playwright..."
if python3 -c "import playwright" 2>/dev/null; then
    echo "✅ Playwright instalado"
    
    # Instalar navegadores si es necesario
    echo "🌐 Verificando navegadores de Playwright..."
    playwright install chromium
else
    echo "❌ Error: Playwright no está instalado correctamente"
    exit 1
fi

# Verificar yt-dlp
echo "🔍 Verificando yt-dlp..."
if command -v yt-dlp &> /dev/null; then
    echo "✅ yt-dlp encontrado: $(yt-dlp --version)"
else
    echo "⚠️ yt-dlp no encontrado. Instalando..."
    pip install yt-dlp
fi

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p config_files
mkdir -p cache
mkdir -p downloads

# Verificar permisos de ejecución
echo "🔧 Configurando permisos..."
chmod +x mcp_server.py
chmod +x edge_x_downloader_clean.py
chmod +x manage_users.py
chmod +x video_selector.py

# Probar el servidor MCP
echo "🧪 Probando servidor MCP..."
if python3 mcp_server.py --help &> /dev/null; then
    echo "✅ Servidor MCP funcional"
else
    echo "❌ Error: El servidor MCP no funciona correctamente"
    exit 1
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "1. Configurar usuarios:"
echo "   python3 manage_users.py"
echo ""
echo "2. Iniciar el servidor MCP:"
echo "   python3 mcp_server.py"
echo ""
echo "3. El servidor estará disponible en: http://localhost:8000"
echo ""
echo "🔧 Herramientas MCP disponibles:"
echo "   - manage_users: Gestionar usuarios"
echo "   - download_images: Descargar imágenes y extraer posts"
echo "   - select_videos: Seleccionar y descargar videos"
echo "   - system_status: Estado del sistema"
echo "   - system_config: Configuración del sistema"
echo ""
echo "📚 Ver documentación completa en: docs/MANUAL_COMPLETO.md"

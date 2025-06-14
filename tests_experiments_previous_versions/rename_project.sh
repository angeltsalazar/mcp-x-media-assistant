#!/bin/bash
# Script para renombrar proyecto y actualizar todas las rutas
# De x_backup a x_assistant_mcp

set -e  # Salir si hay error

OLD_NAME="x_backup"
NEW_NAME="x_assistant_mcp"
OLD_PATH="/Volumes/SSDWD2T/projects/$OLD_NAME"
NEW_PATH="/Volumes/SSDWD2T/projects/$NEW_NAME"

echo "🚀 Script de Renombramiento de Proyecto"
echo "======================================"
echo "De: $OLD_NAME → $NEW_NAME"
echo "Ruta: $OLD_PATH → $NEW_PATH"
echo

# Verificar que estamos en el directorio correcto
if [ ! -f "mcp_server_working.py" ]; then
    echo "❌ Error: No se encontró mcp_server_working.py"
    echo "   Ejecuta este script desde el directorio del proyecto"
    exit 1
fi

echo "✅ Directorio verificado"

# Paso 1: Crear backup
echo "📦 Creando backup..."
BACKUP_DIR="/tmp/x_backup_$(date +%Y%m%d_%H%M%S)"
cp -r . "$BACKUP_DIR"
echo "   Backup creado en: $BACKUP_DIR"

# Paso 2: Actualizar archivos usando Python
echo "🔧 Actualizando rutas en archivos..."
python3 update_project_paths.py

# Paso 3: Instrucciones manuales
echo
echo "🎯 PRÓXIMOS PASOS MANUALES:"
echo "=========================="
echo "1. Salir de VS Code completamente"
echo "2. Renombrar directorio:"
echo "   cd /Volumes/SSDWD2T/projects"
echo "   mv $OLD_NAME $NEW_NAME"
echo "3. Abrir VS Code en el nuevo directorio:"
echo "   code $NEW_PATH"
echo "4. Verificar servidor MCP:"
echo "   @x-media-downloader-local-backup test_tool"
echo
echo "📋 Archivos actualizados automáticamente:"
echo "   • .vscode/mcp.json"
echo "   • .vscode/settings.json" 
echo "   • mcp_server_working.py"
echo "   • video_selector.py"
echo "   • Scripts de testing"
echo
echo "⚠️  Si algo sale mal, restaura desde: $BACKUP_DIR"

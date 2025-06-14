#!/bin/bash

# Script para mover archivos relacionados con X Media Downloader
# Fecha: 12 de junio de 2025
# Autor: Asistente AI

set -e  # Salir en caso de error

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorios
SOURCE_DIR="/Volumes/SSDWD2T/projects/asistente_computadora"
BACKUP_DIR="/Volumes/SSDWD2T/projects/x_backup"
REPORT_FILE="${BACKUP_DIR}/move_report_$(date +%Y%m%d_%H%M%S).md"

# Crear estructura de directorios
echo -e "${BLUE}📁 Creando estructura de directorios...${NC}"
mkdir -p "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}/previous_versions"
mkdir -p "${BACKUP_DIR}/docs"
mkdir -p "${BACKUP_DIR}/docs_previous_versions"
mkdir -p "${BACKUP_DIR}/test_files"
mkdir -p "${BACKUP_DIR}/config_files"

# Función para copiar y verificar archivo
copy_and_verify() {
    local src="$1"
    local dst_dir="$2"
    local description="$3"
    
    if [[ -f "$src" ]]; then
        local filename=$(basename "$src")
        local dst="$dst_dir/$filename"
        
        echo -e "${YELLOW}📋 Copiando: $description${NC}"
        cp "$src" "$dst"
        
        # Verificar que los archivos son idénticos
        if cmp -s "$src" "$dst"; then
            echo -e "${GREEN}✅ Verificado: $filename${NC}"
            echo "- ✅ $description" >> "$REPORT_FILE"
            return 0
        else
            echo -e "${RED}❌ Error en verificación: $filename${NC}"
            echo "- ❌ ERROR: $description" >> "$REPORT_FILE"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  Archivo no encontrado: $src${NC}"
        echo "- ⚠️  No encontrado: $description" >> "$REPORT_FILE"
        return 1
    fi
}

# Función para eliminar archivo original después de verificar
remove_original() {
    local src="$1"
    local description="$2"
    
    if [[ -f "$src" ]]; then
        rm "$src"
        echo -e "${GREEN}🗑️  Eliminado original: $(basename "$src")${NC}"
        echo "- 🗑️  Eliminado: $description" >> "$REPORT_FILE"
    fi
}

# Inicializar reporte
echo "# Reporte de Migración X Media Downloader" > "$REPORT_FILE"
echo "**Fecha:** $(date)" >> "$REPORT_FILE"
echo "**Origen:** $SOURCE_DIR" >> "$REPORT_FILE"
echo "**Destino:** $BACKUP_DIR" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "## Archivos Procesados" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo -e "${BLUE}📝 Iniciando proceso de migración...${NC}"

# Array para almacenar archivos que se copiaron correctamente
declare -a COPIED_FILES=()

# SCRIPTS PRINCIPALES (versiones actuales/estables)
echo -e "${BLUE}📦 Copiando scripts principales...${NC}"
echo "### Scripts Principales" >> "$REPORT_FILE"

# Scripts principales activos
if copy_and_verify "$SOURCE_DIR/edge_x_downloader_clean.py" "$BACKUP_DIR" "Script principal de descarga de imágenes"; then
    COPIED_FILES+=("$SOURCE_DIR/edge_x_downloader_clean.py")
fi

if copy_and_verify "$SOURCE_DIR/x_video_url_extractor.py" "$BACKUP_DIR" "Extractor de URLs de videos"; then
    COPIED_FILES+=("$SOURCE_DIR/x_video_url_extractor.py")
fi

if copy_and_verify "$SOURCE_DIR/x_media_automation.py" "$BACKUP_DIR" "Automatización de descarga de medios"; then
    COPIED_FILES+=("$SOURCE_DIR/x_media_automation.py")
fi

if copy_and_verify "$SOURCE_DIR/x_media_downloader.py" "$BACKUP_DIR" "Descargador de medios general"; then
    COPIED_FILES+=("$SOURCE_DIR/x_media_downloader.py")
fi

if copy_and_verify "$SOURCE_DIR/x_media_downloader_mcp.py" "$BACKUP_DIR" "Descargador de medios con MCP"; then
    COPIED_FILES+=("$SOURCE_DIR/x_media_downloader_mcp.py")
fi

if copy_and_verify "$SOURCE_DIR/quick_x_downloader.py" "$BACKUP_DIR" "Descargador rápido"; then
    COPIED_FILES+=("$SOURCE_DIR/quick_x_downloader.py")
fi

if copy_and_verify "$SOURCE_DIR/simple_x_downloader.py" "$BACKUP_DIR" "Descargador simple"; then
    COPIED_FILES+=("$SOURCE_DIR/simple_x_downloader.py")
fi

if copy_and_verify "$SOURCE_DIR/mcp_x_downloader.py" "$BACKUP_DIR" "Descargador MCP"; then
    COPIED_FILES+=("$SOURCE_DIR/mcp_x_downloader.py")
fi

# VERSIONES ANTERIORES
echo -e "${BLUE}📦 Copiando versiones anteriores...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Versiones Anteriores" >> "$REPORT_FILE"

# Versiones numeradas de edge_x_downloader_clean
for version in v0.1.0 v0.1.1 v0.1.2 v0.1.3 v0.1.4; do
    if copy_and_verify "$SOURCE_DIR/edge_x_downloader_clean_${version}.py" "$BACKUP_DIR/previous_versions" "Edge X Downloader Clean $version"; then
        COPIED_FILES+=("$SOURCE_DIR/edge_x_downloader_clean_${version}.py")
    fi
done

# Otras versiones
if copy_and_verify "$SOURCE_DIR/edge_x_downloader_clean_backup.py" "$BACKUP_DIR/previous_versions" "Backup del descargador edge"; then
    COPIED_FILES+=("$SOURCE_DIR/edge_x_downloader_clean_backup.py")
fi

if copy_and_verify "$SOURCE_DIR/edge_x_downloader.py" "$BACKUP_DIR/previous_versions" "Descargador edge original"; then
    COPIED_FILES+=("$SOURCE_DIR/edge_x_downloader.py")
fi

if copy_and_verify "$SOURCE_DIR/edge_x_downloader_v0.1.0.py" "$BACKUP_DIR/previous_versions" "Edge X Downloader v0.1.0"; then
    COPIED_FILES+=("$SOURCE_DIR/edge_x_downloader_v0.1.0.py")
fi

# Video selectors antiguos
if copy_and_verify "$SOURCE_DIR/video_selector_v0.1.0.py" "$BACKUP_DIR/previous_versions" "Video Selector v0.1.0"; then
    COPIED_FILES+=("$SOURCE_DIR/video_selector_v0.1.0.py")
fi

if copy_and_verify "$SOURCE_DIR/video_selector_v0.1.1.py" "$BACKUP_DIR/previous_versions" "Video Selector v0.1.1"; then
    COPIED_FILES+=("$SOURCE_DIR/video_selector_v0.1.1.py")
fi

# ARCHIVOS DE CONFIGURACIÓN
echo -e "${BLUE}📦 Copiando archivos de configuración...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Archivos de Configuración" >> "$REPORT_FILE"

if copy_and_verify "$SOURCE_DIR/x_usernames.json" "$BACKUP_DIR/config_files" "Configuración de usuarios X"; then
    COPIED_FILES+=("$SOURCE_DIR/x_usernames.json")
fi

# ARCHIVOS DE PRUEBA
echo -e "${BLUE}📦 Copiando archivos de prueba...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Archivos de Prueba" >> "$REPORT_FILE"

# Archivos de test relacionados con X
test_files=(
    "test_x_navigation.py"
    "test_edge_media_extraction.py"
    "test_script_url_cleaning.py"
    "test_filename_extraction.py"
    "test_hybrid_extraction_v4.py"
)

for test_file in "${test_files[@]}"; do
    if copy_and_verify "$SOURCE_DIR/$test_file" "$BACKUP_DIR/test_files" "Archivo de prueba: $test_file"; then
        COPIED_FILES+=("$SOURCE_DIR/$test_file")
    fi
done

# DOCUMENTACIÓN PRINCIPAL
echo -e "${BLUE}📦 Copiando documentación principal...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Documentación Principal" >> "$REPORT_FILE"

if copy_and_verify "$SOURCE_DIR/README_X_MEDIA_DOWNLOADER.md" "$BACKUP_DIR/docs" "Manual principal X Media Downloader"; then
    COPIED_FILES+=("$SOURCE_DIR/README_X_MEDIA_DOWNLOADER.md")
fi

if copy_and_verify "$SOURCE_DIR/MANUAL_COMPLETO.md" "$BACKUP_DIR/docs" "Manual completo del sistema"; then
    COPIED_FILES+=("$SOURCE_DIR/MANUAL_COMPLETO.md")
fi

# DOCUMENTACIÓN ANTERIOR/RELACIONADA
echo -e "${BLUE}📦 Copiando documentación anterior...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Documentación Anterior/Relacionada" >> "$REPORT_FILE"

related_docs=(
    "README_VIDEO_DOWNLOADER.md"
    "README_SISTEMA_SIMPLIFICADO.md"
    "README_USUARIOS_CONFIGURABLES.md"
    "RESUMEN_MEJORAS_EDGE_DOWNLOADER.md"
    "RESOLUCION_PROBLEMA_NAME_360x360.md"
    "RESOLUCION_PROBLEMA_NOMBRES_ARCHIVO.md"
)

for doc in "${related_docs[@]}"; do
    if copy_and_verify "$SOURCE_DIR/$doc" "$BACKUP_DIR/docs_previous_versions" "Documentación: $doc"; then
        COPIED_FILES+=("$SOURCE_DIR/$doc")
    fi
done

# ARCHIVOS ADICIONALES RELACIONADOS
echo -e "${BLUE}📦 Copiando archivos adicionales...${NC}"
echo "" >> "$REPORT_FILE"
echo "### Archivos Adicionales" >> "$REPORT_FILE"

additional_files=(
    "video_selector.py"
    "demo_final_edge_downloader.py"
    "ejemplo_video_downloader.py"
    "demo_video_extractor.py"
    "diagnose_edge_profiles.py"
)

for additional_file in "${additional_files[@]}"; do
    if copy_and_verify "$SOURCE_DIR/$additional_file" "$BACKUP_DIR/previous_versions" "Archivo adicional: $additional_file"; then
        COPIED_FILES+=("$SOURCE_DIR/$additional_file")
    fi
done

# RESUMEN DEL PROCESO
echo "" >> "$REPORT_FILE"
echo "## Resumen del Proceso" >> "$REPORT_FILE"
echo "**Archivos copiados exitosamente:** ${#COPIED_FILES[@]}" >> "$REPORT_FILE"
echo "**Archivos verificados:** ${#COPIED_FILES[@]}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# ELIMINACIÓN DE ARCHIVOS ORIGINALES
echo -e "${BLUE}🗑️  Eliminando archivos originales verificados...${NC}"
echo "## Archivos Originales Eliminados" >> "$REPORT_FILE"

for file in "${COPIED_FILES[@]}"; do
    remove_original "$file" "$(basename "$file")"
done

# ESTRUCTURA FINAL
echo "" >> "$REPORT_FILE"
echo "## Estructura Final" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"
tree "$BACKUP_DIR" >> "$REPORT_FILE" 2>/dev/null || ls -la "$BACKUP_DIR" >> "$REPORT_FILE"
echo '```' >> "$REPORT_FILE"

# INSTRUCCIONES FINALES
echo "" >> "$REPORT_FILE"
echo "## Instrucciones de Uso" >> "$REPORT_FILE"
echo "1. Los scripts principales están en la raíz: \`$BACKUP_DIR/\`" >> "$REPORT_FILE"
echo "2. Las versiones anteriores están en: \`$BACKUP_DIR/previous_versions/\`" >> "$REPORT_FILE"
echo "3. La documentación actual está en: \`$BACKUP_DIR/docs/\`" >> "$REPORT_FILE"
echo "4. La documentación anterior está en: \`$BACKUP_DIR/docs_previous_versions/\`" >> "$REPORT_FILE"
echo "5. Los archivos de prueba están en: \`$BACKUP_DIR/test_files/\`" >> "$REPORT_FILE"
echo "6. La configuración está en: \`$BACKUP_DIR/config_files/\`" >> "$REPORT_FILE"

# MENSAJE FINAL
echo -e "${GREEN}✅ Proceso completado exitosamente!${NC}"
echo -e "${BLUE}📊 Reporte generado en: $REPORT_FILE${NC}"
echo -e "${BLUE}📁 Archivos migrados a: $BACKUP_DIR${NC}"
echo -e "${YELLOW}💡 Los archivos originales han sido eliminados después de verificar la copia${NC}"

# Mostrar resumen
echo -e "${BLUE}🎯 RESUMEN:${NC}"
echo -e "${GREEN}• Archivos copiados y verificados: ${#COPIED_FILES[@]}${NC}"
echo -e "${GREEN}• Archivos originales eliminados: ${#COPIED_FILES[@]}${NC}"
echo -e "${GREEN}• Estructura organizada en: $BACKUP_DIR${NC}"

exit 0

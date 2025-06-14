#!/usr/bin/env python3
"""
Script para actualizar rutas después del cambio de nombre del proyecto
De: x_backup -> x_assistant_mcp
"""

import os
import json
import re
from pathlib import Path


def update_project_paths():
    """Actualiza todas las rutas del proyecto tras cambio de nombre."""

    # Definir rutas
    old_path = "/Volumes/SSDWD2T/projects/x_backup"
    new_path = "/Volumes/SSDWD2T/projects/x_assistant_mcp"

    print("🔄 Actualizando rutas del proyecto...")
    print(f"   De: {old_path}")
    print(f"   A:  {new_path}")
    print()

    # Archivos críticos que DEBEN actualizarse
    critical_files = [
        ".vscode/mcp.json",
        ".vscode/settings.json",
        "mcp_server_working.py",
        "video_selector.py",
    ]

    # Archivos opcionales (testing y documentación)
    optional_files = [
        "test_tools.py",
        "test_simple_server.py",
        "verify_mcp_status.py",
        "mcp_config.json",
        ".vscode/mcp_with_permissions.json",
        "docs/INSTALLATION.md",
    ]

    updated_files = []
    errors = []

    # Actualizar archivos críticos
    print("🔧 Actualizando archivos críticos...")
    for file_path in critical_files:
        if update_file_paths(file_path, old_path, new_path):
            updated_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            errors.append(file_path)
            print(f"   ❌ {file_path} - Error o no encontrado")

    # Actualizar archivos opcionales
    print(f"\n🧪 Actualizando archivos opcionales...")
    for file_path in optional_files:
        if update_file_paths(file_path, old_path, new_path):
            updated_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            print(f"   ⚠️  {file_path} - No encontrado o ya actualizado")

    # Resumen
    print(f"\n📊 Resumen:")
    print(f"   ✅ Archivos actualizados: {len(updated_files)}")
    print(f"   ❌ Errores: {len(errors)}")

    if updated_files:
        print(f"\n📋 Archivos modificados:")
        for file in updated_files:
            print(f"   • {file}")

    if errors:
        print(f"\n⚠️  Archivos con errores:")
        for file in errors:
            print(f"   • {file}")

    print(f"\n🎯 Próximos pasos:")
    print(f"   1. Renombrar directorio: mv x_backup x_assistant_mcp")
    print(f"   2. Reiniciar VS Code")
    print(f"   3. Verificar que el servidor MCP funciona")


def update_file_paths(file_path, old_path, new_path):
    """Actualiza las rutas en un archivo específico."""
    try:
        file_obj = Path(file_path)
        if not file_obj.exists():
            return False

        # Leer contenido
        with open(file_obj, "r", encoding="utf-8") as f:
            content = f.read()

        # Reemplazar rutas
        updated_content = content.replace(old_path, new_path)

        # Solo escribir si hay cambios
        if updated_content != content:
            with open(file_obj, "w", encoding="utf-8") as f:
                f.write(updated_content)
            return True

        return False  # No había cambios necesarios

    except Exception as e:
        print(f"      Error procesando {file_path}: {e}")
        return False


def preview_changes():
    """Muestra una vista previa de los cambios que se realizarán."""
    old_path = "/Volumes/SSDWD2T/projects/x_backup"
    new_path = "/Volumes/SSDWD2T/projects/x_assistant_mcp"

    print("🔍 Vista previa de cambios:")
    print("=" * 50)

    files_to_check = [
        ".vscode/mcp.json",
        ".vscode/settings.json",
        "mcp_server_working.py",
        "video_selector.py",
    ]

    for file_path in files_to_check:
        file_obj = Path(file_path)
        if file_obj.exists():
            with open(file_obj, "r") as f:
                content = f.read()

            if old_path in content:
                print(f"\n📄 {file_path}:")
                lines = content.split("\n")
                for i, line in enumerate(lines, 1):
                    if old_path in line:
                        print(f"   Línea {i}: {line.strip()}")
                        print(f"   →        {line.replace(old_path, new_path).strip()}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        preview_changes()
    else:
        update_project_paths()

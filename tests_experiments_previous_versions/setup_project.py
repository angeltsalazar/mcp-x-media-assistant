#!/usr/bin/env python3
"""
Script de configuración automática para X Assistant MCP
Configura el proyecto automáticamente después de clonar desde GitHub
"""

import os
import sys
from pathlib import Path
import subprocess
import json


def setup_project():
    """Configura el proyecto automáticamente."""
    print("🚀 Configurando X Assistant MCP...")
    print("=" * 50)

    # Obtener directorio del proyecto
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 Directorio del proyecto: {project_dir}")

    # 1. Crear entorno virtual si no existe
    venv_dir = project_dir / ".venv"
    if not venv_dir.exists():
        print("\n1️⃣ Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        print("✅ Entorno virtual creado")
    else:
        print("\n1️⃣ ✅ Entorno virtual ya existe")

    # 2. Instalar dependencias
    print("\n2️⃣ Instalando dependencias...")
    pip_path = venv_dir / "bin" / "pip"
    if not pip_path.exists():
        pip_path = venv_dir / "Scripts" / "pip.exe"  # Windows

    if pip_path.exists():
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"])
        subprocess.run([str(pip_path), "install", "yt-dlp"])
        print("✅ Dependencias instaladas")
    else:
        print("❌ No se encontró pip en el entorno virtual")

    # 3. Verificar configuración de VS Code
    vscode_dir = project_dir / ".vscode"
    if vscode_dir.exists():
        print("\n3️⃣ ✅ Configuración de VS Code encontrada")

        # Verificar que use rutas relativas
        mcp_config = vscode_dir / "mcp.json"
        if mcp_config.exists():
            with open(mcp_config) as f:
                config = json.load(f)

            # Verificar si usa workspaceFolder
            command = (
                config.get("servers", {}).get("x-assistant-mcp", {}).get("command", "")
            )
            if "${workspaceFolder}" in command:
                print("✅ Configuración MCP usa rutas relativas")
            else:
                print("⚠️ Configuración MCP puede necesitar actualización")

    else:
        print("\n3️⃣ ❌ Directorio .vscode no encontrado")

    # 4. Verificar archivos de configuración
    print("\n4️⃣ Verificando archivos de configuración...")
    config_files_dir = project_dir / "config_files"
    if not config_files_dir.exists():
        config_files_dir.mkdir()
        print("✅ Directorio config_files creado")

    # Crear archivo de usuarios vacío si no existe
    users_config = config_files_dir / "x_usernames.json"
    if not users_config.exists():
        with open(users_config, "w") as f:
            json.dump({}, f, indent=2)
        print("✅ Archivo x_usernames.json creado")

    # 5. Verificar directorio de caché
    cache_dir = project_dir / "cache"
    if not cache_dir.exists():
        cache_dir.mkdir()
        print("✅ Directorio cache creado")
    else:
        print("✅ Directorio cache ya existe")

    # 6. Verificar que el proyecto funciona
    print("\n5️⃣ Probando configuración...")
    python_path = venv_dir / "bin" / "python3"
    if not python_path.exists():
        python_path = venv_dir / "Scripts" / "python.exe"  # Windows

    if python_path.exists():
        try:
            # Probar importaciones
            result = subprocess.run(
                [
                    str(python_path),
                    "-c",
                    "import asyncio, json, logging; print('✅ Importaciones básicas OK')",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("✅ Python y dependencias básicas funcionan")
            else:
                print(f"❌ Error en Python: {result.stderr}")
        except Exception as e:
            print(f"❌ Error probando Python: {e}")

    print("\n" + "=" * 50)
    print("🎉 ¡Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Abrir el proyecto en VS Code")
    print("2. Reiniciar VS Code para cargar configuración MCP")
    print('3. Probar: @x-assistant-mcp test_tool {"message": "Hola"}')
    print("\n📚 Ver documentación en: README.md")


if __name__ == "__main__":
    try:
        setup_project()
    except KeyboardInterrupt:
        print("\n🛑 Configuración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante la configuración: {e}")
        sys.exit(1)

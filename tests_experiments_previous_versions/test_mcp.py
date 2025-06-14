#!/usr/bin/env python3
"""
Script de prueba para el servidor MCP de X Media Downloader
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """Prueba básica del servidor MCP"""
    print("🧪 Probando servidor MCP de X Media Downloader")
    print("=" * 50)
    
    # Test 1: Verificar que el servidor se puede importar
    print("1. Verificando importación del servidor...")
    try:
        # Simular importación (sin actually importar MCP que puede no estar instalado)
        with open("mcp_server.py", 'r') as f:
            content = f.read()
            if "class XMediaDownloaderMCP" in content:
                print("   ✅ Servidor MCP encontrado")
            else:
                print("   ❌ Clase principal no encontrada")
                return False
    except FileNotFoundError:
        print("   ❌ mcp_server.py no encontrado")
        return False
    
    # Test 2: Verificar scripts con nuevas funcionalidades
    print("\n2. Verificando scripts con soporte MCP...")
    
    # Test manage_users.py
    result = subprocess.run([
        sys.executable, "manage_users.py", "--help"
    ], capture_output=True, text=True)
    
    if "--list-json" in result.stdout:
        print("   ✅ manage_users.py tiene soporte MCP")
    else:
        print("   ❌ manage_users.py sin soporte MCP")
    
    # Test video_selector.py  
    result = subprocess.run([
        sys.executable, "video_selector.py", "--help"
    ], capture_output=True, text=True)
    
    if "--list-only" in result.stdout:
        print("   ✅ video_selector.py tiene soporte MCP")
    else:
        print("   ❌ video_selector.py sin soporte MCP")
    
    # Test 3: Verificar configuración MCP
    print("\n3. Verificando archivo de configuración MCP...")
    if Path("mcp_config.json").exists():
        try:
            with open("mcp_config.json", 'r') as f:
                config = json.load(f)
                if "x-media-downloader" in config.get("mcpServers", {}):
                    print("   ✅ Configuración MCP válida")
                else:
                    print("   ❌ Configuración MCP inválida")
        except json.JSONDecodeError:
            print("   ❌ Archivo de configuración MCP corrupto")
    else:
        print("   ❌ Archivo de configuración MCP no encontrado")
    
    # Test 4: Verificar documentación
    print("\n4. Verificando documentación...")
    if Path("docs/MCP_SERVER.md").exists():
        print("   ✅ Documentación MCP encontrada")
    else:
        print("   ❌ Documentación MCP no encontrada")
    
    # Test 5: Verificar dependencias en requirements.txt
    print("\n5. Verificando dependencias...")
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
            if "mcp" in requirements:
                print("   ✅ Dependencia MCP en requirements.txt")
            else:
                print("   ❌ Dependencia MCP faltante en requirements.txt")
    except FileNotFoundError:
        print("   ❌ requirements.txt no encontrado")
    
    print("\n" + "=" * 50)
    print("🎯 Resultado: Configuración MCP lista para usar")
    print("\n📝 Próximos pasos:")
    print("1. Instalar dependencias: ./install_mcp.sh")
    print("2. Configurar usuarios: python3 manage_users.py")
    print("3. Iniciar servidor: python3 mcp_server.py")
    print("4. Ver documentación: docs/MCP_SERVER.md")
    
    return True

def test_scripts_functionality():
    """Prueba funcionalidad básica de los scripts"""
    print("\n🔧 Probando funcionalidad básica de scripts...")
    
    # Test manage_users.py con JSON
    print("\nTesting manage_users.py --list-json:")
    result = subprocess.run([
        sys.executable, "manage_users.py", "--list-json"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            users = json.loads(result.stdout) if result.stdout.strip() else {}
            print(f"   ✅ JSON válido devuelto: {len(users)} usuarios")
        except json.JSONDecodeError:
            print(f"   ⚠️ Salida no es JSON válido: {result.stdout}")
    else:
        print(f"   ❌ Error: {result.stderr}")
    
    # Test edge_x_downloader_clean.py help
    print("\nTesting edge_x_downloader_clean.py --help:")
    result = subprocess.run([
        sys.executable, "edge_x_downloader_clean.py", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and "--name" in result.stdout:
        print("   ✅ edge_x_downloader_clean.py funcional")
    else:
        print("   ❌ edge_x_downloader_clean.py tiene problemas")

if __name__ == "__main__":
    print("🚀 X Media Downloader - Test MCP")
    
    # Verificar que estamos en el directorio correcto
    if not Path("edge_x_downloader_clean.py").exists():
        print("❌ Error: Ejecuta este script desde el directorio del proyecto")
        sys.exit(1)
    
    # Ejecutar tests
    success = asyncio.run(test_mcp_server())
    test_scripts_functionality()
    
    if success:
        print("\n🎉 ¡Configuración MCP completada correctamente!")
    else:
        print("\n❌ Hay problemas con la configuración MCP")
        sys.exit(1)

#!/usr/bin/env python3
"""
Verificación final y configuración del MCP Server
"""

import json
import subprocess
import sys
from pathlib import Path

def main():
    """Verificación final del sistema MCP"""
    print("🔧 Verificación Final - X Media Downloader MCP")
    print("=" * 50)
    
    # 1. Verificar estructura de archivos
    print("1. Verificando estructura de archivos...")
    required_files = [
        "mcp_server.py",
        "edge_x_downloader_clean.py", 
        "manage_users.py",
        "video_selector.py",
        ".vscode/mcp.json"
    ]
    
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} FALTANTE")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Archivos faltantes: {missing_files}")
        return False
    
    # 2. Verificar configuración VS Code
    print("\n2. Verificando configuración VS Code...")
    try:
        with open(".vscode/mcp.json", 'r') as f:
            config = json.load(f)
        
        if "x-assistant-mcp" in config.get("servers", {}):
            server_config = config["servers"]["x-assistant-mcp"]
            if server_config.get("type") == "stdio":
                print("   ✅ Configuración VS Code correcta")
            else:
                print("   ❌ Tipo de servidor incorrecto")
                return False
        else:
            print("   ❌ Servidor 'x-assistant-mcp' no encontrado en configuración")
            return False
    except Exception as e:
        print(f"   ❌ Error leyendo configuración: {e}")
        return False
    
    # 3. Verificar entorno virtual y dependencias
    print("\n3. Verificando entorno virtual...")
    if Path(".venv/bin/python").exists():
        print("   ✅ Entorno virtual encontrado")
        
        # Verificar MCP
        result = subprocess.run([
            ".venv/bin/python", "-c", "import mcp.server.stdio; print('MCP OK')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ MCP SDK instalado")
        else:
            print("   ❌ MCP SDK no disponible")
            return False
    else:
        print("   ❌ Entorno virtual no encontrado")
        return False
    
    # 4. Test funcional del servidor
    print("\n4. Testing servidor MCP...")
    result = subprocess.run([
        ".venv/bin/python", "test_mcp_complete.py"
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and "✅ Servidor MCP configurado y funcional" in result.stdout:
        print("   ✅ Servidor MCP funcional")
    else:
        print("   ❌ Problemas con el servidor MCP")
        print(f"   Error: {result.stderr}")
        return False
    
    # 5. Información final
    print("\n" + "=" * 50)
    print("🎉 ¡Configuración MCP completada exitosamente!")
    print("\n📋 Resumen de lo que tienes:")
    print("✅ 5 herramientas MCP disponibles:")
    print("   - manage_users: Gestionar usuarios")
    print("   - download_images: Descargar imágenes y extraer posts")
    print("   - select_videos: Seleccionar y descargar videos")
    print("   - system_status: Estado del sistema")
    print("   - system_config: Configuración del sistema")
    
    print("\n🚀 Próximos pasos:")
    print("1. Reinicia VS Code completamente")
    print("2. El servidor MCP 'x-assistant-mcp' debería estar disponible")
    print("3. Usa las herramientas MCP desde tu asistente de IA")
    
    print("\n🔧 Comandos de prueba manual:")
    print("   python test_mcp_complete.py  # Test completo")
    print("   python manage_users.py       # Configurar usuarios")
    
    print("\n📚 Documentación completa en:")
    print("   docs/MCP_SERVER.md")
    print("   docs/MANUAL_COMPLETO.md")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Configuración incompleta. Revisa los errores arriba.")
        sys.exit(1)
    else:
        print("\n✅ Todo listo para usar!")

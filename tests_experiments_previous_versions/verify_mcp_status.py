#!/usr/bin/env python3
"""
Script para verificar el estado del servidor MCP
"""

import subprocess
import sys
import time
import os

def check_mcp_status():
    """Verifica el estado del servidor MCP"""
    
    print("=== VERIFICACIÓN DEL SERVIDOR MCP ===\n")
    
    # 1. Verificar que el archivo del servidor existe
    server_path = "/Volumes/SSDWD2T/projects/x_backup/mcp_server_working.py"
    if os.path.exists(server_path):
        print(f"✅ Servidor encontrado: {server_path}")
    else:
        print(f"❌ Servidor NO encontrado: {server_path}")
        return False
    
    # 2. Verificar que el intérprete de Python existe
    python_path = "/Volumes/SSDWD2T/projects/x_backup/.venv/bin/python3"
    if os.path.exists(python_path):
        print(f"✅ Python encontrado: {python_path}")
    else:
        print(f"❌ Python NO encontrado: {python_path}")
        return False
    
    # 3. Verificar que el servidor se puede ejecutar
    try:
        result = subprocess.run([
            python_path, "-c", 
            "import sys; sys.path.insert(0, '.'); import mcp_server_working; print('✅ Servidor se puede importar')"
        ], capture_output=True, text=True, timeout=5, cwd="/Volumes/SSDWD2T/projects/x_backup")
        
        if result.returncode == 0:
            print("✅ Servidor se puede ejecutar correctamente")
        else:
            print(f"❌ Error ejecutando servidor: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout ejecutando servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False
    
    # 4. Verificar configuración MCP
    config_path = "/Volumes/SSDWD2T/projects/x_backup/.vscode/mcp.json"
    if os.path.exists(config_path):
        print(f"✅ Configuración MCP encontrada: {config_path}")
        with open(config_path, 'r') as f:
            content = f.read()
            if "x-media-downloader-local-backup" in content:
                print("✅ Configuración contiene el servidor correcto")
            else:
                print("❌ Configuración no contiene el servidor esperado")
                return False
    else:
        print(f"❌ Configuración MCP NO encontrada: {config_path}")
        return False
    
    print("\n🎉 Todas las verificaciones pasaron correctamente!")
    print("\n📋 SIGUIENTES PASOS:")
    print("1. El servidor MCP debería estar disponible en VS Code")
    print("2. Busca en VS Code: Ctrl+Shift+P (Cmd+Shift+P) -> 'MCP'")
    print("3. O verifica en la barra de estado de VS Code")
    print("4. Prueba usar '@x-media-downloader-local-backup' en el chat")
    
    return True

if __name__ == "__main__":
    check_mcp_status()

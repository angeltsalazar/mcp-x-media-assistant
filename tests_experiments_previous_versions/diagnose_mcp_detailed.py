#!/usr/bin/env python3
"""
Diagnóstico detallado del servidor MCP
"""

import sys
import os
import json
import asyncio
from pathlib import Path

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def main():
    print_section("DIAGNÓSTICO DETALLADO MCP SERVER")
    
    # 1. Verificar Python y ubicación
    print_section("1. INFORMACIÓN DE PYTHON")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # 2. Verificar entorno virtual
    print_section("2. ENTORNO VIRTUAL")
    venv_path = Path("/Volumes/SSDWD2T/projects/x_backup/.venv")
    if venv_path.exists():
        print(f"✓ Entorno virtual encontrado: {venv_path}")
        python_exec = venv_path / "bin" / "python3"
        if python_exec.exists():
            print(f"✓ Python ejecutable: {python_exec}")
        else:
            print(f"✗ Python ejecutable no encontrado: {python_exec}")
    else:
        print(f"✗ Entorno virtual no encontrado: {venv_path}")
    
    # 3. Verificar dependencias MCP
    print_section("3. DEPENDENCIAS MCP")
    try:
        import mcp
        print(f"✓ MCP instalado: {mcp.__file__}")
    except ImportError as e:
        print(f"✗ MCP no instalado: {e}")
        return
    
    try:
        from mcp.server.stdio import stdio_server
        from mcp.server import Server
        print("✓ Componentes MCP importados correctamente")
    except ImportError as e:
        print(f"✗ Error importando componentes MCP: {e}")
        return
    
    # 4. Verificar servidor MCP
    print_section("4. SERVIDOR MCP")
    try:
        import mcp_server
        print("✓ mcp_server.py se puede importar")
        
        # Probar lista de herramientas
        async def test_tools():
            try:
                tools = await mcp_server.handle_list_tools()
                print(f"✓ Herramientas disponibles: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool.name}")
                return True
            except Exception as e:
                print(f"✗ Error listando herramientas: {e}")
                return False
        
        success = asyncio.run(test_tools())
        if not success:
            return
            
    except Exception as e:
        print(f"✗ Error importando mcp_server: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Verificar configuración VS Code
    print_section("5. CONFIGURACIÓN VS CODE")
    mcp_config = Path(".vscode/mcp.json")
    if mcp_config.exists():
        print(f"✓ Archivo de configuración encontrado: {mcp_config}")
        try:
            with open(mcp_config) as f:
                config = json.load(f)
            print("✓ Configuración JSON válida")
            print(f"Contenido:\n{json.dumps(config, indent=2)}")
        except Exception as e:
            print(f"✗ Error leyendo configuración: {e}")
    else:
        print(f"✗ Archivo de configuración no encontrado: {mcp_config}")
    
    # 6. Verificar archivos necesarios
    print_section("6. ARCHIVOS DEL PROYECTO")
    required_files = [
        "mcp_server.py",
        "requirements.txt",
        ".venv/bin/python3"
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
    
    # 7. Prueba de conectividad MCP
    print_section("7. PRUEBA DE CONECTIVIDAD")
    print("Intentando crear servidor MCP...")
    try:
        server = mcp_server.server
        print(f"✓ Servidor MCP creado: {server.name}")
    except Exception as e:
        print(f"✗ Error creando servidor: {e}")
        return
    
    print_section("DIAGNÓSTICO COMPLETADO")
    print("Si todos los elementos muestran ✓, el servidor debería funcionar correctamente.")
    print("Si hay errores ✗, revisa esos componentes específicos.")

if __name__ == "__main__":
    main()

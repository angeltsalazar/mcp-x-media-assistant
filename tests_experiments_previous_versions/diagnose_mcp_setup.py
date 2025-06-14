#!/usr/bin/env python3
"""
Verificador de MCP Setup - Diagnóstico completo
"""

import json
import subprocess
import sys
from pathlib import Path
import importlib

def check_mcp_dependencies():
    """Verifica que las dependencias de MCP estén instaladas"""
    print("🔍 Verificando dependencias MCP...")
    
    try:
        import mcp
        print("   ✅ MCP SDK instalado")
        return True
    except ImportError:
        print("   ❌ MCP SDK no encontrado")
        print("   💡 Instala con: pip install mcp")
        return False

def check_server_syntax():
    """Verifica que el servidor no tenga errores de sintaxis"""
    print("🔍 Verificando sintaxis del servidor...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", "mcp_server.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("   ✅ Sintaxis correcta")
            return True
        else:
            print(f"   ❌ Error de sintaxis: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Error verificando sintaxis: {e}")
        return False

def check_vscode_config():
    """Verifica la configuración de VS Code"""
    print("🔍 Verificando configuración de VS Code...")
    
    config_path = Path(".vscode/mcp.json")
    if not config_path.exists():
        print("   ❌ Archivo .vscode/mcp.json no encontrado")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "servers" not in config:
            print("   ❌ Configuración inválida: falta 'servers'")
            return False
        
        servers = config["servers"]
        if not servers:
            print("   ❌ No hay servidores configurados")
            return False
        
        print(f"   ✅ Configuración válida con {len(servers)} servidor(es)")
        for name, server_config in servers.items():
            print(f"      - {name}: {server_config.get('command', 'N/A')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Error de JSON: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error leyendo configuración: {e}")
        return False

def test_server_execution():
    """Prueba ejecutar el servidor brevemente"""
    print("🔍 Probando ejecución del servidor...")
    
    try:
        # Ejecutar el test completo
        result = subprocess.run([
            sys.executable, "test_mcp_complete.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent, timeout=10)
        
        if result.returncode == 0 and "funcional" in result.stdout:
            print("   ✅ Servidor ejecutable y funcional")
            return True
        else:
            print(f"   ❌ Error ejecutando servidor: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Test de servidor tardó demasiado (posible problema)")
        return False
    except Exception as e:
        print(f"   ❌ Error probando servidor: {e}")
        return False

def check_python_environment():
    """Verifica el entorno de Python"""
    print("🔍 Verificando entorno de Python...")
    
    print(f"   Python: {sys.executable}")
    print(f"   Versión: {sys.version}")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        print("   ✅ Entorno virtual detectado")
        return True
    else:
        print("   ⚠️  No se detectó entorno virtual")
        return True

def main():
    """Función principal de verificación"""
    print("🚀 Diagnóstico Completo del Servidor MCP")
    print("=" * 50)
    
    checks = [
        ("Entorno Python", check_python_environment),
        ("Dependencias MCP", check_mcp_dependencies),
        ("Sintaxis del servidor", check_server_syntax),
        ("Configuración VS Code", check_vscode_config),
        ("Ejecución del servidor", test_server_execution),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error en {name}: {e}")
            results.append((name, False))
        print()
    
    print("📊 Resumen del Diagnóstico")
    print("=" * 30)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ¡Todos los checks pasaron! El servidor MCP debería funcionar correctamente.")
        print("💡 Si sigues viendo errores:")
        print("   1. Reinicia VS Code completamente")
        print("   2. Verifica que MCP esté habilitado en las extensiones")
        print("   3. Revisa la consola de VS Code para más detalles")
    else:
        print("⚠️  Algunos checks fallaron. Revisa los errores anteriores.")
        print("💡 Pasos recomendados:")
        print("   1. Instala dependencias faltantes")
        print("   2. Corrige errores de configuración")
        print("   3. Ejecuta este script nuevamente")

if __name__ == "__main__":
    main()

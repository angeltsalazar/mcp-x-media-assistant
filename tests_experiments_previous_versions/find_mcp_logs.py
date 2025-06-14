#!/usr/bin/env python3
"""
Script para monitorear logs de MCP en VS Code
"""

import os
import time
import glob
from pathlib import Path

def find_mcp_logs():
    """Busca archivos de log de MCP en las ubicaciones comunes"""
    
    print("=== BUSCANDO LOGS DE MCP ===\n")
    
    # Ubicaciones posibles de logs de VS Code
    log_locations = [
        "~/Library/Application Support/Code - Insiders/logs",
        "~/Library/Application Support/Code/logs", 
        "~/.vscode-insiders/logs",
        "~/.vscode/logs",
        "/tmp/vscode-logs"
    ]
    
    for location in log_locations:
        expanded_path = os.path.expanduser(location)
        if os.path.exists(expanded_path):
            print(f"📁 Buscando en: {expanded_path}")
            
            # Buscar archivos de log recientes
            pattern = os.path.join(expanded_path, "**/*mcp*")
            mcp_files = glob.glob(pattern, recursive=True)
            
            if mcp_files:
                print(f"   ✅ Encontrados {len(mcp_files)} archivos MCP:")
                for file in mcp_files[-3:]:  # Mostrar los 3 más recientes
                    stat = os.stat(file)
                    mod_time = time.ctime(stat.st_mtime)
                    print(f"   📄 {file} (modificado: {mod_time})")
            else:
                # Buscar logs generales recientes
                today = time.strftime("%Y%m%d")
                general_pattern = os.path.join(expanded_path, f"**/*{today}*")
                recent_files = glob.glob(general_pattern, recursive=True)
                
                if recent_files:
                    print(f"   📄 {len(recent_files)} archivos de log de hoy encontrados")
                else:
                    print(f"   ❌ No se encontraron logs MCP o recientes")
        else:
            print(f"❌ Ubicación no existe: {expanded_path}")
    
    print("\n💡 CONSEJOS PARA VERIFICAR MCP:")
    print("1. Abre VS Code Developer Tools: Help > Toggle Developer Tools")
    print("2. Ve a la pestaña Console")
    print("3. Busca mensajes relacionados con 'MCP' o errores")
    print("4. Filtra por 'mcp' en la consola")

if __name__ == "__main__":
    find_mcp_logs()

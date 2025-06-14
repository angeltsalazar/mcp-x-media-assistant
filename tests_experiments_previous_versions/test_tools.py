#!/usr/bin/env python3
"""
Test rápido de llamada a herramientas del servidor MCP
"""

import json
import subprocess
import sys

def test_tool_call():
    """Prueba la llamada a herramientas del servidor MCP"""
    
    server_cmd = [
        "/Volumes/SSDWD2T/projects/x_backup/.venv/bin/python3",
        "/Volumes/SSDWD2T/projects/x_backup/mcp_server_working.py"
    ]
    
    process = subprocess.Popen(
        server_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/Volumes/SSDWD2T/projects/x_backup",
        text=True,
        bufsize=0
    )
    
    try:
        # 1. Inicializar
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        response = process.stdout.readline()
        print("✓ Inicialización exitosa")
        
        # 2. Probar herramienta de test
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "test_tool",
                "arguments": {"message": "Hola desde VS Code"}
            }
        }
        
        process.stdin.write(json.dumps(tool_request) + "\n")
        process.stdin.flush()
        response = process.stdout.readline()
        
        result = json.loads(response)
        if "result" in result:
            content = result["result"]["content"][0]["text"]
            print(f"✓ Test tool respondió: {content}")
        else:
            print(f"✗ Error en test tool: {result}")
            
        # 3. Probar herramienta de usuarios
        users_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "manage_users",
                "arguments": {"action": "list"}
            }
        }
        
        process.stdin.write(json.dumps(users_request) + "\n")
        process.stdin.flush()
        response = process.stdout.readline()
        
        result = json.loads(response)
        if "result" in result:
            content = result["result"]["content"][0]["text"]
            print(f"✓ Manage users respondió: {content}")
        else:
            print(f"✗ Error en manage users: {result}")
            
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    print("=== PRUEBA DE HERRAMIENTAS MCP ===")
    test_tool_call()
    print("=== FIN DE PRUEBA ===")

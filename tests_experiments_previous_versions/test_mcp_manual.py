#!/usr/bin/env python3
"""
Test manual del servidor MCP - simula la comunicación JSON-RPC
"""

import json
import subprocess
import sys
import threading
import time
from pathlib import Path

def test_mcp_server():
    """Prueba el servidor MCP con comunicación JSON-RPC manual"""
    
    print("=== PRUEBA MANUAL DEL SERVIDOR MCP ===\n")
    
    # Configurar el comando del servidor
    server_cmd = [
        "/Volumes/SSDWD2T/projects/x_backup/.venv/bin/python3",
        "/Volumes/SSDWD2T/projects/x_backup/mcp_server_working.py"
    ]
    
    # Cambiar al directorio de trabajo correcto
    cwd = "/Volumes/SSDWD2T/projects/x_backup"
    
    print(f"Comando: {' '.join(server_cmd)}")
    print(f"Directorio: {cwd}")
    print()
    
    try:
        # Iniciar el proceso del servidor
        process = subprocess.Popen(
            server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            text=True,
            bufsize=0
        )
        
        print("Servidor iniciado, enviando solicitud de inicialización...")
        
        # Mensaje de inicialización MCP
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Enviar solicitud
        request_json = json.dumps(init_request) + "\n"
        print(f"Enviando: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Leer respuesta con timeout
        def read_output():
            try:
                return process.stdout.readline()
            except:
                return None
        
        # Esperar respuesta por 5 segundos
        start_time = time.time()
        response = None
        
        while time.time() - start_time < 5:
            if process.poll() is not None:
                # El proceso terminó
                break
            
            response = read_output()
            if response:
                break
            
            time.sleep(0.1)
        
        if response:
            print(f"Respuesta recibida: {response.strip()}")
            try:
                response_data = json.loads(response)
                if "result" in response_data:
                    print("✓ Servidor respondió correctamente a la inicialización")
                    
                    # Probar listado de herramientas
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list",
                        "params": {}
                    }
                    
                    tools_json = json.dumps(tools_request) + "\n"
                    print(f"\nEnviando solicitud de herramientas: {tools_json.strip()}")
                    
                    process.stdin.write(tools_json)
                    process.stdin.flush()
                    
                    tools_response = read_output()
                    if tools_response:
                        print(f"Respuesta de herramientas: {tools_response.strip()}")
                        tools_data = json.loads(tools_response)
                        if "result" in tools_data and "tools" in tools_data["result"]:
                            tools = tools_data["result"]["tools"]
                            print(f"✓ {len(tools)} herramientas encontradas:")
                            for tool in tools:
                                print(f"  - {tool['name']}")
                        else:
                            print("✗ Respuesta de herramientas inválida")
                    else:
                        print("✗ No se recibió respuesta de herramientas")
                        
                elif "error" in response_data:
                    print(f"✗ Error del servidor: {response_data['error']}")
                else:
                    print("✗ Respuesta inesperada del servidor")
            except json.JSONDecodeError as e:
                print(f"✗ Error decodificando respuesta JSON: {e}")
        else:
            print("✗ No se recibió respuesta del servidor")
        
        # Leer errores si los hay
        if process.stderr:
            stderr_data = process.stderr.read()
            if stderr_data:
                print(f"\nErrores del servidor:\n{stderr_data}")
        
        # Terminar el proceso
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print(f"\nCódigo de salida del proceso: {process.returncode}")
        
    except Exception as e:
        print(f"✗ Error ejecutando prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_server()

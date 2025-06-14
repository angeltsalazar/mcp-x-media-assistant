#!/usr/bin/env python3
"""
Test manual del servidor MCP simple
"""

import json
import subprocess
import sys
import time

def test_simple_server():
    """Prueba el servidor MCP simple"""
    
    print("=== PRUEBA DEL SERVIDOR MCP SIMPLE ===\n")
    
    # Configurar el comando del servidor
    server_cmd = [
        "/Volumes/SSDWD2T/projects/x_backup/.venv/bin/python3",
        "/Volumes/SSDWD2T/projects/x_backup/mcp_server_simple.py"
    ]
    
    cwd = "/Volumes/SSDWD2T/projects/x_backup"
    
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
        
        print("Servidor simple iniciado...")
        
        # Mensaje de inicialización
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Enviar solicitud de inicialización
        request_json = json.dumps(init_request) + "\n"
        print(f"Enviando inicialización: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Leer respuesta
        time.sleep(0.5)  # Dar tiempo al servidor para responder
        response = process.stdout.readline()
        
        if response:
            print(f"Respuesta de inicialización: {response.strip()}")
            try:
                response_data = json.loads(response)
                if "result" in response_data:
                    print("✓ Inicialización exitosa")
                    
                    # Probar listado de herramientas
                    tools_request = {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/list"
                    }
                    
                    tools_json = json.dumps(tools_request) + "\n"
                    print(f"\nSolicitud de herramientas: {tools_json.strip()}")
                    
                    process.stdin.write(tools_json)
                    process.stdin.flush()
                    
                    # Leer respuesta de herramientas
                    time.sleep(0.5)
                    tools_response = process.stdout.readline()
                    
                    if tools_response:
                        print(f"Respuesta de herramientas: {tools_response.strip()}")
                        try:
                            tools_data = json.loads(tools_response)
                            if "result" in tools_data and "tools" in tools_data["result"]:
                                tools = tools_data["result"]["tools"]
                                print(f"✓ {len(tools)} herramientas encontradas")
                                for tool in tools:
                                    print(f"  - {tool['name']}: {tool['description']}")
                                    
                                # Probar llamada a herramienta
                                call_request = {
                                    "jsonrpc": "2.0",
                                    "id": 3,
                                    "method": "tools/call",
                                    "params": {
                                        "name": "test_tool",
                                        "arguments": {}
                                    }
                                }
                                
                                call_json = json.dumps(call_request) + "\n"
                                print(f"\nLlamada a herramienta: {call_json.strip()}")
                                
                                process.stdin.write(call_json)
                                process.stdin.flush()
                                
                                time.sleep(0.5)
                                call_response = process.stdout.readline()
                                
                                if call_response:
                                    print(f"Respuesta de llamada: {call_response.strip()}")
                                    call_data = json.loads(call_response)
                                    if "result" in call_data:
                                        print("✓ Herramienta ejecutada correctamente")
                                    else:
                                        print(f"✗ Error en herramienta: {call_data.get('error', 'Unknown')}")
                                else:
                                    print("✗ No se recibió respuesta de la llamada")
                                    
                            else:
                                print(f"✗ Respuesta de herramientas inválida: {tools_data}")
                        except json.JSONDecodeError as e:
                            print(f"✗ Error decodificando herramientas: {e}")
                    else:
                        print("✗ No se recibió respuesta de herramientas")
                        
                else:
                    print(f"✗ Error en inicialización: {response_data.get('error', 'Unknown')}")
            except json.JSONDecodeError as e:
                print(f"✗ Error decodificando inicialización: {e}")
        else:
            print("✗ No se recibió respuesta de inicialización")
        
        # Terminar proceso
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        print(f"\nCódigo de salida: {process.returncode}")
        
    except Exception as e:
        print(f"✗ Error ejecutando prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_server()

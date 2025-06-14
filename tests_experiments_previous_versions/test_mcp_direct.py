#!/usr/bin/env python3
"""
Script para probar directamente el servidor MCP sin VS Code
"""

import asyncio
import json
import sys
import os

# Importar el servidor MCP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server_working import SimpleMCPServer

async def test_mcp_server():
    """Probar el servidor MCP directamente"""
    print("🚀 Probando servidor MCP directamente...")
    
    # Crear instancia del servidor
    server = SimpleMCPServer("x-media-downloader-test")
    
    # Agregar herramientas (copiado del servidor original)
    from mcp_server_working import (
        test_tool_handler,
        manage_users_handler, 
        download_images_handler,
        system_status_handler
    )
    
    # Registrar herramientas
    server.add_tool(
        "test_tool",
        "Herramienta de prueba para verificar la conectividad del servidor",
        {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Mensaje de prueba (opcional)",
                    "default": "Hola mundo"
                }
            }
        },
        test_tool_handler
    )
    
    server.add_tool(
        "system_status",
        "Obtiene el estado del sistema: usuarios configurados, archivos de caché, módulos disponibles",
        {
            "type": "object",
            "properties": {}
        },
        system_status_handler
    )
    
    server.add_tool(
        "manage_users",
        "Gestiona usuarios del sistema: listar, añadir, editar, eliminar usuarios de X",
        {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "add", "remove", "edit"],
                    "description": "Acción a realizar"
                },
                "user_data": {
                    "type": "object",
                    "properties": {
                        "friendlyname": {"type": "string"},
                        "username": {"type": "string"},
                        "directory_download": {"type": "string"}
                    }
                }
            },
            "required": ["action"]
        },
        manage_users_handler
    )
    
    print("✅ Servidor configurado")
    
    # Probar inicialización
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    
    print("\n📋 Probando inicialización...")
    init_response = await server.handle_request(init_request)
    print(f"Respuesta: {json.dumps(init_response, indent=2)}")
    
    # Probar listado de herramientas
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print("\n🔧 Probando listado de herramientas...")
    tools_response = await server.handle_request(tools_request)
    print(f"Herramientas disponibles: {len(tools_response['result']['tools'])}")
    for tool in tools_response['result']['tools']:
        print(f"  • {tool['name']}: {tool['description']}")
    
    # Probar herramienta de estado
    status_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "system_status",
            "arguments": {}
        }
    }
    
    print("\n📊 Probando system_status...")
    status_response = await server.handle_request(status_request)
    if status_response.get('result', {}).get('content'):
        print(status_response['result']['content'][0]['text'])
    else:
        print(f"Error: {status_response}")
    
    # Probar gestión de usuarios
    users_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "manage_users",
            "arguments": {"action": "list"}
        }
    }
    
    print("\n👥 Probando manage_users...")
    users_response = await server.handle_request(users_request)
    if users_response.get('result', {}).get('content'):
        print(users_response['result']['content'][0]['text'])
    else:
        print(f"Error: {users_response}")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())

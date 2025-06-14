#!/usr/bin/env python3
"""
Script de prueba para verificar el servidor MCP directamente
"""
import json
import asyncio
import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar el servidor
from mcp_server_working import SimpleMCPServer

async def test_server():
    """Probar el servidor MCP directamente."""
    print("🚀 Iniciando prueba del servidor MCP...")
    
    # Crear servidor
    server = SimpleMCPServer("test-server")
    
    # Agregar herramientas (simulando lo que hace el servidor)
    from mcp_server_working import test_tool_handler, manage_users_handler
    
    server.add_tool(
        "test_tool",
        "Herramienta de prueba",
        {"type": "object", "properties": {"message": {"type": "string"}}},
        test_tool_handler
    )
    
    server.add_tool(
        "manage_users",
        "Gestión de usuarios",
        {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "add"]},
                "user_data": {"type": "object"}
            },
            "required": ["action"]
        },
        manage_users_handler
    )
    
    # Probar inicialización
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {}
        }
    }
    
    response = await server.handle_request(init_request)
    print("✅ Inicialización:", response)
    
    # Probar listar herramientas
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    response = await server.handle_request(tools_request)
    print("🔧 Herramientas:", response)
    
    # Probar herramienta de test
    test_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "test_tool",
            "arguments": {"message": "Prueba directa"}
        }
    }
    
    response = await server.handle_request(test_request)
    print("🧪 Test tool:", response)
    
    # Probar listar usuarios
    users_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "manage_users",
            "arguments": {"action": "list"}
        }
    }
    
    response = await server.handle_request(users_request)
    print("👥 Usuarios:", response)
    
    print("🏁 Prueba completada")

if __name__ == "__main__":
    asyncio.run(test_server())

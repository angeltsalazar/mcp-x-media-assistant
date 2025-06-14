#!/usr/bin/env python3
"""
X Media Downloader - Servidor MCP básico para pruebas
Basado en los ejemplos oficiales de MCP
"""

import asyncio
import sys
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

# Crear el servidor
server = Server("x-media-downloader-simple")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Lista todas las herramientas disponibles"""
    return [
        types.Tool(
            name="test_tool",
            description="Una herramienta de prueba",
            inputSchema={"type": "object", "properties": {}},
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.Content]:
    """Maneja las llamadas a herramientas"""
    if name == "test_tool":
        return [types.TextContent(type="text", text="¡Hola desde el servidor MCP!")]
    else:
        raise ValueError(f"Herramienta desconocida: {name}")

async def run():
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1], server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(run())

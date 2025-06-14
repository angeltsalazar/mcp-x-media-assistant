#!/usr/bin/env python3
"""
Servidor MCP exactamente como el ejemplo oficial
"""

import anyio
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

# Usar exactamente la misma estructura del ejemplo oficial
app = Server("mcp-test-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="test",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.Content]:
    if name != "test":
        raise ValueError(f"Unknown tool: {name}")
    return [types.TextContent(type="text", text="Hello from test tool!")]

async def arun():
    async with stdio_server() as streams:
        await app.run(
            streams[0], streams[1], app.create_initialization_options()
        )

if __name__ == "__main__":
    anyio.run(arun)

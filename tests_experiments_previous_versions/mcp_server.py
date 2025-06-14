#!/usr/bin/env python3
"""
X Media Downloader - Model Control Protocol Server
Permite a asistentes de IA controlar el sistema de descarga de medios de X.
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import argparse
import logging

# Importar el SDK de MCP
try:
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    from mcp.types import (
        CallToolRequest,
        CallToolResult,
        ListToolsRequest,
        ListToolsResult,
        TextContent,
        Tool,
    )
except ImportError as e:
    print(f"Error: MCP SDK no está instalado correctamente. Detalle: {e}")
    print("Instala con: pip install mcp")
    sys.exit(1)

# Configurar logging más detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)
logger.info("Iniciando servidor MCP x-media-downloader")

# Crear el servidor MCP
server = Server("x-media-downloader")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """Lista todas las herramientas disponibles"""
    return [
        Tool(
            name="manage_users",
            description="Gestiona usuarios del sistema: listar, añadir, editar, eliminar",
            inputSchema={
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
                            "friendlyname": {"type": "string", "description": "Nombre amigable"},
                            "username": {"type": "string", "description": "Username de X (sin @)"},
                            "directory_download": {"type": "string", "description": "Directorio de descarga"}
                        },
                        "additionalProperties": False,
                        "description": "Datos del usuario (para add/edit)"
                    }
                },
                "required": ["action"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="download_images",
            description="Descarga imágenes y extrae información de posts de usuarios de X",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre amigable del usuario configurado"},
                    "username": {"type": "string", "description": "Username de X directo"},
                    "limit": {"type": "integer", "description": "Límite de posts nuevos a procesar", "minimum": 1},
                    "no_limit": {"type": "boolean", "description": "Procesar todos los posts sin límite", "default": False},
                    "directory": {"type": "string", "description": "Directorio personalizado de descarga"},
                    "mode": {
                        "type": "string",
                        "enum": ["auto", "temporal", "select"],
                        "description": "Modo de navegador",
                        "default": "auto"
                    }
                },
                "additionalProperties": False
            }
        ),
        Tool(
            name="select_videos",
            description="Selecciona y descarga videos desde caché",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre amigable del usuario"},
                    "action": {
                        "type": "string",
                        "enum": ["list", "download_all", "download_selected"],
                        "description": "Acción a realizar",
                        "default": "list"
                    },
                    "video_indices": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Lista de índices de videos a descargar"
                    },
                    "limit": {"type": "integer", "description": "Límite de posts a considerar del caché", "minimum": 1}
                },
                "required": ["name"],
                "additionalProperties": False
            }
        ),
        Tool(
            name="system_status",
            description="Obtiene el estado del sistema: usuarios configurados, archivos de caché, etc.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        ),
        Tool(
            name="system_config",
            description="Gestiona la configuración del sistema",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["get", "set", "reset"],
                        "description": "Acción de configuración",
                        "default": "get"
                    },
                    "config_data": {
                        "type": "object",
                        "description": "Datos de configuración (para set)",
                        "additionalProperties": True
                    }
                },
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Maneja las llamadas a herramientas"""
    try:
        if name == "manage_users":
            return await _manage_users(arguments.get("action"), arguments.get("user_data"))
        elif name == "download_images":
            return await _download_images(
                arguments.get("name"),
                arguments.get("username"),
                arguments.get("limit"),
                arguments.get("no_limit", False),
                arguments.get("directory"),
                arguments.get("mode", "auto")
            )
        elif name == "select_videos":
            return await _select_videos(
                arguments.get("name"),
                arguments.get("action", "list"),
                arguments.get("video_indices"),
                arguments.get("limit")
            )
        elif name == "system_status":
            return await _system_status()
        elif name == "system_config":
            return await _system_config(
                arguments.get("action", "get"),
                arguments.get("config_data")
            )
        else:
            return [TextContent(type="text", text=f"Herramienta desconocida: {name}")]
    
    except Exception as e:
        logger.error(f"Error en herramienta {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _manage_users(action: str, user_data: Optional[Dict[str, str]] = None) -> List[TextContent]:
    """Implementación de gestión de usuarios"""
    try:
        if action == "list":
            result = subprocess.run([
                sys.executable, "manage_users.py", "--list-json"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                users = json.loads(result.stdout) if result.stdout.strip() else {}
                return [TextContent(
                    type="text",
                    text=f"Usuarios configurados:\n{json.dumps(users, indent=2, ensure_ascii=False)}"
                )]
            else:
                return [TextContent(type="text", text=f"Error listando usuarios: {result.stderr}")]
        
        elif action == "add" and user_data:
            cmd = [
                sys.executable, "manage_users.py", "--add-json",
                "--friendlyname", user_data.get("friendlyname", ""),
                "--username", user_data.get("username", ""),
                "--directory", user_data.get("directory_download", "")
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=f"Usuario '{user_data['friendlyname']}' añadido correctamente")]
            else:
                return [TextContent(type="text", text=f"Error añadiendo usuario: {result.stderr}")]
        
        else:
            return [TextContent(type="text", text=f"Acción no soportada: {action}")]
            
    except Exception as e:
        logger.error(f"Error en manage_users: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _download_images(name: Optional[str], username: Optional[str], 
                         limit: Optional[int], no_limit: bool, 
                         directory: Optional[str], mode: str) -> List[TextContent]:
    """Implementación de descarga de imágenes"""
    try:
        cmd = [sys.executable, "edge_x_downloader_clean.py"]
        
        if name:
            cmd.extend(["--name", name])
        elif username:
            cmd.extend(["--username", username])
        
        if no_limit:
            cmd.append("--no-limit")
        elif limit is not None:
            cmd.extend(["--limit", str(limit)])
        
        if directory:
            cmd.extend(["--directory", directory])
        
        if mode == "temporal":
            cmd.append("--temporal")
        elif mode == "select":
            cmd.append("--select")
        else:  # auto es default
            cmd.append("--auto")
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            return [TextContent(
                type="text", 
                text=f"Descarga completada exitosamente:\n{result.stdout}"
            )]
        else:
            return [TextContent(
                type="text", 
                text=f"Error en descarga:\n{result.stderr}"
            )]
            
    except Exception as e:
        logger.error(f"Error en download_images: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _select_videos(name: str, action: str, 
                       video_indices: Optional[List[int]], 
                       limit: Optional[int]) -> List[TextContent]:
    """Implementación de selector de videos"""
    try:
        if action == "list":
            cmd = [sys.executable, "video_selector.py", "--name", name, "--list-only"]
            if limit:
                cmd.extend(["--limit", str(limit)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=result.stdout)]
            else:
                return [TextContent(type="text", text=f"Error listando videos: {result.stderr}")]
        
        elif action == "download_all":
            cmd = [sys.executable, "video_selector.py", "--name", name, "--download-all"]
            if limit:
                cmd.extend(["--limit", str(limit)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=f"Descarga masiva completada:\n{result.stdout}")]
            else:
                return [TextContent(type="text", text=f"Error en descarga masiva: {result.stderr}")]
        
        elif action == "download_selected" and video_indices:
            indices_str = ",".join(map(str, video_indices))
            cmd = [sys.executable, "video_selector.py", "--name", name, "--download-indices", indices_str]
            if limit:
                cmd.extend(["--limit", str(limit)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                return [TextContent(type="text", text=f"Videos seleccionados descargados:\n{result.stdout}")]
            else:
                return [TextContent(type="text", text=f"Error descargando videos seleccionados: {result.stderr}")]
        
        else:
            return [TextContent(type="text", text=f"Acción no válida: {action}")]
            
    except Exception as e:
        logger.error(f"Error en select_videos: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _system_status() -> List[TextContent]:
    """Implementación del estado del sistema"""
    try:
        status = {
            "config_file_exists": Path("config_files/x_usernames.json").exists(),
            "cache_files": [],
            "scripts_available": {}
        }
        
        # Verificar archivos de caché
        cache_dir = Path("cache")
        if cache_dir.exists():
            status["cache_files"] = [f.name for f in cache_dir.glob("*_processed_posts.json")]
        
        # Verificar scripts disponibles
        scripts = ["edge_x_downloader_clean.py", "manage_users.py", "video_selector.py"]
        for script in scripts:
            status["scripts_available"][script] = Path(script).exists()
        
        # Verificar dependencias
        try:
            import playwright
            status["playwright_available"] = True
        except ImportError:
            status["playwright_available"] = False
        
        try:
            result = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
            status["yt_dlp_available"] = result.returncode == 0
            if status["yt_dlp_available"]:
                status["yt_dlp_version"] = result.stdout.strip()
        except FileNotFoundError:
            status["yt_dlp_available"] = False
        
        return [TextContent(
            type="text", 
            text=f"Estado del sistema:\n{json.dumps(status, indent=2, ensure_ascii=False)}"
        )]
        
    except Exception as e:
        logger.error(f"Error en system_status: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def _system_config(action: str, config_data: Optional[Dict[str, Any]]) -> List[TextContent]:
    """Implementación de configuración del sistema"""
    try:
        config_file = Path("config_files/x_usernames.json")
        
        if action == "get":
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return [TextContent(
                    type="text",
                    text=f"Configuración actual:\n{json.dumps(config, indent=2, ensure_ascii=False)}"
                )]
            else:
                return [TextContent(type="text", text="Archivo de configuración no existe")]
        
        elif action == "set" and config_data:
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            return [TextContent(type="text", text="Configuración actualizada")]
        
        elif action == "reset":
            if config_file.exists():
                config_file.unlink()
            return [TextContent(type="text", text="Configuración reiniciada")]
        
        else:
            return [TextContent(type="text", text=f"Acción no válida: {action}")]
            
    except Exception as e:
        logger.error(f"Error en system_config: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Función principal"""
    logger.info("Iniciando función principal del servidor MCP")
    try:
        # Configurar argumentos para compatibilidad, pero MCP maneja la comunicación via stdio
        logger.debug("Configurando streams de stdio")
        async with stdio_server() as streams:
            logger.info("Streams configurados, iniciando servidor")
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error en función principal: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor MCP interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en servidor MCP: {e}")
        sys.exit(1)

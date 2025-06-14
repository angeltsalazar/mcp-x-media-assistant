#!/usr/bin/env python3
"""
X Media Downloader - Servidor MCP completo
Servidor MCP funcional que integra todas las funcionalidades del downloader
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from typing import Any, Dict, List
from pathlib import Path

# Importar módulos del downloader
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.config.user_config import UserConfigManager
    from modules.core.orchestrator import EdgeXDownloader
    from modules.utils.url_utils import URLUtils
    from modules.utils.logging import Logger
    from modules.core.exceptions import XDownloaderException

    MODULES_IMPORTED = True
except ImportError as e:
    print(f"❌ Error importando módulos del downloader: {e}")
    print("Usando funcionalidades básicas...")
    MODULES_IMPORTED = False

    # Fallback classes para funcionalidad básica
    class UserConfigManager:
        @staticmethod
        def load_user_config():
            return {}

        @staticmethod
        def save_user_config(config):
            print("⚠️ Usando UserConfigManager fallback - no se guardará realmente")

        @staticmethod
        def list_configured_users():
            return "No hay usuarios configurados"

        @staticmethod
        def get_user_by_name(name):
            return None

    class EdgeXDownloader:
        def __init__(self, download_dir):
            self.download_dir = download_dir

        async def download_with_edge(self, profile_url, use_auto, use_main, url_limit):
            return {"message": "Funcionalidad de descarga no disponible"}


# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("x-media-downloader-mcp")

# Log del estado de importación
if MODULES_IMPORTED:
    logger.info("✅ Módulos del downloader importados correctamente")
else:
    logger.warning("⚠️ Usando funcionalidades básicas - módulos no disponibles")


class SimpleMCPServer:
    """Servidor MCP completo para X Media Downloader."""

    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
        self.tools = []
        self.request_id = 0

    def add_tool(
        self, name: str, description: str, input_schema: Dict[str, Any], handler
    ):
        """Agrega una herramienta al servidor."""
        self.tools.append(
            {
                "name": name,
                "description": description,
                "inputSchema": input_schema,
                "handler": handler,
            }
        )

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja una solicitud JSON-RPC."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                            "experimental": {},
                        },
                        "serverInfo": {"name": self.name, "version": self.version},
                    },
                }

            elif method == "tools/list":
                tools_list = []
                for tool in self.tools:
                    tools_list.append(
                        {
                            "name": tool["name"],
                            "description": tool["description"],
                            "inputSchema": tool["inputSchema"],
                        }
                    )

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools_list},
                }

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                # Buscar la herramienta
                for tool in self.tools:
                    if tool["name"] == tool_name:
                        try:
                            result = await tool["handler"](arguments)
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": [{"type": "text", "text": result}],
                                    "isError": False,
                                },
                            }
                        except Exception as e:
                            logger.error(f"Error en herramienta {tool_name}: {e}")
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": [
                                        {"type": "text", "text": f"Error: {str(e)}"}
                                    ],
                                    "isError": True,
                                },
                            }

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}",
                    },
                }

            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }

    async def run(self):
        """Ejecuta el servidor MCP."""
        logger.info(f"Iniciando servidor MCP: {self.name}")

        while True:
            try:
                # Leer línea de entrada
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                # Parsear solicitud JSON-RPC
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
                    continue

                # Procesar solicitud
                response = await self.handle_request(request)

                # Enviar respuesta
                response_line = json.dumps(response)
                print(response_line, flush=True)

            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")


# Crear servidor
server = SimpleMCPServer("x-media-downloader")

# ============ HERRAMIENTAS DEL X MEDIA DOWNLOADER ============


async def manage_users_handler(arguments: Dict[str, Any]) -> str:
    """Gestionar usuarios del sistema."""
    try:
        action = arguments.get("action", "list")
        user_data = arguments.get("user_data", {})

        logger.info(
            f"Ejecutando manage_users con acción: {action}, MODULES_IMPORTED: {MODULES_IMPORTED}"
        )

        if action == "list":
            try:
                config = UserConfigManager.load_user_config()
                logger.info(f"Config cargada: {config}")
                if not config:
                    return "📋 No hay usuarios configurados aún.\n\nUsa la acción 'add' para agregar el primer usuario."

                result = "📋 **Usuarios configurados:**\n\n"
                for username, data in config.items():
                    result += (
                        f"• **{data.get('friendlyname', username)}** (@{username})\n"
                    )
                    result += f"  📁 Directorio: `{data.get('directory_download', 'No especificado')}`\n\n"

                return result
            except Exception as e:
                logger.error(f"Error listando usuarios: {e}")
                return f"❌ Error listando usuarios: {str(e)}"

        elif action == "add":
            try:
                friendlyname = user_data.get("friendlyname")
                username = user_data.get("username", "").lstrip("@")
                directory = user_data.get("directory_download")

                logger.info(
                    f"Agregando usuario: {friendlyname} (@{username}) -> {directory}"
                )

                if not all([friendlyname, username, directory]):
                    return "❌ Para agregar un usuario necesitas: friendlyname, username y directory_download"

                config = UserConfigManager.load_user_config()
                logger.info(f"Config antes de agregar: {config}")

                config[username] = {
                    "friendlyname": friendlyname,
                    "username": username,
                    "directory_download": directory,
                }

                logger.info(f"Config después de agregar: {config}")
                UserConfigManager.save_user_config(config)
                logger.info("Usuario guardado correctamente")

                return f"✅ Usuario **{friendlyname}** (@{username}) agregado correctamente.\n📁 Directorio: `{directory}`"

            except Exception as e:
                logger.error(f"Error agregando usuario: {e}")
                return f"❌ Error agregando usuario: {str(e)}"

        elif action == "remove":
            try:
                username = user_data.get("username", "").lstrip("@")
                if not username:
                    return "❌ Especifica el username del usuario a eliminar"

                config = UserConfigManager.load_user_config()
                if username in config:
                    friendlyname = config[username].get("friendlyname", username)
                    del config[username]
                    UserConfigManager.save_user_config(config)
                    return f"✅ Usuario **{friendlyname}** (@{username}) eliminado correctamente."
                else:
                    return f"❌ Usuario @{username} no encontrado"

            except Exception as e:
                return f"❌ Error eliminando usuario: {str(e)}"

        else:
            return f"❌ Acción no válida: {action}. Usa: list, add, remove"

    except Exception as e:
        logger.error(f"Error en manage_users: {e}")
        return f"❌ Error inesperado: {str(e)}"


async def download_images_handler(arguments: Dict[str, Any]) -> str:
    """Descargar imágenes y videos de usuarios de X."""
    try:
        # Parámetros
        name = arguments.get("name")
        username = arguments.get("username")
        limit = arguments.get("limit", 100)
        no_limit = arguments.get("no_limit", False)
        directory = arguments.get("directory")
        mode = arguments.get("mode", "auto")

        # Validar parámetros
        if not name and not username:
            return "❌ Debes especificar 'name' (usuario configurado) o 'username' (username directo)"

        # Configurar usuario
        if name:
            config = UserConfigManager.load_user_config()
            user_data = None
            for user, data in config.items():
                if data.get("friendlyname", "").lower() == name.lower():
                    user_data = data
                    username = user
                    break

            if not user_data:
                return f"❌ Usuario '{name}' no encontrado. Usa 'manage_users' con acción 'list' para ver usuarios disponibles."

            download_dir = (
                Path(directory) if directory else Path(user_data["directory_download"])
            )
            profile_url = URLUtils.build_profile_url(username)

        else:
            # Username directo
            username = username.lstrip("@")
            download_dir = (
                Path(directory)
                if directory
                else Path.home() / "Downloads" / f"X_Media_{username}"
            )
            profile_url = URLUtils.build_profile_url(username)

        # Configurar límite
        if no_limit or limit == 0:
            url_limit = None
        else:
            url_limit = int(limit)

        # Configurar modo de navegador
        use_auto = mode in ["auto", "temporal"]
        use_main = mode == "select"

        # Ejecutar descarga
        try:
            downloader = EdgeXDownloader(download_dir)
            stats = await downloader.download_with_edge(
                profile_url, use_auto, use_main, url_limit
            )

            if isinstance(stats, dict) and "message" in stats:
                return f"⚠️ {stats['message']}"

            # Formatear resultados
            result = f"✅ **Descarga completada para @{username}**\n\n"
            result += f"📁 **Directorio:** `{download_dir}`\n"
            result += f"🔗 **Perfil:** {profile_url}\n"
            result += f"📊 **Modo:** {mode}\n"
            result += (
                f"🔢 **Límite:** {'Sin límite' if url_limit is None else url_limit}\n\n"
            )

            if isinstance(stats, dict):
                result += "📈 **Estadísticas:**\n"
                for key, value in stats.items():
                    result += f"• {key}: {value}\n"

            return result

        except Exception as e:
            return f"❌ Error durante la descarga: {str(e)}"

    except Exception as e:
        logger.error(f"Error en download_images: {e}")
        return f"❌ Error inesperado: {str(e)}"


async def system_status_handler(arguments: Dict[str, Any]) -> str:
    """Obtener el estado del sistema."""
    try:
        result = "🔍 **Estado del Sistema X Media Downloader**\n\n"

        # Estado de usuarios
        try:
            config = UserConfigManager.load_user_config()
            user_count = len(config)
            result += f"👥 **Usuarios configurados:** {user_count}\n"

            if user_count > 0:
                result += "📋 **Lista de usuarios:**\n"
                for username, data in list(config.items())[:5]:  # Mostrar máximo 5
                    result += f"• {data.get('friendlyname', username)} (@{username})\n"
                if user_count > 5:
                    result += f"... y {user_count - 5} más\n"
        except Exception as e:
            result += f"❌ Error verificando usuarios: {str(e)}\n"

        result += "\n"

        # Estado de archivos
        try:
            cache_dir = Path.cwd() / "cache"
            if cache_dir.exists():
                cache_files = list(cache_dir.glob("*.json"))
                result += f"📂 **Archivos de caché:** {len(cache_files)}\n"
            else:
                result += f"📂 **Directorio de caché:** No existe\n"
        except Exception as e:
            result += f"❌ Error verificando caché: {str(e)}\n"

        # Estado de módulos
        result += "\n🔧 **Estado de módulos:**\n"
        modules_status = [
            ("UserConfigManager", "modules.config.user_config"),
            ("EdgeXDownloader", "modules.core.orchestrator"),
            ("URLUtils", "modules.utils.url_utils"),
        ]

        for module_name, module_path in modules_status:
            try:
                __import__(module_path)
                result += f"✅ {module_name}: Disponible\n"
            except ImportError:
                result += f"❌ {module_name}: No disponible\n"

        return result

    except Exception as e:
        logger.error(f"Error en system_status: {e}")
        return f"❌ Error obteniendo estado del sistema: {str(e)}"


async def test_tool_handler(arguments: Dict[str, Any]) -> str:
    """Herramienta de prueba para verificar la conectividad."""
    message = arguments.get("message", "Prueba sin mensaje")
    return f"✅ **Servidor X Media Downloader funcionando correctamente!**\n\n📝 Mensaje recibido: {message}\n🕐 Servidor activo y listo para procesar descargas."


async def admin_tool_handler(arguments: Dict[str, Any]) -> str:
    """Herramienta administrativa que da acceso a funcionalidades del sistema."""
    try:
        action = arguments.get("action", "help")
        params = arguments.get("params", {})

        if action == "help":
            return """🔧 **Herramienta Administrativa X Media Downloader**

📋 **Acciones disponibles:**

• **status** - Obtiene el estado completo del sistema
• **download_test** - Simula una descarga para verificar configuración
• **users** - Gestión de usuarios (equivale a manage_users)
• **download_videos** - Descarga videos pendientes usando video_selector.py

📝 **Uso:**
- Para estado: `{"action": "status"}`
- Para descarga de prueba: `{"action": "download_test", "params": {"username": "nat", "limit": 5}}`
- Para usuarios: `{"action": "users", "params": {"action": "list"}}`
- Para videos: `{"action": "download_videos", "params": {"name": "rachel", "mode": "download", "limit": 10}}`
"""

        elif action == "status":
            # Llamar al handler de system_status
            return await system_status_handler({})

        elif action == "download_test":
            # Simular descarga sin ejecutar realmente
            username = params.get("username", "nat")
            limit = params.get("limit", 5)

            try:
                config = UserConfigManager.load_user_config()
                if username not in config:
                    available_users = list(config.keys())
                    return f"❌ Usuario '{username}' no encontrado.\n\n📋 Usuarios disponibles: {', '.join(available_users)}"

                user_data = config[username]
                profile_url = URLUtils.build_profile_url(username)

                return f"""🎯 **Prueba de Descarga Configurada**

👤 **Usuario:** {user_data.get('friendlyname', username)} (@{username})
🔗 **URL:** {profile_url}
📁 **Directorio:** `{user_data['directory_download']}`
🔢 **Límite:** {limit} posts
🔧 **Modo:** auto

✅ **Configuración válida**
⚠️ **Nota:** Esta es solo una verificación. Para descarga real, usar la herramienta download_images.
"""

            except Exception as e:
                return f"❌ Error en prueba de descarga: {str(e)}"

        elif action == "users":
            # Proxy para manage_users
            user_params = params.copy()
            return await manage_users_handler(user_params)

        elif action == "download_videos":
            # Descarga de videos usando video_selector.py
            name = params.get("name", "")
            mode = params.get("mode", "download")
            limit = params.get("limit", 10)

            if not name:
                return "❌ Falta el parámetro 'name' del usuario"

            # Verificar que el usuario existe
            config = UserConfigManager.load_user_config()
            user_found = False
            username = ""

            for user, data in config.items():
                if data.get("friendlyname", "").lower() == name.lower():
                    user_found = True
                    username = user
                    break

            if not user_found:
                available_users = [
                    data.get("friendlyname", user) for user, data in config.items()
                ]
                return f"❌ Usuario '{name}' no encontrado.\n📋 Usuarios disponibles: {', '.join(available_users)}"

            try:
                # Ejecutar video_selector.py
                cmd = [
                    sys.executable,
                    "video_selector.py",
                    "--name",
                    name,
                    "--limit",
                    str(limit),
                ]

                if mode == "list_only":
                    cmd.append("--list-only")

                logger.info(f"Ejecutando descarga de videos: {' '.join(cmd)}")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=".",
                    timeout=300,  # 5 minutos máximo
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    return f"✅ **Descarga de videos completada para {name}**\n\n📋 **Salida:**\n{output}"
                else:
                    error_output = result.stderr.strip()
                    return f"❌ **Error en descarga de videos:**\n{error_output}"

            except subprocess.TimeoutExpired:
                return "⏱️ **Timeout:** La descarga de videos tomó demasiado tiempo (>5 min)"
            except Exception as e:
                return f"❌ **Error ejecutando video_selector:** {str(e)}"

        else:
            return f"❌ Acción no reconocida: {action}\n\nUsa action='help' para ver opciones disponibles."

    except Exception as e:
        logger.error(f"Error en admin_tool: {e}")
        return f"❌ Error en herramienta administrativa: {str(e)}"


# ============ REGISTRAR HERRAMIENTAS ============

# Herramienta de prueba
server.add_tool(
    "test_tool",
    "Herramienta de prueba para verificar la conectividad del servidor",
    {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Mensaje de prueba (opcional)",
                "default": "Hola mundo",
            }
        },
    },
    test_tool_handler,
)

# Gestión de usuarios
server.add_tool(
    "manage_users",
    "Gestiona usuarios del sistema: listar, añadir, editar, eliminar usuarios de X",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "add", "remove", "edit"],
                "description": "Acción a realizar",
            },
            "user_data": {
                "type": "object",
                "properties": {
                    "friendlyname": {
                        "type": "string",
                        "description": "Nombre amigable para identificar al usuario",
                    },
                    "username": {
                        "type": "string",
                        "description": "Username de X (con o sin @)",
                    },
                    "directory_download": {
                        "type": "string",
                        "description": "Directorio donde descargar los archivos",
                    },
                },
                "description": "Datos del usuario (requerido para add/edit)",
            },
        },
        "required": ["action"],
    },
    manage_users_handler,
)

# Descarga de imágenes
server.add_tool(
    "download_images",
    "Descarga imágenes y videos de perfiles de usuarios de X (Twitter)",
    {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nombre amigable del usuario configurado",
            },
            "username": {
                "type": "string",
                "description": "Username directo de X (con o sin @)",
            },
            "limit": {
                "type": "integer",
                "description": "Límite de posts nuevos a procesar (por defecto 100)",
                "minimum": 1,
                "default": 100,
            },
            "no_limit": {
                "type": "boolean",
                "description": "Procesar todos los posts sin límite",
                "default": False,
            },
            "directory": {
                "type": "string",
                "description": "Directorio personalizado de descarga (opcional)",
            },
            "mode": {
                "type": "string",
                "enum": ["auto", "temporal", "select"],
                "description": "Modo de navegador: auto (perfil automático), temporal (perfil temporal), select (seleccionar perfil)",
                "default": "auto",
            },
        },
    },
    download_images_handler,
)

# Estado del sistema
server.add_tool(
    "system_status",
    "Obtiene el estado del sistema: usuarios configurados, archivos de caché, módulos disponibles",
    {"type": "object", "properties": {}},
    system_status_handler,
)

# Herramienta administrativa
server.add_tool(
    "admin_tool",
    "Herramienta administrativa para acceder a funcionalidades del sistema",
    {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "Acción a realizar"},
            "params": {"type": "object", "description": "Parámetros para la acción"},
        },
    },
    admin_tool_handler,
)

# ============ HANDLER PARA VIDEOS ============


async def video_downloader_handler(arguments: Dict[str, Any]) -> str:
    """Descarga videos usando video_selector.py."""
    try:
        name = arguments.get("name")
        limit = arguments.get("limit")
        mode = arguments.get("mode", "download_all")

        if not name:
            return "❌ Debes especificar el nombre del usuario (name)"

        # Construir comando con Python del venv (ruta relativa)
        project_dir = Path(__file__).parent.absolute()
        python_venv = project_dir / ".venv" / "bin" / "python3"
        cmd = [str(python_venv), "video_selector.py", "--name", name]

        if mode == "download_all":
            cmd.append("--download-all")
        elif mode == "list_only":
            cmd.append("--list-only")

        if limit:
            cmd.extend(["--limit", str(limit)])

        logger.info(f"Ejecutando descarga de videos: {' '.join(cmd)}")

        # Ejecutar comando
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=".",
            timeout=1800,  # 30 minutos máximo
        )

        if result.returncode == 0:
            output = result.stdout
            if (
                "videos descargados exitosamente" in output
                or "Videos procesados" in output
            ):
                return f"✅ **Descarga de videos completada para {name}**\n\n{output}"
            else:
                return f"🔄 **Proceso ejecutado para {name}**\n\n{output}"
        else:
            error_msg = result.stderr or "Error desconocido"
            return f"❌ **Error descargando videos de {name}**\n\n{error_msg}"

    except subprocess.TimeoutExpired:
        return f"⏱️ **Timeout:** La descarga de videos tomó más de 30 minutos"
    except Exception as e:
        logger.error(f"Error en video_downloader: {e}")
        return f"❌ **Error inesperado:** {str(e)}"


# Descarga de videos
server.add_tool(
    "download_videos",
    "Descarga videos de usuarios de X usando video_selector.py",
    {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Nombre del usuario (username o friendlyname)",
            },
            "mode": {
                "type": "string",
                "enum": ["download_all", "list_only"],
                "description": "Modo de operación: download_all para descargar todos, list_only para solo listar",
                "default": "download_all",
            },
            "limit": {
                "type": "integer",
                "description": "Límite de videos a procesar (opcional)",
                "minimum": 1,
            },
        },
        "required": ["name"],
    },
    video_downloader_handler,
)

if __name__ == "__main__":
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Servidor interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en servidor MCP: {e}")
        sys.exit(1)

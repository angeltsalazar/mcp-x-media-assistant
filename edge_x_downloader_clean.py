#!/usr/bin/env python3
"""
X Media Downloader - Punto de entrada principal
Versión Modular
"""
import asyncio
from pathlib import Path

from modules.cli.argument_parser import ArgumentParser
from modules.cli.user_interface import UserInterface
from modules.config.user_config import UserConfigManager
from modules.core.orchestrator import EdgeXDownloader
from modules.core.exceptions import XDownloaderException
from modules.utils.logging import Logger
from modules.utils.url_utils import URLUtils

def setup_user_config(args):
    """
    Determina la configuración del usuario (URL del perfil y directorio de descarga)
    basándose en los argumentos de la CLI.
    """
    if args.name:
        user_data = UserConfigManager.get_user_by_name(args.name)
        if not user_data:
            Logger.warning(f"Usuario '{args.name}' no encontrado. Creando uno nuevo.")
            user_data = UserConfigManager.add_new_user(args.name)
            if not user_data:
                raise XDownloaderException("No se pudo configurar el nuevo usuario.")
        
        username = user_data['username']
        download_dir = Path(user_data['directory_download'])
        Logger.success(f"Usuario seleccionado: {user_data['friendlyname']} (@{username})")

    elif args.username:
        username = args.username.lstrip('@')
        config = UserConfigManager.load_user_config()
        user_data = config.get(username)
        if user_data:
            download_dir = Path(user_data['directory_download'])
            Logger.success(f"Usuario encontrado en config: {user_data['friendlyname']} (@{username})")
        else:
            download_dir = Path.home() / "Downloads" / f"X_Media_{username}"
            Logger.info(f"Usuario no configurado. Usando directorio por defecto: {download_dir}")
    else:
        # Compatibilidad hacia atrás
        username = "milewskaja_nat"
        download_dir = Path.home() / "Downloads" / "X_Media_Edge"
        Logger.warning("No se especificó usuario. Usando perfil por defecto.")

    if args.directory:
        download_dir = Path(args.directory)
        Logger.info(f"Usando directorio personalizado: {download_dir}")

    profile_url = URLUtils.build_profile_url(username)
    return profile_url, download_dir

async def main():
    """
    Función principal que orquesta la aplicación.
    """
    ui = UserInterface()
    try:
        # 1. Parsear argumentos
        arg_parser = ArgumentParser()
        args = arg_parser.parse_arguments()

        # 2. Comando especial: listar usuarios
        if args.list_users:
            UserConfigManager.list_configured_users()
            return

        # 3. Configurar usuario y directorios
        profile_url, download_dir = setup_user_config(args)

        # 4. Configurar modo de navegador
        use_auto, use_main = ui.resolve_browser_mode(args)

        # 5. Configurar límite (manejar --no-limit y --limit 0)
        if args.no_limit or args.limit == 0:
            url_limit = None  # Sin límite
        else:
            url_limit = args.limit  # Usar el límite especificado (por defecto 100)

        # 6. Mostrar info y confirmar
        ui.show_welcome_message(profile_url, use_auto, use_main, url_limit)
        # Auto-confirmar si se proporcionaron argumentos específicos
        auto_confirm = args.username or args.name or args.directory or args.limit != 100
        if not ui.confirm_execution(auto_confirm):
            return

        # 7. Ejecutar descarga
        downloader = EdgeXDownloader(download_dir)
        stats = await downloader.download_with_edge(profile_url, use_auto, use_main, url_limit)
        
        # 7. Mostrar resumen
        ui.show_completion_message(stats)

    except XDownloaderException as e:
        ui.show_error_diagnosis(e)
    except Exception as e:
        Logger.error("Ha ocurrido un error fatal e inesperado.")
        ui.show_error_diagnosis(e)

if __name__ == "__main__":
    asyncio.run(main())

"""
Módulo para la gestión de la interfaz de usuario en la línea de comandos.
"""
import argparse
from ..utils.logging import Logger
from ..core.exceptions import XDownloaderException

class UserInterface:
    """
    Gestiona toda la interacción con el usuario, como mensajes y diálogos.
    """

    def show_welcome_message(self, profile_url: str, use_automation: bool, use_main: bool, url_limit: int = None):
        """Muestra el mensaje de bienvenida y la configuración de la sesión."""
        Logger.info("🎬 X Media Downloader - Optimizado para Microsoft Edge")
        print("=" * 60)
        Logger.info(f"🎯 Perfil objetivo: {profile_url}")
        if use_main:
            Logger.info("✅ Usando perfil principal de Edge")
        elif use_automation:
            Logger.info("✅ Usando perfil de automatización")
        else:
            Logger.info("✅ Usando Edge temporal")
        
        if url_limit is not None:
            Logger.info(f"⚡ Límite de URLs nuevas: {url_limit}")
        
        print("=" * 60)

    def confirm_execution(self, auto_confirm: bool = False) -> bool:
        """Pide al usuario confirmación para continuar."""
        if auto_confirm:
            Logger.info("🚀 Confirmación automática activada - continuando...")
            return True
            
        response = input("🚀 ¿Continuar? (s/n): ").lower().strip()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            Logger.warning("Cancelado por el usuario.")
            return False
        return True

    def resolve_browser_mode(self, args: argparse.Namespace) -> tuple[bool, bool]:
        """Determina el modo de navegador a partir de los argumentos o un diálogo."""
        if args.select:
            return self._show_browser_mode_selection()
        
        use_main_profile = args.main_profile
        use_automation_profile = not use_main_profile and not args.temporal
        
        return use_automation_profile, use_main_profile

    def _show_browser_mode_selection(self) -> tuple[bool, bool]:
        """Muestra un diálogo para que el usuario seleccione el modo de navegador."""
        print("\n" + "="*20 + " SELECCIONAR MODO DE NAVEGADOR " + "="*20)
        print("1. Perfil de automatización (Recomendado)")
        print("2. Perfil principal de Edge")
        print("3. Edge temporal (requiere login manual)")
        
        choice = input("Selecciona una opción (1/2/3): ").strip()
        
        if choice == "2":
            return False, True  # (auto, main)
        if choice == "3":
            return False, False # (auto, main)
        
        return True, False # (auto, main) - por defecto

    def show_completion_message(self, stats: dict):
        """Muestra el mensaje final cuando el proceso se completa."""
        Logger.info("\n" + "🏁 ¡Proceso completado!" + "🏁")
        Logger.success(f"Imágenes descargadas: {stats.get('downloaded', 0)}")
        Logger.info(f"Imágenes saltadas: {stats.get('skipped', 0)}")
        Logger.error(f"Errores: {stats.get('errors', 0)}")
        Logger.info("📊 Revisa el JSON generado para ver la clasificación completa de medios.")

    def show_error_diagnosis(self, error: Exception):
        """Muestra un diagnóstico basado en el tipo de error."""
        Logger.error(f"Ha ocurrido un error: {error}")
        if isinstance(error, XDownloaderException):
            Logger.warning(f"Tipo de error: {type(error).__name__}")
        
        # Aquí se puede añadir lógica de diagnóstico más específica en el futuro
        import traceback
        traceback.print_exc()
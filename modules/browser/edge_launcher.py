"""
Módulo para el lanzamiento y configuración de Microsoft Edge.
"""
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext

class EdgeLauncher:
    """
    Gestiona el ciclo de vida del navegador Edge, incluyendo su lanzamiento
    con un perfil específico y su cierre.
    """
    def __init__(self, use_automation_profile: bool = True, use_main_profile: bool = False):
        self.use_automation_profile = use_automation_profile
        self.use_main_profile = use_main_profile
        self.playwright = None
        self.browser = None

    async def launch_browser(self) -> BrowserContext:
        """Lanza el navegador Edge con el contexto y perfil adecuados."""
        print("🚀 Iniciando Microsoft Edge...")
        self.playwright = await async_playwright().start()
        
        context_options = self._get_browser_context_options()
        
        self.browser = await self.playwright.chromium.launch_persistent_context(
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            headless=False,
            **context_options
        )
        return self.browser

    def _get_browser_context_options(self) -> dict:
        """Prepara las opciones de contexto del navegador, incluyendo el perfil."""
        options = {
            "viewport": {"width": 1280, "height": 720},
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        }
        
        if self.use_main_profile:
            options["user_data_dir"] = str(self._get_main_profile_path())
            print("✅ Usando perfil principal de Edge (con tus credenciales)")
            print("⚠️  NOTA: Esto puede interferir con tu navegación normal si Edge está abierto")
        elif self.use_automation_profile:
            options["user_data_dir"] = str(self._get_automation_profile_path())
            print("✅ Usando perfil de automatización")
        else:
            print("✅ Usando Edge temporal (sin datos persistentes)")
            
        return options

    def _get_automation_profile_path(self) -> Path:
        """Obtiene la ruta al perfil de automatización de Edge."""
        automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "EdgeAutomation"
        automation_dir.mkdir(parents=True, exist_ok=True)
        return automation_dir

    def _get_main_profile_path(self) -> Path:
        """Obtiene la ruta al perfil principal de Edge."""
        return Path.home() / "Library" / "Application Support" / "Microsoft Edge"

    async def close_browser(self):
        """Cierra el navegador y el objeto playwright."""
        if self.browser:
            print("🔚 Cerrando navegador...")
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
"""
Módulo para la gestión del proceso de login en la página.
"""
import asyncio
import time
from playwright.async_api import Page
from ..core.exceptions import LoginException
from ..config.constants import LOGIN_TIMEOUT

class LoginHandler:
    """
    Gestiona la detección de la página de login y la espera
    a que el usuario inicie sesión manualmente.
    """
    def __init__(self, page: Page, navigation_manager):
        self.page = page
        self.navigation_manager = navigation_manager

    async def check_and_handle_login(self, profile_url: str):
        """
        Verifica si se requiere login y maneja el flujo de espera
        y navegación posterior.
        """
        if await self._is_login_required():
            await self._wait_for_manual_login()
            await self._handle_post_login_navigation(profile_url)

    async def _is_login_required(self) -> bool:
        """Verifica si la URL actual corresponde a una página de login."""
        await asyncio.sleep(3)  # Pequeña espera para que la URL se actualice
        current_url = self.page.url
        return "login" in current_url or "i/flow/login" in current_url

    async def _wait_for_manual_login(self):
        """
        Espera a que el usuario inicie sesión manualmente, con un timeout.
        """
        print("🔐 Se requiere login. Por favor, inicia sesión manualmente en la ventana del navegador...")
        print(f"⏳ Tienes {LOGIN_TIMEOUT} segundos para iniciar sesión...")
        
        start_time = time.time()
        
        while await self._is_login_required():
            if time.time() - start_time > LOGIN_TIMEOUT:
                raise LoginException(f"Timeout de {LOGIN_TIMEOUT}s esperando el login manual.")
            
            print("   ...esperando a que salgas de la página de login...")
            await asyncio.sleep(2)
        
        print("✅ Login detectado, continuando con el proceso...")

    async def _handle_post_login_navigation(self, url: str):
        """
        Después del login, navega de nuevo a la URL original para asegurar
        que la página de destino se cargue correctamente.
        """
        print(f"🔄 Navegando nuevamente a la página de perfil después del login...")
        await self.navigation_manager.navigate_to_url(url)
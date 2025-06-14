"""
Módulo para la gestión de la navegación web con Playwright.
"""
import asyncio
from playwright.async_api import Page
from ..core.exceptions import NavigationException

class NavigationManager:
    """
    Gestiona la navegación a URLs, implementando estrategias robustas
    de carga y espera para asegurar que la página se cargue correctamente.
    """
    def __init__(self, page: Page):
        self.page = page

    async def navigate_to_url(self, url: str) -> bool:
        """
        Navega a una URL utilizando múltiples estrategias de carga para
        maximizar la probabilidad de éxito.
        """
        print(f"🌐 Navegando a: {url}")
        
        navigation_success = await self._handle_navigation_strategies(url)
        
        if not navigation_success:
            raise NavigationException(f"No se pudo navegar a la página {url} después de múltiples intentos")
        
        await self.wait_for_page_stabilization()
        return True

    async def wait_for_page_stabilization(self, delay: int = 5):
        """Espera un tiempo fijo para que la página se estabilice."""
        print(f"⏳ Esperando {delay}s para estabilización de la página...")
        await asyncio.sleep(delay)

    async def _handle_navigation_strategies(self, url: str) -> bool:
        """
        Intenta navegar a la URL utilizando una lista de estrategias de
        'wait_until' en orden de preferencia, optimizada para X/Twitter.
        """
        strategies = self._get_navigation_strategies()
        
        for strategy, timeout in strategies:
            try:
                print(f"   🔄 Intentando navegación con estrategia '{strategy}' (timeout: {timeout/1000}s)...")
                await self.page.goto(url, wait_until=strategy, timeout=timeout)
                print(f"   ✅ Navegación exitosa con estrategia '{strategy}'")
                return True
            except Exception as e:
                if "networkidle" in strategy:
                    print(f"   ⚠️  Estrategia 'networkidle' falló como esperado: X/Twitter tiene actividad de red constante")
                else:
                    print(f"   ⚠️  Estrategia '{strategy}' falló: {str(e)[:100]}...")
                if strategy != strategies[-1][0]:
                    print(f"   🔄 Intentando siguiente estrategia...")
                else:
                    print(f"   ❌ Todas las estrategias de navegación fallaron")
        return False

    def _get_navigation_strategies(self) -> list[tuple[str, int]]:
        """
        Define las estrategias de navegación optimizadas para X/Twitter.
        Se prioriza 'load' ya que 'networkidle' siempre falla en X debido a la actividad constante.
        """
        return [
            ("load", 30000),         # Esperar al evento 'load' (más rápido y efectivo para X)
            ("domcontentloaded", 45000),  # Esperar a que el DOM esté listo (fallback rápido)
            ("networkidle", 20000),  # Último intento con timeout reducido
        ]
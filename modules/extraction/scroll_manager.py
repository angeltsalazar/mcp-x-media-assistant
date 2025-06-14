"""
Módulo para la gestión del scroll y la carga de contenido dinámico.
"""
import asyncio
import random
from playwright.async_api import Page
from ..utils.logging import Logger
from .url_extractor import URLExtractor
from ..config.constants import MAX_SCROLLS_DEFAULT

class ScrollManager:
    """
    Gestiona el proceso de scroll en la página para cargar más contenido
    y coordina con el URLExtractor para encontrar nuevos medios.
    """
    def __init__(self, page: Page, url_extractor: URLExtractor):
        self.page = page
        self.url_extractor = url_extractor
        self.cache_manager = None
        self.username = None

    def set_cache_info(self, cache_manager, username: str):
        """Configura el cache manager y username para verificar URLs nuevas."""
        self.cache_manager = cache_manager
        self.username = username

    def _get_organic_scroll_delay(self) -> float:
        """
        Calcula un tiempo de espera orgánico para scrolls que simula comportamiento humano.
        
        Returns:
            Tiempo de espera en segundos entre 2.5 y 4.5 segundos con variaciones
        """
        # Tiempo base más realista para scroll (2.5-4.5 segundos)
        base_delay = random.uniform(2.5, 4.5)
        
        # Ocasionalmente hacer pausas más largas (10% de probabilidad)
        if random.random() < 0.1:
            base_delay += random.uniform(1.0, 2.5)  # Pausa larga ocasional
            Logger.info(f"   ⏱️  Aplicando pausa de scroll larga: {base_delay:.2f}s")
        
        return base_delay

    async def scroll_and_extract(self, max_scrolls: int = MAX_SCROLLS_DEFAULT, target_new_urls: int = None):
        """
        Realiza scrolls en la página, extrayendo URLs después de cada uno,
        hasta encontrar el número objetivo de URLs NUEVAS (no cacheadas) o alcanzar el máximo de scrolls.
        
        Args:
            max_scrolls: Número máximo de scrolls a realizar
            target_new_urls: Objetivo de URLs NUEVAS (no cacheadas) a encontrar
        """
        if target_new_urls is not None:
            Logger.info(f"Objetivo: encontrar {target_new_urls} URLs nuevas (no cacheadas)")
        else:
            Logger.info("Buscando todas las URLs disponibles")
        
        # Extraer URLs iniciales antes del primer scroll
        await self.url_extractor.extract_all_status_urls()
        
        initial_count = len(self.url_extractor.all_status_urls)
        scrolls_without_new_content = 0
        new_urls_found = 0  # Contador de URLs realmente nuevas (no cacheadas)

        for i in range(max_scrolls):
            count_before_scroll = len(self.url_extractor.all_status_urls)
            
            # Scroll más gradual para cargar mejor las imágenes
            await self.page.evaluate("window.scrollBy(0, window.innerHeight * 0.7)")
            
            # Espera orgánica entre scrolls para simular comportamiento humano
            scroll_delay = self._get_organic_scroll_delay()
            await asyncio.sleep(scroll_delay)
            
            # Esperar a que se carguen las imágenes
            try:
                await self.page.wait_for_selector('img[src*="pbs.twimg.com"]', timeout=5000)
            except:
                pass  # Continuar si no hay imágenes nuevas
            
            await self.url_extractor.extract_all_status_urls()
            
            count_after_scroll = len(self.url_extractor.all_status_urls)
            new_urls_this_scroll = count_after_scroll - count_before_scroll
            
            # Contar URLs realmente nuevas (no cacheadas) si tenemos cache disponible
            if target_new_urls is not None and self.cache_manager and self.username:
                # Obtener las URLs nuevas de este scroll
                new_urls_batch = self.url_extractor.all_status_urls[count_before_scroll:count_after_scroll]
                uncached_count = self._count_uncached_urls(new_urls_batch)
                new_urls_found += uncached_count
                
                Logger.info(f"Scroll {i+1}/{max_scrolls}: +{new_urls_this_scroll} URLs totales (+{uncached_count} nuevas no cacheadas) - Total nuevas: {new_urls_found}/{target_new_urls}")
                
                # Verificar si alcanzamos el objetivo de URLs nuevas
                if new_urls_found >= target_new_urls:
                    Logger.success(f"¡Objetivo alcanzado! Encontradas {new_urls_found} URLs nuevas (no cacheadas)")
                    break
            else:
                Logger.info(f"Scroll {i+1}/{max_scrolls}: +{new_urls_this_scroll} URLs nuevas (total acumulado: {count_after_scroll})")

            if new_urls_this_scroll == 0:
                scrolls_without_new_content += 1
            else:
                scrolls_without_new_content = 0

            if self._should_stop_scrolling(scrolls_without_new_content):
                Logger.success("No se encontraron más URLs nuevas, terminando scroll")
                break
                
            # Pausa adicional cada 3 scrolls para estabilización con comportamiento más orgánico
            if (i + 1) % 3 == 0:
                stabilization_delay = random.uniform(3.5, 6.0)  # 3.5-6 segundos
                Logger.info(f"Pausa de estabilización después de {i+1} scrolls: {stabilization_delay:.2f}s...")
                await asyncio.sleep(stabilization_delay)
        
        total_urls_extracted = len(self.url_extractor.all_status_urls) - initial_count
        if target_new_urls is not None and self.cache_manager and self.username:
            Logger.info(f"Resumen scroll: {total_urls_extracted} URLs extraídas, {new_urls_found} nuevas (no cacheadas)")
        else:
            Logger.info(f"Resumen scroll: {total_urls_extracted} URLs nuevas agregadas en total")
        
        # Pausa final orgánica para que todas las imágenes se carguen completamente
        final_delay = random.uniform(2.5, 4.0)
        Logger.info(f"Pausa final para cargar todas las imágenes: {final_delay:.2f}s...")
        await asyncio.sleep(final_delay)
        
        final_count = len(self.url_extractor.all_status_urls)
        Logger.success(f"Proceso de scroll finalizado. Total de URLs extraídas: {final_count}")

    def _count_uncached_urls(self, urls_batch: list) -> int:
        """Cuenta cuántas URLs del lote NO están en cache."""
        if not self.cache_manager or not self.username:
            return len(urls_batch)  # Si no hay cache, todas son nuevas
        
        uncached_count = 0
        for url_item in urls_batch:
            url = url_item.get('url', '')
            status_id = self._extract_status_id(url)
            if status_id and not self.cache_manager.is_status_cached(self.username, status_id):
                uncached_count += 1
        
        return uncached_count
    
    def _extract_status_id(self, url: str) -> str:
        """Extrae el ID del status de una URL."""
        try:
            if '/status/' in url:
                return url.split('/status/')[-1].split('?')[0].split('/')[0]
        except:
            pass
        return ""

    def _should_stop_scrolling(self, no_new_content_count: int) -> bool:
        """Determina si el proceso de scroll debe detenerse."""
        return no_new_content_count >= 3
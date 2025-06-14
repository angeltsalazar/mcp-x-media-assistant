"""
Módulo para la extracción de URLs de status desde la página.
"""
import re
from datetime import datetime
from playwright.async_api import Page
from ..utils.url_utils import URLUtils
from ..utils.logging import Logger

class URLExtractor:
    """
    Extrae y gestiona las URLs de status (tweets) encontradas en la página.
    Mantiene el estado de las URLs procesadas para evitar duplicados.
    """
    def __init__(self, page: Page):
        self.page = page
        # Inicializar conjuntos de control como en la versión original
        self.all_status_urls: list[dict] = []
        self.processed_status_ids: set[str] = set()
        self.unique_urls: set[str] = set()
        # Cache info para verificar URLs nuevas
        self.cache_manager = None
        self.username = None

    def set_cache_info(self, cache_manager, username: str):
        """Configura el cache manager y username para verificar URLs nuevas."""
        self.cache_manager = cache_manager
        self.username = username

    async def extract_all_status_urls(self):
        """
        Busca en la página todos los enlaces que parecen ser de status,
        los procesa y los añade a la lista si no han sido vistos antes.
        """
        Logger.info("Buscando enlaces de status en la página...")
        
        try:
            await self.page.wait_for_selector('a[href*="/status/"], article, [data-testid="tweet"]', timeout=10000)
        except Exception:
            Logger.warning("No se encontró contenido")
            return

        status_links = await self.page.query_selector_all('a[href*="/status/"]')
        new_urls_count = 0
        
        Logger.info(f"Encontrados {len(status_links)} enlaces de status en esta página")

        for link in status_links:
            href = await link.get_attribute('href')
            if not href:
                continue

            full_url = f"https://x.com{href}" if not href.startswith('http') else href
            status_id = URLUtils.extract_status_id_from_url(full_url)

            if status_id and status_id not in self.processed_status_ids:
                self.processed_status_ids.add(status_id)
                
                username_match = re.search(r'x\.com/([^/]+)/', full_url)
                username = username_match.group(1) if username_match else "milewskaja_nat"
                
                post_url = f"https://x.com/{username}/status/{status_id}"

                if post_url not in self.unique_urls:
                    self.unique_urls.add(post_url)
                    
                    # Intentar obtener contexto del tweet
                    tweet_text = await self._extract_tweet_text(link)
                    
                    media_data = self._create_media_data_item(full_url, status_id, username, tweet_text)
                    self.all_status_urls.append(media_data)
                    new_urls_count += 1
                    
                    # Logging detallado - verificar si está en cache
                    media_type = media_data['media_type']
                    is_cached = self._is_url_cached(status_id)
                    cache_status = "📀 (ya en cache)" if is_cached else "🆕 (nueva)"
                    Logger.info(f"URL {len(self.all_status_urls)}: {post_url} ({media_type}) {cache_status}")
        
        if new_urls_count > 0:
            Logger.success(f"Se agregaron {new_urls_count} nuevas URLs de status. Total: {len(self.all_status_urls)}")

    def _create_media_data_item(self, href: str, status_id: str, username: str, tweet_text: str = "Sin texto") -> dict:
        """Crea un diccionario estandarizado para una URL de media encontrada."""
        media_type = "video" if '/video/1' in href else "image"
        
        return {
            "url": f"https://x.com/{username}/status/{status_id}",
            "status_id": status_id,
            "username": username,
            "original_link": href,
            "media_type": media_type,
            "tweet_text": tweet_text[:200] + "..." if len(tweet_text) > 200 else tweet_text,
            "found_at": datetime.now().isoformat(),
            "position": len(self.all_status_urls) + 1
        }

    async def _extract_tweet_text(self, link_element) -> str:
        """Extrae el texto del tweet del contenedor padre."""
        try:
            # Buscar el contenedor del tweet
            tweet_container = await link_element.query_selector('xpath=ancestor::article') or await link_element.query_selector('xpath=ancestor::*[@data-testid="tweet"]')
            if tweet_container:
                text_element = await tweet_container.query_selector('[data-testid="tweetText"]')
                if text_element:
                    text_content = await text_element.text_content()
                    return text_content or "Sin texto"
        except Exception:
            pass
        return "Sin texto"
    
    def _is_url_cached(self, status_id: str) -> bool:
        """Verifica si una URL está en cache."""
        if not self.cache_manager or not self.username:
            return False  # Si no hay cache, todas son nuevas
        
        return self.cache_manager.is_status_cached(self.username, status_id)
"""
Módulo del orquestador principal que coordina todo el flujo de trabajo.
"""
import requests
from pathlib import Path
from ..utils.logging import Logger
from ..utils.file_utils import FileUtils
from ..browser.edge_launcher import EdgeLauncher
from ..browser.navigation import NavigationManager
from ..browser.login_handler import LoginHandler
from ..extraction.url_extractor import URLExtractor
from ..extraction.scroll_manager import ScrollManager
from ..extraction.image_processor import ImageProcessor
from ..download.image_downloader import ImageDownloader
from ..download.download_manager import DownloadManager
from ..config.constants import DEFAULT_HEADERS

class EdgeXDownloader:
    """
    Orquesta el proceso completo de descarga de medios.
    """
    def __init__(self, download_dir: Path):
        self.download_dir = download_dir
        self.session = self._create_http_session()
        FileUtils.ensure_directory_exists(self.download_dir)

    def _create_http_session(self) -> requests.Session:
        """Crea y configura una sesión de requests."""
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)
        return session
    
    def _extract_username_from_url(self, profile_url: str) -> str:
        """Extrae el username de una URL de perfil de X/Twitter."""
        try:
            # Ejemplo: https://x.com/username/media -> username
            # o https://twitter.com/username/media -> username
            parts = profile_url.rstrip('/').split('/')
            for i, part in enumerate(parts):
                if part in ['x.com', 'twitter.com'] and i + 1 < len(parts):
                    return parts[i + 1]
            # Fallback: buscar patrón típico
            if '/media' in profile_url:
                username = profile_url.split('/media')[0].split('/')[-1]
                return username
            return "unknown_user"
        except Exception as e:
            Logger.warning(f"No se pudo extraer username de {profile_url}: {e}")
            return "unknown_user"
    
    def print_info(self):
        """Imprimir información de configuración como en la versión original."""
        Logger.info(f"Directorio de descarga: {self.download_dir}")
        Logger.info("Objetivo: Descargar imágenes de la sección Media de X")
        Logger.warning("NOTA: Los videos se detectan pero NO se descargan")
        Logger.info("Para videos usa: x_video_url_extractor.py")
        print()

    async def download_with_edge(self, profile_url: str, use_automation_profile: bool, use_main_profile: bool, url_limit: int = 100):
        """
        Ejecuta el flujo de trabajo completo de descarga.
        
        Args:
            profile_url: URL del perfil a procesar
            use_automation_profile: Si usar perfil de automatización
            use_main_profile: Si usar perfil principal
            url_limit: Límite de URLs nuevas a procesar (100 por defecto, None para sin límite)
        """
        self.print_info()
        
        launcher = EdgeLauncher(use_automation_profile, use_main_profile)
        stats = {}
        try:
            browser = await launcher.launch_browser()
            page = browser.pages[0] if browser.pages else await browser.new_page()

            # Inicializar componentes
            nav_manager = NavigationManager(page)
            login_handler = LoginHandler(page, nav_manager)
            url_extractor = URLExtractor(page)
            scroll_manager = ScrollManager(page, url_extractor)
            image_processor = ImageProcessor(page)
            image_downloader = ImageDownloader(self.session, self.download_dir)
            download_manager = DownloadManager(image_downloader, self.download_dir)

            # Flujo de trabajo (igual que la versión original)
            await nav_manager.navigate_to_url(profile_url)
            await login_handler.check_and_handle_login(profile_url)
            
            # Extraer username de la URL para el cache
            username = self._extract_username_from_url(profile_url)
            Logger.info(f"🔍 Procesando usuario: @{username}")
            
            # Configurar cache para el scroll manager y URL extractor
            from ..utils.cache_manager import CacheManager
            cache_manager = CacheManager()
            scroll_manager.set_cache_info(cache_manager, username)
            url_extractor.set_cache_info(cache_manager, username)
            
            # Mostrar información sobre el límite
            if url_limit is not None:
                Logger.info(f"⚡ Límite de URLs nuevas configurado: {url_limit}")
            else:
                Logger.info("⚡ Sin límite - procesando todas las URLs disponibles")
            
            # Configurar un límite alto de scrolls para permitir explorar todo el contenido
            # El scroll se detendrá cuando:
            # 1. Se encuentre el número de URLs nuevas solicitado, O
            # 2. No haya más contenido para cargar (determinado por ScrollManager)
            max_scrolls = 100  # Límite alto para permitir explorar todo el contenido disponible
            
            # Hacer scroll hasta encontrar las URLs nuevas necesarias
            await scroll_manager.scroll_and_extract(max_scrolls, url_limit)
            
            # Mostrar resumen de extracción como en la versión original
            videos = [item for item in url_extractor.all_status_urls if item.get('media_type') == 'video']
            images_status = [item for item in url_extractor.all_status_urls if item.get('media_type') == 'image']
            
            Logger.success(f"📊 Resumen de extracción:")
            Logger.info(f"   📹 Status URLs extraídas: {len(url_extractor.all_status_urls)}")
            Logger.info(f"   📷 URLs de status de imágenes: {len(images_status)}")
            Logger.info(f"   🎬 URLs de videos detectadas: {len(videos)}")
            
            # Mostrar información detallada de videos si los hay
            if videos:
                Logger.info(f"🎬 Videos detectados:")
                for i, video in enumerate(videos[:3], 1):  # Mostrar primeros 3
                    Logger.info(f"   📹 Video {i}: {video.get('url', '')}")
                if len(videos) > 3:
                    Logger.info(f"   ... y {len(videos) - 3} videos más")
            
            # Pasar el username y el límite al procesador de imágenes para el cache
            image_urls, status_mapping = await image_processor.convert_status_to_image_urls(url_extractor.all_status_urls, username, url_limit)
            
            Logger.info(f"   📷 URLs de imágenes directas: {len(image_urls)}")
            
            # El download manager ahora descarga todas las URLs de imágenes que fueron procesadas
            # (ya que el límite se aplicó en la fase de conversión)
            stats = await download_manager.download_images_batch(image_urls, status_mapping=status_mapping)
            
            # Marcar en cache SOLO lo que realmente se procesó exitosamente
            cache_manager.mark_downloaded_images(username, stats, str(self.download_dir))
            cache_manager.mark_all_status_as_processed(username, url_extractor.all_status_urls)

            # Mostrar información de videos detectados como en la versión original
            if videos:
                Logger.warning(f"📹 Se detectaron {len(videos)} videos (no descargados automáticamente)")
                Logger.info("💡 Para descargar videos usa: x_video_url_extractor.py")
                Logger.info("🔗 URLs de videos guardadas en el JSON generado")

            # Guardar resultados
            await FileUtils.save_media_json(url_extractor.all_status_urls, self.download_dir, profile_url)

        finally:
            if launcher:
                await launcher.close_browser()
        
        return stats
"""
Módulo para la gestión y coordinación de descargas masivas.
"""
import asyncio
import random
from pathlib import Path
from ..utils.logging import Logger
from .image_downloader import ImageDownloader
from .filename_utils import FilenameUtils
from ..config.constants import DOWNLOAD_TIMEOUT

class DownloadManager:
    """
    Orquesta la descarga de un lote de imágenes, manejando límites,
    progreso, y reportes.
    """
    def __init__(self, image_downloader: ImageDownloader, download_dir: Path):
        self.image_downloader = image_downloader
        self.download_dir = download_dir
        self.stats = {'downloaded': 0, 'skipped': 0, 'errors': 0}

    async def download_images_batch(self, urls: list[str], max_images: int = None, status_mapping: dict = None):
        """
        Descarga una lista de imágenes en lote, respetando un límite máximo.
        Si max_images es None, descarga todas las URLs disponibles.
        
        Args:
            urls: Lista de URLs de imágenes
            max_images: Límite máximo de imágenes a descargar
            status_mapping: Diccionario opcional de {url: status_id} para nombres únicos
        """
        if not urls:
            Logger.warning("No se encontraron URLs de imágenes para descargar.")
            return self.stats

        # Si max_images no se especifica, usar todas las URLs disponibles
        download_urls = urls[:max_images] if max_images is not None else urls
        Logger.info(f"Iniciando descarga de {len(download_urls)} de {len(urls)} imágenes encontradas...")

        for i, url in enumerate(download_urls, 1):
            # Obtener status_id si está disponible en el mapeo
            status_id = status_mapping.get(url) if status_mapping else None
            
            filename = FilenameUtils.clean_filename(url, status_id)
            file_path = self.download_dir / filename
            
            # Debug: mostrar cuando se preserva el nombre original 
            if 'pbs.twimg.com' in url and not filename.startswith('image_'):
                original_name = filename.split('-')[-1].replace('.jpg', '') if status_id else filename.replace('.jpg', '')
                if status_id:
                    Logger.info(f"Nombre único: {status_id}-{original_name}")
                else:
                    Logger.info(f"Preservando nombre original: {original_name}")
            
            Logger.progress(i, len(download_urls), f"Descargando {filename}")

            if file_path.exists():
                Logger.info(f"⏭️  '{filename}' ya existe, saltando.")
                self.stats['skipped'] += 1
                continue

            try:
                await asyncio.to_thread(self.image_downloader.download_image, url, filename)
                self.stats['downloaded'] += 1
                await self._add_organic_delay(i, len(download_urls))
            except Exception as e:
                Logger.error(f"Error procesando {filename}: {e}")
                self.stats['errors'] += 1
        
        self._generate_download_report(len(urls), max_images)
        return self.stats

    async def _add_organic_delay(self, current_index: int, total_items: int):
        """Añade un pequeño delay entre descargas para no saturar el servidor."""
        if current_index < total_items:
            await asyncio.sleep(random.uniform(0.3, 0.8))

    def _generate_download_report(self, total_found: int, limit: int = None):
        """Muestra un resumen detallado al finalizar las descargas como en la versión v0.1.5."""
        Logger.info("\n" + "="*25 + " RESUMEN DE DESCARGA " + "="*25)
        Logger.success(f"Descargadas exitosamente: {self.stats['downloaded']}")
        Logger.info(f"Saltadas (ya existían): {self.stats['skipped']}")
        Logger.error(f"Errores de descarga: {self.stats['errors']}")
        
        total_processed = self.stats['downloaded'] + self.stats['skipped'] + self.stats['errors']
        processed_limit = limit if limit is not None else total_found
        Logger.info(f"Total procesadas: {total_processed}/{processed_limit}")
        
        # Explicación de imágenes faltantes como en la versión original
        if limit is not None and total_found > limit:
            not_processed = total_found - limit
            Logger.info(f"\n💡 === DIAGNÓSTICO DE IMÁGENES FALTANTES ===")
            Logger.info(f"Se encontraron {total_found} URLs de imágenes en total")
            Logger.info(f"Se procesaron {limit} (límite de {limit})")
            Logger.info(f"{not_processed} imágenes no se procesaron debido al límite")
            Logger.info(f"Para descargar más, modifica el parámetro max_images")
        
        # Resumen final como en la versión original
        if self.stats['downloaded'] == 0 and self.stats['skipped'] > 0:
            Logger.info(f"\n✅ === TODAS LAS IMÁGENES YA ESTABAN DESCARGADAS ===")
            Logger.info(f"Directorio: {self.download_dir}")
            Logger.info(f"Total en directorio: {self.stats['skipped']} imágenes")
        elif self.stats['downloaded'] > 0:
            Logger.info(f"\n🎉 === DESCARGA COMPLETADA ===")
            Logger.info(f"Directorio: {self.download_dir}")
            Logger.info(f"Nuevas imágenes: {self.stats['downloaded']}")
            Logger.info(f"Total en directorio: {self.stats['downloaded'] + self.stats['skipped']}")
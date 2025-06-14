#!/usr/bin/env python3
"""
Script para descargar archivos multimedia de X (Twitter) usando Playwright
Autor: Asistente AI
Fecha: 11 de junio de 2025
"""

import os
import asyncio
import requests
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
import json
from datetime import datetime

class XMediaDownloader:
    def __init__(self, download_dir=None):
        """
        Inicializa el descargador de medios de X
        
        Args:
            download_dir (str): Directorio donde descargar los archivos. 
                               Por defecto usa ~/Downloads/X_Media
        """
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Media"
        else:
            self.download_dir = Path(download_dir)
        
        # Crear directorio si no existe
        self.download_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio de descarga: {self.download_dir}")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    async def download_media_from_profile(self, profile_url, max_scrolls=5):
        """
        Descarga medios de un perfil de X
        
        Args:
            profile_url (str): URL del perfil de X
            max_scrolls (int): Número máximo de scrolls para cargar más contenido
        """
        print(f"🚀 Iniciando descarga de medios de: {profile_url}")
        
        async with async_playwright() as p:
            # Lanzar navegador
            browser = await p.chromium.launch(
                headless=False,  # Cambiar a True para modo sin ventana
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            try:
                page = await browser.new_page()
                
                # Configurar viewport
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Navegar a la URL
                print(f"📱 Navegando a: {profile_url}")
                await page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
                
                # Esperar a que cargue el contenido
                await page.wait_for_timeout(3000)
                
                # Buscar medios iniciales
                media_urls = set()
                
                # Scroll para cargar más contenido
                for scroll in range(max_scrolls):
                    print(f"📜 Scroll {scroll + 1}/{max_scrolls}")
                    
                    # Buscar imágenes y videos
                    current_media = await self._extract_media_urls(page)
                    media_urls.update(current_media)
                    
                    # Hacer scroll hacia abajo
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(2000)
                
                print(f"🎯 Encontrados {len(media_urls)} archivos multimedia")
                
                # Descargar archivos
                await self._download_files(media_urls, profile_url)
                
            except Exception as e:
                print(f"❌ Error durante la navegación: {e}")
            
            finally:
                await browser.close()
    
    async def _extract_media_urls(self, page):
        """
        Extrae URLs de medios de la página actual
        
        Args:
            page: Página de Playwright
            
        Returns:
            set: Conjunto de URLs de medios encontradas
        """
        media_urls = set()
        
        try:
            # Buscar imágenes
            images = await page.query_selector_all('img[src*="pbs.twimg.com"]')
            for img in images:
                src = await img.get_attribute('src')
                if src and ('jpg' in src or 'png' in src or 'webp' in src):
                    # Obtener versión de alta calidad
                    if '?format=' in src:
                        high_quality_url = src.split('?')[0] + '?format=jpg&name=large'
                    else:
                        high_quality_url = src
                    media_urls.add(high_quality_url)
            
            # Buscar videos
            videos = await page.query_selector_all('video')
            for video in videos:
                src = await video.get_attribute('src')
                if src:
                    media_urls.add(src)
                
                # Buscar en el elemento source dentro del video
                sources = await video.query_selector_all('source')
                for source in sources:
                    src = await source.get_attribute('src')
                    if src:
                        media_urls.add(src)
            
            # Buscar enlaces de video en data attributes
            video_elements = await page.query_selector_all('[data-testid="videoPlayer"]')
            for element in video_elements:
                # Intentar extraer URL del video del HTML
                html = await element.inner_html()
                video_urls = re.findall(r'https://[^"\']*\.mp4[^"\']*', html)
                media_urls.update(video_urls)
        
        except Exception as e:
            print(f"⚠️  Error extrayendo URLs de medios: {e}")
        
        return media_urls
    
    async def _download_files(self, media_urls, source_url):
        """
        Descarga los archivos de medios
        
        Args:
            media_urls (set): Conjunto de URLs de medios
            source_url (str): URL fuente del perfil
        """
        if not media_urls:
            print("❌ No se encontraron archivos multimedia para descargar")
            return
        
        # Crear subdirectorio con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        profile_name = source_url.split('/')[-2] if source_url.endswith('/') else source_url.split('/')[-1]
        session_dir = self.download_dir / f"{profile_name}_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(media_urls)} archivos en: {session_dir}")
        
        downloaded_count = 0
        failed_count = 0
        
        for i, url in enumerate(media_urls, 1):
            try:
                print(f"⬇️  Descargando {i}/{len(media_urls)}: {url[:60]}...")
                
                # Descargar archivo
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Determinar extensión del archivo
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # Determinar extensión por content-type
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        ext = '.jpg' if 'jpeg' in content_type else '.png'
                    elif 'video' in content_type:
                        ext = '.mp4'
                    else:
                        ext = '.bin'
                    filename = f"media_{i:04d}{ext}"
                
                # Guardar archivo
                file_path = session_dir / filename
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_count += 1
                print(f"✅ Descargado: {filename} ({len(response.content)} bytes)")
                
            except Exception as e:
                failed_count += 1
                print(f"❌ Error descargando {url}: {e}")
        
        # Guardar log de la sesión
        log_data = {
            'timestamp': timestamp,
            'source_url': source_url,
            'total_found': len(media_urls),
            'downloaded': downloaded_count,
            'failed': failed_count,
            'download_dir': str(session_dir),
            'urls': list(media_urls)
        }
        
        log_file = session_dir / 'download_log.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Resumen: {downloaded_count} descargados, {failed_count} fallidos")
        print(f"📋 Log guardado en: {log_file}")

async def main():
    """Función principal"""
    # URL del perfil de X
    profile_url = "https://x.com/milewskaja_nat/media"
    
    # Crear descargador
    downloader = XMediaDownloader()
    
    # Descargar medios
    await downloader.download_media_from_profile(profile_url, max_scrolls=10)

if __name__ == "__main__":
    print("🎬 X Media Downloader")
    print("=" * 50)
    asyncio.run(main())

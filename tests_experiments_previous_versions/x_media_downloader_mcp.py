#!/usr/bin/env python3
"""
Script específico para descargar medios de X usando Playwright MCP
Autor: Asistente AI
Fecha: 11 de junio de 2025
"""

import os
import asyncio
import requests
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright

class XMediaDownloaderMCP:
    def __init__(self, download_dir=None):
        """
        Inicializa el descargador usando Playwright MCP
        """
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Media_Downloads"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio de descarga: {self.download_dir}")
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    async def run_automation(self, profile_url):
        """
        Ejecuta la automatización completa
        """
        print(f"🚀 Iniciando automatización para: {profile_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # Navegar a la página
                print(f"📱 Navegando a: {profile_url}")
                await page.goto(profile_url, wait_until='networkidle', timeout=60000)
                
                # Esperar a que cargue el contenido
                await page.wait_for_timeout(5000)
                
                # Scroll para cargar más contenido
                await self._scroll_and_load_content(page)
                
                # Extraer URLs de medios
                media_urls = await self._extract_all_media(page)
                
                if media_urls:
                    print(f"🎯 Encontrados {len(media_urls)} archivos multimedia")
                    await self._download_all_media(media_urls, profile_url)
                else:
                    print("❌ No se encontraron archivos multimedia")
                
            except Exception as e:
                print(f"❌ Error en la automatización: {e}")
            finally:
                await browser.close()
    
    async def _scroll_and_load_content(self, page, max_scrolls=15):
        """
        Hace scroll para cargar más contenido
        """
        print("📜 Cargando contenido con scroll...")
        
        for i in range(max_scrolls):
            # Scroll hacia abajo
            await page.evaluate("window.scrollBy(0, window.innerHeight)")
            await page.wait_for_timeout(2000)
            
            # Verificar si hay más contenido que cargar
            current_height = await page.evaluate("document.body.scrollHeight")
            await page.wait_for_timeout(1000)
            new_height = await page.evaluate("document.body.scrollHeight")
            
            print(f"   Scroll {i+1}/{max_scrolls} - Altura: {current_height}")
            
            # Si no hay más contenido, parar
            if current_height == new_height:
                print("✅ No hay más contenido que cargar")
                break
    
    async def _extract_all_media(self, page):
        """
        Extrae todas las URLs de medios de la página
        """
        print("🔍 Extrayendo URLs de medios...")
        
        media_urls = set()
        
        try:
            # Extraer imágenes de alta calidad
            images = await page.query_selector_all('img[src*="pbs.twimg.com"]')
            print(f"   Encontradas {len(images)} imágenes")
            
            for img in images:
                src = await img.get_attribute('src')
                if src and any(fmt in src for fmt in ['jpg', 'png', 'webp']):
                    # Convertir a alta calidad
                    high_quality_url = self._get_high_quality_image_url(src)
                    media_urls.add(high_quality_url)
            
            # Extraer videos
            videos = await page.query_selector_all('video')
            print(f"   Encontrados {len(videos)} videos")
            
            for video in videos:
                # Buscar en el atributo src
                src = await video.get_attribute('src')
                if src:
                    media_urls.add(src)
                
                # Buscar en elementos source
                sources = await video.query_selector_all('source')
                for source in sources:
                    src = await source.get_attribute('src')
                    if src:
                        media_urls.add(src)
            
            # Buscar videos en contenedores específicos de Twitter
            video_containers = await page.query_selector_all('[data-testid="videoComponent"]')
            for container in video_containers:
                html = await container.inner_html()
                video_urls = re.findall(r'https://[^"\']+\.mp4[^"\']*', html)
                media_urls.update(video_urls)
            
            # Buscar más patrones de video en el HTML completo
            page_content = await page.content()
            additional_videos = re.findall(r'https://video\.twimg\.com/[^"\']+\.mp4[^"\']*', page_content)
            media_urls.update(additional_videos)
            
        except Exception as e:
            print(f"⚠️  Error extrayendo medios: {e}")
        
        return list(media_urls)
    
    def _get_high_quality_image_url(self, url):
        """
        Convierte URL de imagen a alta calidad
        """
        if '?' in url:
            base_url = url.split('?')[0]
            return f"{base_url}?format=jpg&name=large"
        return url
    
    async def _download_all_media(self, media_urls, source_url):
        """
        Descarga todos los archivos de medios
        """
        if not media_urls:
            return
        
        # Crear directorio de sesión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        username = self._extract_username_from_url(source_url)
        session_dir = self.download_dir / f"{username}_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(media_urls)} archivos en: {session_dir}")
        
        downloaded = 0
        failed = 0
        
        for i, url in enumerate(media_urls, 1):
            try:
                print(f"⬇️  [{i}/{len(media_urls)}] Descargando: {url[:50]}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Determinar nombre de archivo
                filename = self._generate_filename(url, i)
                file_path = session_dir / filename
                
                # Guardar archivo
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"✅ Guardado: {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
            except Exception as e:
                print(f"❌ Error descargando: {e}")
                failed += 1
        
        # Crear log de descarga
        self._create_download_log(session_dir, {
            'source_url': source_url,
            'username': username,
            'timestamp': timestamp,
            'total_found': len(media_urls),
            'downloaded': downloaded,
            'failed': failed,
            'urls': media_urls
        })
        
        print(f"📊 Resumen final: {downloaded} exitosos, {failed} fallidos")
    
    def _extract_username_from_url(self, url):
        """
        Extrae el nombre de usuario de la URL
        """
        try:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part == 'x.com' or part == 'twitter.com':
                    return parts[i + 1] if i + 1 < len(parts) else 'unknown_user'
            return 'unknown_user'
        except:
            return 'unknown_user'
    
    def _generate_filename(self, url, index):
        """
        Genera nombre de archivo apropiado
        """
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                # Determinar extensión por URL
                if 'jpg' in url or 'jpeg' in url:
                    ext = '.jpg'
                elif 'png' in url:
                    ext = '.png'
                elif 'webp' in url:
                    ext = '.webp'
                elif 'mp4' in url:
                    ext = '.mp4'
                else:
                    ext = '.bin'
                
                filename = f"media_{index:04d}{ext}"
            
            return filename
        except:
            return f"media_{index:04d}.bin"
    
    def _create_download_log(self, session_dir, data):
        """
        Crea archivo de log de la descarga
        """
        log_file = session_dir / 'download_session.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📋 Log creado: {log_file}")

async def main():
    """Función principal"""
    url = "https://x.com/milewskaja_nat/media"
    
    print("🎬 X Media Downloader MCP")
    print("=" * 60)
    print(f"🎯 URL objetivo: {url}")
    print()
    
    downloader = XMediaDownloaderMCP()
    await downloader.run_automation(url)
    
    print()
    print("🏁 Proceso completado!")

if __name__ == "__main__":
    asyncio.run(main())

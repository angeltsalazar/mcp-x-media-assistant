#!/usr/bin/env python3
"""
Automatización completa para descargar medios de X usando Playwright
Autor: Asistente AI
Fecha: 11 de junio de 2025

Este script utiliza Playwright para navegar a una página de medios de X,
extraer todas las URLs de imágenes y videos, y descargarlos automáticamente
al directorio Downloads del usuario.
"""

import os
import asyncio
import requests
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urljoin
from playwright.async_api import async_playwright
import time

class XMediaDownloaderAutomation:
    def __init__(self, download_dir=None):
        """Inicializa el descargador automático"""
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Media_Automation"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sesión HTTP para descargas
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    async def extract_and_download_media(self, profile_url):
        """
        Función principal que extrae y descarga medios
        """
        print(f"🚀 Iniciando automatización para: {profile_url}")
        
        async with async_playwright() as p:
            # Configurar navegador
            browser = await p.chromium.launch(
                headless=False,  # Cambiar a True para ejecutar sin ventana
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-extensions',
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            try:
                # Navegar a la página de medios
                print(f"📱 Navegando a: {profile_url}")
                await page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
                await page.wait_for_timeout(3000)
                
                # Hacer clic en la pestaña Media si no estamos ya ahí
                if '/media' not in profile_url:
                    try:
                        await page.click('text=Media')
                        await page.wait_for_timeout(2000)
                    except:
                        # Si hay un modal, cerrarlo
                        try:
                            await page.keyboard.press('Escape')
                            await page.wait_for_timeout(1000)
                            await page.click('text=Media')
                            await page.wait_for_timeout(2000)
                        except:
                            print("⚠️  No se pudo hacer clic en la pestaña Media")
                
                # Scroll para cargar más contenido
                print("📜 Cargando contenido con scroll...")
                await self._scroll_to_load_content(page)
                
                # Extraer URLs de medios
                media_urls = await self._extract_media_urls_from_page(page)
                
                if media_urls:
                    print(f"🎯 Encontrados {len(media_urls)} archivos multimedia")
                    
                    # Descargar archivos
                    username = self._extract_username_from_url(profile_url)
                    await self._download_media_files(media_urls, username, profile_url)
                else:
                    print("❌ No se encontraron archivos multimedia")
                
            except Exception as e:
                print(f"❌ Error durante la automatización: {e}")
            
            finally:
                await browser.close()
    
    async def _scroll_to_load_content(self, page, max_scrolls=20):
        """Hace scroll para cargar más contenido"""
        print("📜 Haciendo scroll para cargar más contenido...")
        
        previous_count = 0
        no_change_count = 0
        
        for i in range(max_scrolls):
            # Contar elementos multimedia actuales
            current_count = await page.evaluate("""
                () => {
                    const mediaLinks = document.querySelectorAll('a[href*="/photo/"], a[href*="/video/"]');
                    return mediaLinks.length;
                }
            """)
            
            print(f"   Scroll {i+1}/{max_scrolls} - Elementos encontrados: {current_count}")
            
            # Si no hay cambios en 3 scrolls consecutivos, parar
            if current_count == previous_count:
                no_change_count += 1
                if no_change_count >= 3:
                    print("✅ No hay más contenido que cargar")
                    break
            else:
                no_change_count = 0
            
            previous_count = current_count
            
            # Hacer scroll
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
        
        print(f"✅ Scroll completado. Total de elementos: {current_count}")
    
    async def _extract_media_urls_from_page(self, page):
        """Extrae todas las URLs de medios de la página"""
        print("🔍 Extrayendo URLs de medios...")
        
        media_urls = await page.evaluate("""
            () => {
                const mediaUrls = new Set();
                
                // Buscar enlaces de fotos
                const photoLinks = document.querySelectorAll('a[href*="/photo/"]');
                photoLinks.forEach(link => {
                    mediaUrls.add(link.href);
                });
                
                // Buscar enlaces de videos
                const videoLinks = document.querySelectorAll('a[href*="/video/"]');
                videoLinks.forEach(link => {
                    mediaUrls.add(link.href);
                });
                
                return Array.from(mediaUrls);
            }
        """)
        
        print(f"🔍 URLs de medios extraídas: {len(media_urls)}")
        return media_urls
    
    async def _get_actual_media_urls(self, media_page_urls):
        """
        Convierte URLs de páginas de medios a URLs directas de archivos
        """
        print("🔗 Convirtiendo URLs de páginas a URLs directas...")
        direct_urls = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            for i, url in enumerate(media_page_urls[:10]):  # Limitar a las primeras 10 para ejemplo
                try:
                    page = await context.new_page()
                    await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(2000)
                    
                    # Buscar imágenes de alta calidad
                    img_urls = await page.evaluate("""
                        () => {
                            const urls = new Set();
                            
                            // Buscar imágenes de alta calidad
                            const images = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                            images.forEach(img => {
                                if (img.src && (img.src.includes('jpg') || img.src.includes('png') || img.src.includes('webp'))) {
                                    // Convertir a alta calidad
                                    let highQualityUrl = img.src;
                                    if (highQualityUrl.includes('?')) {
                                        highQualityUrl = highQualityUrl.split('?')[0] + '?format=jpg&name=large';
                                    }
                                    urls.add(highQualityUrl);
                                }
                            });
                            
                            // Buscar videos
                            const videos = document.querySelectorAll('video[src], source[src]');
                            videos.forEach(video => {
                                if (video.src) {
                                    urls.add(video.src);
                                }
                            });
                            
                            return Array.from(urls);
                        }
                    """)
                    
                    direct_urls.extend(img_urls)
                    await page.close()
                    
                    print(f"   Procesada página {i+1}/{len(media_page_urls[:10])}")
                    
                except Exception as e:
                    print(f"⚠️  Error procesando {url}: {e}")
                    continue
            
            await browser.close()
        
        # Eliminar duplicados
        direct_urls = list(set(direct_urls))
        print(f"🔗 URLs directas obtenidas: {len(direct_urls)}")
        return direct_urls
    
    async def _download_media_files(self, media_page_urls, username, source_url):
        """Descarga los archivos de medios"""
        if not media_page_urls:
            print("❌ No hay URLs para procesar")
            return
        
        # Obtener URLs directas
        direct_urls = await self._get_actual_media_urls(media_page_urls)
        
        if not direct_urls:
            print("❌ No se pudieron extraer URLs directas")
            return
        
        # Crear directorio de sesión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.download_dir / f"{username}_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(direct_urls)} archivos en: {session_dir}")
        
        downloaded = 0
        failed = 0
        
        for i, url in enumerate(direct_urls, 1):
            try:
                print(f"⬇️  [{i}/{len(direct_urls)}] {url[:60]}...")
                
                # Descargar archivo
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Generar nombre de archivo
                filename = self._generate_filename_from_url(url, i)
                file_path = session_dir / filename
                
                # Guardar archivo
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"✅ {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
                # Pequeña pausa para no sobrecargar el servidor
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error descargando {url}: {e}")
                failed += 1
                continue
        
        # Crear log de la sesión
        self._create_session_log(session_dir, {
            'source_url': source_url,
            'username': username,
            'timestamp': timestamp,
            'media_page_urls': len(media_page_urls),
            'direct_urls_found': len(direct_urls),
            'downloaded': downloaded,
            'failed': failed,
            'downloaded_urls': direct_urls
        })
        
        print(f"📊 Descarga completada: {downloaded} exitosos, {failed} fallidos")
        print(f"📂 Archivos guardados en: {session_dir}")
    
    def _extract_username_from_url(self, url):
        """Extrae el nombre de usuario de la URL"""
        try:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part in ['x.com', 'twitter.com'] and i + 1 < len(parts):
                    return parts[i + 1]
            return 'unknown_user'
        except:
            return 'unknown_user'
    
    def _generate_filename_from_url(self, url, index):
        """Genera nombre de archivo apropiado"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                # Determinar extensión por URL
                if any(fmt in url.lower() for fmt in ['jpg', 'jpeg']):
                    ext = '.jpg'
                elif 'png' in url.lower():
                    ext = '.png'
                elif 'webp' in url.lower():
                    ext = '.webp'
                elif 'mp4' in url.lower():
                    ext = '.mp4'
                else:
                    ext = '.bin'
                
                filename = f"media_{index:04d}{ext}"
            
            # Limpiar nombre de archivo
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            return filename
            
        except:
            return f"media_{index:04d}.bin"
    
    def _create_session_log(self, session_dir, data):
        """Crea archivo de log de la sesión"""
        log_file = session_dir / 'download_session.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"📋 Log creado: {log_file}")

async def main():
    """Función principal"""
    # URL del perfil de medios de X
    profile_url = "https://x.com/milewskaja_nat/media"
    
    print("🎬 X Media Downloader Automation")
    print("=" * 60)
    print(f"🎯 URL objetivo: {profile_url}")
    print("⚠️  NOTA: Este script requiere que tengas una sesión activa en X")
    print("   Asegúrate de estar logueado en tu navegador antes de ejecutar")
    print()
    
    # Crear instancia del descargador
    downloader = XMediaDownloaderAutomation()
    
    # Ejecutar automatización
    await downloader.extract_and_download_media(profile_url)
    
    print()
    print("🏁 Automatización completada!")
    print(f"📂 Revisa tu directorio: {downloader.download_dir}")

if __name__ == "__main__":
    asyncio.run(main())

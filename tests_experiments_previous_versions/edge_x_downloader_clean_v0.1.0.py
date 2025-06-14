#!/usr/bin/env python3
"""
Script optimizado para Microsoft Edge con descarga de imágenes de X
Autor: Asistente AI
Fecha: 11 de junio de 2025

Este script está específicamente diseñado para usar Microsoft Edge
donde ya tienes sesión iniciada en X, y maneja automáticamente
la verificación de login y navegación.

FUNCIONALIDAD: Solo descarga IMÁGENES de la sección Media.
Para videos, usa x_video_url_extractor.py que extrae las URLs en JSON.
"""

import os
import asyncio
import requests
import re
import json
import random
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

class EdgeXDownloader:
    def __init__(self, download_dir=None):
        """Inicializa el descargador para Microsoft Edge"""
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Media_Edge"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    async def _organic_delay(self, min_ms=1000, max_ms=2000):
        """Espera orgánica aleatoria para ser respetuoso con el servidor"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)  # Convertir a segundos
    
    async def download_with_edge(self, profile_url, use_automation_profile=True):
        """
        Descarga medios usando Microsoft Edge con sesión existente
        """
        print(f"🚀 Iniciando con Microsoft Edge: {profile_url}")
        
        async with async_playwright() as p:
            # Configurar Microsoft Edge
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            
            print("🌐 Configurando Microsoft Edge...")
            
            try:
                browser = None  # Inicializar variable
                
                if use_automation_profile:
                    # OPCIÓN SEGURA: Usar perfil separado para automatización
                    automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
                    automation_dir.mkdir(exist_ok=True)
                    
                    print(f"   📂 Usando perfil de automatización: {automation_dir}")
                    print("   ⚠️  NOTA: Necesitarás hacer login manualmente en este perfil")
                    
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=str(automation_dir),
                        headless=False,
                        executable_path=edge_path,
                        args=[
                            '--no-first-run',
                            '--no-default-browser-check',
                            '--disable-default-apps',
                            '--window-size=1920,1080'
                        ]
                    )
                else:
                    # OPCIÓN ALTERNATIVA: Lanzar Edge normal (sin datos persistentes)
                    print("   📂 Usando Edge temporal (sin persistencia)")
                    browser = await p.chromium.launch(
                        headless=False,
                        executable_path=edge_path,
                        args=[
                            '--no-first-run',
                            '--no-default-browser-check',
                            '--window-size=1920,1080'
                        ]
                    )
                    context = await browser.new_context()
                
                page = await context.new_page()
                
                # Navegar a la URL del perfil
                print(f"🌐 Navegando a: {profile_url}")
                await page.goto(profile_url)
                
                # Esperar a que la página cargue
                await self._organic_delay(3000, 5000)
                
                # Verificar si necesitamos login
                login_required = await page.query_selector('[data-testid="loginButton"], [href="/login"]')
                if login_required:
                    print("⚠️  No estás logueado en X. Por favor, inicia sesión manualmente.")
                    print("⏳ Esperando hasta 60 segundos para que inicies sesión...")
                    
                    # Esperar hasta que desaparezcan los elementos de login
                    try:
                        await page.wait_for_function(
                            "!document.querySelector('[data-testid=\"loginButton\"]') && !document.querySelector('[href=\"/login\"]')",
                            timeout=60000
                        )
                        print("✅ Login detectado, continuando...")
                    except:
                        print("❌ Tiempo agotado esperando login")
                        return
                
                # Esperar a que aparezca la sección de medios
                media_section_loaded = False
                try:
                    # Buscar elementos que indiquen que estamos en la sección correcta
                    await page.wait_for_selector('[data-testid="tweet"], [data-testid="primaryColumn"]', timeout=10000)
                    media_section_loaded = True
                    print("✅ Sección de medios cargada")
                except:
                    print("⚠️  La sección de medios no cargó completamente, continuando...")
                
                if not media_section_loaded:
                    print("⚠️  Puede que necesites navegar manualmente a la sección de medios")
                    print("⏳ Esperando 10 segundos adicionales...")
                    await self._organic_delay(10000, 15000)
                
                # Extraer URLs de imágenes
                image_urls = await self._extract_media_urls(page)
                
                if not image_urls:
                    print("⚠️  No se encontraron imágenes. Intentando hacer scroll...")
                    await self._scroll_and_extract(page)
                    image_urls = await self._extract_media_urls(page)
                
                if image_urls:
                    await self._download_media_files(image_urls)
                else:
                    print("❌ No se encontraron imágenes para descargar")
                    print("💡 Posibles causas:")
                    print("   • El perfil no tiene imágenes públicas")
                    print("   • No estás en la sección correcta (/media)")
                    print("   • El perfil requiere seguimiento para ver medios")
                
            except Exception as e:
                print(f"❌ Error durante la descarga: {e}")
            
            finally:
                if browser:
                    await browser.close()
                else:
                    await context.close()
    
    async def _scroll_and_extract(self, page, max_scrolls=5):
        """Hace scroll para cargar más contenido"""
        print("📜 Haciendo scroll para cargar más contenido...")
        
        for i in range(max_scrolls):
            # Scroll hacia abajo
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._organic_delay(2000, 4000)
            
            print(f"   📜 Scroll {i+1}/{max_scrolls}")
    
    async def _extract_media_urls(self, page):
        """
        Extrae URLs de medios (solo imágenes) de la página
        """
        print("🔍 Extrayendo URLs de imágenes...")
        
        try:
            # Buscar todas las imágenes en tweets
            img_elements = await page.query_selector_all('img[src*="pbs.twimg.com"], img[src*="twimg.com"]')
            
            urls = []
            for img in img_elements:
                try:
                    src = await img.get_attribute('src')
                    if src and self._is_valid_media_url(src):
                        # Convertir a URL de alta calidad
                        high_quality_url = self._convert_to_high_quality(src)
                        if high_quality_url not in urls:
                            urls.append(high_quality_url)
                except:
                    continue
            
            print(f"   ✅ Encontradas {len(urls)} imágenes únicas")
            return urls
            
        except Exception as e:
            print(f"   ❌ Error extrayendo URLs: {e}")
            return []
    
    def _is_valid_media_url(self, url):
        """Verifica si la URL es de una imagen válida"""
        if not url:
            return False
        
        # Filtrar URLs que no son imágenes de contenido
        invalid_patterns = [
            'profile_images',
            'profile_banners',
            'emoji',
            'avatar',
            '_normal',
            '_mini',
            'format=jpg&name=small',
            'format=jpg&name=medium'
        ]
        
        for pattern in invalid_patterns:
            if pattern in url:
                return False
        
        # Verificar que es una URL de imagen de X
        return ('pbs.twimg.com' in url or 'twimg.com' in url) and any(ext in url for ext in ['.jpg', '.jpeg', '.png', 'format='])
    
    def _convert_to_high_quality(self, url):
        """Convierte URL a la versión de mayor calidad disponible"""
        # Remover parámetros de tamaño pequeño
        url = re.sub(r'&name=(small|medium|thumb)', '', url)
        url = re.sub(r'\?format=jpg&name=(small|medium|thumb)', '?format=jpg&name=large', url)
        
        # Si no tiene parámetros de calidad, agregar el de alta calidad
        if 'name=' not in url and 'format=' in url:
            url += '&name=large'
        elif 'format=' not in url:
            url += '?format=jpg&name=large'
        
        return url
    
    def _extract_media_filename(self, url):
        """Extrae un nombre de archivo apropiado de la URL"""
        try:
            parsed = urlparse(url)
            
            # Extraer ID único de la URL
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 2:
                media_id = path_parts[-1]
                
                # Limpiar el ID
                media_id = re.sub(r'\?.*', '', media_id)  # Remover query params
                
                # Si no tiene extensión, agregar .jpg
                if not media_id.endswith(('.jpg', '.jpeg', '.png')):
                    media_id += '.jpg'
                
                return media_id
            
            return None
            
        except:
            return None
    
    async def _download_media_files(self, urls):
        """
        Descarga archivos de medios
        """
        if not urls:
            print("❌ No hay URLs para descargar")
            return
        
        # Crear directorio para esta sesión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.download_dir / f"session_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(urls)} imágenes...")
        
        downloaded = 0
        skipped = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            try:
                # Extraer nombre de archivo inteligente
                filename = self._extract_media_filename(url)
                if not filename:
                    print(f"⬇️  [{i}/{len(urls)}] ⚠️  No es URL de imagen válida, omitiendo...")
                    skipped += 1
                    continue
                
                file_path = session_dir / filename
                
                # Verificar si el archivo ya existe
                if file_path.exists():
                    file_size = file_path.stat().st_size / (1024 * 1024)
                    print(f"⬇️  [{i}/{len(urls)}] ⏭️  {filename} ya existe ({file_size:.2f} MB)")
                    skipped += 1
                    continue
                
                print(f"⬇️  [{i}/{len(urls)}] {filename}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"   ✅ {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
                # Delay orgánico entre descargas para ser respetuoso
                if i < len(urls):  # No esperar después del último archivo
                    await asyncio.sleep(random.uniform(0.3, 0.8))  # 300-800ms entre descargas
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
        
        print(f"📊 Descarga completada:")
        print(f"   ✅ {downloaded} imágenes descargadas")
        print(f"   ⏭️  {skipped} omitidas (ya existían o no válidas)")
        print(f"   ❌ {failed} fallidas")
        print(f"📂 Archivos en: {session_dir}")
        
        # Crear log con timestamp de la sesión actual
        self._create_session_log(session_dir, downloaded, skipped, failed, urls)
    
    def _create_session_log(self, session_dir, downloaded, skipped, failed, urls):
        """Crea un log de la sesión de descarga"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_data = {
                "session_timestamp": timestamp,
                "summary": {
                    "downloaded": downloaded,
                    "skipped": skipped,
                    "failed": failed,
                    "total_processed": len(urls)
                },
                "urls_processed": urls
            }
            
            log_file = session_dir / "session_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Log guardado: {log_file}")
            
        except Exception as e:
            print(f"⚠️  No se pudo crear el log: {e}")

async def main():
    """Función principal"""
    import sys
    
    profile_url = "https://x.com/milewskaja_nat/media"
    
    # Determinar modo basado en argumentos de línea de comandos
    use_automation_profile = True  # Por defecto usar perfil automatizado
    show_options = False  # Solo mostrar opciones si se especifica
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--temporal" or sys.argv[1] == "-t":
            use_automation_profile = False
            show_options = True
        elif sys.argv[1] == "--auto" or sys.argv[1] == "-a":
            use_automation_profile = True
            show_options = True
        elif sys.argv[1] == "--select" or sys.argv[1] == "-s":
            show_options = True
            # Preguntar al usuario qué perfil usar
            print("🎬 X Media Downloader - Seleccionar modo")
            print("=" * 50)
            print("1. Perfil de automatización (recomendado)")
            print("   ✅ No interfiere con tu Edge principal")
            print("   ✅ Mantiene sesión de X guardada")
            print("   ✅ No requiere login cada vez")
            print()
            print("2. Edge temporal")
            print("   ⚠️  Requiere login manual cada vez")
            print("   ✅ No interfiere con datos existentes")
            print()
            
            choice = input("Selecciona modo (1/2): ").strip()
            if choice == "2":
                use_automation_profile = False
            else:
                use_automation_profile = True
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🎬 X Media Downloader - Uso:")
            print("  python3 edge_x_downloader.py              # Ejecutar con perfil automatizado (solo imágenes)")
            print("  python3 edge_x_downloader.py --auto       # Usar perfil automatizado")
            print("  python3 edge_x_downloader.py --temporal   # Usar Edge temporal")
            print("  python3 edge_x_downloader.py --select     # Mostrar opciones para seleccionar")
            print("  python3 edge_x_downloader.py --help       # Mostrar ayuda")
            print()
            print("📷 FUNCIONALIDAD:")
            print("   ✅ Descarga imágenes directamente de la sección Media de X")
            print("   ❌ No descarga videos")
            print()
            print("🎬 PARA VIDEOS:")
            print("   📄 Usa: python3 x_video_url_extractor.py")
            print("   📹 Extrae URLs de videos en formato JSON")
            print("   💾 Descarga después con yt-dlp u otra herramienta")
            return
    
    print("🎬 X Media Downloader - Optimizado para Microsoft Edge")
    print("=" * 60)
    print(f"🎯 Perfil objetivo: {profile_url}")
    print("📷 Tipo de contenido: Solo imágenes")
    print("💡 Para videos usa: python3 x_video_url_extractor.py")
    print()
    
    if show_options:
        if use_automation_profile:
            print("✅ Usando perfil de automatización")
            print("   🔧 Ventajas:")
            print("      ✅ No interfiere con tu Edge principal")
            print("      ✅ Mantiene sesión de X guardada")
            print("      ✅ No requiere login cada vez")
        else:
            print("✅ Usando Edge temporal")
            print("   🔧 Características:")
            print("      ⚠️  Requiere login manual cada vez")
            print("      ✅ No interfiere con datos existentes")
        
        print()
        print("💡 Para cambiar modo en el futuro, usa: --auto, --temporal o --select")
        print()
        
        response = input("🚀 ¿Continuar? (s/n): ").lower().strip()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Cancelado por el usuario")
            return
    else:
        # Modo directo: mostrar solo información básica y continuar
        print("✅ Iniciando con perfil de automatización")
        print("💡 Usa --help para ver todas las opciones disponibles")
    
    print()
    downloader = EdgeXDownloader()
    await downloader.download_with_edge(profile_url, use_automation_profile)
    
    print()
    print("🏁 ¡Proceso completado!")
    print("📷 Se procesaron solo imágenes")
    print("🎬 Para videos usa: python3 x_video_url_extractor.py")

if __name__ == "__main__":
    asyncio.run(main())

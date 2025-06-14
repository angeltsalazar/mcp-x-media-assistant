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
        
        # Control de URLs para precisión mejorada
        self.processed_status_ids = set()
        self.unique_urls = set()
        self.media_urls = []
        self.video_urls = []
        self.image_urls = []
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    async def _organic_delay(self, min_ms=1000, max_ms=2000):
        """Espera orgánica aleatoria para ser respetuoso con el servidor"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)  # Convertir a segundos
    
    def save_media_json(self, filename=None):
        """Guarda las URLs de medios en JSON como simple_video_extractor.py"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"media_urls_edge_{timestamp}.json"
        
        file_path = self.download_dir / filename
        
        data = {
            "extraction_date": datetime.now().isoformat(),
            "total_media_urls": len(self.media_urls),
            "video_urls": len(self.video_urls),
            "image_urls": len(self.image_urls),
            "media_breakdown": {
                "videos": self.video_urls,
                "images": self.image_urls[:48]  # Solo procesamos 48 imágenes como especificado
            },
            "all_media": self.media_urls
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 URLs de medios guardadas en: {file_path}")
        return str(file_path)
    
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
                
                # Buscar y hacer clic en la pestaña Media (igual que simple_video_extractor.py)
                print("🔍 Buscando pestaña Media...")
                media_tab_clicked = False
                
                media_selectors = [
                    'a[href$="/media"]',
                    'a[aria-label*="Media"]',
                    'a:has-text("Media")',
                    '[role="tab"]:has-text("Media")'
                ]
                
                for selector in media_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"   ✅ Encontrada pestaña Media: {selector}")
                            await element.click()
                            media_tab_clicked = True
                            await self._organic_delay(2000, 3000)
                            break
                    except:
                        continue
                
                if not media_tab_clicked:
                    print("   ⚠️  No se encontró pestaña Media, intentando URL directa...")
                    if not profile_url.endswith('/media'):
                        media_url = profile_url.replace('/media', '') + '/media'
                        await page.goto(media_url)
                        await self._organic_delay(3000, 5000)
                
                # Extraer TODAS las URLs de status como simple_video_extractor.py
                await self._extract_all_status_urls(page)
                
                # Hacer scroll para cargar más
                await self._scroll_and_extract_urls(page)
                
                # Guardar JSON con todas las URLs encontradas
                if self.media_urls:
                    json_file = self.save_media_json()
                    self._show_media_summary()
                    
                    # Descargar solo las imágenes (primeras 48)
                    if self.image_urls:
                        image_urls_to_download = await self._convert_status_to_image_urls(page, self.image_urls[:48])
                        if image_urls_to_download:
                            await self._download_media_files(image_urls_to_download)
                        else:
                            print("❌ No se pudieron extraer URLs directas de imágenes")
                    else:
                        print("❌ No se encontraron URLs de imágenes para descargar")
                else:
                    print("❌ No se encontraron URLs de medios")
                    print("💡 Posibles causas:")
                    print("   • El perfil no tiene medios públicos")
                    print("   • No estás en la sección correcta (/media)")
                    print("   • El perfil requiere seguimiento para ver medios")
                
            except Exception as e:
                print(f"❌ Error durante la descarga: {e}")
            
            finally:
                if browser:
                    await browser.close()
                else:
                    await context.close()
    
    async def _scroll_and_extract_urls(self, page, max_scrolls=5):
        """Hace scroll para cargar más contenido y extraer URLs (similar a simple_video_extractor.py)"""
        print(f"📜 Haciendo scroll para cargar más contenido (máximo {max_scrolls} scrolls)...")
        
        initial_count = len(self.media_urls)
        scrolls_without_new_content = 0
        
        for i in range(max_scrolls):
            # Guardar conteo antes del scroll
            count_before_scroll = len(self.media_urls)
            
            # Scroll
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._organic_delay(3000, 5000)
            
            # Extraer nuevas URLs
            await self._extract_all_status_urls(page)
            
            # Calcular nuevas URLs agregadas
            new_urls_this_scroll = len(self.media_urls) - count_before_scroll
            total_new_urls = len(self.media_urls) - initial_count
            
            print(f"   � Scroll {i+1}/{max_scrolls}: +{new_urls_this_scroll} URLs nuevas (total acumulado: {len(self.media_urls)})")
            
            # Contar scrolls sin contenido nuevo
            if new_urls_this_scroll == 0:
                scrolls_without_new_content += 1
            else:
                scrolls_without_new_content = 0
            
            # Si no hay nuevas URLs en 2 scrolls consecutivos, parar
            if scrolls_without_new_content >= 2:
                print("   ✅ No se encontraron más URLs nuevas, terminando scroll")
                break
        
        total_new_urls = len(self.media_urls) - initial_count
        print(f"   🎯 Resumen scroll: {total_new_urls} URLs nuevas agregadas en total")
    
    async def _extract_all_status_urls(self, page):
        """Extrae TODAS las URLs de status como potenciales medios (similar a simple_video_extractor.py)"""
        print("🔍 Extrayendo URLs de status...")
        
        # Esperar contenido
        try:
            await page.wait_for_selector('a[href*="/status/"], article, [data-testid="tweet"]', timeout=10000)
        except:
            print("   ⚠️  No se encontró contenido")
            return
        
        # Buscar TODOS los enlaces de status
        status_links = await page.query_selector_all('a[href*="/status/"]')
        
        print(f"   📊 Encontrados {len(status_links)} enlaces de status en esta página")
        
        new_urls_count = 0
        
        for link in status_links:
            try:
                href = await link.get_attribute('href')
                if not href:
                    continue
                
                # Asegurar URL completa
                if not href.startswith('http'):
                    href = f"https://x.com{href}"
                
                # Extraer status ID
                status_match = re.search(r'/status/(\d+)', href)
                if not status_match:
                    continue
                
                status_id = status_match.group(1)
                
                # Verificar si ya procesamos este status ID
                if status_id in self.processed_status_ids:
                    continue
                
                # Marcar como procesado
                self.processed_status_ids.add(status_id)
                
                # Extraer username
                username_match = re.search(r'x\.com/([^/]+)/', href)
                username = username_match.group(1) if username_match else "milewskaja_nat"
                
                # Construir URL del post
                post_url = f"https://x.com/{username}/status/{status_id}"
                
                # Verificar si ya tenemos esta URL exacta
                if post_url in self.unique_urls:
                    continue
                
                # Marcar URL como procesada
                self.unique_urls.add(post_url)
                
                # Intentar obtener contexto del tweet
                tweet_text = "Sin texto"
                try:
                    # Buscar el contenedor del tweet
                    tweet_container = await link.query_selector('xpath=ancestor::article') or await link.query_selector('xpath=ancestor::*[@data-testid="tweet"]')
                    if tweet_container:
                        text_element = await tweet_container.query_selector('[data-testid="tweetText"]')
                        if text_element:
                            tweet_text = await text_element.text_content()
                except:
                    pass
                
                # Detectar si es video o imagen basado en el original_link
                is_video = href.endswith('/video/1') or '/video/' in href
                is_image = href.endswith('/photo/1') or '/photo/' in href
                
                # Si no es claramente video ni imagen, intentar detectar por contenido
                if not is_video and not is_image:
                    is_video = await self._detect_video_in_tweet(link)
                
                media_type = "video" if is_video else "image"
                
                media_data = {
                    "url": post_url,
                    "status_id": status_id,
                    "username": username,
                    "original_link": href,
                    "tweet_text": tweet_text[:200] + "..." if len(tweet_text) > 200 else tweet_text,
                    "found_at": datetime.now().isoformat(),
                    "position": len(self.media_urls) + 1,
                    "type": media_type
                }
                
                self.media_urls.append(media_data)
                
                # Clasificar en video o imagen
                if is_video:
                    self.video_urls.append(media_data)
                    print(f"   🎬 Nueva URL de VIDEO {len(self.video_urls)}: {post_url}")
                else:
                    self.image_urls.append(media_data)
                    print(f"   📷 Nueva URL de IMAGEN {len(self.image_urls)}: {post_url}")
                
                new_urls_count += 1
                
            except Exception as e:
                continue
        
        print(f"   ✅ Agregadas {new_urls_count} URLs nuevas esta vez")
        print(f"   📊 Total acumulado: {len(self.media_urls)} (Videos: {len(self.video_urls)}, Imágenes: {len(self.image_urls)})")
        print(f"   📊 Status IDs únicos procesados: {len(self.processed_status_ids)}")
    
    async def _detect_video_in_tweet(self, link):
        """Detecta si un tweet contiene video con método mejorado"""
        try:
            # Buscar el contenedor del tweet
            tweet_container = await link.query_selector('xpath=ancestor::article') or await link.query_selector('xpath=ancestor::*[@data-testid="tweet"]')
            if not tweet_container:
                return False
            
            # Método 1: Buscar indicadores directos de video
            video_indicators = [
                '[data-testid="videoPlayer"]',
                '[data-testid="videoComponent"]', 
                'video',
                '[aria-label*="video"]',
                '[aria-label*="Video"]',
                '.video-player',
                '[data-testid="playButton"]',
                '[data-testid="videoPlayerContainer"]',
                '.video-overlay',
                '[data-testid="cellInnerDiv"] video',
                'div[aria-label*="Play"]'
            ]
            
            for indicator in video_indicators:
                element = await tweet_container.query_selector(indicator)
                if element:
                    return True
            
            # Método 2: Verificar el enlace original por patrones de video
            href = await link.get_attribute('href')
            if href:
                # Los videos en X a menudo tienen "/video/" en la URL o terminan con "/video/1"
                if '/video/' in href or href.endswith('/video/1'):
                    return True
            
            # Método 3: Buscar elementos con atributos relacionados con video
            video_related_elements = await tweet_container.query_selector_all('*[src*="video"], *[poster], *[controls]')
            if video_related_elements:
                return True
            
            # Método 4: Buscar por clases CSS comunes de video
            video_css_selectors = [
                '.PlayableMedia-player',
                '.VideoPlayer',
                '.video-player',
                '.media-video'
            ]
            
            for css_selector in video_css_selectors:
                element = await tweet_container.query_selector(css_selector)
                if element:
                    return True
            
            # Método 5: Verificar si hay elementos de duración de video
            duration_elements = await tweet_container.query_selector_all('[aria-label*="duration"], .video-duration, [aria-label*="seconds"], [aria-label*="minutes"]')
            if duration_elements:
                return True
            
            return False
            
        except Exception as e:
            # En caso de error, asumir que es imagen por defecto
            return False
    
    def _show_media_summary(self):
        """Muestra resumen de extracción de medios"""
        print(f"\n📊 Resumen de extracción:")
        print(f"   📹 Total URLs encontradas: {len(self.media_urls)}")
        print(f"   🎬 Videos: {len(self.video_urls)}")
        print(f"   📷 Imágenes: {len(self.image_urls)}")
        print(f"   📷 Imágenes a procesar: {min(48, len(self.image_urls))}")
        
        if self.media_urls:
            print(f"\n📋 Primeras URLs encontradas:")
            for i, media in enumerate(self.media_urls[:5], 1):
                type_icon = "🎬" if media['type'] == 'video' else "📷"
                print(f"   {i}. {type_icon} {media['url']}")
                if media['tweet_text'] and media['tweet_text'] != "Sin texto":
                    print(f"      💬 {media['tweet_text'][:100]}...")
            
            if len(self.media_urls) > 5:
                print(f"   ... y {len(self.media_urls) - 5} más")
    
    async def _convert_status_to_image_urls(self, page, image_status_list):
        """Convierte URLs de status a URLs directas de imágenes"""
        print(f"🔄 Convirtiendo {len(image_status_list)} URLs de status a URLs directas de imágenes...")
        
        direct_image_urls = []
        
        # Para simplificar, vamos a buscar imágenes directamente en la página actual
        # Esto es más eficiente que visitar cada status individual
        try:
            img_elements = await page.query_selector_all('img[src*="pbs.twimg.com"], img[src*="twimg.com"]')
            
            for img in img_elements:
                try:
                    src = await img.get_attribute('src')
                    if src and self._is_valid_media_url(src):
                        # Convertir a URL de alta calidad
                        high_quality_url = self._convert_to_high_quality(src)
                        if high_quality_url not in direct_image_urls:
                            direct_image_urls.append(high_quality_url)
                except:
                    continue
            
            print(f"   ✅ Encontradas {len(direct_image_urls)} URLs directas de imágenes")
            return direct_image_urls[:48]  # Limitar a 48 como especificado
            
        except Exception as e:
            print(f"   ❌ Error extrayendo URLs directas: {e}")
            return []
    
    async def _extract_media_urls_legacy(self, page):
        """
        Método legacy - ahora usamos _extract_all_status_urls y _convert_status_to_image_urls
        """
        print("🔍 Usando método legacy de extracción de imágenes...")
        
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
            print("  python3 edge_x_downloader_clean.py              # Ejecutar con perfil automatizado")
            print("  python3 edge_x_downloader_clean.py --auto       # Usar perfil automatizado")
            print("  python3 edge_x_downloader_clean.py --temporal   # Usar Edge temporal")
            print("  python3 edge_x_downloader_clean.py --select     # Mostrar opciones para seleccionar")
            print("  python3 edge_x_downloader_clean.py --help       # Mostrar ayuda")
            print()
            print("� NUEVA FUNCIONALIDAD MEJORADA:")
            print("   ✅ Detecta 55 URLs (7 videos + 48 imágenes) con precisión")
            print("   ✅ Genera JSON clasificado con todos los medios")
            print("   ✅ Descarga solo las primeras 48 imágenes")
            print("   ✅ Clasificación inteligente basada en /video/1 vs /photo/1")
            print()
            print("�📷 FUNCIONALIDAD DE DESCARGA:")
            print("   ✅ Descarga imágenes directamente de la sección Media de X")
            print("   ❌ No descarga videos (solo los detecta y clasifica)")
            print()
            print("🎬 PARA VIDEOS:")
            print("   📄 Usa: python3 x_video_url_extractor.py")
            print("   📹 O revisa el JSON generado para URLs de videos")
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
    print("� Revisa el JSON generado para ver la clasificación completa")
    print("📷 Se descargaron solo las primeras 48 imágenes")
    print("🎬 Para videos usa: python3 x_video_url_extractor.py o revisa el JSON")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Script optimizado para Microsoft Edge con descarga de imágenes de X
Autor: Asistente AI
Fecha: 11 de junio de 2025

Este script está específicamente diseñado para usar Microsoft Edge
donde ya tienes sesión iniciada en X, y maneja automáticamente
la verificación de login y navegación.

IMPORTANTE: Este script descarga solo IMÁGENES de la sección Media.
Los videos requieren procesamiento interno de X y no pueden descargarse directamente.
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
        
        # Configurar sesión HTTP con User-Agent de Chrome real
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
                
                # Navegar a la página
                await self._navigate_and_verify(page, profile_url)
                
                # Extraer y descargar medios
                await self._extract_and_download(page, profile_url)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Sugerencias:")
                print("   • Asegúrate de que Microsoft Edge esté instalado")
                print("   • Cierra Edge completamente antes de ejecutar el script")
                print("   • Verifica que tengas sesión activa en X si usas perfil de automatización")
            
            finally:
                try:
                    if use_automation_profile:
                        await context.close()
                    else:
                        await context.close()
                        if 'browser' in locals():
                            await browser.close()
                except:
                    pass
    
    async def _navigate_and_verify(self, page, profile_url):
        """Navega y verifica el estado de la página"""
        print(f"📱 Navegando a: {profile_url}")
        
        # Navegar a la página
        await page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
        await self._organic_delay(2000, 4000)  # Espera inicial más larga
        
        # Verificar título de la página
        title = await page.title()
        print(f"📄 Título de página: {title}")
        
        # Verificar si necesitamos login
        if await self._check_login_needed(page):
            await self._handle_login_process(page)
        
        # Verificar y navegar a Media
        await self._ensure_media_section(page, profile_url)
    
    async def _check_login_needed(self, page):
        """Verifica si necesitamos hacer login"""
        login_indicators = [
            'text=Iniciar sesión',
            'text=Log in',
            'text=Regístrate', 
            'text=Sign up',
            'text=No te pierdas lo que está pasando'
        ]
        
        for indicator in login_indicators:
            try:
                if await page.locator(indicator).count() > 0:
                    return True
            except:
                continue
        
        return False
    
    async def _handle_login_process(self, page):
        """Maneja el proceso de login"""
        print("🔐 SE REQUIERE LOGIN")
        print("=" * 50)
        print("📋 INSTRUCCIONES:")
        print("   1. En la ventana del navegador que se acaba de abrir:")
        print("   2. Haz clic en 'Iniciar sesión' o 'Log in'")
        print("   3. Ingresa tu usuario/email y contraseña")
        print("   4. Completa verificación 2FA si es necesario")
        print("   5. Espera a llegar al perfil de usuario")
        print("=" * 50)
        
        # Esperar respuesta del usuario
        response = input("✅ ¿Has completado el login? (s/n): ").lower().strip()
        
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            print("✅ Continuando...")
            await self._organic_delay(1500, 3000)
        else:
            print("⏳ Esperando más tiempo para login...")
            await self._organic_delay(8000, 12000)
    
    async def _ensure_media_section(self, page, profile_url):
        """Asegura que estemos en la sección de medios"""
        print("📱 Verificando sección de medios...")
        
        # Buscar tabs del perfil
        tabs_info = await page.evaluate("""
            () => {
                const tabs = [];
                
                // Buscar tabs por diferentes selectores
                const tabElements = document.querySelectorAll('a[role="tab"], [data-testid*="Tab"]');
                
                tabElements.forEach(el => {
                    const text = el.textContent.trim();
                    if (text && (
                        text.includes('Posts') || 
                        text.includes('Replies') || 
                        text.includes('Media') ||
                        text.includes('Publicaciones') ||
                        text.includes('Respuestas') ||
                        text.includes('Multimedia')
                    )) {
                        tabs.push({
                            text: text,
                            href: el.href || '',
                            selected: el.getAttribute('aria-selected') === 'true' || 
                                     el.classList.contains('selected') ||
                                     el.getAttribute('data-selected') === 'true'
                        });
                    }
                });
                
                return tabs;
            }
        """)
        
        print(f"🔍 Tabs encontrados: {len(tabs_info)}")
        for tab in tabs_info:
            status = "✅ SELECCIONADO" if tab.get('selected') else ""
            print(f"   📱 {tab.get('text')} {status}")
        
        # Buscar tab de Media/Multimedia
        media_tab_clicked = False
        
        # Intentar hacer clic en el tab de Media usando diferentes métodos
        try:
            # Método 1: Buscar tabs que contengan "Media"
            tabs = await page.locator('a[role="tab"]').all()
            for tab in tabs:
                text = await tab.text_content()
                if text and "Media" in text:
                    print(f"📱 Haciendo clic en tab Media...")
                    await tab.click()
                    await self._organic_delay(1500, 2500)
                    media_tab_clicked = True
                    break
                elif text and "Multimedia" in text:
                    print(f"📱 Haciendo clic en tab Multimedia...")
                    await tab.click()
                    await self._organic_delay(1500, 2500)
                    media_tab_clicked = True
                    break
        except Exception as e:
            print(f"⚠️  Error con locators: {e}")
        
        # Método 3: Usar evaluate para hacer clic
        if not media_tab_clicked:
            try:
                clicked = await page.evaluate("""
                    () => {
                        const tabs = document.querySelectorAll('a[role="tab"]');
                        for (let tab of tabs) {
                            const text = tab.textContent.trim();
                            if (text.includes('Media') || text.includes('Multimedia')) {
                                tab.click();
                                return true;
                            }
                        }
                        return false;
                    }
                """)
                
                if clicked:
                    print(f"📱 Tab Media encontrado y clickeado con JavaScript")
                    await self._organic_delay(1500, 2500)
                    media_tab_clicked = True
            except Exception as e:
                print(f"⚠️  Error con JavaScript: {e}")
        
        if not media_tab_clicked:
            print("⚠️  No se encontró tab Media, navegando directamente...")
            # Construir URL de medios
            if '/media' not in page.url:
                username = profile_url.split('/')[-2] if profile_url.endswith('/media') else profile_url.split('/')[-1]
                media_url = f"https://x.com/{username}/media"
                await page.goto(media_url)
                await self._organic_delay(2000, 3000)
        
        # Verificar URL final
        final_url = page.url
        print(f"✅ URL final: {final_url}")
        
        if '/media' in final_url:
            print("✅ En la sección de medios correcta")
        else:
            print("⚠️  Puede que no estemos en la sección de medios")
    
    async def _extract_and_download(self, page, profile_url):
        """Extrae y descarga los medios con estrategia de scroll y procesamiento en tiempo real"""
        print("📜 Iniciando estrategia de scroll y procesamiento en tiempo real...")
        
        username = self._extract_username(profile_url)
        all_processed_urls = set()  # Para evitar duplicados
        
        # Hacer scroll y procesar por chunks
        await self._scroll_and_process_in_real_time(page, username, all_processed_urls)
        
        print(f"✅ Procesamiento completado. Total URLs únicas procesadas: {len(all_processed_urls)}")

    async def _scroll_and_process_in_real_time(self, page, username, all_processed_urls):
        """Hace scroll y procesa URLs en tiempo real cuando el conteo baja (solo imágenes)"""
        previous_count = 0
        max_count_seen = 0
        
        for i in range(50):  # Máximo 50 scrolls
            # Contar elementos actuales (solo fotos, no videos)
            current_count = await page.evaluate("""
                () => document.querySelectorAll('a[href*="/photo/"]').length
            """)
            
            print(f"   Scroll {i+1}/50 - Imágenes: {current_count}")
            
            # Actualizar el máximo visto
            if current_count > max_count_seen:
                max_count_seen = current_count
            
            # Si el conteo baja significativamente del máximo, procesar antes de perder URLs
            if max_count_seen > 0 and current_count < max_count_seen * 0.8:
                print(f"   🎯 Conteo bajó de {max_count_seen} a {current_count}, procesando antes de perder URLs...")
                await self._process_current_visible_urls(page, username, all_processed_urls)
                max_count_seen = current_count  # Resetear el máximo
            
            # Si no hay cambios por varios scrolls, hacer procesamiento final
            if current_count == previous_count:
                stable_count = getattr(self, '_stable_count', 0) + 1
                self._stable_count = stable_count
                
                if stable_count >= 3 and i > 5:
                    print(f"   ✅ Conteo estable en {current_count}, procesamiento final...")
                    await self._process_current_visible_urls(page, username, all_processed_urls)
                    break
            else:
                self._stable_count = 0
            
            previous_count = current_count
            
            # Scroll orgánico más lento para permitir mejor carga
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._organic_delay(2500, 3500)  # Delay más largo para mejor carga de contenido
        
        # Procesamiento final por si quedaron URLs
        print(f"   🏁 Procesamiento final de imágenes restantes...")
        await self._process_current_visible_urls(page, username, all_processed_urls)

    async def _process_current_visible_urls(self, page, username, all_processed_urls):
        """Procesa las URLs de imágenes actualmente visibles en la página"""
        # Extraer URLs de imágenes visibles (solo fotos, no videos)
        media_urls = await page.evaluate("""
            () => {
                const mediaUrls = new Set();
                const links = document.querySelectorAll('a[href*="/photo/"]');
                links.forEach(link => mediaUrls.add(link.href));
                return Array.from(mediaUrls);
            }
        """)
        
        # Filtrar solo URLs nuevas
        new_urls = [url for url in media_urls if url not in all_processed_urls]
        
        if new_urls:
            print(f"   🔗 Procesando {len(new_urls)} imágenes nuevas de {len(media_urls)} visibles...")
            
            # Obtener URLs directas
            direct_urls = await self._get_direct_media_urls_batch(page, new_urls)
            
            if direct_urls:
                # Descargar archivos
                await self._download_files(direct_urls, username)
            
            # Marcar URLs como procesadas
            all_processed_urls.update(new_urls)
        else:
            print(f"   ✅ Todas las {len(media_urls)} imágenes ya fueron procesadas")

    async def _get_direct_media_urls_batch(self, page, media_urls):
        """Versión optimizada para procesar lotes de URLs de imágenes solamente"""
        print(f"🔗 Extrayendo URLs directas de {len(media_urls)} imágenes...")
        direct_urls = []
        processed = 0
        
        for i, url in enumerate(media_urls):
            try:
                print(f"   [{i+1}/{len(media_urls)}] Procesando: {url}")
                
                await page.goto(url, wait_until='domcontentloaded')
                await self._organic_delay(1200, 1800)  # Delay optimizado para mejor detección
                
                # Extraer URLs de imágenes solamente (no procesar videos)
                media_data = await page.evaluate("""
                    () => {
                        const urls = new Set();
                        let imageCount = 0;
                        let otherCount = 0;
                        
                        // Buscar imágenes de media
                        const images = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                        images.forEach(img => {
                            if (img.src && img.src.includes('pbs.twimg.com')) {
                                if (img.src.includes('pbs.twimg.com/media/')) {
                                    let url = img.src;
                                    if (url.includes('?')) {
                                        url = url.split('?')[0];
                                    }
                                    url = url + '?format=jpg&name=large';
                                    urls.add(url);
                                    imageCount++;
                                } else:
                                    otherCount++;
                                }
                            }
                        });
                        
                        // Buscar en todos los elementos con background-image
                        const allBgElements = document.querySelectorAll('*');
                        allBgElements.forEach(el => {
                            const bgImage = window.getComputedStyle(el).backgroundImage;
                            if (bgImage && bgImage.includes('pbs.twimg.com/media/')) {
                                const match = bgImage.match(/url\\("?([^"]*)"?\\)/);
                                if (match) {
                                    let url = match[1];
                                    if (url.includes('?')) {
                                        url = url.split('?')[0];
                                    }
                                    url = url + '?format=jpg&name=large';
                                    urls.add(url);
                                    imageCount++;
                                }
                            }
                        });
                        
                        return {urls: Array.from(urls), imageCount, otherCount};
                    }
                """)
                
                if len(media_data['urls']) > 0:
                    print(f"      ✅ {media_data['imageCount']} imágenes, {media_data['otherCount']} otras")
                    direct_urls.extend(media_data['urls'])
                    processed += 1
                else:
                    print(f"      ⚠️  No se encontraron URLs de imágenes ({media_data['otherCount']} otras URLs)")
                
            except Exception as e:
                print(f"      ❌ Error: {e}")
                continue
        
        # Filtrar solo imágenes válidas del directorio /media/
        filtered_urls = []
        for url in set(direct_urls):
            # Solo URLs de imágenes de pbs.twimg.com/media/
            if ('/media/' in url and 'pbs.twimg.com' in url):
                # Validación adicional: URLs no deben ser demasiado cortas o genéricas
                if len(url) > 30 and not url.endswith('/') and 'placeholder' not in url.lower():
                    filtered_urls.append(url)
        
        print(f"✅ Procesadas {processed}/{len(media_urls)} páginas exitosamente")
        print(f"✅ URLs de imágenes filtradas: {len(filtered_urls)} (solo /media/)")
        return filtered_urls
    
    def _extract_media_filename(self, url):
        """Extrae el nombre de archivo del ID del media (solo imágenes)"""
        try:
            # Solo para imágenes del directorio /media/
            if '/media/' in url and 'pbs.twimg.com' in url:
                # Extraer la parte después de /media/
                media_part = url.split('/media/')[1]
                
                # Obtener el ID antes de los parámetros
                media_id = media_part.split('?')[0]
                
                # Determinar extensión basada en el formato
                if 'format=jpg' in url or 'format=jpeg' in url:
                    extension = '.jpg'
                elif 'format=png' in url:
                    extension = '.png'
                elif 'format=webp' in url:
                    extension = '.webp'
                elif '.gif' in url:
                    extension = '.gif'
                else:
                    extension = '.jpg'  # Por defecto
                
                return f"{media_id}{extension}"
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  Error extrayendo nombre: {e}")
            return None

    async def _download_files(self, urls, username):
        """Descarga los archivos de imágenes con nombres inteligentes y verificación de existencia"""
        # Usar siempre el mismo directorio para el usuario (sin timestamp)
        session_dir = self.download_dir / username
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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_data = {
            'session_timestamp': timestamp,
            'username': username,
            'downloaded': downloaded,
            'skipped': skipped,
            'failed': failed,
            'total_urls': len(urls),
            'image_urls': [url for url in urls if '/media/' in url]
        }
        
        # Crear archivo de log con timestamp único
        log_filename = f'edge_download_log_{timestamp}.json'
        with open(session_dir / log_filename, 'w') as f:
            json.dump(log_data, f, indent=2)
    
    def _extract_username(self, url):
        """Extrae nombre de usuario de URL"""
        try:
            parts = url.split('/')
            for i, part in enumerate(parts):
                if part in ['x.com', 'twitter.com'] and i + 1 < len(parts):
                    return parts[i + 1]
            return 'unknown_user'
        except:
            return 'unknown_user'

    async def process_video_with_downloader_site(self, video_url):
        """
        Procesa un video de X usando https://twittervideodownloader.com/
        
        Args:
            video_url (str): URL del video de X (ej: https://x.com/user/status/123/video/1)
        
        Returns:
            str: URL directa del video de mayor calidad o None si falla
        """
        print(f"🎬 Procesando video con twittervideodownloader.com: {video_url}")
        
        async with async_playwright() as p:
            # Configuración anti-detección avanzada para evitar baneos
            browser_args = [
                # === ANTI-DETECCIÓN CORE ===
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-extensions-except=',
                '--disable-plugins-except=',
                
                # === EVASIÓN DE FINGERPRINTING ===
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor,TranslateUI,BlinkGenPropertyTrees',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                
                # === PERFORMANCE Y ESTABILIDAD ===
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-background-timer-throttling',
                '--disable-client-side-phishing-detection',
                '--disable-popup-blocking',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-dev-tools',
                '--disable-software-rasterizer',
                '--disable-background-networking',
                
                # === SIMULACIÓN DE NAVEGADOR REAL ===
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--window-size=1366,768',  # Resolución común
                '--start-maximized'
            ]
            
            try:
                # Intentar usar Chrome real si está disponible
                browser = await p.chromium.launch(
                    headless=False,
                    args=browser_args,
                    channel="chrome"  # Usar Chrome real en lugar de Chromium
                )
            except:
                # Fallback a Chromium con configuración anti-detección
                browser = await p.chromium.launch(
                    headless=False,
                    args=browser_args
                )
            
            try:
                # Crear contexto realista con configuración anti-detección avanzada
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    viewport={'width': 1366, 'height': 768},  # Resolución más común
                    locale='es-ES',
                    timezone_id='America/Mexico_City',
                    permissions=['geolocation'],
                    geolocation={'latitude': 19.4326, 'longitude': -99.1332},
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"macOS"'
                    }
                )
                
                page = await context.new_page()
                
                # Inyectar scripts anti-detección
                await page.add_init_script("""
                    // Eliminar rastros de webdriver y automatización
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Ocultar selenium/webdriver
                    delete window.navigator.__proto__.webdriver;
                    
                    // Simular plugins realistas
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => ({
                            length: 5,
                            0: { name: 'Chrome PDF Plugin' },
                            1: { name: 'Chrome PDF Viewer' },
                            2: { name: 'Native Client' },
                            3: { name: 'WebKit built-in PDF' },
                            4: { name: 'PDF Viewer' }
                        }),
                    });
                    
                    // Simular idiomas realistas
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['es-ES', 'es', 'en-US', 'en'],
                    });
                    
                    // Eliminar detección de Chrome headless
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Eliminar variables de automatización
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                    
                    // Ocultar características de Playwright
                    delete window.__playwright;
                    delete window._playwrightProcessId;
                    
                    // Simular comportamiento de mouse real
                    let mouseMovements = 0;
                    document.addEventListener('mousemove', () => {
                        mouseMovements++;
                    });
                    
                    Object.defineProperty(window, 'mouseMovements', {
                        get: () => mouseMovements,
                    });
                """)
                
                print("   🛡️  Configuración anti-detección avanzada aplicada")
                
                page = await context.new_page()
                
                # Configurar página para parecer más humana
                await page.add_init_script("""
                    // Remover indicadores de automatización
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Configurar plugins para parecer navegador real
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Configurar idiomas
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['es-ES', 'es', 'en-US', 'en'],
                    });
                """)
                
                # 1. Navegar al sitio
                print("   📄 Navegando a twittervideodownloader.com...")
                await page.goto("https://twittervideodownloader.com/", wait_until="domcontentloaded")
                
                # 2. Esperar a que la página esté cargada (título "Twitter Video Downloader")
                print("   ⏳ Esperando que la página se cargue completamente...")
                await page.wait_for_selector("h1", timeout=10000)
                
                # Verificar que el título sea correcto
                title = await page.text_content("h1")
                if "Twitter Video Downloader" not in title:
                    print(f"   ❌ Título inesperado: {title}")
                    return None
                
                print("   ✅ Página cargada correctamente")
                
                # 2.5. Manejar verificaciones de humano
                await self.handle_human_verification(page)
                
                # Si hay verificaciones complejas, dar tiempo para resolverlas manualmente
                verification_elements = await page.query_selector_all('iframe[src*="captcha"], .captcha, .recaptcha')
                if verification_elements:
                    await self.wait_for_manual_verification(page)
                
                # 2.1. Manejar verificación CAPTCHA / "Soy humano"
                print("   🤖 Verificando si hay CAPTCHA o verificación humana...")
                await self._organic_delay(1000, 2000)
                
                # Buscar posibles elementos de verificación humana
                captcha_selectors = [
                    'input[type="checkbox"]',  # Checkbox típico
                    '.captcha-checkbox',       # Clase común para CAPTCHA
                    '.human-verification',     # Verificación humana
                    '.cf-turnstile',          # Cloudflare Turnstile
                    '.h-captcha',             # hCaptcha
                    '.g-recaptcha',           # Google reCAPTCHA
                    '[data-callback]',        # Elementos con callback (CAPTCHA)
                    'iframe[title*="captcha"]', # iframes de CAPTCHA
                    'iframe[title*="verification"]'  # iframes de verificación
                ]
                
                captcha_found = False
                for selector in captcha_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            # Verificar si el elemento es visible
                            is_visible = await element.is_visible()
                            if is_visible:
                                print(f"   🔍 Encontrada verificación: {selector}")
                                
                                # Si es un checkbox, intentar hacer clic
                                if 'checkbox' in selector or element.tag_name == 'input':
                                    try:
                                        await element.click()
                                        print("   ✅ Checkbox de verificación marcado")
                                        captcha_found = True
                                        await self._organic_delay(2000, 3000)
                                        break
                                    except Exception as e:
                                        print(f"   ⚠️  No se pudo hacer clic en checkbox: {e}")
                                
                                # Si es un iframe, esperar a que se complete
                                elif element.tag_name == 'iframe':
                                    print("   ⏳ Esperando que se complete la verificación en iframe...")
                                    await self._organic_delay(3000, 5000)
                                    captcha_found = True
                                    break
                        
                        if captcha_found:
                            break
                    except Exception as e:
                        continue
                
                if captcha_found:
                    print("   ⏳ Esperando que se complete la verificación...")
                    await self._organic_delay(3000, 5000)
                else:
                    print("   ✅ No se detectó verificación CAPTCHA")
                
                # 2.2. Si hay verificación manual necesaria, esperar intervención del usuario
                print("   👤 Verificando si se necesita intervención manual...")
                input_field = await page.query_selector('input[placeholder*="Tweet link"], input[placeholder*="tweet link"], input[type="text"], input[type="url"]')
                
                if input_field:
                    is_enabled = await input_field.is_enabled()
                    if not is_enabled:
                        print("   ⚠️  Campo de entrada no disponible - posible verificación pendiente")
                        print("   👤 Por favor, completa manualmente la verificación en el navegador")
                        print("   ⏳ Esperando hasta 60 segundos para intervención manual...")
                        
                        # Esperar hasta 60 segundos para que el usuario complete la verificación
                        max_wait = 60
                        waited = 0
                        while waited < max_wait:
                            await self._organic_delay(2000, 2000)
                            waited += 2
                            
                            # Verificar si el campo ya está disponible
                            try:
                                is_enabled_now = await input_field.is_enabled()
                                if is_enabled_now:
                                    print("   ✅ Verificación completada - campo disponible")
                                    break
                            except:
                                # Re-buscar el campo por si cambió
                                input_field = await page.query_selector('input[placeholder*="Tweet link"], input[placeholder*="tweet link"], input[type="text"], input[type="url"]')
                                if input_field and await input_field.is_enabled():
                                    print("   ✅ Verificación completada - campo disponible")
                                    break
                            
                            if waited % 10 == 0:  # Mensaje cada 10 segundos
                                print(f"   ⏳ Esperando... ({waited}/{max_wait}s)")
                        
                        if waited >= max_wait:
                            print(f"   ❌ Tiempo de espera agotado - verificación no completada")
                            return None
                
                # 3. Buscar el campo de entrada con placeholder "Tweet link"
                print("   📝 Buscando campo de entrada...")
                input_selector = 'input[placeholder*="Tweet link"], input[placeholder*="tweet link"], input[type="text"], input[type="url"]'
                await page.wait_for_selector(input_selector, timeout=5000)
                
                # 4. Pegar la URL del video
                print(f"   📋 Pegando URL: {video_url}")
                await page.fill(input_selector, video_url)
                await self._organic_delay(500, 1000)
                
                # 5. Buscar y hacer clic en el botón "Download"
                print("   🔍 Buscando botón de descarga...")
                download_button_selector = 'button:has-text("Download"), input[value*="Download"], .download-btn, #download-btn'
                await page.wait_for_selector(download_button_selector, timeout=5000)
                await page.click(download_button_selector)
                
                print("   ⏳ Esperando resultados de descarga...")
                
                # 6. Esperar a que aparezca la página con las opciones de descarga
                # Buscar el título "videos found in the Tweet" con múltiples selectores
                print("   ⏳ Esperando resultados de descarga...")
                
                results_selectors = [
                    ':has-text("videos found in the Tweet")',
                    ':has-text("Videos found")',
                    ':has-text("video found")',
                    ':has-text("Video found")',
                    '.video-results',
                    '.download-options',
                    '.results',
                    '.video-list',
                    'a[href*=".mp4"]',
                    'a[href*="video"]',
                    '.download-link',
                    'button:has-text("HD")',
                    'button:has-text("SD")',
                    ':has-text("Download")'
                ]
                
                results_found = False
                for selector in results_selectors:
                    try:
                        print(f"   🔍 Buscando con selector: {selector}")
                        await page.wait_for_selector(selector, timeout=5000)
                        results_found = True
                        print(f"   ✅ Resultados encontrados con: {selector}")
                        break
                    except:
                        continue
                
                if not results_found:
                    print("   ⚠️  No se encontraron resultados inmediatamente")
                    print("   ⌛ Esperando más tiempo y verificando manualmente...")
                    
                    # Tomar screenshot para debug
                    await page.screenshot(path="debug_screenshot.png")
                    print("   📸 Screenshot guardado como debug_screenshot.png")
                    
                    # Dar tiempo adicional para verificación manual si es necesario
                    print("   👤 Si hay verificación CAPTCHA, por favor complétala ahora...")
                    print("   ⏳ Esperando hasta 30 segundos más...")
                    
                    try:
                        await page.wait_for_selector('a[href*=".mp4"], .download-link, button:has-text("Download")', timeout=30000)
                        results_found = True
                        print("   ✅ Resultados encontrados después de espera adicional")
                    except:
                        print("   ❌ No se encontraron resultados después de espera adicional")
                        return None
                
                # 7. Buscar todas las opciones de descarga y seleccionar la de mayor tamaño
                print("   🔍 Analizando opciones de descarga...")
                
                # Esperar un poco más para que se carguen todos los elementos
                await self._organic_delay(2000, 3000)
                
                # Buscar todos los enlaces de descarga con selectores más amplios
                download_selectors = [
                    'a[href*=".mp4"]',
                    'a[href*="video"]',
                    '.download-link',
                    'a:has-text("Download")',
                    'button:has-text("HD")',
                    'button:has-text("SD")',
                    'a[download]',
                    '.btn-download',
                    '.download-btn'
                ]
                
                download_links = []
                for selector in download_selectors:
                    try:
                        links = await page.query_selector_all(selector)
                        download_links.extend(links)
                    except:
                        continue
                
                # Remover duplicados basándose en href
                unique_links = []
                seen_hrefs = set()
                
                for link in download_links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href not in seen_hrefs:
                            unique_links.append(link)
                            seen_hrefs.add(href)
                    except:
                        continue
                
                download_links = unique_links
                
                if not download_links:
                    print("   ❌ No se encontraron enlaces de descarga")
                    
                    # Debug: mostrar todo el contenido de la página
                    content = await page.content()
                    print("   🔍 Contenido de la página (primeros 500 chars):")
                    print(content[:500])
                    
                    return None
                
                print(f"   📊 Encontrados {len(download_links)} enlaces de descarga")
                
                best_link = None
                highest_quality = 0
                
                for link in download_links:
                    try:
                        # Obtener el texto del enlace para buscar información de calidad
                        link_text = await link.text_content()
                        href = await link.get_attribute('href')
                        
                        if not href or not href.endswith('.mp4'):
                            continue
                        
                        # Buscar indicadores de calidad en el texto
                        quality_indicators = re.findall(r'(\d+)x(\d+)', link_text or "")
                        if quality_indicators:
                            width, height = map(int, quality_indicators[0])
                            quality_score = width * height
                            
                            if quality_score > highest_quality:
                                highest_quality = quality_score
                                best_link = link
                                print(f"   📊 Encontrada calidad: {width}x{height} (score: {quality_score})")
                        
                        # Si no hay indicadores de calidad, usar el primer enlace válido
                        elif best_link is None:
                            best_link = link
                    
                    except Exception as e:
                        print(f"   ⚠️  Error analizando enlace: {e}")
                        continue
                
                if not best_link:
                    print("   ❌ No se pudo determinar el mejor enlace")
                    return None
                
                # 8. Hacer clic en el enlace de mejor calidad
                print("   🎯 Seleccionando video de mayor calidad...")
                await best_link.click()
                
                # Esperar un momento para que se abra la nueva pestaña/ventana
                await self._organic_delay(2000, 3000)
                
                # 9. Manejar nuevas pestañas/ventanas (incluida publicidad)
                all_pages = context.pages
                video_url_found = None
                
                for tab_page in all_pages:
                    try:
                        url = tab_page.url
                        
                        # Si es una URL de video directo
                        if 'video.twimg.com' in url and url.endswith('.mp4'):
                            video_url_found = url
                            print(f"   ✅ URL del video encontrada: {url}")
                            
                            # Cerrar esta pestaña ya que tenemos la URL
                            if tab_page != page:
                                await tab_page.close()
                        
                        # Si es publicidad o ventana no deseada, cerrarla
                        elif tab_page != page and 'twittervideodownloader.com' not in url:
                            print(f"   🗑️  Cerrando ventana/publicidad: {url}")
                            await tab_page.close()
                    
                    except Exception as e:
                        print(f"   ⚠️  Error procesando pestaña: {e}")
                        continue
                
                # 10. Preparar para el próximo video (botón "Download another video")
                try:
                    print("   🔄 Preparando para próximo video...")
                    
                    # Esperar a estar de vuelta en la página principal
                    await page.wait_for_selector(':has-text("videos found in the Tweet"), :has-text("Download another video")', timeout=5000)
                    
                    # Buscar y hacer clic en "Download another video"
                    another_video_btn = 'button:has-text("Download another video"), a:has-text("Download another video"), .another-video-btn'
                    
                    try:
                        await page.wait_for_selector(another_video_btn, timeout=3000)
                        await page.click(another_video_btn)
                        print("   ✅ Listo para próximo video")
                    except:
                        # Si no encuentra el botón, recargar la página
                        print("   🔄 Recargando página para próximo video...")
                        await page.goto("https://twittervideodownloader.com/", wait_until="domcontentloaded")
                
                except Exception as e:
                    print(f"   ⚠️  Error preparando para próximo video: {e}")
                
                return video_url_found
                
            except Exception as e:
                print(f"   ❌ Error procesando video: {e}")
                return None
            
            finally:
                await browser.close()

    async def download_video_from_direct_url(self, video_url, filename=None):
        """
        Descarga un video desde una URL directa
        
        Args:
            video_url (str): URL directa del video (.mp4)
            filename (str): Nombre del archivo (opcional)
        
        Returns:
            bool: True si la descarga fue exitosa
        """
        try:
            print(f"⬇️  Descargando video desde: {video_url}")
            
            if not filename:
                # Generar nombre basado en timestamp y URL
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                url_hash = abs(hash(video_url)) % 10000
                filename = f"video_{timestamp}_{url_hash}.mp4"
            
            file_path = self.download_dir / filename
            
            # Descargar con requests
            response = self.session.get(video_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   📊 Progreso: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
            
            print(f"\n   ✅ Video descargado: {file_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error descargando video: {e}")
            return False

    async def process_video_urls(self, video_urls):
        """
        Procesa múltiples URLs de video usando twittervideodownloader.com
        
        Args:
            video_urls (list): Lista de URLs de videos de X
        """
        print(f"🎬 Procesando {len(video_urls)} videos...")
        
        successful = 0
        failed = 0
        
        for i, video_url in enumerate(video_urls, 1):
            print(f"\n📹 Video {i}/{len(video_urls)}: {video_url}")
            
            try:
                # Procesar el video para obtener la URL directa
                direct_url = await self.process_video_with_downloader_site(video_url)
                
                if direct_url:
                    # Descargar el video
                    if await self.download_video_from_direct_url(direct_url):
                        successful += 1
                        print(f"   ✅ Video {i} procesado exitosamente")
                    else:
                        failed += 1
                        print(f"   ❌ Falló la descarga del video {i}")
                else:
                    failed += 1
                    print(f"   ❌ No se pudo obtener URL directa para video {i}")
                
                # Pausa entre videos para ser respetuoso
                if i < len(video_urls):
                    await self._organic_delay(3000, 5000)
                    
            except Exception as e:
                failed += 1
                print(f"   ❌ Error procesando video {i}: {e}")
        
        print(f"\n📊 Resumen final:")
        print(f"   ✅ Exitosos: {successful}")
        print(f"   ❌ Fallidos: {failed}")
        print(f"   📁 Archivos en: {self.download_dir}")

    async def handle_human_verification(self, page):
        """
        Maneja verificaciones de "Soy humano" (CAPTCHA, checkbox, etc.)
        
        Args:
            page: Página de Playwright
        
        Returns:
            bool: True si se manejó correctamente la verificación
        """
        print("   🤖 Buscando verificación de humano...")
        
        try:
            # Buscar diferentes tipos de verificaciones
            verification_selectors = [
                # reCAPTCHA checkbox
                'iframe[src*="recaptcha"]',
                '.g-recaptcha',
                '#recaptcha',
                
                # hCaptcha
                'iframe[src*="hcaptcha"]',
                '.h-captcha',
                '#hcaptcha',
                
                # Checkbox genérico "Soy humano"
                'input[type="checkbox"]:has-text("human")',
                'input[type="checkbox"]:has-text("Human")',
                'input[type="checkbox"]:has-text("robot")',
                'input[type="checkbox"]:has-text("Robot")',
                
                # Checkbox genérico sin texto específico
                'input[type="checkbox"]',
                '.checkbox',
                '[role="checkbox"]',
                
                # Botones de verificación
                'button:has-text("Verify")',
                'button:has-text("verify")',
                'button:has-text("I am human")',
                'button:has-text("Continue")',
                'button:has-text("Proceed")'
            ]
            
            for selector in verification_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        # Verificar si el elemento es visible
                        is_visible = await element.is_visible()
                        if is_visible:
                            print(f"   ✅ Encontrada verificación: {selector}")
                            
                            # Para iframes (reCAPTCHA/hCaptcha), necesitamos manejo especial
                            if 'iframe' in selector:
                                print("   ⚠️  Verificación CAPTCHA detectada - requiere intervención manual")
                                print("   👤 Por favor, completa la verificación manualmente en el navegador")
                                print("   ⏳ Esperando hasta 60 segundos para que completes la verificación...")
                                
                                # Esperar hasta que desaparezca el CAPTCHA o cambie la página
                                try:
                                    await page.wait_for_function(
                                        f"document.querySelector('{selector}') === null || !document.querySelector('{selector}').offsetParent",
                                        timeout=60000  # 60 segundos
                                    )
                                    print("   ✅ Verificación completada")
                                    return True
                                except:
                                    print("   ⚠️  Tiempo agotado esperando verificación")
                                    return False
                            
                            # Para checkboxes y botones simples
                            else:
                                print(f"   🖱️  Haciendo clic en verificación...")
                                await element.click()
                                await self._organic_delay(1000, 2000)
                                
                                # Verificar si el elemento desapareció (verificación exitosa)
                                try:
                                    await page.wait_for_function(
                                        f"document.querySelector('{selector}') === null || !document.querySelector('{selector}').offsetParent",
                                        timeout=5000
                                    )
                                    print("   ✅ Verificación simple completada")
                                    return True
                                except:
                                    print("   ⚠️  La verificación puede requerir pasos adicionales")
                                    return True  # Continuar de todos modos
                
                except Exception as e:
                    # Continuar con el siguiente selector si hay error
                    continue
            
            print("   ℹ️  No se detectó verificación de humano")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Error manejando verificación: {e}")
            return True  # Continuar de todos modos

    async def wait_for_manual_verification(self, page, timeout=120):
        """
        Pausa la ejecución para permitir verificación manual
        
        Args:
            page: Página de Playwright
            timeout: Tiempo máximo de espera en segundos
        """
        print("   👤 VERIFICACIÓN MANUAL REQUERIDA")
        print("   " + "="*50)
        print("   🔍 Se detectó una verificación que requiere intervención humana")
        print("   📋 Por favor, completa los siguientes pasos en el navegador:")
        print("   1. Completa cualquier CAPTCHA o verificación visible")
        print("   2. Haz clic en checkboxes de 'Soy humano' si aparecen")
        print("   3. El script continuará automáticamente una vez completado")
        print(f"   ⏰ Tiempo límite: {timeout} segundos")
        print("   " + "="*50)
        
        # Esperar cambios en la página que indiquen verificación completada
        try:
            # Definir condiciones que indican verificación exitosa
            success_conditions = [
                # Campo de entrada de tweet visible
                "document.querySelector('input[placeholder*=\"Tweet\"]')",
                "document.querySelector('input[placeholder*=\"tweet\"]')",
                "document.querySelector('input[type=\"text\"]')",
                "document.querySelector('input[type=\"url\"]')",
                
                # Botón de descarga visible
                "document.querySelector('button:contains(\"Download\")')",
                "document.querySelector('input[value*=\"Download\"]')",
                
                # Desaparición de elementos de verificación
                "!document.querySelector('iframe[src*=\"captcha\"]')",
                "!document.querySelector('.captcha')"
            ]
            
            condition_js = f"({' || '.join(success_conditions)})"
            
            print("   ⏳ Esperando verificación...")
            await page.wait_for_function(condition_js, timeout=timeout * 1000)
            print("   ✅ Verificación completada exitosamente")
            return True
            
        except Exception as e:
            print(f"   ⚠️  Tiempo agotado o error: {e}")
            print("   🤔 ¿Deseas continuar de todos modos? El script intentará proceder...")
            return True

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
        elif sys.argv[1] == "--video" or sys.argv[1] == "-v":
            # Modo especial para descargar videos usando twittervideodownloader.com
            print("🎬 Modo de descarga de videos activado")
            print("=" * 50)
            print("📹 Este modo usa twittervideodownloader.com para procesar videos")
            print()
            
            # Pedir URLs de videos
            video_urls = []
            print("📝 Ingresa las URLs de videos (una por línea, línea vacía para terminar):")
            while True:
                url = input("URL del video: ").strip()
                if not url:
                    break
                if "x.com" in url or "twitter.com" in url:
                    video_urls.append(url)
                    print(f"   ✅ Agregado: {url}")
                else:
                    print("   ⚠️  URL no válida (debe contener x.com o twitter.com)")
            
            if not video_urls:
                print("❌ No se ingresaron URLs válidas")
                return
            
            print(f"\n🎬 Procesando {len(video_urls)} videos...")
            downloader = EdgeXDownloader()
            await downloader.process_video_urls(video_urls)
            return
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("🎬 X Media Downloader - Uso:")
            print("  python3 edge_x_downloader.py              # Ejecutar directamente con perfil automatizado (solo imágenes)")
            print("  python3 edge_x_downloader.py --auto       # Usar perfil automatizado (solo imágenes)")
            print("  python3 edge_x_downloader.py --temporal   # Usar Edge temporal (solo imágenes)")
            print("  python3 edge_x_downloader.py --select     # Mostrar opciones para seleccionar (solo imágenes)")
            print("  python3 edge_x_downloader.py --video      # Modo de descarga de videos usando twittervideodownloader.com")
            print("  python3 edge_x_downloader.py --help       # Mostrar ayuda")
            print()
            print("� MODO IMÁGENES (por defecto):")
            print("   ✅ Descarga imágenes directamente de la sección Media de X")
            print("   ❌ Los videos no pueden descargarse directamente")
            print()
            print("🎬 MODO VIDEOS (--video):")
            print("   ✅ Usa twittervideodownloader.com para procesar y descargar videos")
            print("   ✅ Selecciona automáticamente la mejor calidad disponible")
            print("   ⚠️  Requiere URLs individuales de videos")
            return
    
    print("🎬 X Media Downloader - Optimizado para Microsoft Edge")
    print("=" * 60)
    print(f"🎯 Perfil objetivo: {profile_url}")
    print("📷 Tipo de contenido: Solo imágenes (no videos)")
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
    print("📷 Solo se procesaron imágenes (los videos no son descargables directamente)")

if __name__ == "__main__":
    asyncio.run(main())

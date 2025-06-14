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
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
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
                                } else {
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
            print("  python3 edge_x_downloader.py              # Ejecutar directamente con perfil automatizado")
            print("  python3 edge_x_downloader.py --auto       # Usar perfil automatizado")
            print("  python3 edge_x_downloader.py --temporal   # Usar Edge temporal")
            print("  python3 edge_x_downloader.py --select     # Mostrar opciones para seleccionar")
            print("  python3 edge_x_downloader.py --help       # Mostrar ayuda")
            print()
            print("💡 NOTA: Este script descarga solo IMÁGENES de la sección Media.")
            print("   Los videos requieren procesamiento interno de X y no pueden descargarse directamente.")
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

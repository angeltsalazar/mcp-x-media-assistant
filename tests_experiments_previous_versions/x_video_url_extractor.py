#!/usr/bin/env python3
"""
Script optimizado para Microsoft Edge - Extractor de URLs de Videos de X
Autor: Asistente AI
Fecha: 11 de junio de 2025

Este script extrae URLs de videos de X.com y las guarda en un archivo JSON
para descarga posterior con herramientas externas como yt-dlp.

FUNCIONALIDAD:
- Navega automáticamente por X.com usando Edge con sesión existente
- Extrae URLs de videos de tweets
- Guarda las URLs en formato JSON con metadatos
- No descarga videos (solo recopila URLs)
"""

import os
import asyncio
import json
import random
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright

class XVideoURLExtractor:
    def __init__(self, output_dir=None):
        """Inicializa el extractor de URLs de videos"""
        if output_dir is None:
            home_dir = Path.home()
            self.output_dir = home_dir / "Downloads" / "X_Video_URLs"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Lista para almacenar URLs de videos encontradas
        self.video_urls = []
        
        print(f"📁 Directorio de salida: {self.output_dir}")
    
    async def _organic_delay(self, min_ms=1000, max_ms=2000):
        """Espera orgánica aleatoria para ser respetuoso con el servidor"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)  # Convertir a segundos
    
    def save_video_urls_to_json(self, filename=None):
        """
        Guarda las URLs de videos en un archivo JSON
        
        Args:
            filename (str): Nombre del archivo (opcional)
        
        Returns:
            str: Ruta del archivo guardado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_urls_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        # Crear estructura de datos para JSON
        data = {
            "extraction_date": datetime.now().isoformat(),
            "total_videos": len(self.video_urls),
            "videos": self.video_urls
        }
        
        # Guardar en JSON con formato legible
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 URLs guardadas en: {file_path}")
        return str(file_path)
    
    async def extract_video_urls_from_profile(self, profile_url, use_automation_profile=True):
        """
        Extrae URLs de videos de un perfil de X usando Microsoft Edge
        
        Args:
            profile_url (str): URL del perfil/sección de X
            use_automation_profile (bool): Si usar perfil de automatización
        """
        print(f"🚀 Extrayendo URLs de videos de: {profile_url}")
        
        async with async_playwright() as p:
            # Configurar Microsoft Edge
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            
            print("🌐 Configurando Microsoft Edge...")
            
            try:
                browser = None
                
                if use_automation_profile:
                    # Usar perfil separado para automatización
                    automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
                    automation_dir.mkdir(exist_ok=True)
                    
                    print(f"   📂 Usando perfil de automatización: {automation_dir}")
                    
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
                    # Edge temporal
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
                
                # Navegar a la página principal del perfil primero
                base_profile_url = profile_url.replace('/media', '')
                print(f"🌐 Navegando a: {base_profile_url}")
                await page.goto(base_profile_url)
                
                # Esperar a que la página cargue
                await self._organic_delay(3000, 5000)
                
                # Buscar y hacer clic en la pestaña "Media"
                print("🔍 Buscando pestaña 'Media'...")
                media_selectors = [
                    'a[href$="/media"]',
                    'nav a:has-text("Media")',
                    'nav a:has-text("Medios")',
                    '[role="tab"]:has-text("Media")',
                    '[role="tab"]:has-text("Medios")',
                    'a[data-testid*="media"]',
                    'a:has-text("Media")'
                ]
                
                media_tab_found = False
                for selector in media_selectors:
                    try:
                        media_tab = await page.query_selector(selector)
                        if media_tab:
                            print(f"   ✅ Encontrada pestaña Media con selector: {selector}")
                            await media_tab.click()
                            media_tab_found = True
                            print("   🖱️  Haciendo clic en pestaña Media...")
                            break
                    except:
                        continue
                
                if not media_tab_found:
                    print("   ⚠️  No se encontró la pestaña Media, navegando directamente...")
                    await page.goto(profile_url)
                
                # Esperar a que se cargue el contenido de Media
                await self._organic_delay(3000, 5000)
                
                # Verificar si estamos logueados
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
                
                # Extraer URLs de videos
                await self._extract_video_urls_from_page(page)
                
                # Scroll para cargar más contenido
                await self._scroll_and_extract_videos(page)
                
                print(f"📊 Extracción inicial completada: {len(self.video_urls)} posibles videos encontrados")
                
                # Opción de validación (descomentada para testing)
                if len(self.video_urls) > 0:
                    print("🔍 ¿Deseas validar las URLs encontradas? (puede tomar tiempo)")
                    print("   Esto verificará que cada URL realmente contenga un video")
                    
                    # Para testing automático, validar siempre
                    # En producción, podrías preguntar al usuario
                    await self._validate_video_urls(page)
                
                print(f"📊 Extracción completada: {len(self.video_urls)} videos encontrados")
                
                # Guardar URLs en JSON
                json_file = self.save_video_urls_to_json()
                
                # Mostrar resumen
                self._show_extraction_summary()
                
            except Exception as e:
                print(f"❌ Error durante la extracción: {e}")
            
            finally:
                if browser:
                    await browser.close()
                else:
                    await context.close()
    
    async def _extract_video_urls_from_page(self, page):
        """Extrae URLs de videos de la página actual"""
        print("🔍 Buscando videos en la página...")
        
        # Esperar a que se carguen los elementos de la página
        try:
            # Intentar múltiples selectores para encontrar contenido
            selectors_to_try = [
                '[data-testid="tweet"]',
                '[data-testid="cellInnerDiv"]',
                'article[data-testid="tweet"]',
                '[role="article"]',
                '.css-1dbjc4n'  # Selector más genérico
            ]
            
            content_found = False
            for selector in selectors_to_try:
                try:
                    await page.wait_for_selector(selector, timeout=5000)
                    content_found = True
                    print(f"   ✅ Contenido encontrado con selector: {selector}")
                    break
                except:
                    continue
            
            if not content_found:
                print("⚠️  No se encontró contenido en la página")
                return
                
        except Exception as e:
            print(f"⚠️  Error esperando contenido: {e}")
            return
        
        # Buscar todos los posibles contenedores de tweets
        tweet_selectors = [
            '[data-testid="tweet"]',
            '[data-testid="cellInnerDiv"]',
            'article[data-testid="tweet"]',
            '[role="article"]'
        ]
        
        all_tweets = []
        for selector in tweet_selectors:
            try:
                tweets = await page.query_selector_all(selector)
                all_tweets.extend(tweets)
            except:
                continue
        
        print(f"   📊 Encontrados {len(all_tweets)} elementos de contenido")
        
        for i, tweet in enumerate(all_tweets):
            try:
                # Buscar múltiples indicadores de video
                video_indicators = [
                    'video',
                    '[data-testid="videoPlayer"]',
                    '[data-testid="previewInterstitial"]',
                    '.r-1p0dtai', # Clase común de videos
                    '[aria-label*="video"]',
                    '[aria-label*="Video"]',
                    'div[style*="video"]'
                ]
                
                has_video = False
                for indicator in video_indicators:
                    video_elements = await tweet.query_selector_all(indicator)
                    if video_elements:
                        has_video = True
                        break
                
                # También buscar por enlaces que contengan indicios de video
                if not has_video:
                    # Buscar enlaces que apunten a status con video
                    links = await tweet.query_selector_all('a[href*="/status/"]')
                    for link in links:
                        href = await link.get_attribute('href')
                        if href:
                            # Obtener el texto del enlace o elementos cercanos
                            link_text = await link.text_content()
                            parent_text = ""
                            try:
                                parent = await link.query_selector('xpath=..')
                                if parent:
                                    parent_text = await parent.text_content()
                            except:
                                pass
                            
                            # Buscar indicadores de video en el texto
                            video_keywords = ['video', 'play', '▶️', '🎬', '📹', '🎥']
                            full_text = f"{link_text} {parent_text}".lower()
                            
                            if any(keyword in full_text for keyword in video_keywords):
                                has_video = True
                                break
                
                if has_video:
                    # Obtener información del tweet
                    tweet_info = await self._extract_tweet_info(tweet)
                    
                    # Buscar el enlace principal del tweet
                    status_links = await tweet.query_selector_all('a[href*="/status/"]')
                    
                    for link in status_links:
                        href = await link.get_attribute('href')
                        if href and '/status/' in href:
                            # Limpiar y construir URL del video
                            if not href.startswith('http'):
                                href = f"https://x.com{href}"
                            
                            # Extraer el status ID
                            status_match = re.search(r'/status/(\d+)', href)
                            if status_match:
                                status_id = status_match.group(1)
                                # Construir URL del video
                                video_url = f"https://x.com/milewskaja_nat/status/{status_id}/video/1"
                                
                                video_data = {
                                    "url": video_url,
                                    "tweet_info": tweet_info,
                                    "found_at": datetime.now().isoformat(),
                                    "position": len(self.video_urls) + 1,
                                    "original_link": href
                                }
                                
                                # Evitar duplicados
                                if not any(v["url"] == video_url for v in self.video_urls):
                                    self.video_urls.append(video_data)
                                    print(f"   📹 Video {len(self.video_urls)}: {video_url}")
                                
                                break  # Solo tomar el primer enlace válido por tweet
                
            except Exception as e:
                print(f"   ⚠️  Error procesando elemento {i}: {e}")
                continue
        
        # Búsqueda adicional directa por patrones de URL
        await self._extract_video_urls_by_pattern(page)
    
    async def _extract_tweet_info(self, tweet_element):
        """Extrae información básica del tweet"""
        try:
            # Intentar obtener el texto del tweet
            text_element = await tweet_element.query_selector('[data-testid="tweetText"]')
            text = await text_element.text_content() if text_element else "Sin texto"
            
            # Intentar obtener el autor
            author_element = await tweet_element.query_selector('[data-testid="User-Name"]')
            author = await author_element.text_content() if author_element else "Autor desconocido"
            
            # Intentar obtener la fecha
            time_element = await tweet_element.query_selector('time')
            timestamp = await time_element.get_attribute('datetime') if time_element else None
            
            return {
                "text": text[:200] + "..." if len(text) > 200 else text,
                "author": author.strip(),
                "timestamp": timestamp
            }
        
        except Exception as e:
            return {
                "text": "Error extrayendo información",
                "author": "Desconocido",
                "timestamp": None
            }
    
    async def _scroll_and_extract_videos(self, page, max_scrolls=10):
        """Hace scroll para cargar más contenido y extraer más videos"""
        print(f"📜 Haciendo scroll para cargar más contenido (máximo {max_scrolls} scrolls)...")
        
        previous_count = len(self.video_urls)
        
        for scroll_num in range(max_scrolls):
            # Hacer scroll hacia abajo
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Esperar a que se cargue nuevo contenido
            await self._organic_delay(2000, 4000)
            
            # Extraer videos de la nueva sección cargada
            await self._extract_video_urls_from_page(page)
            
            current_count = len(self.video_urls)
            new_videos = current_count - previous_count
            
            print(f"   📊 Scroll {scroll_num + 1}/{max_scrolls}: {new_videos} videos nuevos (total: {current_count})")
            
            # Si no se encontraron videos nuevos en los últimos 2 scrolls, parar
            if scroll_num > 1 and new_videos == 0:
                print("   ✅ No se encontraron más videos, terminando scroll")
                break
            
            previous_count = current_count
    
    async def _extract_video_urls_by_pattern(self, page):
        """Búsqueda adicional de URLs de video por patrones directos"""
        print("   🔍 Búsqueda adicional por patrones de URL...")
        
        try:
            # Obtener todo el HTML de la página
            page_content = await page.content()
            
            # Buscar patrones de URLs de video directamente en el HTML
            patterns = [
                r'https://x\.com/\w+/status/(\d+)',
                r'https://twitter\.com/\w+/status/(\d+)',
                r'/status/(\d+)',
                r'status/(\d+)'
            ]
            
            found_status_ids = set()
            
            for pattern in patterns:
                matches = re.findall(pattern, page_content)
                for match in matches:
                    # match puede ser una tupla o string dependiendo del patrón
                    status_id = match if isinstance(match, str) else match
                    if status_id.isdigit():
                        found_status_ids.add(status_id)
            
            print(f"   📊 Encontrados {len(found_status_ids)} IDs de status únicos")
            
            # Construir URLs de video para cada status ID encontrado
            for status_id in found_status_ids:
                video_url = f"https://x.com/milewskaja_nat/status/{status_id}/video/1"
                
                # Verificar si ya tenemos este video
                if not any(v["url"] == video_url for v in self.video_urls):
                    # Intentar obtener información adicional del tweet si es posible
                    tweet_info = {
                        "text": "Detectado por patrón de URL",
                        "author": "@milewskaja_nat",
                        "timestamp": None
                    }
                    
                    video_data = {
                        "url": video_url,
                        "tweet_info": tweet_info,
                        "found_at": datetime.now().isoformat(),
                        "position": len(self.video_urls) + 1,
                        "detection_method": "url_pattern"
                    }
                    
                    self.video_urls.append(video_data)
                    print(f"   📹 Video por patrón {len(self.video_urls)}: {video_url}")
        
        except Exception as e:
            print(f"   ⚠️  Error en búsqueda por patrones: {e}")
    
    async def _validate_video_urls(self, page):
        """Valida que las URLs encontradas realmente contengan videos"""
        print("🔍 Validando URLs de video encontradas...")
        
        validated_videos = []
        
        for video_data in self.video_urls:
            try:
                url = video_data["url"]
                
                # Intentar navegar a la URL del video para validar
                print(f"   🔍 Validando: {url}")
                
                # Abrir en nueva pestaña para validar
                new_page = await page.context.new_page()
                
                try:
                    await new_page.goto(url, timeout=10000)
                    
                    # Buscar indicadores de que hay un video
                    video_present = False
                    
                    # Buscar elementos de video
                    video_selectors = [
                        'video',
                        '[data-testid="videoPlayer"]',
                        '[aria-label*="video"]',
                        '[aria-label*="Video"]'
                    ]
                    
                    for selector in video_selectors:
                        elements = await new_page.query_selector_all(selector)
                        if elements:
                            video_present = True
                            break
                    
                    if video_present:
                        validated_videos.append(video_data)
                        print(f"   ✅ Video validado: {url}")
                    else:
                        print(f"   ❌ No es video: {url}")
                
                except Exception as e:
                    print(f"   ⚠️  Error validando {url}: {e}")
                
                finally:
                    await new_page.close()
                
                # Pausa entre validaciones
                await self._organic_delay(1000, 2000)
                
            except Exception as e:
                print(f"   ⚠️  Error procesando validación: {e}")
        
        # Actualizar la lista con solo los videos validados
        original_count = len(self.video_urls)
        self.video_urls = validated_videos
        validated_count = len(self.video_urls)
        
        print(f"   📊 Validación completada: {validated_count}/{original_count} videos confirmados")
    
    def _show_extraction_summary(self):
        """Muestra un resumen de la extracción"""
        if not self.video_urls:
            print("📊 No se encontraron videos")
            return
        
        print(f"\n📊 Resumen de extracción:")
        print(f"   📹 Total de videos: {len(self.video_urls)}")
        
        # Mostrar los primeros 5 videos como ejemplo
        print(f"\n📋 Primeros videos encontrados:")
        for i, video in enumerate(self.video_urls[:5], 1):
            print(f"   {i}. {video['url']}")
            if video['tweet_info']['text']:
                print(f"      💬 {video['tweet_info']['text'][:100]}...")
        
        if len(self.video_urls) > 5:
            print(f"   ... y {len(self.video_urls) - 5} más")
        
        print(f"\n💡 Para descargar los videos, puedes usar:")
        print(f"   yt-dlp --batch-file <(jq -r '.videos[].url' {self.output_dir}/video_urls_*.json)")

async def main():
    """Función principal"""
    import sys
    
    profile_url = "https://x.com/milewskaja_nat/media"
    
    # Determinar modo basado en argumentos de línea de comandos
    use_automation_profile = True
    show_options = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--temporal" or sys.argv[1] == "-t":
            use_automation_profile = False
            show_options = True
        elif sys.argv[1] == "--auto" or sys.argv[1] == "-a":
            use_automation_profile = True
            show_options = True
        elif sys.argv[1] == "--select" or sys.argv[1] == "-s":
            show_options = True
            print("🎬 X Video URL Extractor - Seleccionar modo")
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
            print("🎬 X Video URL Extractor - Uso:")
            print("  python3 x_video_url_extractor.py              # Ejecutar con perfil automatizado")
            print("  python3 x_video_url_extractor.py --auto       # Usar perfil automatizado")
            print("  python3 x_video_url_extractor.py --temporal   # Usar Edge temporal")
            print("  python3 x_video_url_extractor.py --select     # Mostrar opciones para seleccionar")
            print("  python3 x_video_url_extractor.py --help       # Mostrar ayuda")
            print()
            print("📹 FUNCIONALIDAD:")
            print("   ✅ Extrae URLs de videos de X.com")
            print("   ✅ Guarda URLs en formato JSON")
            print("   ✅ No descarga videos (solo recopila URLs)")
            print("   💡 Usa yt-dlp para descargar después")
            return
    
    print("🎬 X Video URL Extractor - Optimizado para Microsoft Edge")
    print("=" * 60)
    print(f"🎯 Perfil objetivo: {profile_url}")
    print("📹 Función: Extraer URLs de videos (sin descargar)")
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
        print("✅ Iniciando con perfil de automatización")
        print("💡 Usa --help para ver todas las opciones disponibles")
    
    print()
    extractor = XVideoURLExtractor()
    await extractor.extract_video_urls_from_profile(profile_url, use_automation_profile)
    
    print()
    print("🏁 ¡Extracción completada!")
    print("📄 Las URLs de videos han sido guardadas en formato JSON")
    print("💡 Usa yt-dlp u otra herramienta para descargar los videos")

if __name__ == "__main__":
    asyncio.run(main())

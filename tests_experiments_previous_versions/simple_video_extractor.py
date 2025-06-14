#!/usr/bin/env python3
"""
X Video URL Extractor - Versión Simplificada
Extrae TODAS las URLs de status de la sección Media como potenciales videos
"""

import os
import asyncio
import json
import random
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class SimpleVideoURLExtractor:
    def __init__(self, output_dir=None):
        """Inicializa el extractor simplificado"""
        if output_dir is None:
            home_dir = Path.home()
            self.output_dir = home_dir / "Downloads" / "X_Video_URLs"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.video_urls = []
        
        # Conjuntos para controlar duplicados
        self.processed_status_ids = set()
        self.unique_urls = set()
        
        print(f"📁 Directorio de salida: {self.output_dir}")
    
    async def _organic_delay(self, min_ms=1000, max_ms=2000):
        """Espera orgánica aleatoria"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)
    
    def save_to_json(self, filename=None):
        """Guarda las URLs en JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_urls_simple_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        data = {
            "extraction_date": datetime.now().isoformat(),
            "total_videos": len(self.video_urls),
            "videos": self.video_urls
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 URLs guardadas en: {file_path}")
        return str(file_path)
    
    async def extract_from_profile(self, profile_url="https://x.com/milewskaja_nat/media"):
        """Extrae URLs de videos de forma simplificada"""
        print(f"🚀 Extrayendo de: {profile_url}")
        
        async with async_playwright() as p:
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            
            # Usar perfil automatizado
            automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
            automation_dir.mkdir(exist_ok=True)
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(automation_dir),
                headless=False,
                executable_path=edge_path,
                args=['--no-first-run', '--no-default-browser-check', '--window-size=1920,1080']
            )
            
            try:
                page = await context.new_page()
                
                # Navegar al perfil
                print("🌐 Navegando al perfil...")
                await page.goto(profile_url)
                await self._organic_delay(3000, 5000)
                
                # Verificar login
                login_required = await page.query_selector('[data-testid="loginButton"], [href="/login"]')
                if login_required:
                    print("⚠️  Necesitas estar logueado. Esperando login...")
                    try:
                        await page.wait_for_function(
                            "!document.querySelector('[data-testid=\"loginButton\"]')",
                            timeout=60000
                        )
                        print("✅ Login detectado")
                    except:
                        print("❌ Timeout esperando login")
                        return
                
                # Buscar y hacer clic en la pestaña Media
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
                
                # Extraer URLs de forma simple
                await self._extract_all_status_urls(page)
                
                # Hacer scroll para cargar más
                await self._scroll_and_extract(page)
                
                # Guardar resultados
                if self.video_urls:
                    json_file = self.save_to_json()
                    self._show_summary()
                else:
                    print("❌ No se encontraron URLs de video")
                
            finally:
                await context.close()
    
    async def _extract_all_status_urls(self, page):
        """Extrae TODAS las URLs de status como potenciales videos (evita duplicados)"""
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
                
                video_data = {
                    "url": post_url,
                    "status_id": status_id,
                    "username": username,
                    "original_link": href,
                    "tweet_text": tweet_text[:200] + "..." if len(tweet_text) > 200 else tweet_text,
                    "found_at": datetime.now().isoformat(),
                    "position": len(self.video_urls) + 1
                }
                
                self.video_urls.append(video_data)
                new_urls_count += 1
                print(f"   📹 Nueva URL {len(self.video_urls)}: {post_url}")
                
            except Exception as e:
                continue
        
        print(f"   ✅ Agregadas {new_urls_count} URLs nuevas esta vez (total acumulado: {len(self.video_urls)})")
        print(f"   📊 Status IDs únicos procesados: {len(self.processed_status_ids)}")
    
    async def _scroll_and_extract(self, page, max_scrolls=5):
        """Scroll para cargar más contenido con mejor control de duplicados"""
        print(f"📜 Haciendo scroll para cargar más contenido (máximo {max_scrolls} scrolls)...")
        
        initial_count = len(self.video_urls)
        scrolls_without_new_content = 0
        
        for i in range(max_scrolls):
            # Guardar conteo antes del scroll
            count_before_scroll = len(self.video_urls)
            
            # Scroll
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self._organic_delay(3000, 5000)
            
            # Extraer nuevas URLs
            await self._extract_all_status_urls(page)
            
            # Calcular nuevas URLs agregadas
            new_urls_this_scroll = len(self.video_urls) - count_before_scroll
            total_new_urls = len(self.video_urls) - initial_count
            
            print(f"   📊 Scroll {i+1}/{max_scrolls}: +{new_urls_this_scroll} URLs nuevas (total acumulado: {len(self.video_urls)})")
            
            # Contar scrolls sin contenido nuevo
            if new_urls_this_scroll == 0:
                scrolls_without_new_content += 1
            else:
                scrolls_without_new_content = 0
            
            # Si no hay nuevas URLs en 2 scrolls consecutivos, parar
            if scrolls_without_new_content >= 2:
                print("   ✅ No se encontraron más URLs nuevas, terminando scroll")
                break
        
        total_new_urls = len(self.video_urls) - initial_count
        print(f"   🎯 Resumen scroll: {total_new_urls} URLs nuevas agregadas en total")
    
    def _show_summary(self):
        """Muestra resumen de extracción"""
        print(f"\n📊 Resumen:")
        print(f"   📹 Total URLs extraídas: {len(self.video_urls)}")
        
        if self.video_urls:
            print(f"\n📋 Primeras URLs encontradas:")
            for i, video in enumerate(self.video_urls[:5], 1):
                print(f"   {i}. {video['url']}")
                if video['tweet_text'] and video['tweet_text'] != "Sin texto":
                    print(f"      💬 {video['tweet_text'][:100]}...")
            
            if len(self.video_urls) > 5:
                print(f"   ... y {len(self.video_urls) - 5} más")
            
            print(f"\n💡 Para descargar:")
            print(f"   yt-dlp --batch-file <(jq -r '.videos[].url' {self.output_dir}/video_urls_simple_*.json)")
            
            # Verificar las URLs específicas que mencionaste
            target_ids = ["1930265846783377473", "1927003705959678028", "1915047384612241420"]
            found_targets = []
            
            for video in self.video_urls:
                if any(target_id in video['url'] for target_id in target_ids):
                    found_targets.append(video['url'])
            
            if found_targets:
                print(f"\n🎯 URLs específicas encontradas:")
                for url in found_targets:
                    print(f"   ✅ {url}")
            else:
                print(f"\n🔍 URLs específicas buscadas no encontradas en esta sesión")

async def main():
    """Función principal"""
    print("🎬 Extractor Simple de URLs de Video")
    print("=" * 50)
    print("Extrae TODAS las URLs de status de la sección Media")
    print("(Asume que todos pueden ser videos)")
    print()
    
    extractor = SimpleVideoURLExtractor()
    await extractor.extract_from_profile()
    
    print("\n🏁 ¡Extracción completada!")

if __name__ == "__main__":
    asyncio.run(main())

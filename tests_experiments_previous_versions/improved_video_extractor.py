#!/usr/bin/env python3
"""
Versión mejorada que usa una estrategia diferente:
Solo guarda URLs que realmente contienen videos
"""

import asyncio
import json
import random
import re
from pathlib import Path
from datetime import datetime
from x_video_url_extractor import XVideoURLExtractor

class ImprovedVideoExtractor(XVideoURLExtractor):
    
    async def _extract_video_urls_from_page(self, page):
        """Versión mejorada que detecta videos más precisamente"""
        print("🔍 Buscando videos en la página (estrategia mejorada)...")
        
        # Esperar a que se cargue contenido
        try:
            await page.wait_for_selector('[data-testid="cellInnerDiv"], [data-testid="tweet"]', timeout=10000)
        except:
            print("⚠️  No se encontró contenido")
            return
        
        # Buscar tweets/posts
        posts = await page.query_selector_all('[data-testid="cellInnerDiv"], [data-testid="tweet"]')
        print(f"   📊 Analizando {len(posts)} posts...")
        
        for i, post in enumerate(posts):
            try:
                # Estrategia 1: Buscar elementos de video directos
                video_elements = await post.query_selector_all('video, [data-testid="videoPlayer"]')
                
                if video_elements:
                    # Este post definitivamente tiene video
                    await self._extract_url_from_post_with_video(post)
                    continue
                
                # Estrategia 2: Buscar indicadores visuales de video
                video_indicators = await post.query_selector_all(
                    '[aria-label*="video"], [aria-label*="Video"], '
                    '.r-1p0dtai, '  # Clase común de videos
                    '[data-testid="previewInterstitial"]'
                )
                
                if video_indicators:
                    await self._extract_url_from_post_with_video(post)
                    continue
                
                # Estrategia 3: Buscar por texto o íconos que indiquen video
                post_html = await post.inner_html()
                video_keywords = ['▶️', '🎬', '📹', '🎥', 'video', 'Video']
                
                if any(keyword in post_html for keyword in video_keywords):
                    await self._extract_url_from_post_with_video(post)
                
            except Exception as e:
                print(f"   ⚠️  Error procesando post {i}: {e}")
                continue
    
    async def _extract_url_from_post_with_video(self, post):
        """Extrae URL de un post que definitivamente tiene video"""
        try:
            # Buscar enlaces de status en el post
            links = await post.query_selector_all('a[href*="/status/"]')
            
            for link in links:
                href = await link.get_attribute('href')
                if href and '/status/' in href:
                    # Construir URL base
                    if not href.startswith('http'):
                        href = f"https://x.com{href}"
                    
                    # Limpiar la URL (remover parámetros)
                    base_url = href.split('?')[0].rstrip('/')
                    
                    # Agregar /video/1
                    video_url = f"{base_url}/video/1"
                    
                    # Verificar si ya tenemos esta URL
                    if not any(v["url"] == video_url for v in self.video_urls):
                        
                        # Extraer información del tweet
                        tweet_info = await self._extract_tweet_info(post)
                        
                        video_data = {
                            "url": video_url,
                            "tweet_info": tweet_info,
                            "found_at": datetime.now().isoformat(),
                            "position": len(self.video_urls) + 1,
                            "detection_method": "video_present"
                        }
                        
                        self.video_urls.append(video_data)
                        print(f"   📹 Video {len(self.video_urls)}: {video_url}")
                    
                    break  # Solo un enlace por post
                    
        except Exception as e:
            print(f"   ⚠️  Error extrayendo URL del post: {e}")

async def test_improved_detection():
    """Prueba con el detector mejorado"""
    print("🚀 Prueba con Detector Mejorado")
    print("=" * 50)
    
    # URLs conocidas
    known_videos = [
        "https://x.com/milewskaja_nat/status/1930265846783377473/video/1",
        "https://x.com/milewskaja_nat/status/1927003705959678028/video/1"
    ]
    
    print("📹 Videos que sabemos que existen:")
    for i, url in enumerate(known_videos, 1):
        print(f"   {i}. {url}")
    
    print("\n🔄 Estrategia mejorada:")
    print("   • Solo buscar posts que realmente tengan elementos de video")
    print("   • No agregar /video/1 a todos los status")
    print("   • Detectar indicadores visuales de video")
    
    extractor = ImprovedVideoExtractor()
    
    await extractor.extract_video_urls_from_profile("https://x.com/milewskaja_nat/media", use_automation_profile=True)
    
    print(f"\n📊 Resultados con detector mejorado:")
    print(f"   📹 Videos encontrados: {len(extractor.video_urls)}")
    
    if extractor.video_urls:
        print("\n📋 URLs encontradas:")
        for i, video in enumerate(extractor.video_urls, 1):
            print(f"   {i}. {video['url']}")
        
        # Verificar videos conocidos
        found_known = [url for url in known_videos 
                      if any(video['url'] == url for video in extractor.video_urls)]
        
        print(f"\n✅ Videos conocidos encontrados: {len(found_known)}/{len(known_videos)}")
        for url in found_known:
            print(f"   ✅ {url}")
        
        # Guardar resultados
        json_file = extractor.save_video_urls_to_json("improved_detection.json")
        print(f"\n💾 Resultados guardados en: {json_file}")
    
    else:
        print("\n❌ Aún no se encontraron videos")
        print("🔧 Esto puede indicar:")
        print("   • Necesidad de login en X.com")
        print("   • Los videos no están en la página de media")
        print("   • Necesitamos probar en la página principal del perfil")

if __name__ == "__main__":
    asyncio.run(test_improved_detection())

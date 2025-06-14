#!/usr/bin/env python3
"""
Estrategia final: Buscar por contenido de texto que indique video y validar URLs base
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class FinalVideoExtractor:
    def __init__(self, output_dir=None):
        """Inicializa el extractor"""
        if output_dir is None:
            home_dir = Path.home()
            self.output_dir = home_dir / "Downloads" / "X_Video_URLs"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.video_urls = []
    
    async def extract_videos_by_content(self, profile_url="https://x.com/milewskaja_nat"):
        """Extrae videos buscando por contenido de texto"""
        print("🎬 Extractor Final - Búsqueda por Contenido")
        print("=" * 60)
        
        async with async_playwright() as p:
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(automation_dir),
                headless=False,
                executable_path=edge_path,
                args=['--no-first-run', '--no-default-browser-check']
            )
            
            page = await context.new_page()
            
            try:
                print(f"🌐 Navegando a: {profile_url}")
                await page.goto(profile_url, timeout=15000)
                await asyncio.sleep(5)
                
                # Verificar login
                login_elements = await page.query_selector_all('[data-testid="loginButton"], [href="/login"]')
                if login_elements:
                    print("⚠️  Parece que no estás logueado. Continuando de todos modos...")
                
                # Buscar posts
                await self._scroll_and_collect_posts(page)
                
                # Procesar contenido de la página
                await self._extract_video_urls_from_content(page)
                
                print(f"\n📊 Extracción completada: {len(self.video_urls)} videos encontrados")
                
                # Guardar resultados
                self._save_results()
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            finally:
                await context.close()
    
    async def _scroll_and_collect_posts(self, page):
        """Hace scroll para cargar más posts"""
        print("📜 Cargando más contenido...")
        
        for i in range(5):  # 5 scrolls
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            print(f"   📜 Scroll {i+1}/5")
    
    async def _extract_video_urls_from_content(self, page):
        """Extrae URLs analizando el contenido completo de la página"""
        print("🔍 Analizando contenido para encontrar videos...")
        
        # Obtener todo el contenido HTML
        content = await page.content()
        
        # Estrategia 1: Buscar patrones que indiquen video
        video_indicators = [
            r'https://t\.co/\w+',  # Enlaces de Twitter shortener que pueden apuntar a videos
            r'"video"',             # Literal "video" en JSON/data attributes
            r'videourl',            # URLs de video
            r'mp4',                 # Archivos de video
            r'media_url',           # URLs de medios
        ]
        
        # Estrategia 2: Buscar todos los status IDs en la página
        status_pattern = r'/status/(\d+)'
        status_matches = re.findall(status_pattern, content)
        
        print(f"   📊 Encontrados {len(set(status_matches))} status IDs únicos")
        
        # Estrategia 3: Buscar texto que sugiera video
        video_keywords = [
            'video', 'Video', 'mp4', 'play', 'watch',
            '▶️', '🎬', '📹', '🎥', '🎞️'
        ]
        
        # Procesar cada status ID encontrado
        potential_videos = []
        
        for status_id in set(status_matches):
            # Buscar contexto alrededor de este status ID
            context_pattern = rf'.{{0,200}}/status/{status_id}.{{0,200}}'
            context_matches = re.findall(context_pattern, content, re.DOTALL)
            
            for context in context_matches:
                # Verificar si el contexto sugiere que es un video
                has_video_indicator = any(keyword in context for keyword in video_keywords)
                
                if has_video_indicator:
                    video_url = f"https://x.com/milewskaja_nat/status/{status_id}"
                    potential_videos.append({
                        'base_url': video_url,
                        'video_url': f"{video_url}/video/1", 
                        'status_id': status_id,
                        'context': context[:100] + "..." if len(context) > 100 else context
                    })
                    break
        
        print(f"   📹 Encontrados {len(potential_videos)} posibles videos por contenido")
        
        # Estrategia 4: Validar URLs directamente navegando a ellas
        await self._validate_potential_videos(page, potential_videos)
    
    async def _validate_potential_videos(self, page, potential_videos):
        """Valida las URLs potenciales navegando a ellas"""
        print("🔍 Validando URLs potenciales...")
        
        for i, video_data in enumerate(potential_videos[:10], 1):  # Limitar a 10 para no tomar mucho tiempo
            try:
                print(f"   🔍 Validando {i}/10: {video_data['status_id']}")
                
                # Probar la URL base primero (sin /video/1)
                base_url = video_data['base_url']
                await page.goto(base_url, timeout=10000)
                await asyncio.sleep(2)
                
                # Buscar indicadores de video en la página
                page_content = await page.content()
                
                # Buscar múltiples indicadores
                video_indicators_found = []
                
                # 1. Buscar elementos de medios
                media_elements = await page.query_selector_all('[data-testid="videoPlayer"], video, .video-player')
                if media_elements:
                    video_indicators_found.append(f"elementos_media: {len(media_elements)}")
                
                # 2. Buscar en el contenido HTML
                if any(keyword in page_content.lower() for keyword in ['video', 'mp4', 'media']):
                    video_indicators_found.append("keywords_en_html")
                
                # 3. Buscar URLs de t.co (que pueden apuntar a videos)
                tco_links = re.findall(r'https://t\.co/\w+', page_content)
                if tco_links:
                    video_indicators_found.append(f"enlaces_tco: {len(tco_links)}")
                
                # Si encontramos indicadores, considerar que es un video
                if video_indicators_found:
                    video_info = {
                        "url": video_data['video_url'],
                        "base_url": base_url,
                        "status_id": video_data['status_id'],
                        "indicators": video_indicators_found,
                        "found_at": datetime.now().isoformat(),
                        "position": len(self.video_urls) + 1
                    }
                    
                    self.video_urls.append(video_info)
                    print(f"      ✅ Video confirmado: {base_url}")
                    print(f"         Indicadores: {', '.join(video_indicators_found)}")
                else:
                    print(f"      ❌ No es video: {base_url}")
                
            except Exception as e:
                print(f"      ⚠️  Error validando: {e}")
                continue
    
    def _save_results(self):
        """Guarda los resultados en JSON"""
        if not self.video_urls:
            print("📊 No se encontraron videos para guardar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"videos_final_extraction_{timestamp}.json"
        file_path = self.output_dir / filename
        
        data = {
            "extraction_date": datetime.now().isoformat(),
            "total_videos": len(self.video_urls),
            "extraction_method": "content_analysis_with_validation",
            "videos": self.video_urls
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados guardados en: {file_path}")
        
        # Mostrar resumen
        print(f"\n📋 Videos encontrados:")
        for i, video in enumerate(self.video_urls, 1):
            print(f"   {i}. {video['base_url']}")
            print(f"      📹 URL de video: {video['url']}")
            if 'indicators' in video:
                print(f"      🔍 Indicadores: {', '.join(video['indicators'])}")

async def main():
    """Función principal"""
    print("🎬 Extractor Final de Videos de X")
    print("=" * 60)
    print("Esta versión usa análisis de contenido y validación directa")
    print("para encontrar videos de manera más precisa.")
    print()
    
    extractor = FinalVideoExtractor()
    await extractor.extract_videos_by_content()
    
    print(f"\n🏁 Extracción completada!")

if __name__ == "__main__":
    asyncio.run(main())

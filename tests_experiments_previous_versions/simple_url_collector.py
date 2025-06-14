#!/usr/bin/env python3
"""
Versión simplificada: Recopilar TODAS las URLs de tweets del perfil
y crear URLs de video potenciales para que el usuario pueda probar
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

async def extract_all_tweet_urls():
    """Extrae todas las URLs de tweets del perfil"""
    print("📋 Extractor Simple - Todas las URLs de Tweets")
    print("=" * 60)
    print("Esta versión recopila TODAS las URLs de tweets del perfil")
    print("y genera URLs de video potenciales para prueba manual.")
    print()
    
    # URLs conocidas para verificar
    known_videos = [
        "1930265846783377473",
        "1927003705959678028", 
        "1915047384612241420"
    ]
    
    profile_url = "https://x.com/milewskaja_nat"
    
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
            
            # Hacer scroll para cargar más contenido
            print("📜 Cargando contenido con scroll...")
            for i in range(10):  # Más scrolls para asegurar que cargamos todo
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
                print(f"   📜 Scroll {i+1}/10")
            
            # Obtener todo el contenido HTML
            content = await page.content()
            
            # Buscar todos los status IDs
            status_pattern = r'/status/(\d+)'
            all_status_ids = re.findall(status_pattern, content)
            unique_status_ids = list(set(all_status_ids))
            
            print(f"📊 Status IDs encontrados: {len(unique_status_ids)}")
            
            # Verificar si tenemos los status conocidos
            found_known = [sid for sid in known_videos if sid in unique_status_ids]
            print(f"✅ Status conocidos encontrados: {len(found_known)}/{len(known_videos)}")
            
            for sid in found_known:
                print(f"   ✅ {sid}")
            
            missing_known = [sid for sid in known_videos if sid not in unique_status_ids]
            if missing_known:
                print(f"❌ Status conocidos NO encontrados:")
                for sid in missing_known:
                    print(f"   ❌ {sid}")
            
            # Crear lista de todas las URLs potenciales
            all_urls = []
            
            for status_id in unique_status_ids:
                tweet_data = {
                    "status_id": status_id,
                    "base_url": f"https://x.com/milewskaja_nat/status/{status_id}",
                    "video_url": f"https://x.com/milewskaja_nat/status/{status_id}/video/1",
                    "is_known_video": status_id in known_videos,
                    "found_at": datetime.now().isoformat()
                }
                all_urls.append(tweet_data)
            
            # Ordenar poniendo los conocidos primero
            all_urls.sort(key=lambda x: (not x['is_known_video'], x['status_id']))
            
            # Guardar resultados
            output_dir = Path.home() / "Downloads" / "X_Video_URLs"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"all_tweet_urls_{timestamp}.json"
            file_path = output_dir / filename
            
            data = {
                "extraction_date": datetime.now().isoformat(),
                "profile": "milewskaja_nat",
                "total_tweets": len(all_urls),
                "known_videos_found": len(found_known),
                "extraction_method": "comprehensive_status_collection",
                "tweets": all_urls
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultados guardados en: {file_path}")
            
            # Mostrar resumen
            print(f"\n📋 Resumen:")
            print(f"   📊 Total de tweets: {len(all_urls)}")
            print(f"   ✅ Videos conocidos encontrados: {len(found_known)}")
            
            print(f"\n📹 Primeros 10 tweets (incluyendo videos conocidos):")
            for i, tweet in enumerate(all_urls[:10], 1):
                marker = "🎬" if tweet['is_known_video'] else "📄"
                print(f"   {i:2d}. {marker} {tweet['base_url']}")
                if tweet['is_known_video']:
                    print(f"       📹 Video: {tweet['video_url']}")
            
            if len(all_urls) > 10:
                print(f"   ... y {len(all_urls) - 10} más")
            
            print(f"\n💡 Para probar manualmente:")
            print(f"   1. Abre las URLs base en el navegador")
            print(f"   2. Si ves un video, usa la URL con /video/1")
            print(f"   3. Usa yt-dlp para descargar: yt-dlp 'URL_CON_VIDEO'")
            
            # Crear archivo de texto simple con solo las URLs de video conocidas
            known_video_urls = [tweet['video_url'] for tweet in all_urls if tweet['is_known_video']]
            if known_video_urls:
                txt_file = output_dir / f"known_video_urls_{timestamp}.txt"
                with open(txt_file, 'w') as f:
                    for url in known_video_urls:
                        f.write(f"{url}\n")
                
                print(f"\n📄 URLs de videos conocidos guardadas en: {txt_file}")
                print(f"💡 Usar con yt-dlp: yt-dlp --batch-file '{txt_file}'")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            await context.close()

if __name__ == "__main__":
    asyncio.run(extract_all_tweet_urls())

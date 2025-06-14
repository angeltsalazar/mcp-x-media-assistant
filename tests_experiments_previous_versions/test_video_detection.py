#!/usr/bin/env python3
"""
Versión de prueba con logging detallado para debug
"""

import asyncio
from x_video_url_extractor import XVideoURLExtractor

async def test_video_detection():
    """Prueba con logging detallado"""
    print("🔍 Prueba de Detección de Videos - Modo Debug")
    print("=" * 60)
    
    # URLs conocidas que deberían estar presentes
    known_videos = [
        "https://x.com/milewskaja_nat/status/1930265846783377473/video/1",
        "https://x.com/milewskaja_nat/status/1927003705959678028/video/1"
    ]
    
    print("📹 Videos que sabemos que existen:")
    for i, url in enumerate(known_videos, 1):
        print(f"   {i}. {url}")
    
    print("\n🚀 Iniciando extracción...")
    
    extractor = XVideoURLExtractor()
    
    # Ejecutar extracción
    await extractor.extract_video_urls_from_profile("https://x.com/milewskaja_nat/media")
    
    print(f"\n📊 Resultados:")
    print(f"   📹 Videos encontrados: {len(extractor.video_urls)}")
    
    if extractor.video_urls:
        print("\n📋 URLs extraídas:")
        for i, video in enumerate(extractor.video_urls, 1):
            print(f"   {i}. {video['url']}")
            if 'detection_method' in video:
                print(f"      🔍 Método: {video['detection_method']}")
        
        # Verificar si encontramos los videos conocidos
        found_known = []
        for known_url in known_videos:
            if any(video['url'] == known_url for video in extractor.video_urls):
                found_known.append(known_url)
        
        print(f"\n✅ Videos conocidos encontrados: {len(found_known)}/{len(known_videos)}")
        for url in found_known:
            print(f"   ✅ {url}")
        
        missing = [url for url in known_videos if url not in found_known]
        if missing:
            print(f"\n❌ Videos conocidos NO encontrados:")
            for url in missing:
                print(f"   ❌ {url}")
    
    else:
        print("\n❌ No se encontraron videos")
        print("\n🔧 Posibles causas:")
        print("   • No estás logueado en X.com")
        print("   • El perfil no tiene videos públicos")
        print("   • Los selectores necesitan ajuste")
        print("   • La página no cargó correctamente")
    
    # Guardar resultados
    if extractor.video_urls:
        json_file = extractor.save_video_urls_to_json("test_extraction.json")
        print(f"\n💾 Resultados guardados en: {json_file}")

if __name__ == "__main__":
    asyncio.run(test_video_detection())

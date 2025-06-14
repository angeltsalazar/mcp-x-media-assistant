#!/usr/bin/env python3
"""
Test de la nueva implementación mejorada de edge_x_downloader_clean.py
Verifica que use la lógica de simple_video_extractor.py para extraer medios
"""

import asyncio
import sys
import os
from pathlib import Path

# Añadir el directorio actual al path
sys.path.append('/Volumes/SSDWD2T/projects/asistente_computadora')

from edge_x_downloader_clean import EdgeXDownloader

async def test_improved_extraction():
    """Test de la extracción mejorada sin descarga"""
    
    print("🧪 TESTING IMPROVED MEDIA EXTRACTION")
    print("=" * 60)
    print("Usando la lógica mejorada de simple_video_extractor.py")
    print("Sin descargar archivos, solo probando extracción")
    print()
    
    # Crear downloader de prueba
    test_dir = "/tmp/edge_test"
    downloader = EdgeXDownloader(test_dir)
    
    # URL de prueba
    profile_url = "https://x.com/milewskaja_nat/media"
    
    print(f"🎯 URL objetivo: {profile_url}")
    print("🚀 Iniciando test...")
    print()
    
    # Ejecutar solo la parte de extracción
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Usar perfil de automatización
            automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "EdgeAutomation"
            automation_dir.mkdir(parents=True, exist_ok=True)
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(automation_dir),
                headless=False,
                executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                viewport={"width": 1280, "height": 720}
            )
            
            try:
                page = context.pages[0] if context.pages else await context.new_page()
                
                print("🌐 Navegando al perfil...")
                await page.goto(profile_url, wait_until="load", timeout=30000)
                await asyncio.sleep(3)
                
                # Verificar login
                if "login" in page.url:
                    print("⚠️  Se requiere login. Esperando login manual...")
                    while "login" in page.url:
                        await asyncio.sleep(2)
                    print("✅ Login detectado")
                    await page.goto(profile_url, wait_until="load", timeout=30000)
                    await asyncio.sleep(3)
                
                print("🔍 Extrayendo medios usando nueva lógica...")
                
                # Probar la nueva función de extracción
                media_data = await downloader.extract_media_urls_from_page(page)
                
                print(f"\n📊 RESULTADOS:")
                print(f"   📹 Total URLs extraídas: {len(getattr(downloader, 'all_status_urls', []))}")
                
                # Contar videos e imágenes
                all_status = getattr(downloader, 'all_status_urls', [])
                videos = [item for item in all_status if item.get('media_type') == 'video']
                images = [item for item in all_status if item.get('media_type') == 'image']
                
                print(f"   🎬 Videos detectados: {len(videos)}")
                print(f"   📷 Imágenes detectadas: {len(images)}")
                print(f"   📷 URLs directas de imágenes: {len(media_data.get('images', []))}")
                
                # Mostrar algunas URLs de video encontradas
                if videos:
                    print(f"\n🎬 URLs de Videos (primeras 5):")
                    for i, video in enumerate(videos[:5], 1):
                        print(f"   {i}. {video['url']}")
                
                # Mostrar algunas URLs de imagen
                if media_data.get('images'):
                    print(f"\n📷 URLs de Imágenes Directas (primeras 5):")
                    for i, img_url in enumerate(media_data['images'][:5], 1):
                        print(f"   {i}. {img_url}")
                
                # Generar JSON de prueba
                print(f"\n💾 Generando JSON de prueba...")
                json_file = await downloader.save_media_json(profile_url, True)
                
                if json_file:
                    print(f"✅ JSON generado: {json_file}")
                
                # Verificar si encontramos las URLs específicas mencionadas en el documento
                target_ids = ["1930265846783377473", "1927003705959678028", "1915047384612241420"]
                found_targets = []
                
                for item in all_status:
                    if any(target_id in item['url'] for target_id in target_ids):
                        found_targets.append(item['url'])
                
                if found_targets:
                    print(f"\n🎯 URLs específicas encontradas:")
                    for url in found_targets:
                        print(f"   ✅ {url}")
                else:
                    print(f"\n🔍 URLs específicas del documento no encontradas en esta sesión")
                
                print(f"\n✅ TEST COMPLETADO EXITOSAMENTE")
                print(f"📊 Resumen: {len(all_status)} medios, {len(videos)} videos, {len(images)} imágenes")
                
            finally:
                await context.close()
                
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improved_extraction())

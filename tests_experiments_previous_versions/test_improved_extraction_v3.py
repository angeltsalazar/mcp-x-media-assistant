#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en la extracción de URLs de imágenes
Versión 3: Con scroll mejorado y carga completa de imágenes
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from edge_x_downloader_clean import EdgeXDownloader
from playwright.async_api import async_playwright

async def test_improved_extraction_v3():
    """Probar la extracción mejorada de URLs con scroll completo"""
    print("🧪 === PRUEBA DE EXTRACCIÓN MEJORADA v3 ===")
    print("🎯 Objetivo: Mejorar la tasa de conversión mediante scroll completo")
    print()
    
    # Configurar downloader de prueba
    downloader = EdgeXDownloader()
    # Usar configuración hardcodeada para la prueba
    downloader.download_dir = Path("/Volumes/SSDWD2T/fansly/nat")
    downloader.download_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Iniciando Edge para prueba...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            headless=False,
            user_data_dir=str(Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "EdgeAutomation"),
            viewport={"width": 1280, "height": 720}
        )
        
        try:
            page = browser.pages[0] if browser.pages else await browser.new_page()
            
            # URL de prueba (Media tab del perfil)
            test_url = "https://x.com/milewskaja_nat/media"
            print(f"🌐 Navegando a: {test_url}")
            
            await page.goto(test_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)  # Esperar a que cargue contenido
            
            print("🔍 Iniciando extracción de medios con mejoras...")
            
            # Inicializar atributos necesarios
            downloader.processed_status_ids = set()
            downloader.unique_urls = set()
            downloader.all_status_urls = []
            
            # Paso 1: Extraer URLs de status iniciales
            print("\n📋 PASO 1: Extrayendo URLs de status iniciales...")
            await downloader._extract_all_status_urls(page)
            initial_status_count = len(downloader.all_status_urls)
            print(f"✅ URLs de status iniciales extraídas: {initial_status_count}")
            
            # Paso 2: Scroll mejorado y extraer más
            print("\n📜 PASO 2: Scroll mejorado (hasta 8 scrolls)...")
            await downloader._scroll_and_extract_urls(page, max_scrolls=8)
            total_after_scroll = len(downloader.all_status_urls)
            print(f"✅ URLs totales después del scroll: {total_after_scroll}")
            
            # Separar por tipo
            images_status = [item for item in downloader.all_status_urls if item.get('media_type') == 'image']
            videos_status = [item for item in downloader.all_status_urls if item.get('media_type') == 'video']
            
            print(f"📊 Clasificación de status URLs:")
            print(f"   📷 Imágenes: {len(images_status)}")
            print(f"   🎬 Videos: {len(videos_status)}")
            
            # Paso 3: Conversión mejorada con scroll completo
            print("\n🔄 PASO 3: Conversión mejorada a URLs directas...")
            direct_image_urls = await downloader._convert_status_to_image_urls(page)
            
            print(f"✅ URLs directas de imágenes obtenidas: {len(direct_image_urls)}")
            
            # Diagnóstico detallado
            conversion_rate = (len(direct_image_urls) / len(images_status) * 100) if images_status else 0
            print(f"📈 Tasa de conversión mejorada: {conversion_rate:.1f}% ({len(direct_image_urls)}/{len(images_status)})")
            
            # Comparar con la prueba anterior
            previous_rate = 58.3  # De la prueba anterior
            improvement = conversion_rate - previous_rate
            if improvement > 0:
                print(f"🎉 ¡Mejora de {improvement:.1f}% respecto a la prueba anterior!")
            elif improvement < 0:
                print(f"⚠️  Degradación de {abs(improvement):.1f}% respecto a la prueba anterior")
            else:
                print(f"➡️  Sin cambios respecto a la prueba anterior")
            
            # Mostrar las primeras 5 URLs directas
            if direct_image_urls:
                print("\n🔍 Primeras 5 URLs directas de imágenes:")
                for i, url in enumerate(direct_image_urls[:5], 1):
                    filename = downloader.clean_filename(url)
                    print(f"   {i}. {filename} -> {url}")
            
            # Paso 4: Probar el flujo completo
            print("\n🔄 PASO 4: Probando flujo completo...")
            # Reinicializar para probar flujo completo
            downloader.processed_status_ids = set()
            downloader.unique_urls = set()
            downloader.all_status_urls = []
            
            media_data = await downloader.extract_media_urls_from_page(page)
            
            print(f"📊 Resultado final del flujo completo:")
            print(f"   📷 Imágenes: {len(media_data['images'])}")
            print(f"   🎬 Videos: {len(media_data['videos'])}")
            print(f"   📊 Total: {len(media_data['total'])}")
            
            # Paso 5: Generar JSON de prueba
            print("\n💾 PASO 5: Generando JSON de prueba...")
            json_file = await downloader.save_media_json(test_url, True)
            if json_file:
                print(f"✅ JSON guardado: {json_file}")
            
            print("\n🎯 === RESUMEN DE LA PRUEBA v3 ===")
            print(f"✅ Status URLs extraídas: {len(downloader.all_status_urls)}")
            print(f"✅ Status de imágenes: {len(images_status)}")
            print(f"✅ URLs directas convertidas: {len(direct_image_urls)}")
            print(f"✅ Tasa de conversión: {conversion_rate:.1f}%")
            print(f"✅ Mejora respecto a v2: {improvement:+.1f}%")
            print(f"✅ Flujo completo - Imágenes: {len(media_data['images'])}")
            print(f"✅ Flujo completo - Videos: {len(media_data['videos'])}")
            
            if conversion_rate >= 90:
                print("🎉 ¡Prueba EXCELENTE! La extracción está funcionando muy bien.")
            elif conversion_rate >= 80:
                print("✅ ¡Prueba EXITOSA! La extracción está funcionando correctamente.")
            elif conversion_rate >= 60:
                print("⚠️  Prueba PARCIAL. La extracción funciona pero hay margen de mejora.")
            else:
                print("❌ Prueba FALLIDA. La extracción necesita mejoras.")
                
            # Diagnóstico adicional
            if conversion_rate < 80:
                missing_count = len(images_status) - len(direct_image_urls)
                print(f"\n🔍 DIAGNÓSTICO ADICIONAL:")
                print(f"   📊 {missing_count} imágenes no convertidas")
                print(f"   💡 Posibles causas:")
                print(f"      - Imágenes en tweets muy antiguos no cargados")
                print(f"      - Tweets eliminados o protegidos")
                print(f"      - Limitaciones de X en la carga de contenido")
                print(f"      - Necesidad de más tiempo de espera o scrolls")
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_improved_extraction_v3())
    except KeyboardInterrupt:
        print("\n🛑 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando la prueba: {e}")

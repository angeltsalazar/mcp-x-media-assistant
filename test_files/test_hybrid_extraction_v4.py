#!/usr/bin/env python3
"""
Script de prueba para verificar el método híbrido de extracción de URLs
Versión 4: Con método híbrido (DOM + construcción directa)
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from edge_x_downloader_clean import EdgeXDownloader
from playwright.async_api import async_playwright

async def test_hybrid_extraction():
    """Probar el método híbrido de extracción"""
    print("🧪 === PRUEBA DE MÉTODO HÍBRIDO v4 ===")
    print("🎯 Objetivo: Combinar DOM + construcción directa para mejorar conversión")
    print()
    
    # Configurar downloader de prueba
    downloader = EdgeXDownloader()
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
            
            print("🔍 Iniciando extracción híbrida...")
            
            # Inicializar atributos necesarios
            downloader.processed_status_ids = set()
            downloader.unique_urls = set()
            downloader.all_status_urls = []
            
            # Paso 1: Extraer URLs de status
            print("\n📋 PASO 1: Extrayendo URLs de status...")
            await downloader._extract_all_status_urls(page)
            
            # Paso 2: Scroll para cargar más
            print("\n📜 PASO 2: Scroll para cargar más contenido...")
            await downloader._scroll_and_extract_urls(page, max_scrolls=6)
            
            # Separar por tipo
            images_status = [item for item in downloader.all_status_urls if item.get('media_type') == 'image']
            videos_status = [item for item in downloader.all_status_urls if item.get('media_type') == 'video']
            
            print(f"📊 URLs extraídas:")
            print(f"   📷 Imágenes: {len(images_status)}")
            print(f"   🎬 Videos: {len(videos_status)}")
            print(f"   📊 Total: {len(downloader.all_status_urls)}")
            
            # Paso 3: Método híbrido
            print("\n🔄 PASO 3: Aplicando método híbrido...")
            direct_image_urls = await downloader._convert_status_to_image_urls(page)
            
            # Mostrar resultados
            conversion_rate = (len(direct_image_urls) / len(images_status) * 100) if images_status else 0
            print(f"\n📈 RESULTADOS:")
            print(f"   📊 Status de imágenes detectados: {len(images_status)}")
            print(f"   📷 URLs directas obtenidas: {len(direct_image_urls)}")
            print(f"   🎯 Tasa de conversión: {conversion_rate:.1f}%")
            
            # Comparar con versiones anteriores
            previous_rate = 58.3
            improvement = conversion_rate - previous_rate
            if improvement > 0:
                print(f"   🎉 ¡Mejora de {improvement:.1f}% respecto a versiones anteriores!")
            elif improvement < 0:
                print(f"   ⚠️  Degradación de {abs(improvement):.1f}% respecto a versiones anteriores")
            else:
                print(f"   ➡️  Sin cambios respecto a versiones anteriores")
            
            # Mostrar algunas URLs como ejemplo
            if direct_image_urls:
                print(f"\n🔍 Primeras 5 URLs directas obtenidas:")
                for i, url in enumerate(direct_image_urls[:5], 1):
                    filename = downloader.clean_filename(url)
                    print(f"   {i}. {filename}")
            
            # Análisis de qué método fue más efectivo
            print(f"\n🔬 ANÁLISIS DE EFECTIVIDAD:")
            if len(direct_image_urls) >= len(images_status) * 0.9:  # 90% o más
                print("   🎉 EXCELENTE: El método híbrido funcionó muy bien")
            elif len(direct_image_urls) >= len(images_status) * 0.7:  # 70% o más
                print("   ✅ BUENO: El método híbrido mejoró significativamente")
            elif len(direct_image_urls) >= len(images_status) * 0.5:  # 50% o más
                print("   ⚠️  REGULAR: El método híbrido tuvo mejoras limitadas")
            else:
                print("   ❌ INSUFICIENTE: El método híbrido necesita más mejoras")
            
            # Generar JSON final
            print("\n💾 PASO 4: Generando JSON final...")
            json_file = await downloader.save_media_json(test_url, True)
            if json_file:
                print(f"✅ JSON guardado: {json_file}")
            
            print(f"\n🎯 === RESUMEN FINAL ===")
            print(f"✅ Método probado: Híbrido (DOM + construcción directa)")
            print(f"✅ Status URLs: {len(downloader.all_status_urls)}")
            print(f"✅ Imágenes status: {len(images_status)}")
            print(f"✅ URLs directas: {len(direct_image_urls)}")
            print(f"✅ Tasa de conversión: {conversion_rate:.1f}%")
            print(f"✅ Mejora: {improvement:+.1f}%")
            
            return {
                'status_urls': len(downloader.all_status_urls),
                'image_status': len(images_status),
                'direct_urls': len(direct_image_urls),
                'conversion_rate': conversion_rate,
                'improvement': improvement
            }
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            await browser.close()

if __name__ == "__main__":
    try:
        result = asyncio.run(test_hybrid_extraction())
        if result:
            print(f"\n📊 RESULTADO NUMÉRICO: {result['conversion_rate']:.1f}% de conversión")
        else:
            print(f"\n❌ LA PRUEBA FALLÓ")
    except KeyboardInterrupt:
        print("\n🛑 Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando la prueba: {e}")

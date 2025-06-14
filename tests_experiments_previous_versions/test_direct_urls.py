#!/usr/bin/env python3
"""
Prueba simple: navegar directamente a las URLs conocidas para verificar si funcionan
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def test_direct_video_urls():
    """Prueba directa navegando a las URLs de video conocidas"""
    print("🔍 Prueba Directa de URLs de Video")
    print("=" * 50)
    
    # URLs conocidas que proporcionaste
    test_urls = [
        "https://x.com/milewskaja_nat/status/1930265846783377473/video/1",
        "https://x.com/milewskaja_nat/status/1927003705959678028/video/1",
        "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"  # Del ejemplo original
    ]
    
    async with async_playwright() as p:
        # Usar Edge con perfil automatizado
        edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(automation_dir),
            headless=False,
            executable_path=edge_path,
            args=['--no-first-run', '--no-default-browser-check']
        )
        
        page = await context.new_page()
        
        valid_urls = []
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n🔍 Probando URL {i}/3: {url}")
            
            try:
                # Navegar a la URL
                await page.goto(url, timeout=15000)
                await asyncio.sleep(3)  # Esperar a que cargue
                
                # Buscar elementos de video
                video_elements = await page.query_selector_all('video, [data-testid="videoPlayer"]')
                
                if video_elements:
                    print(f"   ✅ VÁLIDA: Encontrados {len(video_elements)} elementos de video")
                    valid_urls.append(url)
                else:
                    print(f"   ❌ NO VÁLIDA: No se encontraron elementos de video")
                
                # También verificar el título de la página
                title = await page.title()
                print(f"   📄 Título: {title[:100]}...")
                
            except Exception as e:
                print(f"   ❌ ERROR navegando: {e}")
        
        await context.close()
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ URLs válidas: {len(valid_urls)}/{len(test_urls)}")
        
        if valid_urls:
            print(f"\n📋 URLs de video confirmadas:")
            for url in valid_urls:
                print(f"   • {url}")
        else:
            print(f"\n❌ Ninguna URL de video fue confirmada")
            print(f"🔧 Posibles causas:")
            print(f"   • No estás logueado en X.com")
            print(f"   • Los videos son privados")
            print(f"   • Las URLs han cambiado")

async def test_profile_main_page():
    """Prueba navegando a la página principal del perfil"""
    print("\n" + "="*60)
    print("🔍 Probando Página Principal del Perfil")
    print("="*60)
    
    profile_url = "https://x.com/milewskaja_nat"  # Página principal, no /media
    
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
            await asyncio.sleep(5)  # Esperar a que cargue
            
            # Buscar posts
            posts = await page.query_selector_all('[data-testid="tweet"], [data-testid="cellInnerDiv"]')
            print(f"📊 Encontrados {len(posts)} posts en la página principal")
            
            videos_found = 0
            
            for i, post in enumerate(posts[:10]):  # Solo revisar los primeros 10
                try:
                    # Buscar videos en este post
                    video_elements = await post.query_selector_all('video, [data-testid="videoPlayer"]')
                    
                    if video_elements:
                        videos_found += 1
                        
                        # Intentar obtener el enlace del tweet
                        links = await post.query_selector_all('a[href*="/status/"]')
                        for link in links:
                            href = await link.get_attribute('href')
                            if href and '/status/' in href:
                                if not href.startswith('http'):
                                    href = f"https://x.com{href}"
                                
                                print(f"   📹 Video encontrado en: {href}")
                                break
                
                except Exception as e:
                    continue
            
            print(f"\n📊 Total de posts con video en página principal: {videos_found}")
            
        except Exception as e:
            print(f"❌ Error navegando a página principal: {e}")
        
        finally:
            await context.close()

async def main():
    """Ejecutar ambas pruebas"""
    print("🧪 Suite de Pruebas para Detección de Videos")
    print("=" * 60)
    
    # Prueba 1: URLs directas
    await test_direct_video_urls()
    
    # Prueba 2: Página principal del perfil
    await test_profile_main_page()
    
    print(f"\n🏁 Pruebas completadas")
    print(f"💡 Si las URLs directas funcionan pero el detector no las encuentra,")
    print(f"   entonces el problema está en la navegación o detección automática.")

if __name__ == "__main__":
    asyncio.run(main())

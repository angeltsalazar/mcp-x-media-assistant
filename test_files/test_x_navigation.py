#!/usr/bin/env python3
"""
Script de prueba rápida para verificar conectividad y navegación a X
"""

import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

async def test_x_navigation():
    """Prueba rápida de navegación a X"""
    print("🧪 Prueba rápida de navegación a X")
    print("=" * 40)
    
    async with async_playwright() as p:
        print("🚀 Iniciando Edge...")
        
        # Usar perfil de automatización
        automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "EdgeAutomation"
        
        browser = await p.chromium.launch_persistent_context(
            executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            user_data_dir=str(automation_dir),
            headless=False,
            viewport={"width": 1280, "height": 720}
        )
        
        try:
            page = browser.pages[0] if browser.pages else await browser.new_page()
            
            print("🌐 Probando navegación básica a X...")
            
            # Estrategias de navegación progresivas
            test_urls = [
                ("X Homepage", "https://x.com"),
                ("Profile Direct", "https://x.com/milewskaja_nat"),
                ("Profile Media", "https://x.com/milewskaja_nat/media")
            ]
            
            for name, url in test_urls:
                print(f"\n📍 Probando: {name} ({url})")
                
                try:
                    # Intentar navegación rápida primero
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    print(f"   ✅ Navegación exitosa")
                    
                    # Verificar estado de la página
                    await asyncio.sleep(2)
                    current_url = page.url
                    title = await page.title()
                    
                    print(f"   📄 URL actual: {current_url}")
                    print(f"   📝 Título: {title[:50]}...")
                    
                    # Verificar si necesita login
                    if "login" in current_url:
                        print(f"   🔐 Página requiere login")
                    else:
                        print(f"   ✅ Página cargada correctamente")
                        
                        # Solo para la página de medios, hacer una verificación adicional
                        if "media" in url:
                            print("   🔍 Verificando elementos de medios...")
                            try:
                                # Buscar elementos específicos de la página de medios
                                images = await page.query_selector_all('img[src*="pbs.twimg.com"]')
                                print(f"   📷 Imágenes encontradas: {len(images)}")
                                
                                if len(images) > 0:
                                    print("   ✅ Página de medios funcional")
                                else:
                                    print("   ⚠️  No se encontraron imágenes (puede requerir scroll)")
                                    
                            except Exception as e:
                                print(f"   ⚠️  Error verificando medios: {e}")
                    
                except asyncio.TimeoutError:
                    print(f"   ❌ Timeout en navegación (20s)")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                # Pausa entre pruebas
                await asyncio.sleep(1)
            
            print(f"\n🏁 Prueba completada")
            
        except Exception as e:
            print(f"❌ Error general: {e}")
        
        finally:
            print("🔚 Cerrando navegador...")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_x_navigation())

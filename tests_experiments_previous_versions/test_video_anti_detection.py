#!/usr/bin/env python3
"""
Script de prueba específico para descargar el video con configuración anti-detección
"""

import asyncio
from playwright.async_api import async_playwright
import random
import time

async def test_video_download():
    """
    Prueba específica para el video con configuración anti-detección mejorada
    """
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print("🎬 Prueba de Descarga con Configuración Anti-Detección")
    print("=" * 60)
    print(f"📹 Video: {video_url}")
    print("🕵️ Usando User-Agent de Chrome real")
    print("🤖 Con configuraciones anti-automatización")
    print()
    
    async with async_playwright() as p:
        # Configurar navegador con características anti-detección
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--disable-default-apps',
                '--disable-infobars',
                '--disable-extensions',
                '--disable-plugins-discovery',
                '--disable-translate',
                '--disable-background-networking',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        try:
            # Crear contexto con configuración de navegador real
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                viewport={'width': 1366, 'height': 768},  # Resolución común
                locale='es-ES',
                timezone_id='Europe/Madrid',
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1'
                }
            )
            
            page = await context.new_page()
            
            # Script anti-detección más completo
            await page.add_init_script("""
                // Remover indicadores de webdriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Simular plugins reales
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {name: 'Chrome PDF Plugin', description: 'Portable Document Format'},
                        {name: 'Chrome PDF Viewer', description: 'Portable Document Format'},
                        {name: 'Native Client', description: 'Native Client'},
                    ],
                });
                
                // Configurar idiomas
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-ES', 'es', 'en-US', 'en'],
                });
                
                // Simular propiedades de hardware
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8,
                });
                
                // Simular memoria del dispositivo
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8,
                });
                
                // Remover chrome automation
                if (window.chrome) {
                    delete window.chrome.runtime.onConnect;
                    delete window.chrome.runtime.onMessage;
                }
                
                // Simular comportamiento de usuario
                const originalQuery = window.document.querySelector;
                window.document.querySelector = function(selector) {
                    return originalQuery.call(this, selector);
                };
            """)
            
            print("🌐 Navegando a twittervideodownloader.com...")
            await page.goto("https://twittervideodownloader.com/", wait_until="domcontentloaded")
            
            # Simular comportamiento humano
            await asyncio.sleep(random.uniform(2, 4))
            
            # Hacer scroll para simular comportamiento humano
            await page.evaluate("window.scrollTo(0, 100)")
            await asyncio.sleep(random.uniform(1, 2))
            
            print("⏳ Esperando que la página se cargue completamente...")
            
            try:
                # Esperar el título
                await page.wait_for_selector("h1, .title, [class*='title']", timeout=10000)
                
                # Verificar múltiples formas de encontrar el título
                title_selectors = ["h1", ".title", "[class*='title']", "title"]
                title_found = False
                
                for selector in title_selectors:
                    try:
                        title_element = await page.query_selector(selector)
                        if title_element:
                            title_text = await title_element.text_content()
                            print(f"📄 Título encontrado: '{title_text}'")
                            if "Twitter" in title_text or "Video" in title_text or "Download" in title_text:
                                title_found = True
                                break
                    except:
                        continue
                
                if not title_found:
                    print("⚠️  No se pudo verificar el título específico, continuando...")
                
            except Exception as e:
                print(f"⚠️  Error verificando título: {e}")
            
            # Buscar campo de entrada con múltiples selectores
            print("🔍 Buscando campo de entrada...")
            input_selectors = [
                'input[placeholder*="Tweet"]',
                'input[placeholder*="tweet"]', 
                'input[placeholder*="link"]',
                'input[placeholder*="URL"]',
                'input[placeholder*="url"]',
                'input[type="text"]',
                'input[type="url"]',
                '.input-field',
                '#url-input',
                '[class*="input"]'
            ]
            
            input_field = None
            for selector in input_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    input_field = await page.query_selector(selector)
                    if input_field:
                        print(f"✅ Campo encontrado con selector: {selector}")
                        break
                except:
                    continue
            
            if not input_field:
                print("❌ No se pudo encontrar el campo de entrada")
                return
            
            # Simular escritura humana
            print(f"📝 Ingresando URL del video...")
            await input_field.click()
            await asyncio.sleep(random.uniform(0.5, 1))
            
            # Escribir carácter por carácter para simular escritura humana
            for char in video_url:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            await asyncio.sleep(random.uniform(1, 2))
            
            # Buscar botón de descarga
            print("🔍 Buscando botón de descarga...")
            download_selectors = [
                'button:has-text("Download")',
                'input[value*="Download"]',
                '.download-btn',
                '#download-btn',
                '[class*="download"]',
                'button[type="submit"]',
                '.btn-primary',
                '.btn'
            ]
            
            download_button = None
            for selector in download_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    download_button = await page.query_selector(selector)
                    if download_button:
                        button_text = await download_button.text_content()
                        if "download" in button_text.lower() or "descargar" in button_text.lower():
                            print(f"✅ Botón encontrado: '{button_text}' con selector: {selector}")
                            break
                except:
                    continue
            
            if not download_button:
                print("❌ No se pudo encontrar el botón de descarga")
                # Mostrar todos los botones disponibles para debug
                buttons = await page.query_selector_all('button, input[type="submit"], .btn')
                print("🔍 Botones disponibles:")
                for i, btn in enumerate(buttons):
                    try:
                        text = await btn.text_content()
                        print(f"   {i+1}. '{text}'")
                    except:
                        pass
                return
            
            # Hacer clic en el botón
            print("🖱️ Haciendo clic en el botón de descarga...")
            await download_button.click()
            
            print("⏳ Esperando resultados...")
            print("🔧 NOTA: Si aparece una verificación CAPTCHA, resuélvela manualmente")
            print("   El script esperará hasta 30 segundos...")
            
            # Esperar más tiempo para los resultados
            try:
                results_selectors = [
                    ':has-text("videos found")',
                    ':has-text("Videos found")', 
                    ':has-text("found in the Tweet")',
                    '.video-results',
                    '.download-options',
                    '.results',
                    '[class*="result"]',
                    'a[href*=".mp4"]'
                ]
                
                results_found = False
                for selector in results_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=30000)
                        print(f"✅ Resultados encontrados con selector: {selector}")
                        results_found = True
                        break
                    except:
                        continue
                
                if not results_found:
                    print("⚠️  Resultados no encontrados con selectores automáticos")
                    print("🔍 Buscando enlaces de video manualmente...")
                    
                    # Buscar todos los enlaces
                    all_links = await page.query_selector_all('a')
                    video_links = []
                    
                    for link in all_links:
                        try:
                            href = await link.get_attribute('href')
                            text = await link.text_content()
                            if href and ('.mp4' in href or 'video' in href.lower()):
                                video_links.append((href, text))
                                print(f"🎬 Enlace de video encontrado: {text} -> {href}")
                        except:
                            continue
                    
                    if video_links:
                        print(f"✅ Encontrados {len(video_links)} enlaces de video")
                        # Usar el primer enlace válido
                        best_link = video_links[0][0]
                        print(f"🎯 Seleccionando: {best_link}")
                        
                        # Aquí podrías descargar el video
                        print(f"📥 URL directa obtenida: {best_link}")
                        return best_link
                    else:
                        print("❌ No se encontraron enlaces de video")
                        return None
                
            except Exception as e:
                print(f"❌ Error esperando resultados: {e}")
                return None
            
            print("⏳ Esperando un momento adicional para que se carguen todas las opciones...")
            await asyncio.sleep(5)
            
            # Buscar enlaces de descarga
            download_links = await page.query_selector_all('a[href*=".mp4"], a[href*="video"]')
            
            if not download_links:
                print("❌ No se encontraron enlaces de descarga directos")
                return None
            
            print(f"✅ Encontrados {len(download_links)} enlaces de descarga")
            
            # Analizar y seleccionar el mejor
            best_link = None
            highest_quality = 0
            
            for i, link in enumerate(download_links):
                try:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    print(f"   {i+1}. {text} -> {href}")
                    
                    # Buscar indicadores de calidad
                    import re
                    quality_match = re.search(r'(\d+)x(\d+)', text or "")
                    if quality_match:
                        width, height = map(int, quality_match.groups())
                        quality_score = width * height
                        if quality_score > highest_quality:
                            highest_quality = quality_score
                            best_link = href
                            print(f"   ⭐ Mejor calidad hasta ahora: {width}x{height}")
                    elif best_link is None and href:
                        best_link = href
                        
                except Exception as e:
                    print(f"   ❌ Error analizando enlace {i+1}: {e}")
            
            if best_link:
                print(f"🎯 URL del video seleccionada: {best_link}")
                return best_link
            else:
                print("❌ No se pudo obtener URL directa")
                return None
                
        except Exception as e:
            print(f"❌ Error general: {e}")
            return None
            
        finally:
            print("🔄 Manteniendo navegador abierto para inspección manual...")
            print("   Presiona Ctrl+C cuando hayas terminado")
            
            try:
                # Mantener abierto para inspección manual
                await asyncio.sleep(300)  # 5 minutos
            except KeyboardInterrupt:
                print("\n👋 Cerrando navegador...")
            
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_video_download())

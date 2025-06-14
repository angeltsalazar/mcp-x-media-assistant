#!/usr/bin/env python3
"""
Descargador simple y robusto con anti-detección básica
"""

import asyncio
import requests
import re
import random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

async def descargar_video_sin_ban():
    """Descarga video con técnicas básicas anti-ban"""
    
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print("🥷 Descargador Anti-Ban Simple")
    print("=" * 50)
    print(f"📹 Video: {video_url}")
    print()
    
    # Directorio de descarga
    download_dir = Path.home() / "Downloads" / "X_Videos_Safe"
    download_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Descarga en: {download_dir}")
    
    async with async_playwright() as p:
        # Configuración básica pero efectiva
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Script anti-detección básico
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        try:
            print("📄 Navegando al sitio...")
            await page.goto("https://twittervideodownloader.com/", timeout=30000)
            
            # Esperar y verificar carga
            await page.wait_for_load_state('domcontentloaded')
            await asyncio.sleep(3)  # Delay humano
            
            # Buscar campo de entrada más simple
            print("📝 Buscando campo de entrada...")
            input_field = await page.wait_for_selector('input', timeout=10000)
            
            if not input_field:
                print("❌ No se encontró campo de entrada")
                return
            
            # Escribir URL
            print(f"⌨️  Escribiendo URL...")
            await input_field.click()
            await asyncio.sleep(1)
            await input_field.fill(video_url)
            await asyncio.sleep(2)
            
            # Buscar y hacer clic en botón
            print("🔍 Buscando botón...")
            button = await page.wait_for_selector('button, input[type="submit"]', timeout=10000)
            
            if button:
                await button.click()
                print("✅ Botón presionado")
            else:
                # Intentar presionar Enter
                await page.keyboard.press('Enter')
                print("✅ Enter presionado")
            
            # Esperar resultados
            print("⏳ Esperando resultados...")
            await asyncio.sleep(5)
            
            # Buscar enlaces de descarga
            print("🔍 Buscando enlaces...")
            
            # Esperar más tiempo si es necesario
            for attempt in range(6):  # 30 segundos total
                links = await page.query_selector_all('a[href*=".mp4"]')
                if links:
                    break
                print(f"   Intento {attempt + 1}/6...")
                await asyncio.sleep(5)
            
            if not links:
                print("❌ No se encontraron enlaces de descarga")
                
                # Debug: tomar screenshot
                await page.screenshot(path="debug_no_links.png")
                print("📸 Screenshot guardado: debug_no_links.png")
                
                # Mostrar contenido de la página
                content = await page.content()
                print("📄 Contenido HTML (primeros 1000 chars):")
                print(content[:1000])
                return
            
            # Seleccionar mejor enlace
            best_link = None
            best_quality = 0
            
            print(f"📊 Encontrados {len(links)} enlaces")
            
            for link in links:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                
                print(f"   🔗 Enlace: {href}")
                print(f"      Texto: {text}")
                
                if href and href.endswith('.mp4'):
                    # Buscar calidad en el texto
                    quality_match = re.search(r'(\d+)x(\d+)', text)
                    if quality_match:
                        width, height = map(int, quality_match.groups())
                        quality = width * height
                        if quality > best_quality:
                            best_quality = quality
                            best_link = href
                    elif not best_link:
                        best_link = href
            
            if not best_link:
                print("❌ No se encontró enlace válido")
                return
            
            print(f"✅ Mejor enlace: {best_link}")
            
            # Descargar video
            print("⬇️  Descargando video...")
            
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            response = session.get(best_link, stream=True)
            response.raise_for_status()
            
            # Nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            file_path = download_dir / filename
            
            # Descargar con progreso
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\\r   📊 {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
            
            print(f"\\n✅ ¡Video descargado!")
            print(f"📁 Archivo: {file_path}")
            
            # Mostrar info del archivo
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"📏 Tamaño: {size_mb:.2f} MB")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Debug screenshot
            try:
                await page.screenshot(path="debug_error.png")
                print("📸 Screenshot de error: debug_error.png")
            except:
                pass
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🎬 Iniciando descarga...")
    asyncio.run(descargar_video_sin_ban())

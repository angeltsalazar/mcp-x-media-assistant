#!/usr/bin/env python3
"""
Descargador con múltiples servicios de respaldo y manejo de bloqueos
"""

import asyncio
import requests
import re
import random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class MultiServiceVideoDownloader:
    def __init__(self):
        self.download_dir = Path.home() / "Downloads" / "X_Videos_Multi"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Lista de servicios alternativos
        self.services = [
            {
                'name': 'TwitterVideoDownloader',
                'url': 'https://twittervideodownloader.com/',
                'input_selector': 'input[placeholder*="Tweet"], input[type="text"], input[type="url"]',
                'button_selector': 'button:has-text("Download"), input[type="submit"]',
                'result_selector': 'a[href*=".mp4"]'
            },
            {
                'name': 'SaveTweetVid',
                'url': 'https://savetweetvid.com/',
                'input_selector': 'input[type="text"], input[type="url"]',
                'button_selector': 'button, input[type="submit"]',
                'result_selector': 'a[href*=".mp4"], .download-link'
            },
            {
                'name': 'DownloadTwitterVideo',
                'url': 'https://www.downloadtwittervideo.com/',
                'input_selector': 'input[type="text"], input[type="url"]',
                'button_selector': 'button, input[type="submit"]',
                'result_selector': 'a[href*=".mp4"]'
            }
        ]
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    async def test_service_availability(self, service_url):
        """Prueba si un servicio está disponible"""
        try:
            response = self.session.get(service_url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    async def try_service(self, service, video_url, page):
        """Intenta descargar usando un servicio específico"""
        print(f"🔄 Probando {service['name']}...")
        
        try:
            # Navegar al servicio
            print(f"   📄 Navegando a {service['url']}")
            await page.goto(service['url'], wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
            
            # Buscar campo de entrada
            print("   📝 Buscando campo de entrada...")
            input_field = await page.wait_for_selector(service['input_selector'], timeout=10000)
            
            if not input_field:
                print("   ❌ Campo de entrada no encontrado")
                return None
            
            # Escribir URL
            print("   ⌨️  Escribiendo URL...")
            await input_field.click()
            await asyncio.sleep(1)
            await input_field.fill(video_url)
            await asyncio.sleep(2)
            
            # Buscar botón
            print("   🔍 Buscando botón de descarga...")
            try:
                button = await page.wait_for_selector(service['button_selector'], timeout=5000)
                await button.click()
            except:
                # Intentar Enter como alternativa
                await page.keyboard.press('Enter')
            
            print("   ⏳ Esperando resultados...")
            
            # Esperar resultados con múltiples intentos
            for attempt in range(8):  # 40 segundos total
                try:
                    links = await page.query_selector_all(service['result_selector'])
                    if links:
                        print(f"   ✅ Encontrados {len(links)} enlaces")
                        
                        # Buscar mejor enlace
                        best_link = None
                        best_quality = 0
                        
                        for link in links:
                            href = await link.get_attribute('href')
                            text = await link.inner_text()
                            
                            if href and href.endswith('.mp4'):
                                # Buscar calidad
                                quality_match = re.search(r'(\\d+)x(\\d+)', text)
                                if quality_match:
                                    width, height = map(int, quality_match.groups())
                                    quality = width * height
                                    if quality > best_quality:
                                        best_quality = quality
                                        best_link = href
                                elif not best_link:
                                    best_link = href
                        
                        if best_link:
                            print(f"   🎯 Mejor enlace encontrado: {best_link}")
                            return best_link
                
                except Exception as e:
                    pass
                
                print(f"   ⏳ Intento {attempt + 1}/8...")
                await asyncio.sleep(5)
            
            print("   ❌ No se encontraron enlaces válidos")
            return None
            
        except Exception as e:
            print(f"   ❌ Error con {service['name']}: {e}")
            return None
    
    async def download_video(self, video_url):
        """Descarga video probando múltiples servicios"""
        print("📱 Descargador Multi-Servicio")
        print("=" * 50)
        print(f"📹 Video: {video_url}")
        print(f"📁 Descarga en: {self.download_dir}")
        print()
        
        # Verificar disponibilidad de servicios
        print("🔍 Verificando servicios disponibles...")
        available_services = []
        
        for service in self.services:
            if await self.test_service_availability(service['url']):
                available_services.append(service)
                print(f"   ✅ {service['name']} - Disponible")
            else:
                print(f"   ❌ {service['name']} - No disponible")
        
        if not available_services:
            print("❌ Ningún servicio está disponible actualmente")
            return False
        
        print(f"\\n🎯 Probando {len(available_services)} servicios disponibles...")
        
        async with async_playwright() as p:
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
            
            # Anti-detección básica
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            try:
                # Probar cada servicio disponible
                for service in available_services:
                    direct_url = await self.try_service(service, video_url, page)
                    
                    if direct_url:
                        print(f"\\n✅ ¡Éxito con {service['name']}!")
                        
                        # Descargar el video
                        if await self._download_file(direct_url):
                            return True
                        else:
                            print("❌ Error en la descarga, probando siguiente servicio...")
                            continue
                    else:
                        print(f"❌ {service['name']} falló, probando siguiente...")
                        continue
                
                print("\\n❌ Todos los servicios fallaron")
                return False
                
            finally:
                await browser.close()
    
    async def _download_file(self, url):
        """Descarga archivo desde URL directa"""
        try:
            print(f"⬇️  Descargando desde: {url}")
            
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"video_{timestamp}.mp4"
            file_path = self.download_dir / filename
            
            # Descargar
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
            
            print(f"\\n✅ ¡Descarga exitosa!")
            print(f"📁 Archivo: {file_path}")
            
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"📏 Tamaño: {size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error descargando: {e}")
            return False

async def main():
    """Función principal"""
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print("🎬 Sistema Multi-Servicio para Videos de X")
    print("=" * 60)
    print("🛡️  Características:")
    print("   ✅ Múltiples servicios de respaldo")
    print("   ✅ Detección automática de disponibilidad")
    print("   ✅ Anti-detección básica")
    print("   ✅ Recuperación automática de errores")
    print()
    
    respuesta = input("🚀 ¿Iniciar descarga multi-servicio? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Cancelado")
        return
    
    try:
        downloader = MultiServiceVideoDownloader()
        success = await downloader.download_video(video_url)
        
        if success:
            print("\\n🎉 ¡Proceso completado exitosamente!")
        else:
            print("\\n😞 No se pudo completar la descarga")
            print("\\n💡 Sugerencias:")
            print("   • Verifica tu conexión a internet")
            print("   • El video podría ser privado o eliminado")
            print("   • Los servicios podrían estar temporalmente inaccesibles")
    
    except KeyboardInterrupt:
        print("\\n\\n👋 Interrumpido por el usuario")
    except Exception as e:
        print(f"\\n❌ Error general: {e}")

if __name__ == "__main__":
    asyncio.run(main())

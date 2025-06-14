#!/usr/bin/env python3
"""
Descargador de videos de X con evasión avanzada de detección
Específicamente diseñado para evitar baneos y detección como bot
"""

import asyncio
import requests
import re
import random
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

class AntiDetectionVideoDownloader:
    def __init__(self, download_dir=None):
        """Inicializa el descargador con configuración anti-detección"""
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Videos_AntiDetection"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sesión HTTP con headers realistas
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    async def _human_delay(self, min_ms=800, max_ms=3000):
        """Delay orgánico que simula comportamiento humano"""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)
    
    async def _simulate_human_behavior(self, page):
        """Simula comportamiento humano en la página"""
        # Mover mouse aleatoriamente
        width = 1366
        height = 768
        
        for _ in range(random.randint(2, 5)):
            x = random.randint(50, width - 50)
            y = random.randint(50, height - 50)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Scroll aleatorio
        for _ in range(random.randint(1, 3)):
            await page.evaluate("window.scrollBy(0, arguments[0])", random.randint(-200, 200))
            await asyncio.sleep(random.uniform(0.2, 0.5))
    
    async def process_video_stealth(self, video_url):
        """
        Procesa un video usando técnicas stealth avanzadas
        """
        print(f"🥷 Procesando video con modo stealth: {video_url}")
        
        async with async_playwright() as p:
            # === CONFIGURACIÓN ANTI-DETECCIÓN EXTREMA ===
            browser_args = [
                # Core anti-detección
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-extensions-except=',
                '--disable-plugins-except=',
                
                # Evasión de fingerprinting
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor,TranslateUI,BlinkGenPropertyTrees',
                '--disable-ipc-flooding-protection',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-field-trial-config',
                '--disable-back-forward-cache',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-component-extensions-with-background-pages',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-background-timer-throttling',
                '--disable-client-side-phishing-detection',
                '--disable-popup-blocking',
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
                '--no-sandbox',
                '--disable-dev-tools',
                '--disable-software-rasterizer',
                '--disable-background-networking',
                
                # Simulación de navegador real
                '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                '--window-size=1366,768',
                '--start-maximized'
            ]
            
            try:
                # Intentar usar Chrome real
                browser = await p.chromium.launch(
                    headless=False,
                    args=browser_args,
                    channel="chrome"
                )
                print("   ✅ Usando Chrome real")
            except:
                # Fallback a Chromium
                browser = await p.chromium.launch(
                    headless=False,
                    args=browser_args
                )
                print("   ⚠️  Usando Chromium (fallback)")
            
            try:
                # Crear contexto super realista
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1366, 'height': 768},
                    locale='es-ES',
                    timezone_id='America/Mexico_City',
                    geolocation={'latitude': 19.4326, 'longitude': -99.1332},
                    permissions=['geolocation'],
                    extra_http_headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"macOS"'
                    }
                )
                
                page = await context.new_page()
                
                # === INYECCIÓN MASIVA DE SCRIPTS ANTI-DETECCIÓN ===
                await page.add_init_script("""
                    // === ELIMINAR RASTROS DE AUTOMATIZACIÓN ===
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    delete window.navigator.__proto__.webdriver;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                    delete window.__playwright;
                    delete window._playwrightProcessId;
                    
                    // === SIMULAR PLUGINS REALISTAS ===
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => ({
                            length: 5,
                            0: { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                            1: { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                            2: { name: 'Native Client', description: '', filename: 'internal-nacl-plugin' },
                            3: { name: 'WebKit built-in PDF', description: 'Portable Document Format', filename: 'internal-pdf-viewer' },
                            4: { name: 'PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' }
                        }),
                    });
                    
                    // === SIMULAR IDIOMAS REALISTAS ===
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['es-ES', 'es', 'en-US', 'en'],
                    });
                    
                    // === SIMULAR HARDWARE REALISTA ===
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8,
                    });
                    
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8,
                    });
                    
                    // === PERMISOS REALISTAS ===
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // === CANVAS FINGERPRINTING CON RUIDO ===
                    const getContext = HTMLCanvasElement.prototype.getContext;
                    HTMLCanvasElement.prototype.getContext = function(type) {
                        if (type === '2d') {
                            const context = getContext.call(this, type);
                            const imageData = context.getImageData;
                            context.getImageData = function(sx, sy, sw, sh) {
                                const data = imageData.call(this, sx, sy, sw, sh);
                                // Agregar ruido mínimo pero detectable
                                for (let i = 0; i < data.data.length; i += 4) {
                                    if (Math.random() < 0.001) {
                                        data.data[i] = data.data[i] + Math.floor(Math.random() * 10) - 5;
                                        data.data[i + 1] = data.data[i + 1] + Math.floor(Math.random() * 10) - 5;
                                        data.data[i + 2] = data.data[i + 2] + Math.floor(Math.random() * 10) - 5;
                                    }
                                }
                                return data;
                            };
                            return context;
                        }
                        return getContext.call(this, type);
                    };
                    
                    // === SIMULAR ACTIVIDAD DE USUARIO ===
                    let mouseMovements = 0;
                    let keystrokes = 0;
                    let clicks = 0;
                    
                    document.addEventListener('mousemove', () => mouseMovements++);
                    document.addEventListener('keydown', () => keystrokes++);
                    document.addEventListener('click', () => clicks++);
                    
                    // Simular actividad inicial
                    setTimeout(() => {
                        mouseMovements = Math.floor(Math.random() * 50) + 10;
                        keystrokes = Math.floor(Math.random() * 20) + 5;
                        clicks = Math.floor(Math.random() * 10) + 2;
                    }, 1000);
                    
                    Object.defineProperty(window, 'userActivity', {
                        get: () => ({ mouseMovements, keystrokes, clicks }),
                    });
                    
                    // === OVERRIDE DE MÉTODOS DETECTABLES ===
                    const originalToString = Function.prototype.toString;
                    Function.prototype.toString = function() {
                        if (this === navigator.permissions.query) {
                            return 'function query() { [native code] }';
                        }
                        return originalToString.call(this);
                    };
                """)
                
                print("   🛡️  Scripts anti-detección inyectados")
                
                # === NAVEGACIÓN HUMANA ===
                print("   👤 Simulando comportamiento humano...")
                await self._human_delay(2000, 4000)  # Delay inicial
                
                print("   📄 Navegando a twittervideodownloader.com...")
                await page.goto("https://twittervideodownloader.com/", 
                             wait_until="domcontentloaded", 
                             timeout=30000)
                
                # Simular comportamiento humano después de cargar
                await self._simulate_human_behavior(page)
                
                # === VERIFICAR CARGA Y TÍTULO ===
                print("   ⏳ Verificando carga de la página...")
                await page.wait_for_selector("h1, title, .title", timeout=15000)
                
                # Verificar título más flexiblemente
                title = await page.title()
                page_text = await page.text_content("body")
                
                if "Twitter Video Downloader" not in title and "Twitter Video Downloader" not in page_text:
                    print(f"   ⚠️  Título/contenido inesperado - Título: {title}")
                    print(f"   📄 Contenido (primeros 200 chars): {page_text[:200]}")
                
                print("   ✅ Página cargada")
                
                # === MANEJO DE VERIFICACIONES ===
                await self._handle_verifications(page)
                
                # === PROCESO DE DESCARGA ===
                await self._human_delay(1000, 2000)
                
                print("   📝 Buscando campo de entrada...")
                input_selectors = [
                    'input[placeholder*="Tweet"]',
                    'input[placeholder*="tweet"]', 
                    'input[placeholder*="link"]',
                    'input[type="text"]',
                    'input[type="url"]',
                    '#url',
                    '.url-input',
                    '[name="url"]'
                ]
                
                input_element = None
                for selector in input_selectors:
                    try:
                        input_element = await page.wait_for_selector(selector, timeout=3000)
                        if input_element:
                            print(f"   ✅ Campo encontrado: {selector}")
                            break
                    except:
                        continue
                
                if not input_element:
                    print("   ❌ No se encontró campo de entrada")
                    return None
                
                # Simular escritura humana
                print(f"   ⌨️  Escribiendo URL...")
                await self._type_like_human(page, input_element, video_url)
                
                await self._human_delay(1000, 2000)
                
                # Buscar botón de descarga
                print("   🔍 Buscando botón de descarga...")
                button_selectors = [
                    'button:has-text("Download")',
                    'input[value*="Download"]',
                    '.download-btn',
                    '#download-btn',
                    'button[type="submit"]',
                    '.btn-download'
                ]
                
                download_button = None
                for selector in button_selectors:
                    try:
                        download_button = await page.wait_for_selector(selector, timeout=3000)
                        if download_button:
                            print(f"   ✅ Botón encontrado: {selector}")
                            break
                    except:
                        continue
                
                if not download_button:
                    print("   ❌ No se encontró botón de descarga")
                    return None
                
                # Simular hover antes de click
                await download_button.hover()
                await self._human_delay(500, 1000)
                await download_button.click()
                
                print("   ⏳ Esperando resultados...")
                
                # === BUSCAR RESULTADOS ===
                results_found = await self._wait_for_results(page)
                
                if not results_found:
                    return None
                
                # === EXTRAER MEJOR CALIDAD ===
                direct_url = await self._extract_best_quality_url(page)
                
                return direct_url
                
            except Exception as e:
                print(f"   ❌ Error durante procesamiento: {e}")
                return None
            
            finally:
                await browser.close()
    
    async def _handle_verifications(self, page):
        """Maneja verificaciones CAPTCHA y similares"""
        print("   🔍 Verificando captchas y verificaciones...")
        
        # Buscar elementos de verificación
        verification_selectors = [
            'iframe[src*="recaptcha"]',
            'iframe[src*="hcaptcha"]',
            '.g-recaptcha',
            '.h-captcha',
            'input[type="checkbox"]',
            '.checkbox'
        ]
        
        for selector in verification_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    print(f"   ⚠️  Verificación detectada: {selector}")
                    
                    if 'iframe' in selector:
                        print("   👤 CAPTCHA detectado - Completa manualmente")
                        print("   ⏰ Esperando hasta 90 segundos...")
                        try:
                            await page.wait_for_function(
                                f"!document.querySelector('{selector}') || !document.querySelector('{selector}').offsetParent",
                                timeout=90000
                            )
                            print("   ✅ Verificación completada")
                        except:
                            print("   ⏰ Tiempo agotado - Continuando...")
                    else:
                        # Checkbox simple
                        await element.click()
                        await self._human_delay(1000, 2000)
                        
            except:
                continue
        
        print("   ✅ Verificaciones procesadas")
    
    async def _type_like_human(self, page, element, text):
        """Simula escritura humana"""
        await element.click()
        await self._human_delay(200, 500)
        
        # Limpiar campo
        await element.fill("")
        await self._human_delay(100, 300)
        
        # Escribir caracter por caracter con delays variables
        for char in text:
            await element.type(char)
            delay = random.randint(50, 200)
            if char in ['.', '/', ':']:
                delay = random.randint(100, 300)  # Más delay en caracteres especiales
            await asyncio.sleep(delay / 1000)
    
    async def _wait_for_results(self, page):
        """Espera resultados de descarga"""
        result_selectors = [
            ':has-text("videos found")',
            ':has-text("Videos found")',
            ':has-text("video found")',
            'a[href*=".mp4"]',
            '.download-link',
            '.video-results',
            'button:has-text("HD")',
            'button:has-text("SD")'
        ]
        
        for attempt in range(3):
            print(f"   🔍 Intento {attempt + 1}/3 buscando resultados...")
            
            for selector in result_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=10000)
                    print(f"   ✅ Resultados encontrados: {selector}")
                    return True
                except:
                    continue
            
            if attempt < 2:
                print("   ⏳ Esperando más tiempo...")
                await self._human_delay(3000, 5000)
        
        print("   ❌ No se encontraron resultados")
        return False
    
    async def _extract_best_quality_url(self, page):
        """Extrae la URL de mejor calidad"""
        print("   🎯 Extrayendo mejor calidad...")
        
        # Buscar todos los enlaces de descarga
        links = await page.query_selector_all('a[href*=".mp4"], a[href*="video"], .download-link')
        
        if not links:
            print("   ❌ No se encontraron enlaces")
            return None
        
        best_url = None
        highest_quality = 0
        
        for link in links:
            try:
                href = await link.get_attribute('href')
                text = await link.text_content()
                
                if not href or not href.endswith('.mp4'):
                    continue
                
                # Buscar indicadores de calidad
                quality_match = re.search(r'(\d+)x(\d+)', text or "")
                if quality_match:
                    width, height = map(int, quality_match.groups())
                    quality_score = width * height
                    
                    if quality_score > highest_quality:
                        highest_quality = quality_score
                        best_url = href
                        print(f"   📊 Mejor calidad encontrada: {width}x{height}")
                elif best_url is None:
                    best_url = href
            
            except:
                continue
        
        if best_url:
            print(f"   ✅ URL extraída: {best_url}")
        
        return best_url
    
    async def download_video(self, video_url, filename=None):
        """Descarga video desde URL directa"""
        try:
            print(f"⬇️  Descargando: {video_url}")
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                url_hash = abs(hash(video_url)) % 10000
                filename = f"video_{timestamp}_{url_hash}.mp4"
            
            file_path = self.download_dir / filename
            
            response = self.session.get(video_url, stream=True)
            response.raise_for_status()
            
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
            
            print(f"\\n   ✅ Descargado: {file_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

async def main():
    """Función principal para probar"""
    print("🥷 Descargador Anti-Detección de Videos X")
    print("=" * 60)
    
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print(f"📹 Video objetivo: {video_url}")
    print()
    print("🛡️  Características anti-detección:")
    print("   ✅ Chrome real (no Chromium)")
    print("   ✅ Headers HTTP realistas")
    print("   ✅ Comportamiento de mouse humano")
    print("   ✅ Delays orgánicos variables")
    print("   ✅ Canvas fingerprinting con ruido")
    print("   ✅ Eliminación de rastros de automatización")
    print("   ✅ Simulación de actividad de usuario")
    print()
    
    respuesta = input("🚀 ¿Continuar con descarga stealth? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Cancelado")
        return
    
    try:
        downloader = AntiDetectionVideoDownloader()
        
        print(f"\\n📁 Directorio: {downloader.download_dir}")
        print("\\n🥷 Iniciando modo stealth...")
        
        direct_url = await downloader.process_video_stealth(video_url)
        
        if direct_url:
            print(f"\\n✅ URL obtenida: {direct_url}")
            
            if await downloader.download_video(direct_url):
                print("\\n🎉 ¡Descarga completada!")
                
                # Mostrar archivos
                videos = list(downloader.download_dir.glob("*.mp4"))
                if videos:
                    print("\\n📋 Videos descargados:")
                    for video in videos:
                        size_mb = video.stat().st_size / (1024 * 1024)
                        print(f"   📹 {video.name} ({size_mb:.2f} MB)")
            else:
                print("\\n❌ Error en descarga")
        else:
            print("\\n❌ No se pudo obtener URL directa")
    
    except KeyboardInterrupt:
        print("\\n\\n👋 Interrumpido por usuario")
    except Exception as e:
        print(f"\\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Script optimizado para Microsoft Edge con descarga de imágenes de X
Autor: Asistente AI
Fecha: 11 de junio de 2025

Este script está específicamente diseñado para usar Microsoft Edge
donde ya tienes sesión iniciada en X, y maneja automáticamente
la verificación de login y navegación.

FUNCIONALIDAD: Solo descarga IMÁGENES de la sección Media.
Para videos, usa x_video_url_extractor.py que extrae las URLs en JSON.

NUEVA FUNCIONALIDAD:
- Soporte para múltiples usuarios configurados en x_usernames.json
- Parámetro --name para seleccionar usuario por nombre amigable
- Configuración automática de directorios personalizados por usuario
"""

import os
import asyncio
import requests
import re
import json
import random
import argparse
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

# Configuración de usuarios
CONFIG_FILE = "x_usernames.json"

def load_user_config():
    """Cargar configuración de usuarios desde x_usernames.json"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error al cargar configuración: {e}")
        return {}

def save_user_config(config):
    """Guardar configuración de usuarios en x_usernames.json"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuración guardada en {CONFIG_FILE}")
    except Exception as e:
        print(f"⚠️  Error al guardar configuración: {e}")

def get_user_by_name(name):
    """Obtener información de usuario por nombre amigable"""
    config = load_user_config()
    for user_data in config.values():
        if user_data.get('friendlyname') == name:
            return user_data
    return None

def add_new_user(name):
    """Añadir un nuevo usuario a la configuración"""
    config = load_user_config()
    
    print(f"🔧 Configurando nuevo usuario: {name}")
    username = input("📝 Ingresa el username de X (sin @): ").strip()
    if username.startswith('@'):
        username = username[1:]
    
    # Validar que no esté vacío
    if not username:
        print("❌ El username no puede estar vacío")
        return None
    
    # Verificar si el username ya existe
    if username in config:
        print(f"⚠️  El username '{username}' ya existe en la configuración")
        existing_user = config[username]
        print(f"   Nombre amigable: {existing_user.get('friendlyname')}")
        print(f"   Directorio: {existing_user.get('directory_download')}")
        return existing_user
    
    directory = input("📁 Ingresa la ruta del directorio de descarga: ").strip()
    if not directory:
        # Usar directorio por defecto basado en el nombre
        home_dir = Path.home()
        directory = str(home_dir / "Downloads" / f"X_Media_{name}")
        print(f"📁 Usando directorio por defecto: {directory}")
    
    # Crear el directorio si no existe
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    user_data = {
        "friendlyname": name,
        "username": username,
        "directory_download": directory
    }
    
    config[username] = user_data
    save_user_config(config)
    
    return user_data

def list_configured_users():
    """Listar todos los usuarios configurados"""
    config = load_user_config()
    if not config:
        print("📝 No hay usuarios configurados aún")
        return
    
    print("👥 Usuarios configurados:")
    print("=" * 50)
    for username, user_data in config.items():
        print(f"  • Nombre: {user_data.get('friendlyname')}")
        print(f"    Username: @{username}")
        print(f"    Directorio: {user_data.get('directory_download')}")
        print()

class EdgeXDownloader:
    def __init__(self, download_dir=None):
        """Inicializa el descargador para Microsoft Edge"""
        if download_dir is None:
            home_dir = Path.home()
            self.download_dir = home_dir / "Downloads" / "X_Media_Edge"
        else:
            self.download_dir = Path(download_dir)
        
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Control de URLs para precisión mejorada
        self.processed_status_ids = set()

    def print_info(self):
        """Imprimir información de configuración"""
        print(f"📁 Directorio de descarga: {self.download_dir}")
        print("🎯 Objetivo: Descargar imágenes de la sección Media de X")
        print("⚠️  NOTA: Los videos se detectan pero NO se descargan")
        print("📹 Para videos usa: x_video_url_extractor.py")
        print()

    async def download_image(self, url, filename):
        """Descargar una imagen individual"""
        try:
            file_path = self.download_dir / filename
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return len(response.content)
        except Exception as e:
            print(f"⚠️  Error descargando {filename}: {e}")
            return 0

    def clean_filename(self, url):
        """Crear nombre de archivo limpio desde URL"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"image_{timestamp}.jpg"
            
            # Limpiar caracteres problemáticos
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return filename
        except Exception:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            return f"image_{timestamp}.jpg"

    def is_video_url(self, url):
        """Determinar si una URL es de video usando criterios más precisos"""
        # Método 1: Buscar patrones específicos de video en la URL
        video_patterns = [
            r'/video/1/',
            r'\.mp4',
            r'\.m4v',
            r'\.webm',
            r'ext_tw_video',
            r'video\.twimg\.com',
            r'/amplify_video/',
            r'/tweet_video/',
            r'format=mp4'
        ]
        
        for pattern in video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # Método 2: Si contiene /photo/1/ es definitivamente imagen
        if '/photo/1/' in url:
            return False
        
        # Método 3: Extensiones de imagen conocidas
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        url_lower = url.lower()
        if any(ext in url_lower for ext in image_extensions):
            return False
        
        return False

    def extract_status_id_from_url(self, url):
        """Extraer el ID del status/tweet desde la URL de media"""
        try:
            # Buscar patrones como /status/1234567890123456789/
            match = re.search(r'/status/(\d+)', url)
            if match:
                return match.group(1)
            
            # También buscar en parámetros de query
            if 'status' in url:
                match = re.search(r'status[=/](\d+)', url)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None

    async def extract_media_urls_from_page(self, page):
        """Extraer URLs de medios con clasificación mejorada"""
        print("🔍 Extrayendo URLs de medios...")
        
        # Esperar a que la página cargue completamente
        try:
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=10000)
        except Exception:
            print("⚠️  No se encontraron tweets, continuando...")
        
        # Recopilar todas las URLs de imágenes y videos
        all_urls = []
        
        # Método 1: Interceptar requests de red
        network_urls = []
        
        def handle_response(response):
            url = response.url
            if any(domain in url for domain in ['pbs.twimg.com', 'video.twimg.com']):
                if url not in network_urls:
                    network_urls.append(url)
        
        page.on('response', handle_response)
        
        # Scroll para cargar más contenido
        print("📜 Haciendo scroll para cargar contenido...")
        for _ in range(5):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
        
        # Método 2: Extraer desde elementos DOM
        dom_urls = await page.evaluate("""
            () => {
                const urls = [];
                
                // Buscar imágenes en tweets
                const images = document.querySelectorAll('img[src*="pbs.twimg.com"]');
                images.forEach(img => {
                    if (img.src && !urls.includes(img.src)) {
                        urls.push(img.src);
                    }
                });
                
                // Buscar videos
                const videos = document.querySelectorAll('video[src], video source[src]');
                videos.forEach(video => {
                    const src = video.src || video.getAttribute('src');
                    if (src && !urls.includes(src)) {
                        urls.push(src);
                    }
                });
                
                // Buscar en atributos de datos
                const mediaContainers = document.querySelectorAll('[data-testid*="media"], [role="img"]');
                mediaContainers.forEach(container => {
                    const bgImage = window.getComputedStyle(container).backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        const match = bgImage.match(/url\\(["']?([^"']+)["']?\\)/);
                        if (match && match[1] && !urls.includes(match[1])) {
                            urls.push(match[1]);
                        }
                    }
                });
                
                return urls;
            }
        """)
        
        # Combinar URLs de ambos métodos
        all_urls = list(set(network_urls + dom_urls))
        
        # Filtrar y limpiar URLs
        filtered_urls = []
        for url in all_urls:
            # Filtrar URLs válidas
            if (('pbs.twimg.com' in url or 'video.twimg.com' in url) and 
                'profile_images' not in url and 
                'profile_banners' not in url):
                
                # Limpiar parámetros innecesarios pero mantener format y name
                clean_url = re.sub(r'&?[a-zA-Z0-9_]+=(?:large|medium|small|thumb)', '', url)
                clean_url = re.sub(r'\?.*?(?=&name=|&format=|$)', '?', clean_url)
                clean_url = re.sub(r'\?&', '?', clean_url)
                clean_url = re.sub(r'\?$', '', clean_url)
                
                # Asegurar calidad máxima para imágenes
                if 'pbs.twimg.com' in clean_url and not self.is_video_url(clean_url):
                    if '?' in clean_url:
                        clean_url += '&name=large'
                    else:
                        clean_url += '?name=large'
                
                filtered_urls.append(clean_url)
        
        # Eliminar duplicados manteniendo orden
        unique_urls = []
        seen = set()
        for url in filtered_urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        
        # Clasificar URLs
        images = []
        videos = []
        
        for url in unique_urls:
            if self.is_video_url(url):
                videos.append(url)
            else:
                images.append(url)
        
        print(f"📊 URLs encontradas: {len(unique_urls)} total")
        print(f"   📷 Imágenes: {len(images)}")
        print(f"   🎬 Videos: {len(videos)}")
        
        return {
            'images': images,
            'videos': videos,
            'total': unique_urls
        }

    async def download_images_batch(self, urls, max_images=48):
        """Descargar imágenes en lote con límite"""
        if not urls:
            print("❌ No hay imágenes para descargar")
            return
        
        # Limitar número de imágenes
        download_urls = urls[:max_images]
        print(f"📥 Iniciando descarga de {len(download_urls)} imágenes...")
        
        downloaded = 0
        skipped = 0
        
        for i, url in enumerate(download_urls, 1):
            try:
                filename = self.clean_filename(url)
                file_path = self.download_dir / filename
                
                # Verificar si ya existe
                if file_path.exists():
                    file_size = file_path.stat().st_size / (1024 * 1024)
                    print(f"⬇️  [{i}/{len(download_urls)}] ⏭️  {filename} ya existe ({file_size:.2f} MB)")
                    skipped += 1
                    continue
                
                print(f"⬇️  [{i}/{len(download_urls)}] {filename}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"   ✅ {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
                # Delay orgánico entre descargas para ser respetuoso
                if i < len(download_urls):  # No esperar después del último archivo
                    await asyncio.sleep(random.uniform(0.3, 0.8))  # 300-800ms entre descargas
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print(f"📊 Resumen de descarga:")
        print(f"   ✅ Descargadas: {downloaded}")
        print(f"   ⏭️  Saltadas (ya existían): {skipped}")
        print(f"   ❌ Errores: {len(download_urls) - downloaded - skipped}")

    async def save_session_data(self, media_data, profile_url, use_automation_profile):
        """Guardar datos de la sesión en JSON"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = self.download_dir / f"session_{timestamp}"
            session_dir.mkdir(exist_ok=True)
            
            # Preparar datos del log
            log_data = {
                "session_info": {
                    "timestamp": timestamp,
                    "profile_url": profile_url,
                    "automation_profile": use_automation_profile,
                    "download_directory": str(self.download_dir)
                },
                "statistics": {
                    "total_urls": len(media_data['total']),
                    "images_found": len(media_data['images']),
                    "videos_found": len(media_data['videos']),
                    "images_downloaded": min(len(media_data['images']), 48)
                },
                "urls_classified": {
                    "images": media_data['images'][:48],  # Solo las primeras 48
                    "videos": media_data['videos'],
                    "all_urls": media_data['total']
                }
            }
            
            # Guardar log completo
            log_file = session_dir / "session_log.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Log guardado: {log_file}")
            
        except Exception as e:
            print(f"⚠️  No se pudo crear el log: {e}")

    async def download_with_edge(self, profile_url, use_automation_profile=True):
        """Ejecutar el proceso de descarga con Microsoft Edge"""
        self.print_info()
        
        async with async_playwright() as p:
            print("🚀 Iniciando Microsoft Edge...")
            
            # Configurar contexto del navegador
            context_options = {
                "viewport": {"width": 1280, "height": 720},
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            }
            
            if use_automation_profile:
                # Usar perfil de automatización
                automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge" / "EdgeAutomation"
                automation_dir.mkdir(parents=True, exist_ok=True)
                context_options["user_data_dir"] = str(automation_dir)
                print("✅ Usando perfil de automatización")
            else:
                print("✅ Usando Edge temporal (sin datos persistentes)")
            
            browser = await p.chromium.launch_persistent_context(
                executable_path="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                headless=False,
                **context_options
            )
            
            try:
                page = browser.pages[0] if browser.pages else await browser.new_page()
                
                print(f"🌐 Navegando a: {profile_url}")
                await page.goto(profile_url, wait_until="networkidle", timeout=30000)
                
                # Verificar si necesita login
                await asyncio.sleep(3)
                current_url = page.url
                
                if "login" in current_url or "i/flow/login" in current_url:
                    print("🔐 Se requiere login. Por favor, inicia sesión manualmente...")
                    print("⏳ Esperando a que inicies sesión...")
                    
                    # Esperar hasta que salga de la página de login
                    while "login" in page.url or "i/flow/login" in page.url:
                        await asyncio.sleep(2)
                        print("⏳ Aún en página de login...")
                    
                    print("✅ Login detectado, continuando...")
                    await page.goto(profile_url, wait_until="networkidle", timeout=30000)
                
                # Extraer URLs de medios
                media_data = await self.extract_media_urls_from_page(page)
                
                # Guardar datos de sesión
                await self.save_session_data(media_data, profile_url, use_automation_profile)
                
                # Descargar solo imágenes (máximo 48)
                if media_data['images']:
                    await self.download_images_batch(media_data['images'], max_images=48)
                else:
                    print("❌ No se encontraron imágenes para descargar")
                
                if media_data['videos']:
                    print(f"📹 Se detectaron {len(media_data['videos'])} videos (no descargados)")
                    print("💡 Para descargar videos usa: x_video_url_extractor.py")
                
            except Exception as e:
                print(f"❌ Error durante el proceso: {e}")
                import traceback
                traceback.print_exc()
            
            finally:
                print("🔚 Cerrando navegador...")
                await browser.close()

async def main():
    """Función principal"""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='X Media Downloader - Optimizado para Microsoft Edge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 edge_x_downloader_clean.py --name usuario1
  python3 edge_x_downloader_clean.py --name usuario1 --auto
  python3 edge_x_downloader_clean.py --list-users
  python3 edge_x_downloader_clean.py --username milewskaja_nat
        """
    )
    
    parser.add_argument('--name', '-n', 
                       help='Nombre amigable del usuario configurado')
    parser.add_argument('--username', '-u', 
                       help='Username de X directamente (sin @)')
    parser.add_argument('--directory', '-d', 
                       help='Directorio de descarga personalizado')
    parser.add_argument('--auto', '-a', action='store_true',
                       help='Usar perfil de automatización')
    parser.add_argument('--temporal', '-t', action='store_true',
                       help='Usar Edge temporal')
    parser.add_argument('--select', '-s', action='store_true',
                       help='Mostrar opciones para seleccionar modo')
    parser.add_argument('--list-users', action='store_true',
                       help='Listar usuarios configurados')
    
    args = parser.parse_args()
    
    # Listar usuarios y salir si se solicita
    if args.list_users:
        list_configured_users()
        return
    
    # Determinar configuración de usuario
    user_data = None
    profile_url = None
    download_dir = None
    
    if args.name:
        # Buscar usuario por nombre amigable
        user_data = get_user_by_name(args.name)
        if not user_data:
            print(f"❌ Usuario '{args.name}' no encontrado en configuración")
            user_data = add_new_user(args.name)
            if not user_data:
                print("❌ No se pudo configurar el usuario")
                return
        
        profile_url = f"https://x.com/{user_data['username']}/media"
        download_dir = user_data['directory_download']
        print(f"✅ Usuario seleccionado: {user_data['friendlyname']} (@{user_data['username']})")
        
    elif args.username:
        # Usar username directamente
        username = args.username
        if username.startswith('@'):
            username = username[1:]
        
        profile_url = f"https://x.com/{username}/media"
        
        # Buscar en configuración por si existe
        config = load_user_config()
        if username in config:
            user_data = config[username]
            download_dir = user_data['directory_download']
            print(f"✅ Usuario encontrado en configuración: {user_data['friendlyname']} (@{username})")
        else:
            # Usar directorio por defecto o especificado
            if args.directory:
                download_dir = args.directory
            else:
                home_dir = Path.home()
                download_dir = str(home_dir / "Downloads" / f"X_Media_{username}")
            print(f"📝 Usando username: @{username} (no está en configuración)")
    
    else:
        # Modo por defecto (compatibilidad hacia atrás)
        profile_url = "https://x.com/milewskaja_nat/media"
        print("⚠️  Usando configuración por defecto. Para usar usuarios configurados:")
        print("   python3 edge_x_downloader_clean.py --name <usuario>")
        print("   python3 edge_x_downloader_clean.py --list-users")
        print()
    
    # Usar directorio personalizado si se especifica
    if args.directory:
        download_dir = args.directory
    
    # Determinar modo de navegador
    use_automation_profile = True  # Por defecto
    show_options = False
    
    if args.temporal:
        use_automation_profile = False
        show_options = True
    elif args.auto:
        use_automation_profile = True
        show_options = True
    elif args.select:
        show_options = True
        # Preguntar al usuario qué perfil usar
        print("🎬 X Media Downloader - Seleccionar modo")
        print("=" * 50)
        print("1. Perfil de automatización (recomendado)")
        print("   ✅ No interfiere con tu Edge principal")
        print("   ✅ Mantiene sesión de X guardada")
        print("   ✅ No requiere login cada vez")
        print()
        print("2. Edge temporal")
        print("   ⚠️  Requiere login manual cada vez")
        print("   ✅ No interfiere con datos existentes")
        print()
        
        choice = input("Selecciona modo (1/2): ").strip()
        if choice == "2":
            use_automation_profile = False
        else:
            use_automation_profile = True
    
    print("🎬 X Media Downloader - Optimizado para Microsoft Edge")
    print("=" * 60)
    print(f"🎯 Perfil objetivo: {profile_url}")
    print("📷 Tipo de contenido: Solo imágenes")
    print("💡 Para videos usa: python3 x_video_url_extractor.py")
    print()
    
    if show_options:
        if use_automation_profile:
            print("✅ Usando perfil de automatización")
            print("   🔧 Ventajas:")
            print("      ✅ No interfiere con tu Edge principal")
            print("      ✅ Mantiene sesión de X guardada")
            print("      ✅ No requiere login cada vez")
        else:
            print("✅ Usando Edge temporal")
            print("   🔧 Características:")
            print("      ⚠️  Requiere login manual cada vez")
            print("      ✅ No interfiere con datos existentes")
        
        print()
        print("💡 Para cambiar modo en el futuro, usa: --auto, --temporal o --select")
        print()
        
        response = input("🚀 ¿Continuar? (s/n): ").lower().strip()
        if response not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Cancelado por el usuario")
            return
    else:
        # Modo directo: mostrar solo información básica y continuar
        print("✅ Iniciando con perfil de automatización")
        print("💡 Usa --help para ver todas las opciones disponibles")
    
    print()
    downloader = EdgeXDownloader(download_dir)
    await downloader.download_with_edge(profile_url, use_automation_profile)
    
    print()
    print("🏁 ¡Proceso completado!")
    print("📊 Revisa el JSON generado para ver la clasificación completa")
    print("📷 Se descargaron solo las primeras 48 imágenes")
    print("🎬 Para videos usa: python3 x_video_url_extractor.py o revisa el JSON")

if __name__ == "__main__":
    asyncio.run(main())

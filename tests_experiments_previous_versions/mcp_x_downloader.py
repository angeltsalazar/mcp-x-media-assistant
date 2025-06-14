#!/usr/bin/env python3
"""
Script para usar las herramientas MCP de Playwright disponibles
Este script muestra cómo usar las herramientas MCP paso a paso
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime

class MCPXDownloader:
    def __init__(self):
        """Inicializa el descargador MCP"""
        home_dir = Path.home()
        self.download_dir = home_dir / "Downloads" / "X_Media_MCP"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    def extract_urls_from_snapshot(self, snapshot_text):
        """
        Extrae URLs de medios de un snapshot de página
        """
        import re
        
        # Buscar URLs de fotos y videos en el texto del snapshot
        photo_pattern = r'/milewskaja_nat/status/\d+/photo/\d+'
        video_pattern = r'/milewskaja_nat/status/\d+/video/\d+'
        
        photo_matches = re.findall(photo_pattern, snapshot_text)
        video_matches = re.findall(video_pattern, snapshot_text)
        
        # Convertir a URLs completas
        base_url = "https://x.com"
        urls = []
        
        for match in photo_matches:
            urls.append(base_url + match)
        
        for match in video_matches:
            urls.append(base_url + match)
        
        return list(set(urls))  # Eliminar duplicados
    
    def download_media_from_urls(self, urls):
        """Descarga medios de una lista de URLs"""
        if not urls:
            print("❌ No hay URLs para descargar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.download_dir / f"milewskaja_nat_mcp_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Procesando {len(urls)} URLs en: {session_dir}")
        
        downloaded = 0
        failed = 0
        extracted_urls = []
        
        for i, page_url in enumerate(urls, 1):
            try:
                print(f"🔍 [{i}/{len(urls)}] Procesando: {page_url}")
                
                # Intentar extraer URL directa de imagen
                if '/photo/' in page_url:
                    direct_url = self._try_extract_image_url(page_url)
                    if direct_url:
                        extracted_urls.append(direct_url)
                        
                        # Descargar imagen
                        if self._download_file(direct_url, session_dir, i):
                            downloaded += 1
                        else:
                            failed += 1
                    else:
                        failed += 1
                        
                elif '/video/' in page_url:
                    print(f"   ⚠️  Video: {page_url} (requiere procesamiento adicional)")
                    failed += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
        
        # Crear log
        log_data = {
            'timestamp': timestamp,
            'method': 'MCP',
            'page_urls': urls,
            'extracted_urls': extracted_urls,
            'downloaded': downloaded,
            'failed': failed
        }
        
        log_file = session_dir / 'mcp_download_log.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Resultado: {downloaded} exitosos, {failed} fallidos")
        print(f"📋 Log: {log_file}")
    
    def _try_extract_image_url(self, page_url):
        """Intenta extraer URL directa de imagen"""
        try:
            # Extraer ID del tweet
            tweet_id = page_url.split('/status/')[1].split('/')[0]
            
            # URLs posibles de alta calidad
            possible_urls = [
                f"https://pbs.twimg.com/media/{tweet_id}?format=jpg&name=large",
                f"https://pbs.twimg.com/media/{tweet_id}?format=jpg&name=orig",
                f"https://pbs.twimg.com/media/{tweet_id}?format=png&name=large",
                f"https://pbs.twimg.com/media/{tweet_id}?format=webp&name=large",
            ]
            
            for url in possible_urls:
                try:
                    response = self.session.head(url, timeout=10)
                    if response.status_code == 200:
                        return url
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"   ⚠️  Error extrayendo URL: {e}")
            return None
    
    def _download_file(self, url, session_dir, index):
        """Descarga un archivo individual"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Generar nombre de archivo
            if 'jpg' in url:
                ext = '.jpg'
            elif 'png' in url:
                ext = '.png'
            elif 'webp' in url:
                ext = '.webp'
            else:
                ext = '.bin'
            
            filename = f"media_{index:04d}{ext}"
            file_path = session_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            size_mb = len(response.content) / (1024 * 1024)
            print(f"   ✅ {filename} ({size_mb:.2f} MB)")
            return True
            
        except Exception as e:
            print(f"   ❌ Error descargando: {e}")
            return False

def demo_mcp_usage():
    """
    Demostración de cómo usar las herramientas MCP
    """
    print("📚 Cómo usar las herramientas MCP de Playwright:")
    print()
    print("1. Navegar a la página:")
    print("   mcp_playwright_browser_navigate('https://x.com/milewskaja_nat/media')")
    print()
    print("2. Tomar snapshot de la página:")
    print("   mcp_playwright_browser_snapshot()")
    print()
    print("3. Hacer scroll para cargar más contenido:")
    print("   mcp_playwright_browser_press_key('End')")
    print()
    print("4. Extraer URLs del snapshot y usar este script para descargar")
    print()
    
    # URLs de ejemplo extraídas del snapshot anterior
    sample_urls = [
        "https://x.com/milewskaja_nat/status/1932808465879032308/photo/1",
        "https://x.com/milewskaja_nat/status/1932443907234693417/photo/1",
        "https://x.com/milewskaja_nat/status/1932086197486022855/photo/1",
        "https://x.com/milewskaja_nat/status/1931714359903858783/photo/1",
        "https://x.com/milewskaja_nat/status/1931363385586671698/photo/1",
    ]
    
    print("🔧 Ejecutando demo con URLs de ejemplo...")
    downloader = MCPXDownloader()
    downloader.download_media_from_urls(sample_urls)

def main():
    """Función principal"""
    print("🎬 MCP X Media Downloader")
    print("=" * 50)
    print()
    
    demo_mcp_usage()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script de descarga rápida con URLs extraídas
Basado en las URLs encontradas durante la exploración con Playwright MCP
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re

# URLs extraídas de la página de medios
MEDIA_URLS = [
    # URLs de fotos
    "https://x.com/milewskaja_nat/status/1932808465879032308/photo/1",
    "https://x.com/milewskaja_nat/status/1932443907234693417/photo/1", 
    "https://x.com/milewskaja_nat/status/1932086197486022855/photo/1",
    "https://x.com/milewskaja_nat/status/1931714359903858783/photo/1",
    "https://x.com/milewskaja_nat/status/1931363385586671698/photo/1",
    "https://x.com/milewskaja_nat/status/1931002252799402243/photo/1",
    "https://x.com/milewskaja_nat/status/1930636377164480756/photo/1",
    "https://x.com/milewskaja_nat/status/1929904913896628560/photo/1",
    "https://x.com/milewskaja_nat/status/1929544352402935813/photo/1",
    "https://x.com/milewskaja_nat/status/1929184320066900211/photo/1",
    "https://x.com/milewskaja_nat/status/1928820034102571012/photo/1",
    "https://x.com/milewskaja_nat/status/1928454814809100686/photo/1",
    "https://x.com/milewskaja_nat/status/1928094140442570974/photo/1",
    "https://x.com/milewskaja_nat/status/1927736111956201794/photo/1",
    "https://x.com/milewskaja_nat/status/1927375046848270435/photo/1",
    "https://x.com/milewskaja_nat/status/1926643410967945226/photo/1",
    "https://x.com/milewskaja_nat/status/1926285968614572148/photo/1",
    "https://x.com/milewskaja_nat/status/1925915409556901946/photo/1",
    "https://x.com/milewskaja_nat/status/1925563238529335431/photo/1",
    "https://x.com/milewskaja_nat/status/1925189948178587765/photo/1",
    "https://x.com/milewskaja_nat/status/1924831341285085300/photo/1",
    "https://x.com/milewskaja_nat/status/1924471298962379044/photo/1",
    "https://x.com/milewskaja_nat/status/1924115995137913130/photo/1",
    "https://x.com/milewskaja_nat/status/1923744480798142774/photo/1",
    "https://x.com/milewskaja_nat/status/1923386501255016475/photo/1",
    "https://x.com/milewskaja_nat/status/1923020446733119825/photo/1",
    "https://x.com/milewskaja_nat/status/1922655358314500305/photo/1",
    "https://x.com/milewskaja_nat/status/1922296508054905200/photo/1",
    "https://x.com/milewskaja_nat/status/1921571648358035887/photo/1",
    "https://x.com/milewskaja_nat/status/1920843701217112104/photo/1",
    "https://x.com/milewskaja_nat/status/1920494780498219262/photo/1",
    "https://x.com/milewskaja_nat/status/1920118646719861118/photo/1",
    "https://x.com/milewskaja_nat/status/1919786884949028984/photo/1",
    "https://x.com/milewskaja_nat/status/1919397114087424166/photo/1",
    "https://x.com/milewskaja_nat/status/1919035480164684212/photo/1",
    "https://x.com/milewskaja_nat/status/1918310051778892208/photo/1",
    "https://x.com/milewskaja_nat/status/1917953693221265755/photo/1",
    "https://x.com/milewskaja_nat/status/1917224269592891847/photo/1",
    "https://x.com/milewskaja_nat/status/1916865955667263607/photo/1",
    "https://x.com/milewskaja_nat/status/1916494076767064524/photo/1",
    "https://x.com/milewskaja_nat/status/1916141950702412288/photo/1",
    "https://x.com/milewskaja_nat/status/1915776336834007349/photo/1",
    "https://x.com/milewskaja_nat/status/1915409021281972344/photo/1",
    "https://x.com/milewskaja_nat/status/1914699259267469691/photo/1",
    "https://x.com/milewskaja_nat/status/1914320807313965566/photo/1",
    "https://x.com/milewskaja_nat/status/1913957325758406791/photo/1",
    "https://x.com/milewskaja_nat/status/1913608001644003451/photo/1",
    "https://x.com/milewskaja_nat/status/1913129156096782783/photo/1",
    
    # URLs de videos
    "https://x.com/milewskaja_nat/status/1930265846783377473/video/1",
    "https://x.com/milewskaja_nat/status/1927003705959678028/video/1",
    "https://x.com/milewskaja_nat/status/1921941880549282067/video/1",
    "https://x.com/milewskaja_nat/status/1921206537864798331/video/1",
    "https://x.com/milewskaja_nat/status/1918669761384161494/video/1",
    "https://x.com/milewskaja_nat/status/1917586166200569917/video/1",
    "https://x.com/milewskaja_nat/status/1915047384612241420/video/1",
]

class QuickXDownloader:
    def __init__(self):
        """Inicializa el descargador rápido"""
        home_dir = Path.home()
        self.download_dir = home_dir / "Downloads" / "X_Media_Quick"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    def convert_to_direct_urls(self, page_urls):
        """
        Convierte URLs de páginas de Twitter a URLs directas
        """
        direct_urls = []
        
        for page_url in page_urls:
            try:
                # Para fotos, intentar generar URL directa
                if '/photo/' in page_url:
                    # Extraer ID del tweet
                    tweet_id = page_url.split('/status/')[1].split('/')[0]
                    # URLs típicas de imágenes de alta calidad en Twitter
                    possible_urls = [
                        f"https://pbs.twimg.com/media/{tweet_id}?format=jpg&name=large",
                        f"https://pbs.twimg.com/media/{tweet_id}?format=png&name=large",
                        f"https://pbs.twimg.com/media/{tweet_id}?format=webp&name=large",
                    ]
                    
                    for url in possible_urls:
                        try:
                            response = self.session.head(url, timeout=10)
                            if response.status_code == 200:
                                direct_urls.append(url)
                                break
                        except:
                            continue
                
                elif '/video/' in page_url:
                    # Los videos son más complejos, necesitan extracción del HTML
                    print(f"⚠️  Video detectado: {page_url} (requiere procesamiento adicional)")
                    
            except Exception as e:
                print(f"⚠️  Error procesando {page_url}: {e}")
                continue
        
        return direct_urls
    
    def download_files(self, urls):
        """Descarga archivos de las URLs directas"""
        if not urls:
            print("❌ No hay URLs para descargar")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.download_dir / f"milewskaja_nat_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(urls)} archivos en: {session_dir}")
        
        downloaded = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            try:
                print(f"⬇️  [{i}/{len(urls)}] {url[:60]}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Generar nombre de archivo
                filename = self._generate_filename(url, i)
                file_path = session_dir / filename
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"✅ {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed += 1
        
        # Crear log
        log_data = {
            'timestamp': timestamp,
            'total_attempted': len(urls),
            'downloaded': downloaded,
            'failed': failed,
            'urls': urls
        }
        
        log_file = session_dir / 'download_log.json'
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Resultado: {downloaded} exitosos, {failed} fallidos")
        print(f"📋 Log: {log_file}")
        return session_dir
    
    def _generate_filename(self, url, index):
        """Genera nombre de archivo"""
        try:
            if 'jpg' in url:
                ext = '.jpg'
            elif 'png' in url:
                ext = '.png'
            elif 'webp' in url:
                ext = '.webp'
            elif 'mp4' in url:
                ext = '.mp4'
            else:
                ext = '.bin'
            
            return f"media_{index:04d}{ext}"
        except:
            return f"media_{index:04d}.bin"

def main():
    """Función principal"""
    print("🎬 Quick X Media Downloader")
    print("=" * 50)
    print(f"📊 URLs de páginas a procesar: {len(MEDIA_URLS)}")
    print()
    
    downloader = QuickXDownloader()
    
    # Convertir URLs de páginas a URLs directas
    print("🔗 Convirtiendo URLs de páginas a URLs directas...")
    direct_urls = downloader.convert_to_direct_urls(MEDIA_URLS)
    
    if direct_urls:
        print(f"✅ URLs directas encontradas: {len(direct_urls)}")
        
        # Descargar archivos
        session_dir = downloader.download_files(direct_urls)
        
        print()
        print("🏁 Descarga completada!")
        print(f"📂 Archivos en: {session_dir}")
    else:
        print("❌ No se pudieron extraer URLs directas")
        print("💡 Prueba ejecutar el script completo: x_media_automation.py")

if __name__ == "__main__":
    main()

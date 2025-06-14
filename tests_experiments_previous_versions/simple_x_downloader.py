#!/usr/bin/env python3
"""
Script simple para descargar medios de X usando las herramientas MCP de Playwright
Autor: Asistente AI
Fecha: 11 de junio de 2025
"""

import os
import requests
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re

class SimpleXDownloader:
    def __init__(self):
        """Inicializa el descargador simple"""
        # Directorio de descarga
        home_dir = Path.home()
        self.download_dir = home_dir / "Downloads" / "X_Media"
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
        # Sesión HTTP
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        print(f"📁 Directorio de descarga: {self.download_dir}")
    
    def download_from_urls(self, media_urls, username="milewskaja_nat"):
        """
        Descarga archivos de una lista de URLs
        
        Args:
            media_urls (list): Lista de URLs de medios
            username (str): Nombre de usuario para el directorio
        """
        if not media_urls:
            print("❌ No hay URLs para descargar")
            return
        
        # Crear directorio de sesión
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.download_dir / f"{username}_{timestamp}"
        session_dir.mkdir(exist_ok=True)
        
        print(f"💾 Descargando {len(media_urls)} archivos en: {session_dir}")
        
        downloaded = 0
        failed = 0
        
        for i, url in enumerate(media_urls, 1):
            try:
                print(f"⬇️  [{i}/{len(media_urls)}] {url[:60]}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Generar nombre de archivo
                filename = self._generate_filename(url, i)
                file_path = session_dir / filename
                
                # Guardar archivo
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                size_mb = len(response.content) / (1024 * 1024)
                print(f"✅ {filename} ({size_mb:.2f} MB)")
                downloaded += 1
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed += 1
        
        print(f"📊 Resultado: {downloaded} exitosos, {failed} fallidos")
        return session_dir
    
    def _generate_filename(self, url, index):
        """Genera nombre de archivo"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                if 'jpg' in url or 'jpeg' in url:
                    ext = '.jpg'
                elif 'png' in url:
                    ext = '.png'
                elif 'webp' in url:
                    ext = '.webp'
                elif 'mp4' in url:
                    ext = '.mp4'
                else:
                    ext = '.bin'
                filename = f"media_{index:04d}{ext}"
            
            return filename
        except:
            return f"media_{index:04d}.bin"

def main():
    """Función principal - usar con URLs extraídas manualmente"""
    print("🎬 Simple X Media Downloader")
    print("=" * 50)
    
    # URLs de ejemplo (debes extraerlas usando Playwright MCP primero)
    sample_urls = [
        # Agrega aquí las URLs que extraigas con las herramientas MCP
    ]
    
    if not sample_urls:
        print("ℹ️  Para usar este script:")
        print("1. Usa las herramientas MCP de Playwright para navegar a la página")
        print("2. Extrae las URLs de medios")
        print("3. Agrega las URLs a la lista sample_urls en este script")
        print("4. Ejecuta el script nuevamente")
        return
    
    downloader = SimpleXDownloader()
    downloader.download_from_urls(sample_urls)

if __name__ == "__main__":
    main()

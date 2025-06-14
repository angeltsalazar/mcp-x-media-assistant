#!/usr/bin/env python3
"""
Prueba rápida de la funcionalidad de nombres únicos sin usar el downloader completo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.download.download_manager import DownloadManager
from modules.download.image_downloader import ImageDownloader
from modules.download.filename_utils import FilenameUtils
import asyncio
import tempfile

async def test_download_with_unique_names():
    """Prueba rápida de descarga con nombres únicos"""
    print("🧪 PROBANDO DESCARGA CON NOMBRES ÚNICOS")
    print("=" * 50)
    
    # Datos de prueba (misma imagen, diferentes status)
    test_data = [
        {
            "url": "https://pbs.twimg.com/media/GiqGYSZXUAAvjFk?format=jpg&name=large",
            "status_id": "1933144407659655592"
        },
        {
            "url": "https://pbs.twimg.com/media/GiqGYSZXUAAvjFk?format=jpg&name=large", 
            "status_id": "1885467152867635251"
        }
    ]
    
    print("📋 URLs de prueba:")
    for i, item in enumerate(test_data, 1):
        filename = FilenameUtils.clean_filename(item["url"], item["status_id"])
        print(f"  {i}. Status: {item['status_id']}")
        print(f"     URL: {item['url']}")
        print(f"     Archivo: {filename}")
        print()
    
    # Crear directorio temporal
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"🗂️  Directorio temporal: {temp_dir}")
        
        # Simular descarga (solo crear archivos vacíos para ver los nombres)
        for item in test_data:
            filename = FilenameUtils.clean_filename(item["url"], item["status_id"])
            file_path = Path(temp_dir) / filename
            
            # Crear archivo vacío
            file_path.touch()
            print(f"✅ Creado: {filename}")
        
        # Listar archivos resultantes
        files = list(Path(temp_dir).glob("*.jpg"))
        print(f"\n📁 Archivos generados ({len(files)}):")
        for file in sorted(files):
            print(f"   📄 {file.name}")
        
        if len(files) == len(test_data):
            print(f"\n✅ ÉXITO: Se generaron {len(files)} archivos únicos")
            print("✅ No hay colisiones de nombres")
        else:
            print(f"\n❌ ERROR: Se esperaban {len(test_data)} archivos, se generaron {len(files)}")

if __name__ == "__main__":
    asyncio.run(test_download_with_unique_names())

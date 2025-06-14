#!/usr/bin/env python3
"""
Test script para la nueva lógica de cache selectivo.
"""
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.utils.cache_manager import CacheManager

def test_selective_cache():
    print("🧪 PROBANDO NUEVA LÓGICA DE CACHE SELECTIVO")
    print("=" * 50)
    
    # Crear instancia
    cache = CacheManager()
    username = 'test_selective'
    
    # Simular datos como los reales
    status_urls = [
        {'url': 'https://x.com/user/status/1001', 'media_type': 'image'},   # Con imagen descargada
        {'url': 'https://x.com/user/status/1002', 'media_type': 'image'},   # Con imagen descargada
        {'url': 'https://x.com/user/status/1003', 'media_type': 'video'},   # Video (siempre procesado)
        {'url': 'https://x.com/user/status/1004', 'media_type': 'image'},   # SIN imagen extraída
        {'url': 'https://x.com/user/status/1005', 'media_type': 'image'},   # SIN imagen extraída
        {'url': 'https://x.com/user/status/1006', 'media_type': 'video'},   # Otro video
    ]
    
    print(f"📊 Total status URLs: {len(status_urls)}")
    videos = [s for s in status_urls if s['media_type'] == 'video']
    images = [s for s in status_urls if s['media_type'] == 'image']
    print(f"🎬 Videos: {len(videos)}")
    print(f"📷 Imágenes: {len(images)}")
    print()
    
    # 1. Simular mapeos válidos (solo algunos tienen imagen extraída exitosamente)
    print("1️⃣ SIMULANDO EXTRACCIÓN DE IMÁGENES...")
    valid_mappings = {
        '1001': 'https://pbs.twimg.com/media/GrUYcfLXgAAuRsX?format=jpg&name=large',
        '1002': 'https://pbs.twimg.com/media/GrPVTI9XAAQvyj9?format=jpg&name=large',
        # 1003 es video (no tiene mapeo de imagen)
        # 1004 y 1005 no tienen mapeo (no se pudo extraer imagen)
        # 1006 es video (no tiene mapeo de imagen)
    }
    
    cache.update_cache_with_new_mappings(username, valid_mappings)
    print(f"✅ Mapeos agregados: {len(valid_mappings)} de {len(images)} imágenes")
    print(f"❌ Sin mapeo: {len(images) - len(valid_mappings)} imágenes")
    print()
    
    # 2. Aplicar nueva lógica de marcado selectivo
    print("2️⃣ APLICANDO LÓGICA SELECTIVA DE MARCADO...")
    cache.mark_all_status_as_processed(username, status_urls)
    print()
    
    # 3. Verificar qué se marcó como procesado
    print("3️⃣ VERIFICANDO RESULTADOS...")
    stats = cache.get_cache_stats(username)
    print(f"📊 Posts marcados como procesados: {stats['total_posts']}")
    print(f"📊 Mapeos de imagen válidos: {stats['total_mappings']}")
    print()
    
    # 4. Simular segunda ejecución - ver qué se considera cacheado vs requiere procesamiento
    print("4️⃣ SIMULANDO SEGUNDA EJECUCIÓN...")
    cached_urls, uncached = cache.get_cached_image_urls(username, status_urls)
    print(f"💾 Cache hit: {len(cached_urls)} imágenes (ya procesadas)")
    print(f"🔄 Cache miss: {len(uncached)} status de imagen requieren procesamiento")
    
    # Mostrar detalles
    if uncached:
        uncached_ids = [cache._extract_status_id(s.get('url', '')) for s in uncached]
        print(f"   🔄 IDs que requieren reprocesamiento: {uncached_ids}")
    
    print()
    print("✅ RESULTADO CORRECTO ESPERADO:")
    print("   - Videos (1003, 1006): marcados como procesados ✓")
    print("   - Imágenes con mapeo (1001, 1002): marcadas como procesadas ✓") 
    print("   - Imágenes sin mapeo (1004, 1005): NO marcadas (permitir reintento) ✓")
    print()
    print("🎯 En la segunda ejecución:")
    print(f"   - Cache hit: {len(valid_mappings)} imágenes (1001, 1002)")
    print(f"   - Cache miss: {len(images) - len(valid_mappings)} imágenes (1004, 1005)")
    print("   - Videos se saltan automáticamente")

if __name__ == "__main__":
    test_selective_cache()

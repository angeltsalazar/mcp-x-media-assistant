#!/usr/bin/env python3
"""
Función mejorada para limpiar URLs de X con mejor manejo de parámetros
"""

import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def clean_image_url_advanced(url):
    """
    Versión avanzada de limpieza de URLs usando urllib.parse
    para manejo más robusto de parámetros
    """
    if not (('pbs.twimg.com' in url or 'video.twimg.com' in url) and 
            'profile_images' not in url and 
            'profile_banners' not in url):
        return None
    
    # Para URLs de video, no modificar mucho
    if 'video.twimg.com' in url:
        return url
    
    # Para imágenes, usar urllib.parse para manejo robusto
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Filtrar parámetros que no queremos
    filtered_params = {}
    for key, values in query_params.items():
        # Saltar parámetros name= con tamaños pequeños
        if key == 'name' and values and values[0] in ['360x360', 'small', 'medium', 'thumb', 'orig', '240x240', '120x120']:
            continue
        # Saltar otros parámetros problemáticos
        if values and values[0] in ['medium', 'small', 'thumb']:
            continue
        # Mantener otros parámetros
        filtered_params[key] = values
    
    # Asegurar que las imágenes tengan format=jpg y name=large
    filtered_params['format'] = ['jpg']
    filtered_params['name'] = ['large']
    
    # Reconstruir la URL
    new_query = urlencode(filtered_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)

def test_advanced_cleaning():
    """Test con la función avanzada"""
    
    test_urls = [
        "https://pbs.twimg.com/media/ABCDEFG?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/HIJKLMN?name=360x360&format=jpg",
        "https://pbs.twimg.com/media/OPQRSTU?format=jpg&name=360x360&other=param",
        "https://pbs.twimg.com/media/VWXYZ12?format=jpg&name=small",
        "https://pbs.twimg.com/media/STUVWXY",
        "https://pbs.twimg.com/media/Z123456?format=jpg&name=large",
        "https://pbs.twimg.com/media/COMPLEX?format=jpg&name=360x360&param1=value1&param2=value2",
        "https://video.twimg.com/amplify_video/ABCDEF?tag=123",
    ]
    
    print("🔬 TESTING ADVANCED URL CLEANING")
    print("="*60)
    
    for i, url in enumerate(test_urls, 1):
        cleaned = clean_image_url_advanced(url)
        print(f"\n{i}. Original:")
        print(f"   {url}")
        print(f"   Cleaned:")
        print(f"   {cleaned}")
        
        if cleaned and 'pbs.twimg.com' in cleaned:
            has_name_large = 'name=large' in cleaned
            has_format_jpg = 'format=jpg' in cleaned
            has_small_name = any(size in cleaned for size in ['360x360', 'small', 'medium', 'thumb', '240x240'])
            
            status = "✅" if (has_name_large and has_format_jpg and not has_small_name) else "❌"
            print(f"   Status: {status}")

if __name__ == "__main__":
    test_advanced_cleaning()

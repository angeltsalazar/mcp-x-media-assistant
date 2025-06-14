#!/usr/bin/env python3
"""
Script para probar el procesamiento de URLs de imágenes
"""

import re

def is_video_url(url):
    """Determinar si una URL es de video usando criterios más precisos"""
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
    
    if '/photo/1/' in url:
        return False
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    url_lower = url.lower()
    if any(ext in url_lower for ext in image_extensions):
        return False
    
    return False

def process_image_url(url):
    """Procesar URL de imagen como lo hace el script principal"""
    print(f"📥 URL original: {url}")
    
    # Filtrar URLs válidas
    if not (('pbs.twimg.com' in url or 'video.twimg.com' in url) and 
            'profile_images' not in url and 
            'profile_banners' not in url):
        print("❌ URL no válida (no es de pbs.twimg.com o es imagen de perfil)")
        return None
    
    # Limpiar parámetros innecesarios pero mantener format y name
    # Eliminar parámetros de tamaño específicos (incluyendo name con tamaños pequeños)
    clean_url = re.sub(r'&?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', '', url)
    clean_url = re.sub(r'\?name=(?:360x360|small|medium|thumb|orig)(?=&|$)', '?', clean_url)
    clean_url = re.sub(r'&?[a-zA-Z0-9_]+=(?:medium|small|thumb)(?=&|$)', '', url)
    
    # Limpiar sintaxis
    clean_url = re.sub(r'\?&', '?', clean_url)  # Corregir ?& a ?
    clean_url = re.sub(r'&+', '&', clean_url)   # Eliminar && múltiples
    clean_url = re.sub(r'\?$', '', clean_url)   # Eliminar ? al final si no hay parámetros
    
    print(f"🧹 Después de limpiar: {clean_url}")
    
    # Asegurar calidad máxima para imágenes
    if 'pbs.twimg.com' in clean_url and not is_video_url(clean_url):
        # Verificar si ya tiene parámetros
        if '?' in clean_url:
            # Ya tiene parámetros, añadir format y name si no existen
            if 'format=' not in clean_url:
                clean_url += '&format=jpg'
                print("➕ Añadido format=jpg")
            # Siempre añadir name=large (ya eliminamos los name pequeños arriba)
            if 'name=' not in clean_url:
                clean_url += '&name=large'
                print("➕ Añadido name=large")
        else:
            # No tiene parámetros, añadir ambos
            clean_url += '?format=jpg&name=large'
            print("➕ Añadido format=jpg&name=large")
    
    print(f"✅ URL final: {clean_url}")
    return clean_url

def test_url_processing():
    """Probar el procesamiento con URLs de ejemplo"""
    print("🧪 Probando procesamiento de URLs de imágenes")
    print("=" * 60)
    
    test_urls = [
        # URL antigua que funcionaba bien
        "https://pbs.twimg.com/media/Go6AVW6W8AAdE8O?format=jpg&name=large",
        
        # URL nueva problemática
        "https://pbs.twimg.com/media/GpJg07XXQAAM08M?name=large",
        
        # URLs problemáticas que mencionas (con name=360x360)
        "https://pbs.twimg.com/media/GpoTbA-XwAAm4-O?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/GpY0bHRWMAAGQk8?format=jpg&name=360x360",
        
        # URL sin parámetros
        "https://pbs.twimg.com/media/GpJg07XXQAAM08M",
        
        # URL con parámetros mixtos
        "https://pbs.twimg.com/media/GpJg07XXQAAM08M?name=medium&other=param",
        
        # URL con name=small
        "https://pbs.twimg.com/media/GpJg07XXQAAM08M?format=jpg&name=small",
        
        # URL de video (no debería procesarse como imagen)
        "https://video.twimg.com/ext_tw_video/123/pu/vid/avc1/filename.mp4",
        
        # URL de imagen de perfil (debería ser filtrada)
        "https://pbs.twimg.com/profile_images/123/avatar.jpg"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. PRUEBA {i}")
        print("-" * 30)
        result = process_image_url(url)
        if result:
            print(f"🎯 Resultado exitoso")
        else:
            print(f"❌ URL filtrada o error")
        print()

if __name__ == "__main__":
    test_url_processing()

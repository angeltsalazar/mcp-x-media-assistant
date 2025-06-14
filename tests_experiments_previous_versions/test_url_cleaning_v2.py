#!/usr/bin/env python3
"""
Test mejorado para verificar el procesamiento de URLs de imágenes
"""

import re

def test_url_cleaning():
    """Test mejorado para la limpieza de URLs"""
    
    test_urls = [
        # URLs problemáticas con name=360x360
        "https://pbs.twimg.com/media/ABCDEFG?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/HIJKLMN?name=360x360&format=jpg",
        "https://pbs.twimg.com/media/OPQRSTU?format=jpg&name=360x360&other=param",
        
        # URLs con otros tamaños pequeños
        "https://pbs.twimg.com/media/VWXYZ12?format=jpg&name=small",
        "https://pbs.twimg.com/media/345ABCD?format=jpg&name=medium",
        "https://pbs.twimg.com/media/EFGHIJK?format=jpg&name=thumb",
        "https://pbs.twimg.com/media/LMNOPQR?format=jpg&name=240x240",
        
        # URLs sin parámetros
        "https://pbs.twimg.com/media/STUVWXY",
        
        # URLs ya con name=large (debe mantenerlas)
        "https://pbs.twimg.com/media/Z123456?format=jpg&name=large",
        
        # URLs complejas con múltiples parámetros
        "https://pbs.twimg.com/media/COMPLEX?format=jpg&name=360x360&param1=value1&param2=value2",
        
        # URLs de video (no deben modificarse mucho)
        "https://video.twimg.com/amplify_video/ABCDEF?tag=123",
    ]
    
    def clean_image_url(url):
        """Nueva lógica de limpieza"""
        # Filtrar URLs válidas
        if not (('pbs.twimg.com' in url or 'video.twimg.com' in url) and 
                'profile_images' not in url and 
                'profile_banners' not in url):
            return None
            
        # Limpiar parámetros de tamaño específicos y problemas comunes
        clean_url = url
        
        # Eliminar todos los parámetros name= con valores pequeños/específicos
        clean_url = re.sub(r'[?&]name=(?:360x360|small|medium|thumb|orig|240x240|120x120)', '', clean_url)
        
        # Eliminar otros parámetros de tamaño innecesarios
        clean_url = re.sub(r'[?&][a-zA-Z0-9_]+=(?:medium|small|thumb)', '', clean_url)
        
        # Limpiar sintaxis problemática iterativamente
        clean_url = re.sub(r'\?&', '?', clean_url)  # Corregir ?& a ?
        clean_url = re.sub(r'&+', '&', clean_url)   # Eliminar && múltiples
        clean_url = re.sub(r'&$', '', clean_url)    # Eliminar & al final
        clean_url = re.sub(r'\?$', '', clean_url)   # Eliminar ? al final si no hay parámetros
        clean_url = re.sub(r'\?&', '?', clean_url)  # Segunda pasada para casos complejos
        
        # Asegurar calidad máxima para imágenes
        if 'pbs.twimg.com' in clean_url and 'video' not in clean_url.lower():
            # Eliminar cualquier parámetro name= restante (por si acaso)
            clean_url = re.sub(r'[?&]name=[^&]*', '', clean_url)
            
            # Limpiar sintaxis otra vez después de eliminar name=
            clean_url = re.sub(r'\?&', '?', clean_url)
            clean_url = re.sub(r'&+', '&', clean_url)
            clean_url = re.sub(r'&$', '', clean_url)
            clean_url = re.sub(r'\?$', '', clean_url)
            
            # Verificar si ya tiene parámetros
            if '?' in clean_url:
                # Ya tiene parámetros, asegurar format=jpg y name=large
                if 'format=' not in clean_url:
                    clean_url += '&format=jpg'
                # Siempre añadir name=large
                clean_url += '&name=large'
            else:
                # No tiene parámetros, añadir ambos
                clean_url += '?format=jpg&name=large'
        
        return clean_url
    
    print("🧪 TESTING URL CLEANING LOGIC")
    print("="*60)
    
    for i, url in enumerate(test_urls, 1):
        cleaned = clean_image_url(url)
        print(f"\n{i}. Original:")
        print(f"   {url}")
        print(f"   Cleaned:")
        print(f"   {cleaned}")
        
        # Verificar resultados esperados
        if cleaned and 'pbs.twimg.com' in cleaned:
            has_name_large = 'name=large' in cleaned
            has_format_jpg = 'format=jpg' in cleaned
            has_small_name = any(size in cleaned for size in ['360x360', 'small', 'medium', 'thumb', '240x240'])
            
            status = "✅" if (has_name_large and has_format_jpg and not has_small_name) else "❌"
            print(f"   Status: {status}")
            if not has_name_large:
                print(f"   ⚠️  Missing name=large")
            if not has_format_jpg:
                print(f"   ⚠️  Missing format=jpg")
            if has_small_name:
                print(f"   ⚠️  Still has small size parameter")
    
    print("\n" + "="*60)
    print("🔍 Test completed!")

if __name__ == "__main__":
    test_url_cleaning()

"""
Módulo con utilidades para el manejo y manipulación de URLs.
"""
import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

class URLUtils:
    """
    Proporciona métodos estáticos para operaciones comunes con URLs.
    """

    @staticmethod
    def extract_status_id_from_url(url: str) -> str | None:
        """Extraer el ID del status/tweet desde la URL."""
        try:
            match = re.search(r'/status/(\d+)', url)
            if match:
                return match.group(1)
            
            if 'status' in url:
                match = re.search(r'status[=/](\d+)', url)
                if match:
                    return match.group(1)
            
            return None
        except Exception:
            return None

    @staticmethod
    def clean_image_url_robust(url: str) -> str | None:
        """
        Limpieza robusta de URLs usando urllib.parse para mejor manejo de parámetros.
        Implementación idéntica a la versión v0.1.5 para mantener compatibilidad.
        """
        if not (('pbs.twimg.com' in url or 'video.twimg.com' in url) and 
                'profile_images' not in url and 
                'profile_banners' not in url):
            return None
        
        # Para URLs de video, no modificar mucho
        if 'video.twimg.com' in url or URLUtils._is_video_url(url):
            return url
        
        try:
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
                # Mantener otros parámetros válidos
                if key not in ['name', 'format']:  # Estos los vamos a establecer explícitamente
                    filtered_params[key] = values
            
            # Asegurar que las imágenes tengan format=jpg y name=large
            filtered_params['format'] = ['jpg']
            filtered_params['name'] = ['large']
            
            # Reconstruir la URL
            new_query = urlencode(filtered_params, doseq=True)
            new_parsed = parsed._replace(query=new_query)
            
            return urlunparse(new_parsed)
            
        except Exception as e:
            # Fallback a la URL original
            return url

    @staticmethod
    def _is_video_url(url: str) -> bool:
        """Determinar si una URL es de video usando criterios específicos."""
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
        
        # Si contiene /photo/1/ es definitivamente imagen
        if '/photo/1/' in url:
            return False
        
        # Extensiones de imagen conocidas
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        url_lower = url.lower()
        if any(ext in url_lower for ext in image_extensions):
            return False
        
        return False

    @staticmethod
    def build_profile_url(username: str) -> str:
        """Construye la URL del perfil de medios de un usuario."""
        return f"https://x.com/{username}/media"

    @staticmethod
    def is_valid_media_url(url: str) -> bool:
        """Verifica si una URL parece ser una URL de medios válida de Twitter."""
        return 'pbs.twimg.com' in url or 'video.twimg.com' in url
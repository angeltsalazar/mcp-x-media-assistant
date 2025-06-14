"""
Módulo para la clasificación de medios (imagen vs. video).
"""
import re
from ..config.constants import VIDEO_PATTERNS, IMAGE_EXTENSIONS

class MediaClassifier:
    """
    Proporciona métodos estáticos para clasificar URLs de medios.
    """

    @staticmethod
    def is_video_url(url: str) -> bool:
        """
        Determina si una URL corresponde a un video basándose en una lista
        de patrones de expresiones regulares.
        """
        # Si contiene /photo/1/, es definitivamente una imagen.
        if '/photo/1/' in url:
            return False
        
        # Comprobar si coincide con algún patrón de video.
        for pattern in VIDEO_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        return False

    @staticmethod
    def classify_media_type(url: str) -> str:
        """Clasifica una URL como 'video', 'image' o 'unknown'."""
        if MediaClassifier.is_video_url(url):
            return "video"
        
        # Comprobar extensiones de imagen conocidas.
        url_lower = url.lower()
        if any(ext in url_lower for ext in IMAGE_EXTENSIONS):
            return "image"
            
        # Si no es video y no tiene extensión de imagen, asumir imagen por defecto
        # en el contexto de la sección de "Media".
        if 'pbs.twimg.com' in url:
            return "image"
            
        return "unknown"
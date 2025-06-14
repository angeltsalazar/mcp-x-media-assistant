"""
Módulo con utilidades para la creación y limpieza de nombres de archivo.
"""
import re
import os
from datetime import datetime
from urllib.parse import urlparse

class FilenameUtils:
    """
    Proporciona métodos estáticos para generar nombres de archivo limpios y seguros.
    """

    @staticmethod
    def clean_filename(url: str, status_id: str = None) -> str:
        """
        Crea un nombre de archivo limpio desde una URL, preservando el nombre original de Twitter.
        Si se proporciona status_id, se usa como prefijo para evitar colisiones de nombres.
        
        Args:
            url: URL de la imagen
            status_id: ID del status de Twitter (opcional, recomendado para evitar colisiones)
            
        Returns:
            Nombre de archivo en formato: {status_id}-{nombre_original}.jpg
        """
        try:
            parsed = urlparse(url)
            original_name = None
            
            # Para URLs de Twitter, extraer el nombre real del path
            if 'pbs.twimg.com' in url:
                # El path es algo como /media/GpEIoIaXoAAj_ZE
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 2 and path_parts[0] == 'media':
                    original_name = path_parts[1]  # Obtener GpEIoIaXoAAj_ZE
                    
                    # Limpiar caracteres problemáticos pero conservar el nombre
                    clean_name = re.sub(r'[<>:"/\\|?*]', '_', original_name)
                    
                    # Si tenemos status_id, usarlo como prefijo
                    if status_id:
                        clean_name = f"{status_id}-{clean_name}"
                    
                    # Asegurar extensión .jpg
                    if not clean_name.lower().endswith('.jpg'):
                        clean_name += '.jpg'
                    
                    return clean_name
            
            # Fallback para otros tipos de URLs
            filename = os.path.basename(parsed.path)
            
            if not filename or '.' not in filename:
                # Usar timestamp como último recurso
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                base_name = f"image_{timestamp}"
                # Agregar status_id si está disponible
                if status_id:
                    base_name = f"{status_id}-{base_name}"
                filename = f"{base_name}.jpg"
            else:
                # Si tenemos status_id, agregarlo como prefijo
                if status_id:
                    name_part = os.path.splitext(filename)[0]
                    ext_part = os.path.splitext(filename)[1] or '.jpg'
                    filename = f"{status_id}-{name_part}{ext_part}"
            
            # Limpiar caracteres problemáticos
            filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
            
            return filename
        except Exception as e:
            # En caso de error, usar timestamp como fallback
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            base_name = f"image_{timestamp}"
            if status_id:
                base_name = f"{status_id}-{base_name}"
            return f"{base_name}.jpg"

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Elimina caracteres no válidos de un nombre de archivo.
        """
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    @staticmethod
    def generate_fallback_filename() -> str:
        """
        Genera un nombre de archivo único basado en la fecha y hora actuales.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"image_{timestamp}.jpg"
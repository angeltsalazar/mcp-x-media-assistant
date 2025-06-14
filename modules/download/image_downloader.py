"""
Módulo para la descarga de una imagen individual.
"""
import requests
from pathlib import Path
from ..utils.logging import Logger
from ..core.exceptions import DownloadException

class ImageDownloader:
    """
    Gestiona la descarga de una única imagen desde una URL.
    """
    def __init__(self, session: requests.Session, download_dir: Path):
        self.session = session
        self.download_dir = download_dir

    def download_image(self, url: str, filename: str) -> int:
        """
        Descarga una imagen y la guarda en el directorio de descargas.
        Devuelve el tamaño del archivo en bytes.
        """
        try:
            file_path = self.download_dir / filename
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            size_bytes = len(response.content)
            size_mb = size_bytes / (1024 * 1024)
            Logger.success(f"'{filename}' descargado ({size_mb:.2f} MB)")
            
            return size_bytes
            
        except requests.exceptions.RequestException as e:
            raise DownloadException(f"Error de red al descargar {filename}: {e}")
        except IOError as e:
            raise DownloadException(f"Error de disco al guardar {filename}: {e}")
        except Exception as e:
            raise DownloadException(f"Error inesperado al descargar {filename}: {e}")
"""
Módulo con utilidades para el manejo de archivos y directorios.
"""
import json
from pathlib import Path
from datetime import datetime

class FileUtils:
    """
    Proporciona métodos estáticos para operaciones comunes de sistema de archivos.
    """

    @staticmethod
    def ensure_directory_exists(path: Path):
        """Asegura que un directorio exista, creándolo si es necesario."""
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_size_mb(filepath: Path) -> float:
        """Obtiene el tamaño de un archivo en megabytes."""
        if not filepath.exists():
            return 0.0
        return filepath.stat().st_size / (1024 * 1024)

    @staticmethod
    async def save_media_json(media_data: list, base_dir: Path, profile_url: str) -> str:
        """
        Guarda los datos de medios extraídos en un archivo JSON.
        Este es el archivo principal de resultados para el usuario.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"x_media_extraction_{timestamp}.json"
            file_path = base_dir / filename
            
            FileUtils.ensure_directory_exists(base_dir)

            videos = [item for item in media_data if item.get('media_type') == 'video']
            images = [item for item in media_data if item.get('media_type') == 'image']
            
            data_to_save = {
                "extraction_date": datetime.now().isoformat(),
                "profile_url": profile_url,
                "total_media_found": len(media_data),
                "video_count": len(videos),
                "image_count": len(images),
                "media_breakdown": {
                    "videos": videos,
                    "images": images
                },
                "extractor_version": "edge_x_downloader_modular_v1.0"
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Datos de medios guardados en: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"⚠️  Error al guardar JSON de medios: {e}")
            return None

    @staticmethod
    async def save_extraction_log(log_content: dict, base_dir: Path) -> str:
        """
        Guarda un log detallado de la sesión para depuración.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_dir = base_dir / f"session_logs"
            FileUtils.ensure_directory_exists(session_dir)
            
            log_file = session_dir / f"session_log_{timestamp}.json"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_content, f, indent=2, ensure_ascii=False)
            
            print(f"📋 Log de sesión guardado: {log_file}")
            return str(log_file)
            
        except Exception as e:
            print(f"⚠️  No se pudo crear el log de sesión: {e}")
            return None
"""
Módulo para gestionar cache de posts procesados por usuario.
Evita reprocesar URLs ya conocidas para optimizar el rendimiento.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class CacheManager:
    """
    Gestiona el cache de posts procesados para cada usuario,
    permitiendo evitar reprocesamiento innecesario.
    """
    
    def __init__(self, cache_dir: str = None):
        if cache_dir is None:
            # Crear directorio de cache en el directorio del proyecto
            self.cache_dir = Path(__file__).parent.parent.parent / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_expiry_days = 7  # Cache válido por 7 días
        
        # 🔄 Migrar caches antiguos del directorio raíz
        self._migrate_old_caches()
    
    def get_cache_file_path(self, username: str) -> Path:
        """Obtiene la ruta del archivo de cache para un usuario."""
        return self.cache_dir / f"{username}_processed_posts.json"
    
    def load_user_cache(self, username: str) -> Dict:
        """Carga el cache de posts procesados para un usuario."""
        cache_file = self.get_cache_file_path(username)
        
        if not cache_file.exists():
            return {
                "last_updated": None,
                "processed_posts": {},
                "status_to_image_mapping": {}
            }
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar si el cache ha expirado
            if self._is_cache_expired(cache_data.get("last_updated")):
                print(f"💡 Cache de {username} expirado, se regenerará")
                return {
                    "last_updated": None,
                    "processed_posts": {},
                    "status_to_image_mapping": {}
                }
            
            return cache_data
        except (json.JSONDecodeError, KeyError) as e:
            print(f"⚠️  Error leyendo cache de {username}: {e}")
            return {
                "last_updated": None,
                "processed_posts": {},
                "status_to_image_mapping": {}
            }
    
    def save_user_cache(self, username: str, processed_posts: Dict, status_to_image_mapping: Dict):
        """Guarda el cache de posts procesados para un usuario."""
        cache_file = self.get_cache_file_path(username)
        
        cache_data = {
            "last_updated": datetime.now().isoformat(),
            "processed_posts": processed_posts,
            "status_to_image_mapping": status_to_image_mapping
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cache de {username} guardado: {len(processed_posts)} posts procesados")
        except Exception as e:
            print(f"⚠️  Error guardando cache de {username}: {e}")
    
    def get_cached_image_urls(self, username: str, status_urls: List[Dict]) -> tuple[List[str], List[Dict]]:
        """
        Obtiene URLs de imágenes desde cache y devuelve las URLs no cacheadas.
        
        Returns:
            tuple: (cached_image_urls, uncached_status_urls)
        """
        cache_data = self.load_user_cache(username)
        cached_mapping = cache_data.get("status_to_image_mapping", {})
        
        cached_image_urls = []
        uncached_status_urls = []
        
        for status_item in status_urls:
            if status_item.get('media_type') != 'image':
                continue
                
            status_url = status_item.get('url', '')
            status_id = self._extract_status_id(status_url)
            
            if status_id in cached_mapping:
                # Usar imagen cacheada
                cached_image_url = cached_mapping[status_id]
                if cached_image_url not in cached_image_urls:
                    cached_image_urls.append(cached_image_url)
                    print(f"   💾 Imagen cacheada: {status_id} -> {cached_image_url}")
            else:
                # Necesita procesamiento
                uncached_status_urls.append(status_item)
        
        print(f"💾 Cache hit: {len(cached_image_urls)} imágenes cacheadas")
        print(f"🔄 Cache miss: {len(uncached_status_urls)} status requieren procesamiento")
        
        return cached_image_urls, uncached_status_urls

    def get_url_to_status_mapping(self, username: str, image_urls: List[str]) -> Dict[str, str]:
        """
        Obtiene el mapeo de URLs de imágenes a status_ids desde cache.
        
        Args:
            username: Nombre del usuario
            image_urls: Lista de URLs de imágenes
            
        Returns:
            Diccionario {url: status_id}
        """
        cache_data = self.load_user_cache(username)
        cached_mapping = cache_data.get("status_to_image_mapping", {})
        
        url_to_status = {}
        for status_id, image_url in cached_mapping.items():
            if image_url in image_urls:
                url_to_status[image_url] = status_id
                
        return url_to_status
    
    def update_cache_with_new_mappings(self, username: str, new_mappings: Dict[str, str]):
        """
        Actualiza el cache con nuevos mapeos de status_id -> image_url.
        MEJORADO: Evita sobrescribir mapeos existentes incorrectamente.
        """
        cache_data = self.load_user_cache(username)
        
        # Verificar mapeos existentes antes de actualizar
        existing_mappings = cache_data.get("status_to_image_mapping", {})
        conflicting_mappings = 0
        
        # Actualizar mapeos solo si son válidos
        for status_id, image_url in new_mappings.items():
            if status_id in existing_mappings:
                existing_url = existing_mappings[status_id]
                if existing_url != image_url:
                    print(f"⚠️  Conflicto de mapeo para {status_id}: {existing_url} vs {image_url}")
                    conflicting_mappings += 1
                    # Mantener el mapeo existente para evitar corrupción
                    continue
            
            # Solo añadir si es un mapeo nuevo y válido
            if image_url and image_url.strip():
                cache_data["status_to_image_mapping"][status_id] = image_url
                
                # Actualizar posts procesados (para compatibilidad)
                cache_data["processed_posts"][status_id] = {
                    "processed_at": datetime.now().isoformat(),
                    "image_url": image_url
                }
        
        if conflicting_mappings > 0:
            print(f"⚠️  Se encontraron {conflicting_mappings} conflictos de mapeo - manteniendo mapeos existentes")
        
        # Guardar cache actualizado
        self.save_user_cache(
            username, 
            cache_data["processed_posts"], 
            cache_data["status_to_image_mapping"]
        )

    def is_status_cached(self, username: str, status_id: str) -> bool:
        """Verifica si un status ID específico ya está en cache (procesado)."""
        cache_data = self.load_user_cache(username)
        return status_id in cache_data.get("processed_posts", {})
    
    def mark_downloaded_images(self, username: str, downloaded_stats: dict, download_dir: str):
        """
        Marca en cache solo las imágenes que fueron descargadas exitosamente.
        Esto asegura que solo se consideren 'procesadas' las que realmente tenemos.
        """
        from pathlib import Path
        
        cache_data = self.load_user_cache(username)
        current_time = datetime.now().isoformat()
        
        # Obtener lista de archivos exitosamente descargados
        successful_downloads = downloaded_stats.get('successful_downloads', [])
        
        marked_count = 0
        for status_id, image_url in cache_data["status_to_image_mapping"].items():
            if image_url:
                # Extraer nombre original de la imagen
                filename = self._extract_original_filename(image_url)
                file_path = Path(download_dir) / f"{filename}.jpg"
                
                # Verificar si el archivo existe
                if file_path.exists():
                    # Marcar como procesado exitosamente
                    cache_data["processed_posts"][status_id] = {
                        "processed_at": current_time,
                        "media_type": "image",
                        "image_url": image_url,
                        "downloaded": True,
                        "filename": f"{filename}.jpg"
                    }
                    marked_count += 1
        
        if marked_count > 0:
            self.save_user_cache(
                username, 
                cache_data["processed_posts"], 
                cache_data["status_to_image_mapping"]
            )
            print(f"📁 {marked_count} imágenes descargadas marcadas como procesadas en cache")
    
    def _extract_original_filename(self, image_url: str) -> str:
        """Extrae el nombre original del archivo de una URL de imagen de Twitter."""
        try:
            # Ejemplo: https://pbs.twimg.com/media/GrUYcfLXgAAuRsX?format=jpg&name=large
            # -> GrUYcfLXgAAuRsX
            if 'pbs.twimg.com/media/' in image_url:
                filename_part = image_url.split('pbs.twimg.com/media/')[-1]
                filename = filename_part.split('?')[0]  # Remover parámetros
                return filename
            return "unknown"
        except Exception:
            return "unknown"
    
    def mark_all_status_as_processed(self, username: str, all_status_urls: list[dict]):
        """
        Marca SOLO los status que realmente deben considerarse procesados:
        1. Videos (ya identificados, no necesitan reprocesamiento)
        2. Imágenes con mapeo válido (que tienen URL de imagen extraída)
        
        Los status sin imagen extraída NO se marcan como procesados para permitir
        reintento en futuras ejecuciones.
        """
        cache_data = self.load_user_cache(username)
        current_time = datetime.now().isoformat()
        
        processed_count = 0
        for status_item in all_status_urls:
            status_id = self._extract_status_id(status_item.get('url', ''))
            if status_id and status_id not in cache_data["processed_posts"]:
                
                media_type = status_item.get('media_type', '')
                
                # Marcar videos como procesados (ya identificados correctamente)
                if media_type == 'video':
                    cache_data["processed_posts"][status_id] = {
                        "processed_at": current_time,
                        "media_type": "video",
                        "image_url": None
                    }
                    processed_count += 1
                    
                # Marcar imágenes solo si tienen mapeo válido en cache
                elif media_type == 'image' and status_id in cache_data["status_to_image_mapping"]:
                    image_url = cache_data["status_to_image_mapping"][status_id]
                    cache_data["processed_posts"][status_id] = {
                        "processed_at": current_time,
                        "media_type": "image",
                        "image_url": image_url
                    }
                    processed_count += 1
                
                # NO marcar imágenes sin mapeo válido - permitir reintento
        
        if processed_count > 0:
            # Guardar cache actualizado
            self.save_user_cache(
                username, 
                cache_data["processed_posts"], 
                cache_data["status_to_image_mapping"]
            )
            print(f"📝 {processed_count} status marcados como realmente procesados (videos + imágenes extraídas)")
        else:
            print("📝 No hay nuevos status para marcar como procesados")
    
    def _is_cache_expired(self, last_updated_str: Optional[str]) -> bool:
        """Verifica si el cache ha expirado."""
        if not last_updated_str:
            return True
        
        try:
            last_updated = datetime.fromisoformat(last_updated_str)
            expiry_date = last_updated + timedelta(days=self.cache_expiry_days)
            return datetime.now() > expiry_date
        except ValueError:
            return True
    
    def _extract_status_id(self, status_url: str) -> str:
        """Extrae el ID del status desde la URL."""
        # Ejemplo: https://x.com/username/status/1234567890 -> 1234567890
        try:
            return status_url.split('/status/')[-1].split('?')[0].split('/')[0]
        except Exception:
            return ""
    
    def clear_user_cache(self, username: str):
        """Limpia el cache de un usuario específico."""
        cache_file = self.get_cache_file_path(username)
        if cache_file.exists():
            cache_file.unlink()
            print(f"🗑️  Cache de {username} eliminado")
    
    def get_cache_stats(self, username: str) -> Dict:
        """Obtiene estadísticas del cache de un usuario."""
        cache_data = self.load_user_cache(username)
        
        return {
            "last_updated": cache_data.get("last_updated"),
            "total_posts": len(cache_data.get("processed_posts", {})),
            "total_mappings": len(cache_data.get("status_to_image_mapping", {})),
            "cache_file": str(self.get_cache_file_path(username)),
            "is_expired": self._is_cache_expired(cache_data.get("last_updated"))
        }
    
    def _migrate_old_caches(self):
        """Migra caches antiguos del directorio raíz al directorio cache/"""
        project_root = Path(__file__).parent.parent.parent
        old_cache_pattern = project_root.glob("cache_*_posts.json")
        
        migrated_count = 0
        for old_cache_file in old_cache_pattern:
            try:
                # Extraer username del nombre del archivo
                # cache_username_posts.json -> username
                filename = old_cache_file.name
                if filename.startswith("cache_") and filename.endswith("_posts.json"):
                    username = filename[6:-11]  # Remover "cache_" y "_posts.json"
                    
                    new_cache_file = self.cache_dir / f"{username}_processed_posts.json"
                    
                    if not new_cache_file.exists():
                        # Cargar datos del archivo antiguo
                        with open(old_cache_file, 'r', encoding='utf-8') as f:
                            old_data = json.load(f)
                        
                        # Convertir al nuevo formato
                        new_data = {
                            "last_updated": datetime.now().isoformat(),
                            "processed_posts": {},
                            "status_to_image_mapping": old_data  # Los datos antiguos van aquí
                        }
                        
                        # Guardar en el nuevo formato
                        with open(new_cache_file, 'w', encoding='utf-8') as f:
                            json.dump(new_data, f, indent=2, ensure_ascii=False)
                        
                        # Eliminar archivo antiguo
                        old_cache_file.unlink()
                        
                        migrated_count += 1
                        print(f"🔄 Cache migrado: {old_cache_file.name} → cache/{username}_processed_posts.json")
                    
            except Exception as e:
                print(f"⚠️  Error migrando {old_cache_file.name}: {e}")
        
        if migrated_count > 0:
            print(f"✅ {migrated_count} caches migrados al directorio cache/")
        elif migrated_count == 0 and any(project_root.glob("cache_*_posts.json")):
            print("💡 Algunos archivos de cache antiguo no pudieron migrarse automáticamente")
    
    def clean_conflicting_mappings(self, username: str) -> int:
        """
        Limpia mapeos conflictivos en el cache donde múltiples status_ids apuntan a la misma imagen.
        Returns: número de conflictos limpiados
        """
        cache_data = self.load_user_cache(username)
        mapping = cache_data.get("status_to_image_mapping", {})
        processed_posts = cache_data.get("processed_posts", {})
        
        if not mapping:
            return 0
        
        # Crear mapeo inverso para detectar conflictos
        image_to_statuses = {}
        for status_id, image_url in mapping.items():
            if image_url not in image_to_statuses:
                image_to_statuses[image_url] = []
            image_to_statuses[image_url].append(status_id)
        
        # Encontrar imágenes con múltiples status_ids (conflictos)
        conflicts_cleaned = 0
        for image_url, status_list in image_to_statuses.items():
            if len(status_list) > 1:
                print(f"🔍 Imagen {image_url} mapeada a {len(status_list)} status diferentes")
                
                # Mantener solo el primer mapeo (más antiguo)
                primary_status = status_list[0]
                for duplicate_status in status_list[1:]:
                    print(f"   🗑️  Eliminando mapeo duplicado: {duplicate_status}")
                    mapping.pop(duplicate_status, None)
                    processed_posts.pop(duplicate_status, None)
                    conflicts_cleaned += 1
        
        if conflicts_cleaned > 0:
            print(f"🧹 Se limpiaron {conflicts_cleaned} mapeos conflictivos")
            # Guardar cache limpio
            self.save_user_cache(username, processed_posts, mapping)
        
        return conflicts_cleaned

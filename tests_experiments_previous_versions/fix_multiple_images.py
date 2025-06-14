#!/usr/bin/env python3
"""
Herramienta para diagnosticar y reparar problemas de mapeo de múltiples imágenes.
Este script identifica y corrige casos donde un status_id se asigna incorrectamente 
a múltiples imágenes que no le pertenecen.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.utils.cache_manager import CacheManager
from modules.utils.logging import Logger

class MultipleImagesFixer:
    """
    Diagnostica y repara problemas de mapeo de múltiples imágenes.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        
    def diagnose_cache_problems(self, username: str) -> Dict:
        """
        Diagnostica problemas en el cache de un usuario.
        
        Returns:
            Dict con información sobre problemas encontrados
        """
        Logger.info(f"🔍 Diagnosticando cache de {username}...")
        
        cache_data = self.cache_manager.load_user_cache(username)
        processed_posts = cache_data.get("processed_posts", {})
        status_to_image_mapping = cache_data.get("status_to_image_mapping", {})
        
        problems = {
            "duplicate_mappings": {},  # status_id: [list of images]
            "missing_mappings": [],    # status_ids without image mapping
            "orphaned_mappings": [],   # mappings without processed_posts entry
            "inconsistent_data": []    # processed_posts vs mapping inconsistencies
        }
        
        # 1. Buscar mapeos duplicados (un status_id mapeado a múltiples imágenes)
        # NOTA: Esto debería ser normal para carruseles, pero verificamos anomalías
        status_image_count = {}
        for status_id, image_url in status_to_image_mapping.items():
            if status_id not in status_image_count:
                status_image_count[status_id] = []
            status_image_count[status_id].append(image_url)
        
        for status_id, images in status_image_count.items():
            if len(images) > 1:
                problems["duplicate_mappings"][status_id] = images
        
        # 2. Buscar status sin mapeo de imagen (tipo 'image' pero sin URL)
        for status_id, post_data in processed_posts.items():
            if post_data.get("media_type") == "image":
                if status_id not in status_to_image_mapping:
                    problems["missing_mappings"].append(status_id)
        
        # 3. Buscar mapeos huérfanos (en mapping pero no en processed_posts)
        for status_id in status_to_image_mapping:
            if status_id not in processed_posts:
                problems["orphaned_mappings"].append(status_id)
        
        # 4. Buscar inconsistencias entre processed_posts y mapping
        for status_id, post_data in processed_posts.items():
            if post_data.get("media_type") == "image":
                post_image_url = post_data.get("image_url")
                mapping_image_url = status_to_image_mapping.get(status_id)
                
                if post_image_url != mapping_image_url:
                    problems["inconsistent_data"].append({
                        "status_id": status_id,
                        "post_image_url": post_image_url,
                        "mapping_image_url": mapping_image_url
                    })
        
        # Mostrar diagnóstico
        Logger.info(f"📊 DIAGNÓSTICO COMPLETO para {username}:")
        Logger.info(f"   📝 Total processed_posts: {len(processed_posts)}")
        Logger.info(f"   🔗 Total status_to_image_mapping: {len(status_to_image_mapping)}")
        Logger.info(f"   ⚠️  Mapeos duplicados: {len(problems['duplicate_mappings'])}")
        Logger.info(f"   ❌ Mapeos faltantes: {len(problems['missing_mappings'])}")
        Logger.info(f"   👻 Mapeos huérfanos: {len(problems['orphaned_mappings'])}")
        Logger.info(f"   🔄 Datos inconsistentes: {len(problems['inconsistent_data'])}")
        
        # Detalles específicos del problema reportado
        target_status_id = "1933144407659655592"
        if target_status_id in problems["duplicate_mappings"]:
            Logger.warning(f"🎯 PROBLEMA ESPECÍFICO ENCONTRADO:")
            Logger.warning(f"   Status ID: {target_status_id}")
            Logger.warning(f"   Imágenes mapeadas: {len(problems['duplicate_mappings'][target_status_id])}")
            for i, img_url in enumerate(problems['duplicate_mappings'][target_status_id], 1):
                Logger.warning(f"   {i}. {img_url}")
        elif target_status_id in status_to_image_mapping:
            Logger.info(f"🎯 Status ID {target_status_id} encontrado con mapeo único:")
            Logger.info(f"   Imagen: {status_to_image_mapping[target_status_id]}")
        else:
            Logger.warning(f"🎯 Status ID {target_status_id} NO encontrado en mapeos")
        
        return problems
    
    def fix_cache_problems(self, username: str, problems: Dict) -> bool:
        """
        Repara problemas encontrados en el cache.
        
        Args:
            username: Nombre del usuario
            problems: Problemas encontrados por diagnose_cache_problems
        
        Returns:
            True si se realizaron reparaciones
        """
        Logger.info(f"🔧 Iniciando reparación de cache para {username}...")
        
        cache_data = self.cache_manager.load_user_cache(username)
        processed_posts = cache_data.get("processed_posts", {})
        status_to_image_mapping = cache_data.get("status_to_image_mapping", {})
        
        changes_made = False
        
        # 1. Corregir mapeos huérfanos
        if problems["orphaned_mappings"]:
            Logger.info(f"🔧 Corrigiendo {len(problems['orphaned_mappings'])} mapeos huérfanos...")
            for status_id in problems["orphaned_mappings"]:
                image_url = status_to_image_mapping.get(status_id)
                processed_posts[status_id] = {
                    "processed_at": datetime.now().isoformat(),
                    "media_type": "image",
                    "image_url": image_url
                }
                changes_made = True
                Logger.info(f"   ✅ Agregado processed_post para {status_id}")
        
        # 2. Corregir datos inconsistentes
        if problems["inconsistent_data"]:
            Logger.info(f"🔧 Corrigiendo {len(problems['inconsistent_data'])} inconsistencias...")
            for inconsistency in problems["inconsistent_data"]:
                status_id = inconsistency["status_id"]
                mapping_url = inconsistency["mapping_image_url"]
                
                # Dar prioridad al mapeo (más confiable)
                if mapping_url:
                    processed_posts[status_id]["image_url"] = mapping_url
                    changes_made = True
                    Logger.info(f"   ✅ Corregida URL para {status_id}")
        
        # 3. Limpiar mapeos problemáticos del status_id específico
        target_status_id = "1933144407659655592"
        if target_status_id in problems["duplicate_mappings"]:
            Logger.warning(f"🎯 Corrigiendo mapeo problemático para {target_status_id}...")
            
            # Mantener solo la primera imagen (la correcta)
            duplicate_images = problems["duplicate_mappings"][target_status_id]
            if duplicate_images:
                correct_image = duplicate_images[0]  # Asumir que la primera es correcta
                status_to_image_mapping[target_status_id] = correct_image
                
                # Actualizar processed_posts
                if target_status_id in processed_posts:
                    processed_posts[target_status_id]["image_url"] = correct_image
                
                Logger.info(f"   ✅ Mantenida imagen correcta: {correct_image}")
                Logger.info(f"   🗑️  Removidas {len(duplicate_images) - 1} imágenes duplicadas")
                changes_made = True
        
        # Guardar cambios si se hicieron
        if changes_made:
            self.cache_manager.save_user_cache(username, processed_posts, status_to_image_mapping)
            Logger.success(f"✅ Cache de {username} reparado exitosamente")
            return True
        else:
            Logger.info(f"💡 No se requirieron reparaciones para {username}")
            return False
    
    def create_backup_cache(self, username: str) -> str:
        """
        Crea una copia de seguridad del cache antes de repararlo.
        
        Returns:
            Ruta del archivo de backup
        """
        cache_file = self.cache_manager.get_cache_file_path(username)
        if not cache_file.exists():
            Logger.warning(f"⚠️  No existe cache para {username}")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = cache_file.parent / f"{username}_backup_{timestamp}.json"
        
        try:
            # Copiar archivo
            import shutil
            shutil.copy2(cache_file, backup_file)
            Logger.success(f"💾 Backup creado: {backup_file}")
            return str(backup_file)
        except Exception as e:
            Logger.error(f"❌ Error creando backup: {e}")
            return ""
    
    def analyze_filename_conflicts(self, download_dir: str) -> Dict:
        """
        Analiza conflictos en nombres de archivo en el directorio de descargas.
        
        Args:
            download_dir: Directorio donde están las descargas
            
        Returns:
            Dict con información sobre conflictos encontrados
        """
        if not download_dir:
            Logger.error("❌ No se especificó directorio de descargas")
            return {}
        
        download_path = Path(download_dir)
        if not download_path.exists():
            Logger.error(f"❌ Directorio no existe: {download_dir}")
            return {}
        
        Logger.info(f"🔍 Analizando conflictos de archivos en {download_dir}...")
        
        # Buscar archivos que empiecen con el status_id problemático
        target_status_id = "1933144407659655592"
        target_files = list(download_path.glob(f"{target_status_id}-*"))
        
        conflicts = {
            "target_status_files": target_files,
            "potential_conflicts": [],
            "analysis": {}
        }
        
        Logger.info(f"📊 Archivos encontrados con status_id {target_status_id}: {len(target_files)}")
        
        for file_path in target_files:
            Logger.info(f"   📁 {file_path.name}")
            
            # Extraer información del nombre del archivo
            filename_parts = file_path.stem.split('-', 1)  # Split en 2 partes máximo
            if len(filename_parts) >= 2:
                status_part = filename_parts[0]
                image_part = filename_parts[1]
                
                conflicts["analysis"][file_path.name] = {
                    "status_id": status_part,
                    "image_id": image_part,
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                }
        
        return conflicts

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python fix_multiple_images.py <username> [download_dir]")
        print("Ejemplo: python fix_multiple_images.py rachelc00k /Volumes/SSDWD2T/fansly/rachel")
        sys.exit(1)
    
    username = sys.argv[1]
    download_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    fixer = MultipleImagesFixer()
    
    try:
        # 1. Crear backup del cache
        Logger.info("🔄 PASO 1: Creando backup del cache...")
        backup_path = fixer.create_backup_cache(username)
        if backup_path:
            Logger.success(f"✅ Backup creado: {backup_path}")
        
        # 2. Diagnosticar problemas
        Logger.info("🔄 PASO 2: Diagnosticando problemas...")
        problems = fixer.diagnose_cache_problems(username)
        
        # 3. Analizar conflictos de archivos si se proporciona directorio
        if download_dir:
            Logger.info("🔄 PASO 3: Analizando conflictos de archivos...")
            file_conflicts = fixer.analyze_filename_conflicts(download_dir)
        
        # 4. Reparar cache si hay problemas
        has_problems = (
            problems["duplicate_mappings"] or 
            problems["missing_mappings"] or 
            problems["orphaned_mappings"] or 
            problems["inconsistent_data"]
        )
        
        if has_problems:
            Logger.info("🔄 PASO 4: Reparando cache...")
            if fixer.fix_cache_problems(username, problems):
                Logger.success("✅ Cache reparado exitosamente")
            else:
                Logger.info("💡 No se realizaron cambios")
        else:
            Logger.success("✅ No se encontraron problemas en el cache")
        
        # 5. Mostrar resumen final
        Logger.info("📋 RESUMEN FINAL:")
        Logger.info(f"   👤 Usuario: {username}")
        Logger.info(f"   📁 Directorio: {download_dir or 'No especificado'}")
        Logger.info(f"   💾 Backup: {backup_path or 'No creado'}")
        Logger.info(f"   🔧 Reparaciones: {'Realizadas' if has_problems else 'No necesarias'}")
        
        if download_dir and 'file_conflicts' in locals():
            target_files = file_conflicts.get("target_status_files", [])
            Logger.info(f"   📊 Archivos con status problemático: {len(target_files)}")
        
        Logger.success("🎉 Diagnóstico y reparación completados")
        
    except Exception as e:
        Logger.error(f"❌ Error durante la reparación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

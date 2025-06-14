#!/usr/bin/env python3
"""
Herramienta para corregir nombres de archivo incorrectos causados por mapeos erróneos.
Esta herramienta identifica archivos que tienen el status_id incorrecto en su nombre
y los renombra con el status_id correcto basándose en su contenido de imagen.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.utils.cache_manager import CacheManager
from modules.utils.logging import Logger

class FilenameFixer:
    """
    Corrige nombres de archivo incorrectos causados por mapeos erróneos.
    """
    
    def __init__(self):
        self.cache_manager = CacheManager()
        
    def extract_image_id_from_filename(self, filename: str) -> Optional[str]:
        """
        Extrae el ID de imagen (parte después del guión) del nombre del archivo.
        
        Args:
            filename: Nombre del archivo (ej: "1933144407659655592-GtPolpRWUAA-FaC.jpg")
            
        Returns:
            ID de imagen (ej: "GtPolpRWUAA-FaC") o None si no se puede extraer
        """
        try:
            # Remover extensión
            basename = Path(filename).stem
            
            # Buscar patrón: status_id-image_id
            if '-' in basename:
                parts = basename.split('-', 1)  # Solo dividir en la primera ocurrencia
                if len(parts) >= 2:
                    return parts[1]  # Retornar la parte de la imagen
            return None
        except Exception as e:
            Logger.error(f"Error extrayendo image_id de {filename}: {e}")
            return None
    
    def find_correct_status_id_for_image(self, image_id: str, all_caches: Dict[str, Dict]) -> Optional[str]:
        """
        Busca el status_id correcto para un image_id dado en todos los caches de usuarios.
        
        Args:
            image_id: ID de la imagen (ej: "GrfRyvOXwAA7Vsz")
            all_caches: Diccionario con caches de todos los usuarios
            
        Returns:
            status_id correcto o None si no se encuentra
        """
        for username, cache_data in all_caches.items():
            status_to_image_mapping = cache_data.get("status_to_image_mapping", {})
            
            for status_id, image_url in status_to_image_mapping.items():
                if image_url and image_id in image_url:
                    Logger.info(f"   🎯 Encontrado mapeo correcto: {image_id} -> {status_id} (usuario: {username})")
                    return status_id
        
        return None
    
    def load_all_user_caches(self) -> Dict[str, Dict]:
        """
        Carga los caches de todos los usuarios disponibles.
        
        Returns:
            Diccionario {username: cache_data}
        """
        Logger.info("📚 Cargando caches de todos los usuarios...")
        
        all_caches = {}
        cache_files = list(self.cache_manager.cache_dir.glob("*_processed_posts.json"))
        
        for cache_file in cache_files:
            try:
                # Extraer username del nombre del archivo
                username = cache_file.stem.replace("_processed_posts", "")
                
                cache_data = self.cache_manager.load_user_cache(username)
                all_caches[username] = cache_data
                
                mappings_count = len(cache_data.get("status_to_image_mapping", {}))
                Logger.info(f"   📁 {username}: {mappings_count} mapeos cargados")
                
            except Exception as e:
                Logger.error(f"Error cargando cache {cache_file}: {e}")
        
        Logger.info(f"📚 Cargados {len(all_caches)} caches de usuarios")
        return all_caches
    
    def analyze_incorrect_filenames(self, download_dir: str, target_status_id: str) -> Dict:
        """
        Analiza archivos que tienen un status_id incorrecto en su nombre.
        
        Args:
            download_dir: Directorio de descargas
            target_status_id: Status ID que se está usando incorrectamente
            
        Returns:
            Diccionario con análisis de archivos incorrectos
        """
        download_path = Path(download_dir)
        if not download_path.exists():
            Logger.error(f"❌ Directorio no existe: {download_dir}")
            return {}
        
        Logger.info(f"🔍 Analizando archivos con status_id incorrecto: {target_status_id}...")
        
        # Buscar archivos que empiecen con el status_id objetivo
        target_files = list(download_path.glob(f"{target_status_id}-*"))
        
        # Cargar todos los caches para buscar mapeos correctos
        all_caches = self.load_all_user_caches()
        
        analysis = {
            "total_files": len(target_files),
            "correct_files": [],
            "incorrect_files": [],
            "proposed_renames": [],
            "unknown_images": []
        }
        
        Logger.info(f"📊 Encontrados {len(target_files)} archivos con status_id {target_status_id}")
        
        for file_path in target_files:
            image_id = self.extract_image_id_from_filename(file_path.name)
            if not image_id:
                Logger.warning(f"⚠️  No se pudo extraer image_id de {file_path.name}")
                continue
            
            # Buscar el status_id correcto para esta imagen
            correct_status_id = self.find_correct_status_id_for_image(image_id, all_caches)
            
            if correct_status_id:
                if correct_status_id == target_status_id:
                    # Archivo correcto
                    analysis["correct_files"].append({
                        "filename": file_path.name,
                        "image_id": image_id,
                        "status_id": correct_status_id
                    })
                    Logger.info(f"   ✅ Correcto: {file_path.name}")
                else:
                    # Archivo incorrecto - necesita renombre
                    new_filename = f"{correct_status_id}-{image_id}.jpg"
                    analysis["incorrect_files"].append({
                        "current_filename": file_path.name,
                        "image_id": image_id,
                        "wrong_status_id": target_status_id,
                        "correct_status_id": correct_status_id,
                        "proposed_filename": new_filename
                    })
                    analysis["proposed_renames"].append({
                        "old_path": str(file_path),
                        "new_path": str(file_path.parent / new_filename),
                        "old_name": file_path.name,
                        "new_name": new_filename
                    })
                    Logger.warning(f"   ❌ Incorrecto: {file_path.name} -> {new_filename}")
            else:
                # No se encontró mapeo para esta imagen
                analysis["unknown_images"].append({
                    "filename": file_path.name,
                    "image_id": image_id
                })
                Logger.warning(f"   ❓ Sin mapeo: {file_path.name} (image_id: {image_id})")
        
        # Mostrar resumen
        Logger.info(f"📊 ANÁLISIS COMPLETO:")
        Logger.info(f"   ✅ Archivos correctos: {len(analysis['correct_files'])}")
        Logger.info(f"   ❌ Archivos incorrectos: {len(analysis['incorrect_files'])}")
        Logger.info(f"   ❓ Imágenes sin mapeo: {len(analysis['unknown_images'])}")
        Logger.info(f"   🔄 Renombres propuestos: {len(analysis['proposed_renames'])}")
        
        return analysis
    
    def fix_filenames(self, download_dir: str, analysis: Dict, dry_run: bool = True) -> bool:
        """
        Ejecuta el renombrado de archivos basándose en el análisis.
        
        Args:
            download_dir: Directorio de descargas
            analysis: Resultado del análisis de archivos incorrectos
            dry_run: Si True, solo muestra lo que haría sin ejecutar
            
        Returns:
            True si se ejecutaron renombres exitosamente
        """
        proposed_renames = analysis.get("proposed_renames", [])
        
        if not proposed_renames:
            Logger.info("💡 No hay archivos para renombrar")
            return False
        
        if dry_run:
            Logger.info(f"🔍 SIMULACIÓN DE RENOMBRADO ({len(proposed_renames)} archivos):")
            for i, rename_info in enumerate(proposed_renames, 1):
                Logger.info(f"   {i}. {rename_info['old_name']} -> {rename_info['new_name']}")
            Logger.info("💡 Para ejecutar los renombres, usa --execute")
            return False
        else:
            Logger.info(f"🔄 EJECUTANDO RENOMBRADO de {len(proposed_renames)} archivos...")
            
            success_count = 0
            error_count = 0
            
            for i, rename_info in enumerate(proposed_renames, 1):
                try:
                    old_path = Path(rename_info['old_path'])
                    new_path = Path(rename_info['new_path'])
                    
                    # Verificar que el archivo original existe
                    if not old_path.exists():
                        Logger.error(f"   ❌ [{i}/{len(proposed_renames)}] Archivo no existe: {old_path}")
                        error_count += 1
                        continue
                    
                    # Verificar que el archivo destino no existe
                    if new_path.exists():
                        Logger.error(f"   ❌ [{i}/{len(proposed_renames)}] Archivo destino ya existe: {new_path}")
                        error_count += 1
                        continue
                    
                    # Ejecutar renombre
                    old_path.rename(new_path)
                    Logger.success(f"   ✅ [{i}/{len(proposed_renames)}] {rename_info['old_name']} -> {rename_info['new_name']}")
                    success_count += 1
                    
                except Exception as e:
                    Logger.error(f"   ❌ [{i}/{len(proposed_renames)}] Error renombrando {rename_info['old_name']}: {e}")
                    error_count += 1
            
            Logger.info(f"📊 RESULTADO DEL RENOMBRADO:")
            Logger.info(f"   ✅ Exitosos: {success_count}")
            Logger.info(f"   ❌ Errores: {error_count}")
            Logger.info(f"   📊 Total: {len(proposed_renames)}")
            
            return success_count > 0

def main():
    """Función principal"""
    if len(sys.argv) < 3:
        print("Uso: python fix_filenames.py <download_dir> <target_status_id> [--execute]")
        print("Ejemplo: python fix_filenames.py /Volumes/SSDWD2T/fansly/rachel 1933144407659655592")
        print("")
        print("Opciones:")
        print("  --execute    Ejecutar renombres (por defecto solo simula)")
        sys.exit(1)
    
    download_dir = sys.argv[1]
    target_status_id = sys.argv[2]
    
    # Procesar argumentos opcionales
    execute_renames = "--execute" in sys.argv
    
    fixer = FilenameFixer()
    
    try:
        Logger.info(f"🔄 INICIANDO CORRECCIÓN DE NOMBRES DE ARCHIVO")
        Logger.info(f"   📁 Directorio: {download_dir}")
        Logger.info(f"   🎯 Status ID problemático: {target_status_id}")
        Logger.info(f"   ⚙️  Modo: {'EJECUTAR' if execute_renames else 'SIMULAR'}")
        
        # 1. Analizar archivos incorrectos
        Logger.info("🔄 PASO 1: Analizando archivos incorrectos...")
        analysis = fixer.analyze_incorrect_filenames(download_dir, target_status_id)
        
        if not analysis:
            Logger.error("❌ No se pudo realizar el análisis")
            sys.exit(1)
        
        # 2. Ejecutar renombres
        if analysis.get("proposed_renames"):
            Logger.info(f"🔄 PASO 2: {'Ejecutando' if execute_renames else 'Simulando'} renombres...")
            success = fixer.fix_filenames(download_dir, analysis, dry_run=not execute_renames)
            
            if execute_renames and success:
                Logger.success("✅ Renombrado completado exitosamente")
            elif not execute_renames:
                Logger.info("💡 Simulación completada. Usa --execute para realizar los cambios")
        else:
            Logger.success("✅ No se encontraron archivos que necesiten renombrado")
        
        # 3. Mostrar resumen final
        Logger.info("📋 RESUMEN FINAL:")
        Logger.info(f"   📁 Directorio analizado: {download_dir}")
        Logger.info(f"   📊 Total de archivos: {analysis.get('total_files', 0)}")
        Logger.info(f"   ✅ Archivos correctos: {len(analysis.get('correct_files', []))}")
        Logger.info(f"   ❌ Archivos incorrectos: {len(analysis.get('incorrect_files', []))}")
        Logger.info(f"   ❓ Imágenes sin mapeo: {len(analysis.get('unknown_images', []))}")
        Logger.info(f"   🔄 Acción: {'Renombres ejecutados' if execute_renames else 'Solo simulación'}")
        
        Logger.success("🎉 Proceso completado")
        
    except Exception as e:
        Logger.error(f"❌ Error durante la corrección: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

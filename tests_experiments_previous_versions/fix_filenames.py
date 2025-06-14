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
        }\n        \n        Logger.info(f\"📊 Encontrados {len(target_files)} archivos con status_id {target_status_id}\")\n        \n        for file_path in target_files:\n            image_id = self.extract_image_id_from_filename(file_path.name)\n            if not image_id:\n                Logger.warning(f\"⚠️  No se pudo extraer image_id de {file_path.name}\")\n                continue\n            \n            # Buscar el status_id correcto para esta imagen\n            correct_status_id = self.find_correct_status_id_for_image(image_id, all_caches)\n            \n            if correct_status_id:\n                if correct_status_id == target_status_id:\n                    # Archivo correcto\n                    analysis[\"correct_files\"].append({\n                        \"filename\": file_path.name,\n                        \"image_id\": image_id,\n                        \"status_id\": correct_status_id\n                    })\n                    Logger.info(f\"   ✅ Correcto: {file_path.name}\")\n                else:\n                    # Archivo incorrecto - necesita renombre\n                    new_filename = f\"{correct_status_id}-{image_id}.jpg\"\n                    analysis[\"incorrect_files\"].append({\n                        \"current_filename\": file_path.name,\n                        \"image_id\": image_id,\n                        \"wrong_status_id\": target_status_id,\n                        \"correct_status_id\": correct_status_id,\n                        \"proposed_filename\": new_filename\n                    })\n                    analysis[\"proposed_renames\"].append({\n                        \"old_path\": str(file_path),\n                        \"new_path\": str(file_path.parent / new_filename),\n                        \"old_name\": file_path.name,\n                        \"new_name\": new_filename\n                    })\n                    Logger.warning(f\"   ❌ Incorrecto: {file_path.name} -> {new_filename}\")\n            else:\n                # No se encontró mapeo para esta imagen\n                analysis[\"unknown_images\"].append({\n                    \"filename\": file_path.name,\n                    \"image_id\": image_id\n                })\n                Logger.warning(f\"   ❓ Sin mapeo: {file_path.name} (image_id: {image_id})\")\n        \n        # Mostrar resumen\n        Logger.info(f\"📊 ANÁLISIS COMPLETO:\")\n        Logger.info(f\"   ✅ Archivos correctos: {len(analysis['correct_files'])}\")\n        Logger.info(f\"   ❌ Archivos incorrectos: {len(analysis['incorrect_files'])}\")\n        Logger.info(f\"   ❓ Imágenes sin mapeo: {len(analysis['unknown_images'])}\")\n        Logger.info(f\"   🔄 Renombres propuestos: {len(analysis['proposed_renames'])}\")\n        \n        return analysis\n    \n    def fix_filenames(self, download_dir: str, analysis: Dict, dry_run: bool = True) -> bool:\n        \"\"\"\n        Ejecuta el renombrado de archivos basándose en el análisis.\n        \n        Args:\n            download_dir: Directorio de descargas\n            analysis: Resultado del análisis de archivos incorrectos\n            dry_run: Si True, solo muestra lo que haría sin ejecutar\n            \n        Returns:\n            True si se ejecutaron renombres exitosamente\n        \"\"\"\n        proposed_renames = analysis.get(\"proposed_renames\", [])\n        \n        if not proposed_renames:\n            Logger.info(\"💡 No hay archivos para renombrar\")\n            return False\n        \n        if dry_run:\n            Logger.info(f\"🔍 SIMULACIÓN DE RENOMBRADO ({len(proposed_renames)} archivos):\")\n            for i, rename_info in enumerate(proposed_renames, 1):\n                Logger.info(f\"   {i}. {rename_info['old_name']} -> {rename_info['new_name']}\")\n            Logger.info(\"💡 Para ejecutar los renombres, usa --execute\")\n            return False\n        else:\n            Logger.info(f\"🔄 EJECUTANDO RENOMBRADO de {len(proposed_renames)} archivos...\")\n            \n            success_count = 0\n            error_count = 0\n            \n            for i, rename_info in enumerate(proposed_renames, 1):\n                try:\n                    old_path = Path(rename_info['old_path'])\n                    new_path = Path(rename_info['new_path'])\n                    \n                    # Verificar que el archivo original existe\n                    if not old_path.exists():\n                        Logger.error(f\"   ❌ [{i}/{len(proposed_renames)}] Archivo no existe: {old_path}\")\n                        error_count += 1\n                        continue\n                    \n                    # Verificar que el archivo destino no existe\n                    if new_path.exists():\n                        Logger.error(f\"   ❌ [{i}/{len(proposed_renames)}] Archivo destino ya existe: {new_path}\")\n                        error_count += 1\n                        continue\n                    \n                    # Ejecutar renombre\n                    old_path.rename(new_path)\n                    Logger.success(f\"   ✅ [{i}/{len(proposed_renames)}] {rename_info['old_name']} -> {rename_info['new_name']}\")\n                    success_count += 1\n                    \n                except Exception as e:\n                    Logger.error(f\"   ❌ [{i}/{len(proposed_renames)}] Error renombrando {rename_info['old_name']}: {e}\")\n                    error_count += 1\n            \n            Logger.info(f\"📊 RESULTADO DEL RENOMBRADO:\")\n            Logger.info(f\"   ✅ Exitosos: {success_count}\")\n            Logger.info(f\"   ❌ Errores: {error_count}\")\n            Logger.info(f\"   📊 Total: {len(proposed_renames)}\")\n            \n            return success_count > 0\n    \n    def create_rename_script(self, analysis: Dict, output_file: str) -> str:\n        \"\"\"\n        Crea un script bash con los comandos de renombrado.\n        \n        Args:\n            analysis: Resultado del análisis\n            output_file: Archivo donde guardar el script\n            \n        Returns:\n            Contenido del script generado\n        \"\"\"\n        proposed_renames = analysis.get(\"proposed_renames\", [])\n        \n        if not proposed_renames:\n            Logger.info(\"💡 No hay renombres para generar script\")\n            return \"\"\n        \n        script_lines = [\n            \"#!/bin/bash\",\n            \"# Script de renombrado generado automáticamente\",\n            f\"# Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\",\n            f\"# Total de archivos a renombrar: {len(proposed_renames)}\",\n            \"\",\n            \"echo 'Iniciando renombrado de archivos...'\",\n            \"\"\n        ]\n        \n        for i, rename_info in enumerate(proposed_renames, 1):\n            old_name = rename_info['old_name']\n            new_name = rename_info['new_name']\n            \n            script_lines.extend([\n                f\"echo '[{i}/{len(proposed_renames)}] Renombrando {old_name} -> {new_name}'\",\n                f\"mv '{old_name}' '{new_name}'\",\n                \"if [ $? -eq 0 ]; then\",\n                f\"    echo '✅ Éxito: {old_name} -> {new_name}'\",\n                \"else\",\n                f\"    echo '❌ Error renombrando {old_name}'\",\n                \"fi\",\n                \"\"\n            ])\n        \n        script_lines.extend([\n            \"echo 'Renombrado completado.'\",\n            f\"echo 'Total de archivos procesados: {len(proposed_renames)}'\"\n        ])\n        \n        script_content = \"\\n\".join(script_lines)\n        \n        try:\n            with open(output_file, 'w', encoding='utf-8') as f:\n                f.write(script_content)\n            \n            # Hacer el script ejecutable\n            import os\n            os.chmod(output_file, 0o755)\n            \n            Logger.success(f\"📝 Script de renombrado creado: {output_file}\")\n            Logger.info(f\"   Para ejecutar: cd {Path(proposed_renames[0]['old_path']).parent} && bash {output_file}\")\n            \n        except Exception as e:\n            Logger.error(f\"❌ Error creando script: {e}\")\n        \n        return script_content\n\ndef main():\n    \"\"\"Función principal\"\"\"\n    if len(sys.argv) < 3:\n        print(\"Uso: python fix_filenames.py <download_dir> <target_status_id> [--execute] [--script output.sh]\")\n        print(\"Ejemplo: python fix_filenames.py /Volumes/SSDWD2T/fansly/rachel 1933144407659655592\")\n        print(\"\")\n        print(\"Opciones:\")\n        print(\"  --execute    Ejecutar renombres (por defecto solo simula)\")\n        print(\"  --script     Generar script bash con los renombres\")\n        sys.exit(1)\n    \n    download_dir = sys.argv[1]\n    target_status_id = sys.argv[2]\n    \n    # Procesar argumentos opcionales\n    execute_renames = \"--execute\" in sys.argv\n    generate_script = \"--script\" in sys.argv\n    \n    script_file = None\n    if generate_script:\n        try:\n            script_index = sys.argv.index(\"--script\") + 1\n            if script_index < len(sys.argv):\n                script_file = sys.argv[script_index]\n            else:\n                script_file = \"rename_files.sh\"\n        except (ValueError, IndexError):\n            script_file = \"rename_files.sh\"\n    \n    fixer = FilenameFixer()\n    \n    try:\n        Logger.info(f\"🔄 INICIANDO CORRECCIÓN DE NOMBRES DE ARCHIVO\")\n        Logger.info(f\"   📁 Directorio: {download_dir}\")\n        Logger.info(f\"   🎯 Status ID problemático: {target_status_id}\")\n        Logger.info(f\"   ⚙️  Modo: {'EJECUTAR' if execute_renames else 'SIMULAR'}\")\n        \n        # 1. Analizar archivos incorrectos\n        Logger.info(\"🔄 PASO 1: Analizando archivos incorrectos...\")\n        analysis = fixer.analyze_incorrect_filenames(download_dir, target_status_id)\n        \n        if not analysis:\n            Logger.error(\"❌ No se pudo realizar el análisis\")\n            sys.exit(1)\n        \n        # 2. Generar script si se solicita\n        if generate_script and script_file:\n            Logger.info(f\"🔄 PASO 2: Generando script de renombrado...\")\n            fixer.create_rename_script(analysis, script_file)\n        \n        # 3. Ejecutar renombres\n        if analysis.get(\"proposed_renames\"):\n            Logger.info(f\"🔄 PASO 3: {'Ejecutando' if execute_renames else 'Simulando'} renombres...\")\n            success = fixer.fix_filenames(download_dir, analysis, dry_run=not execute_renames)\n            \n            if execute_renames and success:\n                Logger.success(\"✅ Renombrado completado exitosamente\")\n            elif not execute_renames:\n                Logger.info(\"💡 Simulación completada. Usa --execute para realizar los cambios\")\n        else:\n            Logger.success(\"✅ No se encontraron archivos que necesiten renombrado\")\n        \n        # 4. Mostrar resumen final\n        Logger.info(\"📋 RESUMEN FINAL:\")\n        Logger.info(f\"   📁 Directorio analizado: {download_dir}\")\n        Logger.info(f\"   📊 Total de archivos: {analysis.get('total_files', 0)}\")\n        Logger.info(f\"   ✅ Archivos correctos: {len(analysis.get('correct_files', []))}\")\n        Logger.info(f\"   ❌ Archivos incorrectos: {len(analysis.get('incorrect_files', []))}\")\n        Logger.info(f\"   ❓ Imágenes sin mapeo: {len(analysis.get('unknown_images', []))}\")\n        Logger.info(f\"   🔄 Acción: {'Renombres ejecutados' if execute_renames else 'Solo simulación'}\")\n        \n        if generate_script and script_file:\n            Logger.info(f\"   📝 Script generado: {script_file}\")\n        \n        Logger.success(\"🎉 Proceso completado\")\n        \n    except Exception as e:\n        Logger.error(f\"❌ Error durante la corrección: {e}\")\n        sys.exit(1)\n\nif __name__ == \"__main__\":\n    main()"

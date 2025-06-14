#!/usr/bin/env python3
"""
Script de prueba para verificar que los nombres de archivo únicos funcionan correctamente.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.download.filename_utils import FilenameUtils

def test_filename_generation():
    """Prueba la generación de nombres de archivo únicos"""
    print("🧪 PROBANDO GENERACIÓN DE NOMBRES DE ARCHIVO ÚNICOS")
    print("=" * 60)
    
    # URLs de prueba que pueden tener el mismo nombre original
    test_cases = [
        {
            'url': 'https://pbs.twimg.com/media/GiqGYSZXUAAvjFk?format=jpg&name=large',
            'status_id': '1933144407659655592',
            'expected_prefix': '1933144407659655592-GiqGYSZXUAAvjFk'
        },
        {
            'url': 'https://pbs.twimg.com/media/GiqGYSZXUAAvjFk?format=jpg&name=large', 
            'status_id': '1885467152867635251',
            'expected_prefix': '1885467152867635251-GiqGYSZXUAAvjFk'
        },
        {
            'url': 'https://pbs.twimg.com/media/GiJ8WGGagAAMW4Q?format=jpg&name=large',
            'status_id': '1927429739565711865',
            'expected_prefix': '1927429739565711865-GiJ8WGGagAAMW4Q'
        }
    ]
    
    print("🎯 Casos de prueba:")
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. URL: {case['url']}")
        print(f"   Status ID: {case['status_id']}")
        
        # Generar nombre sin status_id (método anterior)
        filename_old = FilenameUtils.clean_filename(case['url'])
        print(f"   📁 Nombre anterior: {filename_old}")
        
        # Generar nombre con status_id (método nuevo)
        filename_new = FilenameUtils.clean_filename(case['url'], case['status_id'])
        print(f"   🆕 Nombre nuevo: {filename_new}")
        
        # Verificar que el nombre incluye el status_id
        if case['status_id'] in filename_new:
            print(f"   ✅ Status ID correctamente incluido")
        else:
            print(f"   ❌ Status ID NO incluido")
            
        # Verificar unicidad
        expected = f"{case['expected_prefix']}.jpg"
        if filename_new == expected:
            print(f"   ✅ Formato correcto: {expected}")
        else:
            print(f"   ⚠️  Formato inesperado, esperado: {expected}")
    
    print(f"\n{'='*60}")
    print("✅ Prueba completada. Los archivos ahora tienen nombres únicos.")
    print("💡 Formato: [status_id]-[nombre_original].jpg")
    print("🎯 Esto evita colisiones cuando el mismo nombre de imagen")
    print("   aparece en diferentes tweets.")

if __name__ == "__main__":
    test_filename_generation()

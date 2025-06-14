#!/usr/bin/env python3
"""
Test para verificar que las mejoras en el mapeo de múltiples imágenes funcionen correctamente.
"""

import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.extraction.image_processor import ImageProcessor
from modules.utils.logging import Logger

class MockPage:
    """Mock de page para testing."""
    def __init__(self):
        self.evaluation_result = []
    
    async def evaluate(self, script):
        # Simular múltiples imágenes encontradas en tweets
        return [
            'https://pbs.twimg.com/media/GpEIo1aXoAAj_ZE?format=jpg&name=large',
            'https://pbs.twimg.com/media/GpEIo2bXoAAj_ZF?format=jpg&name=large',
            'https://pbs.twimg.com/media/GpEIo3cXoAAj_ZG?format=jpg&name=large',
            'https://pbs.twimg.com/media/GpEIo4dXoAAj_ZH?format=jpg&name=large',
            'https://pbs.twimg.com/media/GpEIo5eXoAAj_ZI?format=jpg&name=large'
        ]
    
    async def goto(self, url, **kwargs):
        pass

def test_correlation_mapping():
    """Test para verificar que la correlación mejorada funcione."""
    Logger.info("🧪 Iniciando test de mapeo de múltiples imágenes...")
    
    # Crear instancia del procesador con mock
    processor = ImageProcessor(MockPage())
    
    # Simular URLs de imágenes sin mapeo
    image_urls = [
        'https://pbs.twimg.com/media/GpEIo1aXoAAj_ZE?format=jpg&name=large',
        'https://pbs.twimg.com/media/GpEIo2bXoAAj_ZF?format=jpg&name=large',
        'https://pbs.twimg.com/media/GpEIo3cXoAAj_ZG?format=jpg&name=large',
        'https://pbs.twimg.com/media/GpEIo4dXoAAj_ZH?format=jpg&name=large',
        'https://pbs.twimg.com/media/GpEIo5eXoAAj_ZI?format=jpg&name=large'
    ]
    
    # Simular status URLs (menos status que imágenes para simular carruseles)
    status_urls = [
        {'url': 'https://x.com/user/status/1234567890123456789', 'media_type': 'image'},
        {'url': 'https://x.com/user/status/1234567890123456790', 'media_type': 'image'},
    ]
    
    # Mapping existente vacío
    existing_mapping = {}
    
    # Ejecutar el mapeo
    processor._create_correlation_mappings(image_urls, status_urls, existing_mapping)
    
    # Verificar resultados
    Logger.info(f"📊 Resultados del test:")
    Logger.info(f"   Total de imágenes: {len(image_urls)}")
    Logger.info(f"   Total de status: {len(status_urls)}")
    Logger.info(f"   Mapeos creados: {len(existing_mapping)}")
    
    # Mostrar mapeos creados
    for img_url, status_id in existing_mapping.items():
        Logger.info(f"   🔗 {img_url} -> {status_id}")
    
    # Verificaciones
    assert len(existing_mapping) == len(image_urls), f"Se esperaban {len(image_urls)} mapeos, se obtuvieron {len(existing_mapping)}"
    
    # Verificar que se permiten múltiples mapeos al mismo status_id (carruseles)
    status_ids_used = list(existing_mapping.values())
    unique_status_ids = set(status_ids_used)
    Logger.info(f"   🎯 Status únicos utilizados: {len(unique_status_ids)}")
    Logger.info(f"   📈 Promedio de imágenes por status: {len(image_urls) / len(unique_status_ids):.1f}")
    
    Logger.success("✅ Test de mapeo de múltiples imágenes completado exitosamente!")
    return True

if __name__ == "__main__":
    try:
        test_correlation_mapping()
        Logger.success("🎉 Todos los tests pasaron correctamente!")
    except Exception as e:
        Logger.error(f"❌ Test falló: {e}")
        sys.exit(1)

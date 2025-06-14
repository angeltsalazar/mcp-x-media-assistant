#!/usr/bin/env python3
"""
Test específico para verificar que el método 2 crea mapeos correctamente
incluso para imágenes duplicadas.
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from modules.extraction.image_processor import ImageProcessor
from modules.utils.cache_manager import CacheManager
from modules.utils.logging import Logger

class TestMethod2Mapping:
    def __init__(self):
        self.page = MagicMock()
        self.processor = ImageProcessor(self.page)
        self.processor.username = "testuser"
        self.processor.cache_manager = CacheManager()
        
    async def test_method2_creates_mappings_for_duplicates(self):
        """Test que el método 2 crea mapeos incluso para imágenes duplicadas"""
        print("\n🧪 Test: Método 2 crea mapeos para duplicados")
        
        # URLs de status de prueba
        status_urls = [
            {'url': 'https://twitter.com/user/status/123456789', 'media_type': 'image'},
            {'url': 'https://twitter.com/user/status/987654321', 'media_type': 'image'},
        ]
        
        # Lista de imágenes pre-existente (simulando que ya encontramos esta imagen por método 1)
        existing_image_urls = ['https://pbs.twimg.com/media/image1.jpg:large']
        
        # Mock del comportamiento de la página
        self.page.goto = AsyncMock()
        self.page.evaluate = AsyncMock()
        
        # Configurar el mock para que ambos status devuelvan la misma imagen
        self.page.evaluate.side_effect = [
            # Primera navegación: devuelve la imagen ya existente
            ['https://pbs.twimg.com/media/image1.jpg:orig'],
            # Segunda navegación: devuelve la misma imagen
            ['https://pbs.twimg.com/media/image1.jpg:orig']
        ]
        
        # Ejecutar el método 2
        constructed_count, mappings = await self.processor._construct_direct_urls(
            status_urls, existing_image_urls, 2
        )
        
        # Verificaciones
        print(f"   📊 Constructed count: {constructed_count}")
        print(f"   📊 Mappings creados: {len(mappings)}")
        print(f"   📊 Mapeos: {mappings}")
        print(f"   📊 URLs finales: {existing_image_urls}")
        
        # Assertions
        assert constructed_count == 0, f"No deberían añadirse nuevas imágenes duplicadas, pero count = {constructed_count}"
        assert len(mappings) == 2, f"Deberían crearse 2 mapeos, pero se crearon {len(mappings)}"
        assert '123456789' in mappings, "Debería existir mapeo para status 123456789"
        assert '987654321' in mappings, "Debería existir mapeo para status 987654321"
        assert mappings['123456789'] == 'https://pbs.twimg.com/media/image1.jpg:large', "Mapeo 1 incorrecto"
        assert mappings['987654321'] == 'https://pbs.twimg.com/media/image1.jpg:large', "Mapeo 2 incorrecto"
        
        print("   ✅ Test pasado: Método 2 crea mapeos correctamente para duplicados")
        return True
    
    async def test_method2_handles_invalid_urls(self):
        """Test que el método 2 solo reporta como inválidas las URLs realmente no extraíbles"""
        print("\n🧪 Test: Método 2 maneja URLs inválidas correctamente")
        
        status_urls = [
            {'url': 'https://twitter.com/user/status/111111111', 'media_type': 'image'},  # Sin imagen
            {'url': 'https://twitter.com/user/status/222222222', 'media_type': 'image'},  # Con imagen válida
        ]
        
        existing_image_urls = []
        
        # Mock para simular: primera URL sin imágenes, segunda con imagen
        self.page.evaluate.side_effect = [
            [],  # Primera navegación: sin imágenes
            ['https://pbs.twimg.com/media/image2.jpg:orig']  # Segunda: con imagen
        ]
        
        # Ejecutar el método 2
        constructed_count, mappings = await self.processor._construct_direct_urls(
            status_urls, existing_image_urls, 2
        )
        
        print(f"   📊 Constructed count: {constructed_count}")
        print(f"   📊 Mappings creados: {len(mappings)}")
        print(f"   📊 Mapeos: {mappings}")
        
        # Verificaciones
        assert constructed_count == 1, f"Debería añadirse 1 imagen, pero count = {constructed_count}"
        assert len(mappings) == 1, f"Debería crearse 1 mapeo, pero se crearon {len(mappings)}"
        assert '222222222' in mappings, "Debería existir mapeo para status con imagen válida"
        assert '111111111' not in mappings, "No debería existir mapeo para status sin imagen"
        
        print("   ✅ Test pasado: Método 2 maneja URLs inválidas correctamente")
        return True

async def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests del método 2...")
    
    test_suite = TestMethod2Mapping()
    
    try:
        # Test 1: Mapeos para duplicados
        await test_suite.test_method2_creates_mappings_for_duplicates()
        
        # Test 2: URLs inválidas
        await test_suite.test_method2_handles_invalid_urls()
        
        print("\n🎉 Todos los tests pasaron correctamente!")
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

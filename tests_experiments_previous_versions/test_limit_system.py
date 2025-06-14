#!/usr/bin/env python3
"""
Script de prueba para verificar que el sistema de límites funciona correctamente.
Simula un usuario sin cache para probar que el scroll se detiene al encontrar URLs nuevas.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from modules.extraction.scroll_manager import ScrollManager
from modules.extraction.url_extractor import URLExtractor
from modules.utils.cache_manager import CacheManager

class MockPage:
    """Mock de la página para pruebas"""
    def __init__(self):
        self.urls_to_return = [
            {'url': 'https://x.com/testuser/status/111', 'media_type': 'image'},
            {'url': 'https://x.com/testuser/status/222', 'media_type': 'image'},
            {'url': 'https://x.com/testuser/status/333', 'media_type': 'image'},
            {'url': 'https://x.com/testuser/status/444', 'media_type': 'image'},
            {'url': 'https://x.com/testuser/status/555', 'media_type': 'video'},
        ]
        self.current_index = 0
        
    async def evaluate(self, script):
        """Mock del scroll"""
        await asyncio.sleep(0.1)  # Simular tiempo de scroll
        
    async def wait_for_selector(self, selector, timeout=5000):
        """Mock de espera de selector"""
        await asyncio.sleep(0.1)

class MockURLExtractor:
    """Mock del extractor de URLs"""
    def __init__(self, mock_page):
        self.page = mock_page
        self.all_status_urls = []
        
    async def extract_all_status_urls(self):
        """Simula la extracción de URLs, agregando algunas cada vez"""
        # Simular que cada scroll agrega 2 URLs nuevas
        new_urls = self.page.urls_to_return[len(self.all_status_urls):len(self.all_status_urls)+2]
        self.all_status_urls.extend(new_urls)
        return len(new_urls)

async def test_limit_system():
    """Prueba el sistema de límites"""
    print("🧪 PROBANDO SISTEMA DE LÍMITES DE URLs NUEVAS")
    print("=" * 50)
    
    # Crear mocks
    mock_page = MockPage()
    mock_url_extractor = MockURLExtractor(mock_page)
    
    # Crear scroll manager
    scroll_manager = ScrollManager(mock_page, mock_url_extractor)
    
    # Crear cache manager temporal (sin cache existente)
    cache_manager = CacheManager()
    test_username = "temp_test_user"
    
    # Limpiar cache de prueba si existe
    cache_file = cache_manager.get_cache_file_path(test_username)
    if cache_file.exists():
        cache_file.unlink()
        print(f"🧹 Cache de prueba limpiado: {test_username}")
    
    # Configurar scroll manager
    scroll_manager.set_cache_info(cache_manager, test_username)
    
    print(f"🎯 Objetivo: encontrar 3 URLs nuevas (sin cache existente)")
    print(f"📊 URLs disponibles en mock: {len(mock_page.urls_to_return)}")
    print()
    
    # Ejecutar scroll con límite de 3 URLs nuevas
    await scroll_manager.scroll_and_extract(max_scrolls=10, target_new_urls=3)
    
    print()
    print("📈 RESULTADOS:")
    print(f"📊 Total URLs extraídas: {len(mock_url_extractor.all_status_urls)}")
    print(f"🔍 URLs extraídas: {[url['url'].split('/')[-1] for url in mock_url_extractor.all_status_urls]}")
    
    # Verificar si se detuvo correctamente
    if len(mock_url_extractor.all_status_urls) >= 3:
        print("✅ ÉXITO: El sistema se detuvo al encontrar suficientes URLs nuevas")
    else:
        print("❌ ERROR: El sistema no encontró suficientes URLs")
        
    # Limpiar cache de prueba
    if cache_file.exists():
        cache_file.unlink()
        print(f"🧹 Cache de prueba limpiado")

if __name__ == "__main__":
    asyncio.run(test_limit_system())

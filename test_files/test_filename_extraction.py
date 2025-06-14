#!/usr/bin/env python3
"""
Test para verificar la extracción correcta de nombres de archivo
"""

import sys
import os
sys.path.append('/Volumes/SSDWD2T/projects/asistente_computadora')

from edge_x_downloader_clean import EdgeXDownloader

def test_filename_extraction():
    """Test de extracción de nombres de archivo"""
    
    downloader = EdgeXDownloader("/tmp/test")
    
    test_cases = [
        # URLs típicas de Twitter con diferentes formatos
        {
            "url": "https://pbs.twimg.com/media/GpEIoIaXoAAj_ZE?format=jpg&name=large",
            "expected": "GpEIoIaXoAAj_ZE.jpg"
        },
        {
            "url": "https://pbs.twimg.com/media/GpoTbA-XwAAm4-O?format=jpg&name=large",
            "expected": "GpoTbA-XwAAm4-O.jpg"
        },
        {
            "url": "https://pbs.twimg.com/media/GpY0bHRWMAAGQk8?format=jpg&name=large",
            "expected": "GpY0bHRWMAAGQk8.jpg"
        },
        {
            "url": "https://pbs.twimg.com/media/ABC123_def?format=jpg&name=large",
            "expected": "ABC123_def.jpg"
        },
        {
            "url": "https://pbs.twimg.com/media/Test-Image?format=jpg&name=large",
            "expected": "Test-Image.jpg"
        },
        # URL sin parámetros
        {
            "url": "https://pbs.twimg.com/media/SimpleImage",
            "expected": "SimpleImage.jpg"
        },
        # URL con caracteres problemáticos
        {
            "url": "https://pbs.twimg.com/media/Test<>Image?format=jpg&name=large",
            "expected": "Test__Image.jpg"
        },
        # URL de video (debería funcionar también)
        {
            "url": "https://video.twimg.com/amplify_video/ABCDEF?tag=123",
            "expected": "ABCDEF"
        }
    ]
    
    print("🧪 TESTING FILENAME EXTRACTION")
    print("="*70)
    
    for i, test_case in enumerate(test_cases, 1):
        url = test_case["url"]
        expected = test_case["expected"]
        
        result = downloader.clean_filename(url)
        
        print(f"\n{i}. URL:")
        print(f"   {url}")
        print(f"   Expected: {expected}")
        print(f"   Got:      {result}")
        
        # Verificar resultado
        if result == expected:
            print(f"   Status: ✅ PASSED")
        else:
            print(f"   Status: ❌ FAILED")
            
            # Análisis adicional para URLs de Twitter
            if 'pbs.twimg.com' in url:
                # Verificar si al menos conserva el nombre base
                base_name = expected.replace('.jpg', '')
                if base_name in result:
                    print(f"   Note: ⚠️  Contains base name but format differs")
                else:
                    print(f"   Note: ❌ Base name lost completely")
    
    print("\n" + "="*70)
    print("🔍 Test completed!")

if __name__ == "__main__":
    test_filename_extraction()

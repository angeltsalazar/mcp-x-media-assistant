#!/usr/bin/env python3
"""
Test completo: URL cleaning + filename extraction
"""

import sys
import os
sys.path.append('/Volumes/SSDWD2T/projects/asistente_computadora')

from edge_x_downloader_clean import EdgeXDownloader

def test_complete_workflow():
    """Test del flujo completo: limpieza de URL + extracción de nombre"""
    
    downloader = EdgeXDownloader("/tmp/test")
    
    # URLs problemáticas reales como las que mencionaste
    test_urls = [
        "https://pbs.twimg.com/media/GpoTbA-XwAAm4-O?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/GpY0bHRWMAAGQk8?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/GpEIoIaXoAAj_ZE?format=jpg&name=small",
        "https://pbs.twimg.com/media/TestImage123?name=medium&format=jpg"
    ]
    
    print("🔄 TESTING COMPLETE WORKFLOW")
    print("="*80)
    
    for i, original_url in enumerate(test_urls, 1):
        print(f"\n{i}. PROCESSING: {original_url}")
        
        # Paso 1: Limpiar URL
        cleaned_url = downloader.clean_image_url_robust(original_url)
        print(f"   📝 Cleaned URL: {cleaned_url}")
        
        # Paso 2: Extraer nombre de archivo
        filename = downloader.clean_filename(cleaned_url)
        print(f"   📁 Filename: {filename}")
        
        # Verificaciones
        has_large = 'name=large' in cleaned_url if cleaned_url else False
        has_format = 'format=jpg' in cleaned_url if cleaned_url else False
        has_no_small = not any(size in cleaned_url for size in ['360x360', 'small', 'medium']) if cleaned_url else True
        preserves_original = any(part in filename for part in original_url.split('/media/')[-1].split('?')[0]) if '?' in original_url else True
        
        all_good = has_large and has_format and has_no_small and preserves_original
        
        print(f"   ✅ Has name=large: {has_large}")
        print(f"   ✅ Has format=jpg: {has_format}")
        print(f"   ✅ No small params: {has_no_small}")
        print(f"   ✅ Preserves name: {preserves_original}")
        print(f"   🎯 OVERALL: {'✅ PASS' if all_good else '❌ FAIL'}")
    
    print("\n" + "="*80)
    print("🎉 Complete workflow test finished!")

if __name__ == "__main__":
    test_complete_workflow()

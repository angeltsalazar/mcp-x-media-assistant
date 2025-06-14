#!/usr/bin/env python3
"""
Test rápido del script principal con URLs problemáticas
"""

import sys
import os
sys.path.append('/Volumes/SSDWD2T/projects/asistente_computadora')

from edge_x_downloader_clean import EdgeXDownloader

def test_script_url_cleaning():
    """Test del método de limpieza en el script principal"""
    
    downloader = EdgeXDownloader("/tmp/test")
    
    test_urls = [
        "https://pbs.twimg.com/media/GpoTbA-XwAAm4-O?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/GpY0bHRWMAAGQk8?format=jpg&name=360x360",
        "https://pbs.twimg.com/media/HIJKLMN?name=360x360&format=jpg",
        "https://pbs.twimg.com/media/STUVWXY",
        "https://video.twimg.com/amplify_video/ABCDEF?tag=123",
    ]
    
    print("🧪 TESTING SCRIPT URL CLEANING")
    print("="*60)
    
    for i, url in enumerate(test_urls, 1):
        cleaned = downloader.clean_image_url_robust(url)
        print(f"\n{i}. Original:")
        print(f"   {url}")
        print(f"   Cleaned:")
        print(f"   {cleaned}")
        
        if cleaned and 'pbs.twimg.com' in cleaned:
            has_name_large = 'name=large' in cleaned
            has_format_jpg = 'format=jpg' in cleaned
            has_small_name = any(size in cleaned for size in ['360x360', 'small', 'medium', 'thumb', '240x240'])
            
            status = "✅" if (has_name_large and has_format_jpg and not has_small_name) else "❌"
            print(f"   Status: {status}")
            if not has_name_large:
                print(f"   ⚠️  Missing name=large")
            if not has_format_jpg:
                print(f"   ⚠️  Missing format=jpg")
            if has_small_name:
                print(f"   ⚠️  Still has small size parameter")

if __name__ == "__main__":
    test_script_url_cleaning()

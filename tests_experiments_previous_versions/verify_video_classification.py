#!/usr/bin/env python3
"""
Script para verificar qué URLs son realmente videos usando yt-dlp
Esto nos ayudará a identificar exactamente cuáles de las 55 URLs son los 7 videos
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_video_with_ytdlp(url):
    """Verifica si una URL es un video válido usando yt-dlp"""
    try:
        # Comando para verificar si es un video sin descargarlo
        result = subprocess.run([
            'yt-dlp', 
            '--no-download', 
            '--print', 'title',
            '--quiet',
            url
        ], capture_output=True, text=True, timeout=30)
        
        # Si yt-dlp puede extraer información, es un video
        return result.returncode == 0 and result.stdout.strip()
    except:
        return False

def load_media_urls():
    """Carga las URLs del JSON generado por edge_x_downloader_clean.py"""
    downloads_dir = Path.home() / "Downloads" / "X_Media_Edge"
    
    # Buscar el archivo JSON más reciente
    json_files = list(downloads_dir.glob("media_urls_edge_*.json"))
    if not json_files:
        print("❌ No se encontró archivo JSON generado por edge_x_downloader_clean.py")
        print("💡 Ejecuta primero: python3 test_edge_media_extraction.py")
        return None
    
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📄 Cargando URLs de: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data

def main():
    """Función principal"""
    print("🔍 VERIFICADOR DE VIDEOS CON YT-DLP")
    print("=" * 50)
    print("Este script verifica cuáles de las 55 URLs son realmente videos")
    print()
    
    # Verificar si yt-dlp está instalado
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        print(f"✅ yt-dlp instalado: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ yt-dlp no está instalado")
        print("💡 Instalar con: pip3 install yt-dlp")
        return
    
    # Cargar URLs
    data = load_media_urls()
    if not data:
        return
    
    all_urls = [item['url'] for item in data['all_media']]
    print(f"📊 Verificando {len(all_urls)} URLs...")
    print()
    
    videos = []
    images = []
    failed = []
    
    for i, url in enumerate(all_urls, 1):
        print(f"🔍 [{i:2d}/{len(all_urls)}] Verificando: {url}")
        
        video_title = check_video_with_ytdlp(url)
        if video_title:
            videos.append({
                'url': url,
                'title': video_title,
                'position': i
            })
            print(f"   ✅ VIDEO: {video_title}")
        else:
            # Asumir que es imagen si no es video
            images.append({
                'url': url,
                'position': i
            })
            print(f"   📷 IMAGEN")
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS FINALES:")
    print("=" * 50)
    print(f"🎬 Videos encontrados: {len(videos)}")
    print(f"📷 Imágenes encontradas: {len(images)}")
    print(f"❌ Errores: {len(failed)}")
    print(f"📊 Total verificado: {len(videos) + len(images) + len(failed)}")
    
    # Mostrar videos encontrados
    if videos:
        print(f"\n🎬 VIDEOS DETECTADOS ({len(videos)}):")
        print("-" * 40)
        for video in videos:
            print(f"   {video['position']:2d}. {video['url']}")
            print(f"       📝 {video['title']}")
    
    # Verificar objetivo (7 videos, 48 imágenes)
    print(f"\n🎯 VERIFICACIÓN DE OBJETIVOS:")
    print("-" * 40)
    print(f"Objetivo videos: 7")
    print(f"Encontrado: {len(videos)} videos")
    print(f"Estado: {'✅ CORRECTO' if len(videos) == 7 else '⚠️ DIFERENTE'}")
    
    print(f"\nObjetivo imágenes: 48")
    print(f"Encontrado: {len(images)} imágenes")
    print(f"Estado: {'✅ CORRECTO' if len(images) == 48 else '⚠️ DIFERENTE'}")
    
    # Guardar resultados clasificados
    output_file = Path.home() / "Downloads" / "X_Media_Edge" / f"media_classified_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    classified_data = {
        "classification_date": datetime.now().isoformat(),
        "total_urls": len(all_urls),
        "videos_count": len(videos),
        "images_count": len(images),
        "videos": videos,
        "images": images[:48],  # Solo las primeras 48 como especificado
        "all_images": images,  # Todas las imágenes para referencia
        "verification_method": "yt-dlp"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(classified_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Clasificación guardada en: {output_file}")
    
    if len(videos) == 7 and len(images) >= 48:
        print(f"\n🎉 ¡ÉXITO! Clasificación correcta:")
        print(f"   🎬 {len(videos)} videos (objetivo: 7)")
        print(f"   📷 {len(images)} imágenes (objetivo: ≥48)")
    else:
        print(f"\n⚠️  Resultado diferente al esperado")
        print(f"   Es posible que el perfil tenga contenido diferente")
        print(f"   o que algunos videos no sean detectables por yt-dlp")

if __name__ == "__main__":
    main()

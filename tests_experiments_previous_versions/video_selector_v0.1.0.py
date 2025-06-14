#!/usr/bin/env python3
"""
Script para elegir qué videos descargar interactivamente
"""

import json
import subprocess
import sys
from pathlib import Path

def load_video_list():
    """Carga la lista de videos del JSON más reciente"""
    video_dir = Path.home() / "Downloads" / "X_Video_URLs"
    json_files = list(video_dir.glob("video_urls_simple_*.json"))
    
    if not json_files:
        print("❌ No se encontraron archivos JSON con videos")
        return None
    
    # Usar el más reciente
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    print(f"📄 Cargando videos desde: {latest_file.name}")
    print(f"📊 Total de videos disponibles: {data['total_videos']}")
    
    return data['videos']

def show_video_list(videos, start=0, count=10):
    """Muestra una lista de videos"""
    print(f"\n📋 Videos {start+1}-{min(start+count, len(videos))} de {len(videos)}:")
    print("=" * 80)
    
    for i in range(start, min(start + count, len(videos))):
        video = videos[i]
        print(f"{i+1:2d}. {video['url']}")
        if video['tweet_text'] and video['tweet_text'] != 'Sin texto':
            text = video['tweet_text'][:60] + "..." if len(video['tweet_text']) > 60 else video['tweet_text']
            print(f"    💬 {text}")
        print()

def download_video(url):
    """Descarga un video específico"""
    print(f"⬇️  Descargando: {url}")
    
    cmd = [
        "yt-dlp", 
        "--cookies-from-browser", "edge",
        "-o", "~/Downloads/Videos/%(title)s.%(ext)s",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Descarga exitosa!")
        else:
            print(f"❌ Error en descarga: {result.stderr}")
    except Exception as e:
        print(f"❌ Error ejecutando yt-dlp: {e}")

def main():
    """Función principal"""
    print("🎬 Selector Interactivo de Videos")
    print("=" * 50)
    
    videos = load_video_list()
    if not videos:
        return
    
    current_page = 0
    page_size = 10
    
    while True:
        show_video_list(videos, current_page * page_size, page_size)
        
        print("Opciones:")
        print("  1-N:  Descargar video número N")
        print("  'n':  Siguiente página")
        print("  'p':  Página anterior") 
        print("  'a':  Descargar TODOS los videos")
        print("  'q':  Salir")
        print()
        
        choice = input("¿Qué deseas hacer? ").strip().lower()
        
        if choice == 'q':
            print("👋 ¡Hasta luego!")
            break
        elif choice == 'n':
            if (current_page + 1) * page_size < len(videos):
                current_page += 1
            else:
                print("⚠️  Ya estás en la última página")
        elif choice == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                print("⚠️  Ya estás en la primera página")
        elif choice == 'a':
            print(f"⚠️  ¿Estás seguro de descargar TODOS los {len(videos)} videos? (s/n)")
            confirm = input().strip().lower()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                for i, video in enumerate(videos, 1):
                    print(f"\n📹 Descargando {i}/{len(videos)}: {video['url']}")
                    download_video(video['url'])
            break
        elif choice.isdigit():
            video_num = int(choice)
            if 1 <= video_num <= len(videos):
                download_video(videos[video_num - 1]['url'])
            else:
                print(f"❌ Número inválido. Debe estar entre 1 y {len(videos)}")
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()

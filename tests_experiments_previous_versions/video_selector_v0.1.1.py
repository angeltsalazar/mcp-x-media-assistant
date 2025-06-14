#!/usr/bin/env python3
"""
Script para elegir qué videos e imágenes descargar interactivamente
"""

import json
import subprocess
import sys
import requests
from pathlib import Path

def load_video_list():
    """Carga la lista de medios del JSON más reciente"""
    video_dir = Path.home() / "Downloads" / "X_Video_URLs"
    json_files = list(video_dir.glob("video_urls_simple_*.json"))
    
    if not json_files:
        print("❌ No se encontraron archivos JSON con medios")
        return None
    
    # Usar el más reciente
    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    print(f"📄 Cargando medios desde: {latest_file.name}")
    
    return data['videos']

def filter_by_type(medias, media_type='video'):
    """Filtra videos o imágenes según el tipo"""
    if media_type == 'video':
        filtered = [m for m in medias if m['original_link'].endswith('/video/1')]
    else:  # photo
        filtered = [m for m in medias if m['original_link'].endswith('/photo/1')]
    
    return filtered

def show_media_list(media_items, start=0, count=10, media_type='video'):
    """Muestra una lista de videos o imágenes"""
    type_emoji = "🎬" if media_type == 'video' else "🖼️"
    type_name = "Videos" if media_type == 'video' else "Imágenes"
    
    print(f"\n📋 {type_name} {start+1}-{min(start+count, len(media_items))} de {len(media_items)}:")
    print("=" * 80)
    
    for i in range(start, min(start + count, len(media_items))):
        item = media_items[i]
        print(f"{i+1:2d}. {type_emoji} {item['url']}")
        if item['tweet_text'] and item['tweet_text'] != 'Sin texto':
            text = item['tweet_text'][:60] + "..." if len(item['tweet_text']) > 60 else item['tweet_text']
            print(f"    💬 {text}")
        print()

def download_video(url):
    """Descarga un video específico"""
    print(f"⬇️  Descargando video: {url}")
    
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

def download_image(item):
    """Descarga una imagen específica"""
    print(f"⬇️  Descargando imagen: {item['url']}")
    
    # Crear directorio si no existe
    download_dir = Path.home() / "Downloads" / "X_Images"
    download_dir.mkdir(exist_ok=True)
    
    try:
        # Convertir URL a formato de imagen de alta calidad
        # Cambiar /status/ID a /status/ID/photo/1 y luego obtener la imagen real
        base_url = item['url']
        
        # Hacer request para obtener la página y extraer la imagen real
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        # Intentar descargar directamente desde la URL original  
        img_urls_to_try = [
            f"{base_url}/photo/1:large",
            f"{base_url}/photo/1:orig",
            f"{base_url}/photo/1"
        ]
        
        downloaded = False
        for img_url_try in img_urls_to_try:
            try:
                response = requests.get(img_url_try, headers=headers, stream=True, timeout=10)
                if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
                    # Generar nombre de archivo
                    filename = f"img_{item['status_id']}.jpg"
                    filepath = download_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    print(f"✅ Imagen guardada: {filepath}")
                    downloaded = True
                    break
            except:
                continue
        
        if not downloaded:
            print(f"❌ No se pudo descargar la imagen. Intenta usar yt-dlp manualmente:")
            print(f"   yt-dlp --cookies-from-browser edge '{item['url']}'")
            
    except Exception as e:
        print(f"❌ Error descargando imagen: {e}")
        print(f"💡 Intenta usar yt-dlp manualmente:")
        print(f"   yt-dlp --cookies-from-browser edge '{item['url']}'")

def main():
    """Función principal"""
    print("🎬🖼️  Selector Interactivo de Videos e Imágenes")
    print("=" * 50)
    
    all_medias = load_video_list()
    if not all_medias:
        return
    
    # Por defecto mostrar videos
    current_type = 'video'
    current_medias = filter_by_type(all_medias, current_type)
    
    # Contar totales
    total_videos = len(filter_by_type(all_medias, 'video'))
    total_images = len(filter_by_type(all_medias, 'photo'))
    
    print(f"📊 Total disponible: {total_videos} videos, {total_images} imágenes")
    
    current_page = 0
    page_size = 10
    
    while True:
        show_media_list(current_medias, current_page * page_size, page_size, current_type)
        
        print("Opciones:")
        print("  1-N:  Descargar elemento número N")
        print("  'v':  Mostrar videos")
        print("  'i':  Mostrar imágenes") 
        print("  'n':  Siguiente página")
        print("  'p':  Página anterior") 
        print("  'a':  Descargar TODOS los elementos mostrados")
        print("  'q':  Salir")
        print()
        
        choice = input("¿Qué deseas hacer? ").strip().lower()
        
        if choice == 'q':
            print("👋 ¡Hasta luego!")
            break
        elif choice == 'v':
            current_type = 'video'
            current_medias = filter_by_type(all_medias, current_type)
            current_page = 0
            print(f"🎬 Cambiando a vista de videos ({len(current_medias)} disponibles)")
        elif choice == 'i':
            current_type = 'photo'
            current_medias = filter_by_type(all_medias, current_type) 
            current_page = 0
            print(f"🖼️  Cambiando a vista de imágenes ({len(current_medias)} disponibles)")
        elif choice == 'n':
            if (current_page + 1) * page_size < len(current_medias):
                current_page += 1
            else:
                print("⚠️  Ya estás en la última página")
        elif choice == 'p':
            if current_page > 0:
                current_page -= 1
            else:
                print("⚠️  Ya estás en la primera página")
        elif choice == 'a':
            type_name = "videos" if current_type == 'video' else "imágenes"
            print(f"⚠️  ¿Estás seguro de descargar TODOS los {len(current_medias)} {type_name}? (s/n)")
            confirm = input().strip().lower()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                for i, item in enumerate(current_medias, 1):
                    print(f"\n� Descargando {i}/{len(current_medias)}")
                    if current_type == 'video':
                        download_video(item['url'])
                    else:
                        download_image(item)
            break
        elif choice.isdigit():
            item_num = int(choice)
            if 1 <= item_num <= len(current_medias):
                item = current_medias[item_num - 1]
                if current_type == 'video':
                    download_video(item['url'])
                else:
                    download_image(item)
            else:
                print(f"❌ Número inválido. Debe estar entre 1 y {len(current_medias)}")
        else:
            print("❌ Opción no válida")

if __name__ == "__main__":
    main()

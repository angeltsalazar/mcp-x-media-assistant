#!/usr/bin/env python3
"""
Script para elegir qué videos e imágenes descargar interactivamente
Trabaja desde archivos de caché para evitar reescanear
Marca URLs como procesadas en el mismo archivo de caché
"""

import json
import subprocess
import sys
import os
import time
import random
from pathlib import Path
import random
import asyncio
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import argparse


# ===== DELAY ORGÁNICO =====
def get_organic_delay(base_delay=2, variance=0.5, min_delay=1, max_delay=5):
    """
    Genera un delay orgánico más realista

    Args:
        base_delay: Delay base en segundos
        variance: Varianza del delay (porcentaje del base_delay)
        min_delay: Delay mínimo en segundos
        max_delay: Delay máximo en segundos

    Returns:
        float: Delay en segundos
    """
    # Aplicar varianza gaussiana
    variance_seconds = base_delay * variance
    delay = random.gauss(base_delay, variance_seconds)

    # Aplicar límites
    delay = max(min_delay, min(max_delay, delay))

    return delay


def apply_organic_delay(base_delay=2, variance=0.5, min_delay=1, max_delay=5):
    """
    Aplica un delay orgánico con mensaje informativo

    Args:
        base_delay: Delay base en segundos
        variance: Varianza del delay
        min_delay: Delay mínimo en segundos
        max_delay: Delay máximo en segundos
    """
    delay = get_organic_delay(base_delay, variance, min_delay, max_delay)
    print(f"⏳ Esperando {delay:.1f}s (delay orgánico)...")
    time.sleep(delay)


def load_user_config(name_param):
    """Carga la configuración de un usuario específico por nombre o friendlyname"""
    config_path = Path("config_files/x_usernames.json")

    if not config_path.exists():
        print(f"❌ No se encontró el archivo de configuración: {config_path}")
        return None, None

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Buscar primero por clave directa (nombre del usuario)
    if name_param in config:
        return config[name_param], name_param

    # Buscar por friendlyname
    for username, user_data in config.items():
        if user_data.get("friendlyname") == name_param:
            return user_data, username

    print(f"❌ Usuario '{name_param}' no encontrado en la configuración")
    print(f"📝 Usuarios disponibles: {list(config.keys())}")
    print(
        f"📝 Nombres amigables disponibles: {[data.get('friendlyname', 'N/A') for data in config.values()]}"
    )
    return None, None


def load_cached_posts(username):
    """Carga el archivo de posts cacheados del usuario"""
    cache_path = Path(f"cache/{username}_processed_posts.json")

    if not cache_path.exists():
        print(f"❌ No se encontró archivo de caché: {cache_path}")
        return None

    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"📄 Cargando caché desde: {cache_path}")
    return data, cache_path


def save_cached_posts(data, cache_path):
    """Guarda el archivo de posts cacheados actualizado"""
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 Caché actualizado: {cache_path}")


def extract_media_from_posts(posts_data, username, limit=None):
    """Extrae información de medios desde los posts cacheados"""
    media_items = []

    # El formato real del caché es: {"processed_posts": {"post_id": {"processed_date": "..."}}}
    processed_posts = posts_data.get("processed_posts", {})

    count = 0
    videos_found = 0

    for post_id, post_data in processed_posts.items():
        # Solo procesar posts que tienen media_type: "video"
        if post_data.get("media_type") != "video":
            continue

        videos_found += 1

        # Verificar si ya fue procesado para video
        if post_data.get("video_processed", False):
            continue

        # Generar URL del post
        post_url = f"https://x.com/{username}/status/{post_id}"

        # Generar URL del video usando el formato indicado por el usuario
        video_url = f"{post_url}/video/1"

        # Crear entrada de video
        video_item = {
            "post_id": post_id,
            "url": video_url,
            "original_link": video_url,
            "tweet_text": f"Post ID: {post_id}",
            "post_url": post_url,
            "media_type": "video",
            "processed_date": post_data.get("processed_at", "unknown"),
        }

        media_items.append(video_item)

        count += 1
        if limit and count >= limit:
            break

    print(f"🎬 Videos encontrados: {videos_found}")
    print(f"📊 Videos pendientes por procesar: {len(media_items)}")

    return media_items


def _get_organic_delay(base_delay: float = 2.0) -> float:
    """
    Calcula un tiempo de espera orgánico y aleatorio para simular comportamiento humano en descargas.
    """
    # Variación aleatoria del ±40% del tiempo base
    variation = random.uniform(-0.4, 0.6)  # -40% a +60% para mayor naturalidad
    delay = base_delay * (1 + variation)

    # Asegurar que esté dentro del rango deseado (1.2 - 3.2 segundos)
    delay = max(1.2, min(3.2, delay))

    # Ocasionalmente agregar pausas más largas (8% de probabilidad)
    if random.random() < 0.08:
        delay += random.uniform(2.0, 4.0)  # Pausa larga ocasional
        print(f"   ⏱️  Aplicando pausa larga entre videos: {delay:.2f}s")

    return delay


def _add_download_delay(current_index: int, total_items: int):
    """
    Añade delay orgánico entre descargas de videos múltiples.
    Solo aplica delay si no es el último elemento.
    """
    if current_index < total_items - 1:  # No delay después del último video
        delay = _get_organic_delay()
        print(f"   ⏸️  Esperando {delay:.2f}s antes del siguiente video...")
        time.sleep(delay)


def mark_post_as_video_processed(posts_data, post_id):
    """Marca un post como procesado para video en el caché"""
    processed_posts = posts_data.get("processed_posts", {})

    if post_id in processed_posts:
        processed_posts[post_id]["video_processed"] = True
        processed_posts[post_id]["video_processed_at"] = datetime.now().isoformat()
        return True
    else:
        print(f"⚠️  Post {post_id} no encontrado en caché")
        return False


def download_video(item, posts_data, cache_path, user_config):
    """Descarga un video específico y marca como procesado"""
    print(f"⬇️  Descargando video: {item['url']}")

    # Usar el directorio de descarga del usuario
    download_dir = user_config.get("directory_download", "~/Downloads/Videos")

    # Crear el directorio si no existe
    os.makedirs(os.path.expanduser(download_dir), exist_ok=True)

    print(f"📁 Directorio de descarga: {download_dir}")

    # Usar la ruta relativa de yt-dlp en el venv
    import os
    from pathlib import Path

    script_dir = Path(__file__).parent.absolute()
    venv_ytdlp = script_dir / ".venv" / "bin" / "yt-dlp"
    cmd = [
        str(venv_ytdlp),
        "--cookies-from-browser",
        "edge",
        "-o",
        f"{download_dir}/%(title)s.%(ext)s",
        item["url"],
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Descarga exitosa!")
            # Marcar como procesado usando el post_id
            if mark_post_as_video_processed(posts_data, item["post_id"]):
                save_cached_posts(posts_data, cache_path)
                print("✅ Marcado como procesado en caché")
        else:
            print(f"❌ Error en descarga: {result.stderr}")
    except Exception as e:
        print(f"❌ Error ejecutando yt-dlp: {e}")


def download_image(item, posts_data, cache_path):
    """Funcionalidad de imágenes removida - usar edge_x_downloader_clean.py"""
    print("� Nota: Para descargar imágenes usa:")
    print("   python3 edge_x_downloader_clean.py")
    return


def show_media_list(media_items, start, count, media_type):
    """Muestra una lista paginada de elementos multimedia"""
    type_emoji = "🎬" if media_type == "video" else "🖼️"

    print(
        f"\n{type_emoji} {media_type.title()}s disponibles (página {start//count + 1}):"
    )
    print("-" * 60)

    end = min(start + count, len(media_items))
    if start >= len(media_items):
        print("❌ No hay más elementos")
        return

    for i in range(start, end):
        item = media_items[i]
        print(f"{i+1:2d}. {type_emoji} {item['url']}")
        if item.get("tweet_text") and item["tweet_text"] != "Sin texto":
            text = (
                item["tweet_text"][:60] + "..."
                if len(item["tweet_text"]) > 60
                else item["tweet_text"]
            )
            print(f"    💬 {text}")
        print()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Selector de videos desde caché")
    parser.add_argument(
        "--name",
        required=True,
        help="Nombre del usuario o friendlyname (configuración)",
    )
    parser.add_argument("--limit", type=int, help="Límite de posts a procesar")
    parser.add_argument(
        "--list-only",
        action="store_true",
        help="Solo listar videos, no descargar (para MCP)",
    )
    parser.add_argument(
        "--download-all",
        action="store_true",
        help="Descargar todos los videos automáticamente (para MCP)",
    )
    parser.add_argument(
        "--download-indices",
        help="Descargar videos específicos por índices separados por comas (para MCP)",
    )

    args = parser.parse_args()

    if args.list_only:
        run_list_only_mode(args)
        return

    if args.download_all:
        run_download_all_mode(args)
        return

    if args.download_indices:
        run_download_indices_mode(args)
        return

    # Modo interactivo normal
    run_interactive_mode(args)


def run_list_only_mode(args):
    """Modo solo listar videos para MCP"""
    user_config, config_key = load_user_config(args.name)
    if not user_config:
        return

    username = user_config.get("username", config_key)
    posts_data, cache_path = load_cached_posts(config_key)
    if not posts_data:
        return

    all_medias = extract_media_from_posts(posts_data, username, args.limit)
    if not all_medias:
        print("❌ No se encontraron videos pendientes para procesar")
        return

    print(f"📊 Videos disponibles para {user_config.get('friendlyname', config_key)}:")
    for i, item in enumerate(all_medias, 1):
        print(f"{i:2d}. {item['url']}")
        if item.get("tweet_text") and item["tweet_text"] != "Sin texto":
            text = (
                item["tweet_text"][:60] + "..."
                if len(item["tweet_text"]) > 60
                else item["tweet_text"]
            )
            print(f"    💬 {text}")

    print(f"\n📈 Total: {len(all_medias)} videos pendientes")


def run_download_all_mode(args):
    """Modo descargar todos los videos para MCP"""
    user_config, config_key = load_user_config(args.name)
    if not user_config:
        return

    username = user_config.get("username", config_key)
    posts_data, cache_path = load_cached_posts(config_key)
    if not posts_data:
        return

    all_medias = extract_media_from_posts(posts_data, username, args.limit)
    if not all_medias:
        print("❌ No se encontraron videos pendientes para procesar")
        return

    print(f"🔄 Descargando {len(all_medias)} videos...")

    for i, item in enumerate(all_medias, 1):
        print(f"\n🔄 Descargando {i}/{len(all_medias)}: {item['url']}")
        download_video(item, posts_data, cache_path, user_config)

        # Aplicar delay orgánico solo si no es el último video
        if i < len(all_medias):
            _add_download_delay(i - 1, len(all_medias))

    print("✅ Descarga masiva completada")


def run_download_indices_mode(args):
    """Modo descargar videos específicos por índices para MCP"""
    try:
        indices = [int(x.strip()) for x in args.download_indices.split(",")]
    except ValueError:
        print("❌ Índices inválidos. Deben ser números separados por comas.")
        return

    user_config, config_key = load_user_config(args.name)
    if not user_config:
        return

    username = user_config.get("username", config_key)
    posts_data, cache_path = load_cached_posts(config_key)
    if not posts_data:
        return

    all_medias = extract_media_from_posts(posts_data, username, args.limit)
    if not all_medias:
        print("❌ No se encontraron videos pendientes para procesar")
        return

    # Validar índices
    valid_indices = []
    for idx in indices:
        if 1 <= idx <= len(all_medias):
            valid_indices.append(idx)
        else:
            print(f"⚠️ Índice {idx} fuera de rango (1-{len(all_medias)})")

    if not valid_indices:
        print("❌ No hay índices válidos para descargar")
        return

    print(f"🔄 Descargando {len(valid_indices)} videos seleccionados...")

    for i, idx in enumerate(valid_indices, 1):
        item = all_medias[idx - 1]  # Convertir a índice base 0
        print(f"\n🔄 Descargando {i}/{len(valid_indices)}: {item['url']}")
        download_video(item, posts_data, cache_path, user_config)

        # Aplicar delay orgánico solo si no es el último video
        if i < len(valid_indices):
            _add_download_delay(i - 1, len(valid_indices))

    print("✅ Descarga de videos seleccionados completada")


def run_interactive_mode(args):
    """Modo interactivo original"""
    print("🎬🖼️  Selector Interactivo de Videos (desde caché)")
    print("=" * 60)

    # Cargar configuración del usuario (por nombre o friendlyname)
    user_config, config_key = load_user_config(args.name)
    if not user_config:
        return

    username = user_config.get("username", config_key)
    friendlyname = user_config.get("friendlyname", config_key)
    download_dir = user_config.get("directory_download", "~/Downloads/Videos")

    print(f"👤 Usuario objetivo: {username}")
    print(f"💝 Nombre amigable: {friendlyname}")
    print(f"📁 Directorio de descarga: {download_dir}")

    # Cargar caché del usuario (usar la clave de configuración)
    posts_data, cache_path = load_cached_posts(config_key)
    if not posts_data:
        return

    # Extraer medios desde el caché (con el username real)
    all_medias = extract_media_from_posts(posts_data, username, args.limit)
    if not all_medias:
        print("❌ No se encontraron videos pendientes para procesar")
        print("💡 Todos los videos en caché pueden estar ya procesados")
        return

    # Solo trabajamos con videos ahora
    current_medias = all_medias

    # Contar estadísticas
    processed_posts = posts_data.get("processed_posts", {})
    total_posts = len(processed_posts)

    # Contar posts con video
    video_posts = sum(
        1
        for post_data in processed_posts.values()
        if post_data.get("media_type") == "video"
    )

    # Contar videos ya procesados
    processed_videos = sum(
        1
        for post_data in processed_posts.values()
        if post_data.get("media_type") == "video"
        and post_data.get("video_processed", False)
    )

    print(f"📊 Total posts en caché: {total_posts}")
    print(f"🎬 Posts con video: {video_posts}")
    print(f"✅ Videos ya procesados: {processed_videos}")
    print(f"� Videos pendientes: {len(all_medias)}")
    if args.limit:
        print(f"🔢 Límite aplicado: {args.limit} posts")

    current_page = 0
    page_size = 10

    while True:
        show_media_list(current_medias, current_page * page_size, page_size, "video")

        print("Opciones:")
        print("  1-N:  Descargar video número N")
        print("  'n':  Siguiente página")
        print("  'p':  Página anterior")
        print("  'a':  Descargar TODOS los videos")
        print("  's':  Mostrar estadísticas")
        print("  'q':  Salir")

        choice = input("\n➤ Elige una opción: ").strip().lower()

        if choice == "q":
            print("👋 ¡Hasta luego!")
            break
        elif choice == "s":
            # Recalcular estadísticas actualizadas
            video_posts = sum(
                1
                for post_data in processed_posts.values()
                if post_data.get("media_type") == "video"
            )
            processed_videos = sum(
                1
                for post_data in processed_posts.values()
                if post_data.get("media_type") == "video"
                and post_data.get("video_processed", False)
            )

            print(f"\n📊 Estadísticas:")
            print(f"   Posts totales en caché: {total_posts}")
            print(f"   Posts con video: {video_posts}")
            print(f"   Videos ya procesados: {processed_videos}")
            print(f"   Videos pendientes: {len(current_medias)}")
            print(f"   Usuario: {username} ({friendlyname})")
            continue
        elif choice == "n":
            if (current_page + 1) * page_size < len(current_medias):
                current_page += 1
            else:
                print("⚠️  Ya estás en la última página")
        elif choice == "p":
            if current_page > 0:
                current_page -= 1
            else:
                print("⚠️  Ya estás en la primera página")
        elif choice == "a":
            print(
                f"⚠️  ¿Estás seguro de descargar TODOS los {len(current_medias)} videos? (s/n)"
            )
            confirm = input().strip().lower()
            if confirm in ["s", "si", "sí", "y", "yes"]:
                for i, item in enumerate(current_medias, 1):
                    print(f"\n🔄 Descargando {i}/{len(current_medias)}")
                    download_video(item, posts_data, cache_path, user_config)
                    _add_download_delay(
                        i - 1, len(current_medias)
                    )  # Añadir delay después de cada descarga
                    # Actualizar la lista para reflejar los cambios
                    current_medias = extract_media_from_posts(
                        posts_data, username, args.limit
                    )
                print("✅ Descarga masiva completada")
                break
        elif choice.isdigit():
            item_num = int(choice)
            if 1 <= item_num <= len(current_medias):
                item = current_medias[item_num - 1]
                download_video(item, posts_data, cache_path, user_config)
                # Actualizar la lista para reflejar los cambios
                current_medias = extract_media_from_posts(
                    posts_data, username, args.limit
                )
                if not current_medias:
                    print("🎉 ¡Todos los videos han sido procesados!")
                    break
            else:
                print(f"❌ Número inválido. Debe estar entre 1 y {len(current_medias)}")
        else:
            print("❌ Opción no válida")


if __name__ == "__main__":
    main()

"""
EJEMPLOS DE USO:

1. Procesar videos usando el nombre completo del usuario:
   python3 video_selector.py --name rachelc00k

2. Procesar videos usando el nombre amigable (friendlyname):
   python3 video_selector.py --name rachel

3. Procesar solo los primeros 10 videos:
   python3 video_selector.py --name rachel --limit 10

4. Procesar videos de otro usuario por nombre amigable:
   python3 video_selector.py --name nat --limit 20

FUNCIONAMIENTO:
- Acepta tanto nombres de usuario completos como nombres amigables (friendlyname)
- Lee directamente del archivo de caché del usuario (cache/{name}_processed_posts.json)
- Genera URLs de video usando el formato: https://x.com/{username}/status/{post_id}/video/1
- Solo procesa posts que tienen 'media_type': 'video' en el caché
- Descarga videos al directorio configurado en 'directory_download' para cada usuario
- Marca automáticamente videos como procesados en el caché
- Crea el directorio de descarga automáticamente si no existe

CONFIGURACIÓN REQUERIDA:
- config_files/x_usernames.json debe contener:
  * username: nombre real del usuario en X
  * friendlyname: nombre corto/amigable 
  * directory_download: directorio donde descargar los videos
- Debe existir el archivo de caché cache/{name}_processed_posts.json
- yt-dlp debe estar instalado y configurado con cookies de Edge

VENTAJAS:
- No necesita acceso directo a X/Twitter (usa URLs cacheadas)
- Descarga a directorios específicos por usuario
- Evita reescanear posts ya procesados
- Control granular de descarga individual o masiva
- Marcado automático de procesamiento en caché
- Soporte para nombres amigables más fáciles de recordar
"""

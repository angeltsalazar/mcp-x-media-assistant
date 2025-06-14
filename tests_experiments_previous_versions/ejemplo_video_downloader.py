#!/usr/bin/env python3
"""
Ejemplo de uso del sistema de descarga de videos
Este script muestra cómo usar la funcionalidad de descarga de videos
usando twittervideodownloader.com
"""

import asyncio
from edge_x_downloader import EdgeXDownloader

async def ejemplo_descarga_video():
    """
    Ejemplo específico para descargar el video mencionado
    """
    print("🎬 Ejemplo de Descarga de Video de X")
    print("=" * 50)
    
    # URL del video específico mencionado
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print(f"📹 Video objetivo: {video_url}")
    print()
    print("🔄 Proceso que se ejecutará:")
    print("   1. Abrir twittervideodownloader.com")
    print("   2. Esperar que cargue (título 'Twitter Video Downloader')")
    print("   3. Pegar la URL en el campo 'Tweet link'")
    print("   4. Hacer clic en 'Download'")
    print("   5. Esperar página con 'videos found in the Tweet'")
    print("   6. Seleccionar la opción de mayor calidad")
    print("   7. Obtener URL directa del video (.mp4)")
    print("   8. Descargar el video")
    print("   9. Preparar sitio para próximo video")
    print()
    
    respuesta = input("🚀 ¿Proceder con la descarga? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Cancelado por el usuario")
        return
    
    # Crear el descargador
    downloader = EdgeXDownloader()
    
    print("\n🎬 Iniciando proceso de descarga...")
    
    try:
        # Procesar el video para obtener la URL directa
        direct_url = await downloader.process_video_with_downloader_site(video_url)
        
        if direct_url:
            print(f"\n✅ URL directa obtenida: {direct_url}")
            
            # Descargar el video
            success = await downloader.download_video_from_direct_url(direct_url)
            
            if success:
                print("\n🎉 ¡Video descargado exitosamente!")
                print(f"📁 Ubicación: {downloader.download_dir}")
            else:
                print("\n❌ Error en la descarga del video")
        else:
            print("\n❌ No se pudo obtener la URL directa del video")
            
    except Exception as e:
        print(f"\n❌ Error durante el proceso: {e}")

async def ejemplo_multiples_videos():
    """
    Ejemplo para descargar múltiples videos
    """
    print("🎬 Ejemplo de Descarga de Múltiples Videos")
    print("=" * 50)
    
    # Lista de URLs de videos (puedes agregar más)
    video_urls = [
        "https://x.com/milewskaja_nat/status/1915047384612241420/video/1",
        # Agregar más URLs aquí según sea necesario
    ]
    
    print(f"📹 Videos a procesar: {len(video_urls)}")
    for i, url in enumerate(video_urls, 1):
        print(f"   {i}. {url}")
    
    print()
    respuesta = input("🚀 ¿Proceder con la descarga de todos los videos? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Cancelado por el usuario")
        return
    
    # Crear el descargador
    downloader = EdgeXDownloader()
    
    # Procesar todos los videos
    await downloader.process_video_urls(video_urls)

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("🎬 Sistema de Descarga de Videos de X")
    print("=" * 50)
    print("1. Descargar video específico (ejemplo predefinido)")
    print("2. Descargar múltiples videos")
    print("3. Ingresar URLs manualmente")
    print("4. Salir")
    print()

async def main():
    """Función principal del ejemplo"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("Selecciona una opción (1-4): ").strip()
            
            if opcion == "1":
                await ejemplo_descarga_video()
            elif opcion == "2":
                await ejemplo_multiples_videos()
            elif opcion == "3":
                # Modo interactivo para ingresar URLs
                print("\n📝 Ingresa las URLs de videos (línea vacía para terminar):")
                video_urls = []
                
                while True:
                    url = input("URL del video: ").strip()
                    if not url:
                        break
                    if "x.com" in url or "twitter.com" in url:
                        video_urls.append(url)
                        print(f"   ✅ Agregado: {url}")
                    else:
                        print("   ⚠️  URL no válida (debe contener x.com o twitter.com)")
                
                if video_urls:
                    downloader = EdgeXDownloader()
                    await downloader.process_video_urls(video_urls)
                else:
                    print("❌ No se ingresaron URLs válidas")
            elif opcion == "4":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

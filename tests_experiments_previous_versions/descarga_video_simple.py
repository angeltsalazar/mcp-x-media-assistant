#!/usr/bin/env python3
"""
Script simple para descargar el video específico con pausa manual para verificación
"""

import asyncio
from pathlib import Path
from edge_x_downloader import EdgeXDownloader

async def descargar_video_con_pausa_manual():
    """
    Descarga el video específico con pausa manual para verificación humana
    """
    print("🎬 Descarga de Video con Verificación Manual")
    print("=" * 60)
    
    # URL del video específico
    video_url = "https://x.com/milewskaja_nat/status/1915047384612241420/video/1"
    
    print(f"📹 Video objetivo: {video_url}")
    print()
    print("🔄 Proceso:")
    print("   1. Abrirá twittervideodownloader.com")
    print("   2. Si hay verificación CAPTCHA, tendrás 2 minutos para completarla")
    print("   3. El script continuará automáticamente después")
    print("   4. Descargará el video de mayor calidad")
    print()
    
    respuesta = input("🚀 ¿Continuar? (s/n): ").lower().strip()
    if respuesta not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Cancelado")
        return
    
    try:
        downloader = EdgeXDownloader()
        
        print(f"\n📁 Los videos se guardarán en: {downloader.download_dir}")
        print("\n🎬 Iniciando descarga...")
        
        # Procesar el video
        direct_url = await downloader.process_video_with_downloader_site(video_url)
        
        if direct_url:
            print(f"\n✅ URL directa obtenida: {direct_url}")
            
            # Descargar el video
            success = await downloader.download_video_from_direct_url(direct_url)
            
            if success:
                print("\n🎉 ¡Video descargado exitosamente!")
                print(f"📁 Ubicación: {downloader.download_dir}")
                
                # Mostrar archivos descargados
                videos = list(downloader.download_dir.glob("*.mp4"))
                if videos:
                    print(f"\n📋 Archivos descargados:")
                    for video in videos:
                        size_mb = video.stat().st_size / (1024 * 1024)
                        print(f"   📹 {video.name} ({size_mb:.2f} MB)")
            else:
                print("\n❌ Error en la descarga")
        else:
            print("\n❌ No se pudo obtener la URL directa del video")
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nℹ️  Consejos:")
        print("   • Verifica tu conexión a internet")
        print("   • Asegúrate de que la URL del video sea válida")
        print("   • El sitio puede estar temporalmente inaccesible")

if __name__ == "__main__":
    asyncio.run(descargar_video_con_pausa_manual())

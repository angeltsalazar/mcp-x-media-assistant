#!/usr/bin/env python3
"""
Demostración del extractor de URLs de videos de X
"""

import asyncio
import json
from pathlib import Path
from x_video_url_extractor import XVideoURLExtractor

async def demo_extraer_urls():
    """Demostración de extracción de URLs de videos"""
    print("🎬 Demo: Extractor de URLs de Videos de X")
    print("=" * 50)
    
    # Crear el extractor
    extractor = XVideoURLExtractor()
    
    # URL del perfil de medios
    profile_url = "https://x.com/milewskaja_nat/media"
    
    print(f"📹 Extrayendo URLs de: {profile_url}")
    print("⚠️  Asegúrate de estar logueado en X.com en Edge")
    print()
    
    try:
        # Extraer URLs de videos
        await extractor.extract_video_urls_from_profile(profile_url)
        
        if extractor.video_urls:
            print(f"\n✅ Extracción exitosa: {len(extractor.video_urls)} videos encontrados")
            
            # Mostrar algunos ejemplos
            print("\n📋 URLs de videos extraídas:")
            for i, video in enumerate(extractor.video_urls[:3], 1):
                print(f"   {i}. {video['url']}")
            
            if len(extractor.video_urls) > 3:
                print(f"   ... y {len(extractor.video_urls) - 3} más")
            
            # Guardar en JSON
            json_file = extractor.save_video_urls_to_json()
            
            print(f"\n💾 URLs guardadas en: {json_file}")
            print("\n💡 Para descargar los videos puedes usar:")
            print("   1. yt-dlp con el archivo JSON:")
            print(f'      yt-dlp --batch-file <(jq -r ".videos[].url" "{json_file}")')
            print("   2. O copiar las URLs manualmente desde el archivo JSON")
            
        else:
            print("\n⚠️  No se encontraron videos")
            print("💡 Posibles causas:")
            print("   • El perfil no tiene videos públicos")
            print("   • No estás logueado en X.com")
            print("   • El perfil requiere seguimiento")
    
    except Exception as e:
        print(f"\n❌ Error durante la extracción: {e}")

def mostrar_archivo_json_ejemplo():
    """Muestra cómo se ve un archivo JSON de salida"""
    print("\n📄 Ejemplo de archivo JSON generado:")
    print("=" * 40)
    
    ejemplo = {
        "extraction_date": "2025-06-11T14:30:22.123456",
        "total_videos": 2,
        "videos": [
            {
                "url": "https://x.com/milewskaja_nat/status/1915047384612241420/video/1",
                "tweet_info": {
                    "text": "Este es un ejemplo de tweet con video...",
                    "author": "@milewskaja_nat",
                    "timestamp": "2024-10-21T15:30:00.000Z"
                },
                "found_at": "2025-06-11T14:30:22.123456",
                "position": 1
            },
            {
                "url": "https://x.com/milewskaja_nat/status/1234567890123456789/video/1",
                "tweet_info": {
                    "text": "Otro tweet con video...",
                    "author": "@milewskaja_nat", 
                    "timestamp": "2024-10-20T12:15:00.000Z"
                },
                "found_at": "2025-06-11T14:30:23.456789",
                "position": 2
            }
        ]
    }
    
    print(json.dumps(ejemplo, indent=2, ensure_ascii=False))

async def main():
    """Función principal del demo"""
    print("🎬 Sistema de Extracción de URLs de Videos de X")
    print("=" * 60)
    print("Este script extrae URLs de videos sin descargarlos.")
    print("Las URLs se guardan en JSON para descarga posterior.")
    print()
    
    print("Opciones:")
    print("1. Ejecutar extracción de URLs")
    print("2. Ver ejemplo de archivo JSON")
    print("3. Salir")
    print()
    
    while True:
        try:
            opcion = input("Selecciona una opción (1-3): ").strip()
            
            if opcion == "1":
                await demo_extraer_urls()
                break
            elif opcion == "2":
                mostrar_archivo_json_ejemplo()
                break
            elif opcion == "3":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Usa 1, 2 o 3.")
        
        except KeyboardInterrupt:
            print("\n👋 Interrumpido por el usuario. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

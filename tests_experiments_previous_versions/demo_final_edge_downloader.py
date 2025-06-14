#!/usr/bin/env python3
"""
Script de demostración final - edge_x_downloader_clean.py mejorado
Demuestra la detección precisa de 55 URLs (7 videos + 48 imágenes) y descarga solo las imágenes
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime

async def demo_extraction_and_download():
    """Demostración completa del script mejorado"""
    print("🎬 DEMOSTRACIÓN FINAL - X Media Downloader Mejorado")
    print("=" * 70)
    print("📊 Objetivo: Detectar 55 URLs (7 videos + 48 imágenes)")
    print("📷 Funcionalidad: Descargar solo las primeras 48 imágenes")
    print("📄 Generar JSON con clasificación precisa")
    print()
    
    # Importar el script mejorado
    from edge_x_downloader_clean import EdgeXDownloader
    
    downloader = EdgeXDownloader()
    
    print("🚀 Iniciando proceso completo...")
    print("   1. Extracción de URLs con clasificación precisa")
    print("   2. Generación de JSON con medios clasificados")
    print("   3. Descarga de imágenes (limitado a 48)")
    print()
    
    # Ejecutar el proceso completo
    await downloader.download_with_edge("https://x.com/milewskaja_nat/media", use_automation_profile=True)
    
    print("\n🎯 RESUMEN FINAL:")
    print("=" * 50)
    print(f"📹 Total URLs encontradas: {len(downloader.media_urls)}")
    print(f"🎬 Videos detectados: {len(downloader.video_urls)}")
    print(f"📷 Imágenes detectadas: {len(downloader.image_urls)}")
    
    if len(downloader.media_urls) == 55 and len(downloader.video_urls) == 7 and len(downloader.image_urls) == 48:
        print("✅ ¡OBJETIVO ALCANZADO! Detección precisa completada")
    else:
        print("⚠️  Resultados diferentes a los esperados")
    
    print("\n💡 FUNCIONALIDADES IMPLEMENTADAS:")
    print("   ✅ Detección precisa basada en original_link (/video/1 vs /photo/1)")
    print("   ✅ Control de duplicados por status_id")
    print("   ✅ Generación de JSON clasificado")
    print("   ✅ Descarga selectiva (solo imágenes)")
    print("   ✅ Limitación a 48 imágenes procesadas")
    
    # Mostrar ejemplos de URLs detectadas
    if downloader.video_urls:
        print(f"\n🎬 EJEMPLOS DE VIDEOS DETECTADOS:")
        for i, video in enumerate(downloader.video_urls[:3], 1):
            print(f"   {i}. {video['url']}")
            print(f"      📎 {video['original_link']}")
    
    if downloader.image_urls:
        print(f"\n📷 EJEMPLOS DE IMÁGENES DETECTADAS:")
        for i, image in enumerate(downloader.image_urls[:3], 1):
            print(f"   {i}. {image['url']}")
            print(f"      📎 {image['original_link']}")

async def main():
    """Función principal"""
    print("🧪 ¿Ejecutar demostración completa? (incluye descarga de imágenes)")
    print("⚠️  Esto abrirá Edge y descargará archivos reales")
    
    response = input("Continuar? (s/n): ").lower().strip()
    if response not in ['s', 'si', 'sí', 'y', 'yes']:
        print("❌ Demostración cancelada")
        print()
        print("💡 Para probar solo la extracción sin descarga:")
        print("   python3 test_edge_media_extraction.py")
        return
    
    await demo_extraction_and_download()
    
    print("\n🏁 ¡Demostración completada!")
    print("📊 Revisa los archivos JSON generados para ver la clasificación detallada")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de medios de edge_x_downloader_clean.py
Este script ejecuta solo la parte de extracción sin descargar archivos
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
from playwright.async_api import async_playwright

# Importar la clase modificada
from edge_x_downloader_clean import EdgeXDownloader

class TestMediaExtractor(EdgeXDownloader):
    """Versión de prueba que solo extrae URLs sin descargar"""
    
    def __init__(self):
        super().__init__()
        print("🧪 Modo de prueba: Solo extracción de URLs, sin descarga")
    
    async def test_extraction(self, profile_url="https://x.com/milewskaja_nat/media"):
        """Ejecuta solo la extracción de URLs para verificar precisión"""
        print(f"🔬 Probando extracción de URLs de: {profile_url}")
        
        async with async_playwright() as p:
            edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
            
            # Usar perfil automatizado
            automation_dir = Path.home() / "Library" / "Application Support" / "Microsoft Edge Automation"
            automation_dir.mkdir(exist_ok=True)
            
            context = await p.chromium.launch_persistent_context(
                user_data_dir=str(automation_dir),
                headless=False,
                executable_path=edge_path,
                args=['--no-first-run', '--no-default-browser-check', '--window-size=1920,1080']
            )
            
            try:
                page = await context.new_page()
                
                # Navegar al perfil
                print("🌐 Navegando al perfil...")
                await page.goto(profile_url)
                await self._organic_delay(3000, 5000)
                
                # Verificar login
                login_required = await page.query_selector('[data-testid="loginButton"], [href="/login"]')
                if login_required:
                    print("⚠️  Necesitas estar logueado. Esperando login...")
                    try:
                        await page.wait_for_function(
                            "!document.querySelector('[data-testid=\"loginButton\"]')",
                            timeout=60000
                        )
                        print("✅ Login detectado")
                    except:
                        print("❌ Timeout esperando login")
                        return
                
                # Buscar pestaña Media
                print("🔍 Buscando pestaña Media...")
                media_tab_clicked = False
                
                media_selectors = [
                    'a[href$="/media"]',
                    'a[aria-label*="Media"]',
                    'a:has-text("Media")',
                    '[role="tab"]:has-text("Media")'
                ]
                
                for selector in media_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"   ✅ Encontrada pestaña Media: {selector}")
                            await element.click()
                            media_tab_clicked = True
                            await self._organic_delay(2000, 3000)
                            break
                    except:
                        continue
                
                if not media_tab_clicked:
                    print("   ⚠️  No se encontró pestaña Media, intentando URL directa...")
                    if not profile_url.endswith('/media'):
                        media_url = profile_url.replace('/media', '') + '/media'
                        await page.goto(media_url)
                        await self._organic_delay(3000, 5000)
                
                # Extraer URLs
                print("🔍 Iniciando extracción de URLs...")
                await self._extract_all_status_urls(page)
                
                # Hacer scroll para cargar más
                await self._scroll_and_extract_urls(page, max_scrolls=3)  # Menos scrolls para prueba
                
                # Mostrar resultados
                self._show_test_results()
                
                # Guardar JSON
                if self.media_urls:
                    json_file = self.save_media_json()
                    print(f"📄 Archivo JSON guardado: {json_file}")
                    
                    # Verificar que tengamos el número correcto de URLs
                    self._verify_target_numbers()
                
            finally:
                await context.close()
    
    def _show_test_results(self):
        """Muestra resultados detallados de la prueba"""
        print(f"\n📊 RESULTADOS DE LA PRUEBA:")
        print("=" * 50)
        print(f"📹 Total URLs extraídas: {len(self.media_urls)}")
        print(f"🎬 Videos detectados: {len(self.video_urls)}")
        print(f"📷 Imágenes detectadas: {len(self.image_urls)}")
        print(f"🆔 Status IDs únicos: {len(self.processed_status_ids)}")
        print(f"🔗 URLs únicas: {len(self.unique_urls)}")
        
        if self.media_urls:
            print(f"\n📋 DESGLOSE POR TIPO:")
            print("-" * 30)
            
            # Mostrar primeros videos
            if self.video_urls:
                print(f"🎬 VIDEOS ({len(self.video_urls)}):")
                for i, video in enumerate(self.video_urls[:3], 1):
                    print(f"   {i}. {video['url']}")
                if len(self.video_urls) > 3:
                    print(f"   ... y {len(self.video_urls) - 3} más")
            
            print()
            
            # Mostrar primeras imágenes
            if self.image_urls:
                print(f"📷 IMÁGENES ({len(self.image_urls)}):")
                for i, image in enumerate(self.image_urls[:5], 1):
                    print(f"   {i}. {image['url']}")
                if len(self.image_urls) > 5:
                    print(f"   ... y {len(self.image_urls) - 5} más")
    
    def _verify_target_numbers(self):
        """Verifica si alcanzamos los números objetivo (55 total: 7 videos, 48 imágenes)"""
        print(f"\n🎯 VERIFICACIÓN DE OBJETIVOS:")
        print("-" * 40)
        
        target_total = 55
        target_videos = 7
        target_images = 48
        
        total_found = len(self.media_urls)
        videos_found = len(self.video_urls)
        images_found = len(self.image_urls)
        
        print(f"Objetivo total: {target_total} URLs")
        print(f"Encontrado: {total_found} URLs")
        print(f"Estado: {'✅ CORRECTO' if total_found >= target_total else '⚠️ INSUFICIENTE' if total_found > 0 else '❌ FALLIDO'}")
        
        print(f"\nObjetivo videos: {target_videos}")
        print(f"Encontrado: {videos_found} videos")
        print(f"Estado: {'✅ CORRECTO' if videos_found >= target_videos else '⚠️ INSUFICIENTE' if videos_found > 0 else '❌ FALLIDO'}")
        
        print(f"\nObjetivo imágenes: {target_images}")
        print(f"Encontrado: {images_found} imágenes")
        print(f"Estado: {'✅ CORRECTO' if images_found >= target_images else '⚠️ INSUFICIENTE' if images_found > 0 else '❌ FALLIDO'}")
        
        if total_found >= target_total and videos_found >= target_videos and images_found >= target_images:
            print(f"\n🎉 ¡ÉXITO! Se alcanzaron todos los objetivos")
        elif total_found > 0:
            print(f"\n⚠️  Extracción parcial - puede necesitar más scrolls o el perfil tiene menos contenido")
        else:
            print(f"\n❌ Error en la extracción - revisar configuración")

async def main():
    """Función principal de prueba"""
    print("🧪 PRUEBA DE EXTRACCIÓN DE MEDIOS")
    print("=" * 60)
    print("Este script verifica que edge_x_downloader_clean.py")
    print("tenga la misma precisión que simple_video_extractor.py")
    print("Objetivo: 55 URLs (7 videos + 48 imágenes)")
    print()
    
    # Importar playwright aquí para verificar instalación
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Error: playwright no está instalado")
        print("💡 Instalar con: pip3 install playwright")
        print("💡 Después ejecutar: playwright install")
        return
    
    tester = TestMediaExtractor()
    await tester.test_extraction()
    
    print("\n🏁 ¡Prueba completada!")

if __name__ == "__main__":
    asyncio.run(main())

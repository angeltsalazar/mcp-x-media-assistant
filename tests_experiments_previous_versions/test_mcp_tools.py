#!/usr/bin/env python3
"""
Script de prueba para las herramientas MCP del X Media Downloader
"""

import asyncio
import json
import sys
import os

# Importar los manejadores desde el servidor MCP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.config.user_config import UserConfigManager
    from modules.core.orchestrator import EdgeXDownloader
    from modules.utils.url_utils import URLUtils
    print("✅ Módulos importados correctamente")
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

async def test_system_status():
    """Probar la herramienta de estado del sistema"""
    print("\n🔍 Probando system_status...")
    
    try:
        # Usuarios configurados
        config = UserConfigManager.load_user_config()
        users_count = len(config)
        
        # Archivos de caché
        cache_dir = "cache"
        cache_files = []
        if os.path.exists(cache_dir):
            cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
        
        # Módulos disponibles
        modules_status = {
            "UserConfigManager": "✅ Disponible",
            "EdgeXDownloader": "✅ Disponible",
            "URLUtils": "✅ Disponible"
        }
        
        result = f"""📊 **Estado del Sistema X Media Downloader**

👥 **Usuarios configurados:** {users_count}
{chr(10).join([f"• {data.get('friendlyname', username)} (@{username})" for username, data in config.items()])}

📁 **Archivos de caché:** {len(cache_files)}
{chr(10).join([f"• {f}" for f in cache_files[:5]])}
{'• ... y más' if len(cache_files) > 5 else ''}

🔧 **Módulos disponibles:**
{chr(10).join([f"• {name}: {status}" for name, status in modules_status.items()])}

📂 **Directorio de trabajo:** `{os.getcwd()}`
🐍 **Python:** `{sys.executable}`
"""
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"❌ Error obteniendo estado del sistema: {str(e)}"
        print(error_msg)
        return error_msg

async def test_download_simulation():
    """Simular una descarga sin ejecutar realmente"""
    print("\n📥 Probando simulación de descarga...")
    
    try:
        # Parámetros de prueba
        username = "milewskaja_nat"  # Usuario existente
        config = UserConfigManager.load_user_config()
        
        if username not in config:
            return f"❌ Usuario {username} no encontrado en configuración"
        
        user_data = config[username]
        download_dir = user_data['directory_download']
        profile_url = URLUtils.build_profile_url(username)
        
        result = f"""🎯 **Simulación de Descarga**

👤 **Usuario:** {user_data.get('friendlyname', username)} (@{username})
🔗 **URL del perfil:** {profile_url}
📁 **Directorio de descarga:** `{download_dir}`
🔧 **Modo:** auto (simulación)
🔢 **Límite:** 5 posts (prueba)

⚠️ **Nota:** Esta es una simulación. La descarga real requiere Edge y puede ser lenta.

✅ **Configuración válida - Lista para descarga real**
"""
        
        print(result)
        return result
        
    except Exception as e:
        error_msg = f"❌ Error en simulación: {str(e)}"
        print(error_msg)
        return error_msg

async def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del servidor MCP...")
    
    # Probar estado del sistema
    await test_system_status()
    
    # Probar simulación de descarga
    await test_download_simulation()
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    asyncio.run(main())

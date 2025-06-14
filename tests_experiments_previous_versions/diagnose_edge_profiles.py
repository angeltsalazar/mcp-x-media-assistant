#!/usr/bin/env python3
"""
Script de diagnóstico para verificar perfiles de Edge y credenciales
"""

import os
import json
from pathlib import Path

def check_edge_profiles():
    """Verificar qué perfiles de Edge existen y su contenido"""
    print("🔍 Diagnóstico de Perfiles de Microsoft Edge")
    print("=" * 50)
    
    edge_base = Path.home() / "Library" / "Application Support" / "Microsoft Edge"
    
    if not edge_base.exists():
        print("❌ Microsoft Edge no está instalado o no se encuentra")
        return
    
    print(f"📁 Directorio base de Edge: {edge_base}")
    print()
    
    # Verificar perfil principal (Default)
    default_profile = edge_base / "Default"
    print("1. 🏠 PERFIL PRINCIPAL (Default)")
    print("-" * 30)
    if default_profile.exists():
        print("✅ Existe")
        
        # Verificar cookies
        cookies_file = default_profile / "Cookies"
        if cookies_file.exists():
            size_mb = cookies_file.stat().st_size / (1024 * 1024)
            print(f"   🍪 Cookies: ✅ Existe ({size_mb:.2f} MB)")
        else:
            print("   🍪 Cookies: ❌ No existe")
        
        # Verificar datos de login
        login_data = default_profile / "Login Data"
        if login_data.exists():
            size_mb = login_data.stat().st_size / (1024 * 1024)
            print(f"   🔐 Login Data: ✅ Existe ({size_mb:.2f} MB)")
        else:
            print("   🔐 Login Data: ❌ No existe")
        
        # Verificar historial
        history_file = default_profile / "History"
        if history_file.exists():
            size_mb = history_file.stat().st_size / (1024 * 1024)
            print(f"   📜 Historial: ✅ Existe ({size_mb:.2f} MB)")
        else:
            print("   📜 Historial: ❌ No existe")
            
    else:
        print("❌ No existe")
    
    print()
    
    # Verificar perfil de automatización
    automation_profile = edge_base / "EdgeAutomation"
    print("2. 🤖 PERFIL DE AUTOMATIZACIÓN (EdgeAutomation)")
    print("-" * 45)
    if automation_profile.exists():
        print("✅ Existe")
        
        automation_default = automation_profile / "Default"
        if automation_default.exists():
            print("   📁 Carpeta Default: ✅ Existe")
            
            # Verificar cookies
            cookies_file = automation_default / "Cookies"
            if cookies_file.exists():
                size_mb = cookies_file.stat().st_size / (1024 * 1024)
                print(f"   🍪 Cookies: ✅ Existe ({size_mb:.2f} MB)")
            else:
                print("   🍪 Cookies: ❌ No existe")
            
            # Verificar datos de login
            login_data = automation_default / "Login Data"
            if login_data.exists():
                size_mb = login_data.stat().st_size / (1024 * 1024)
                print(f"   🔐 Login Data: ✅ Existe ({size_mb:.2f} MB)")
            else:
                print("   🔐 Login Data: ❌ No existe")
            
            # Verificar historial
            history_file = automation_default / "History"
            if history_file.exists():
                size_mb = history_file.stat().st_size / (1024 * 1024)
                print(f"   📜 Historial: ✅ Existe ({size_mb:.2f} MB)")
            else:
                print("   📜 Historial: ❌ No existe")
        else:
            print("   📁 Carpeta Default: ❌ No existe")
    else:
        print("❌ No existe")
    
    print()
    print("💡 RECOMENDACIONES:")
    print("-" * 20)
    
    # Análisis y recomendaciones
    default_has_data = (default_profile / "Cookies").exists() and (default_profile / "Login Data").exists()
    automation_has_data = (automation_profile / "Default" / "Cookies").exists() and (automation_profile / "Default" / "Login Data").exists()
    
    if default_has_data and automation_has_data:
        print("✅ Ambos perfiles tienen datos")
        print("   • Usa --auto para perfil de automatización (recomendado)")
        print("   • Usa --main-profile para perfil principal")
    elif default_has_data and not automation_has_data:
        print("⚠️  Solo el perfil principal tiene datos")
        print("   • Usa --main-profile para usar tus credenciales")
        print("   • O inicia sesión en el perfil de automatización")
    elif not default_has_data and automation_has_data:
        print("✅ Solo el perfil de automatización tiene datos")
        print("   • Usa --auto (configuración actual)")
    else:
        print("❌ Ningún perfil tiene datos")
        print("   • Necesitas iniciar sesión en X en algún perfil")
    
    print()
    print("🚀 COMANDOS SUGERIDOS:")
    print("-" * 25)
    if default_has_data:
        print("   python3 edge_x_downloader_clean.py --name nat --main-profile")
    if automation_has_data:
        print("   python3 edge_x_downloader_clean.py --name nat --auto")
    print("   python3 edge_x_downloader_clean.py --name nat --select")

if __name__ == "__main__":
    check_edge_profiles()

#!/usr/bin/env python3
"""
Script de gestión de usuarios para X Media Downloader
Permite añadir, eliminar y modificar usuarios configurados
"""

import json
import os
from pathlib import Path
import argparse
import sys

CONFIG_FILE = "config_files/x_usernames.json"

def load_config():
    """Cargar configuración"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error al cargar configuración: {e}")
        return {}

def save_config(config):
    """Guardar configuración"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✅ Configuración guardada en {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar configuración: {e}")
        return False

def list_users():
    """Listar usuarios"""
    config = load_config()
    if not config:
        print("📝 No hay usuarios configurados")
        return
    
    print("👥 Usuarios configurados:")
    print("=" * 60)
    for i, (username, data) in enumerate(config.items(), 1):
        print(f"{i}. {data['friendlyname']}")
        print(f"   Username: @{username}")
        print(f"   Directorio: {data['directory_download']}")
        print()

def add_user():
    """Añadir nuevo usuario"""
    config = load_config()
    
    print("➕ Añadir nuevo usuario")
    print("=" * 30)
    
    friendlyname = input("🏷️  Nombre amigable: ").strip()
    if not friendlyname:
        print("❌ El nombre amigable no puede estar vacío")
        return
    
    # Verificar si el nombre amigable ya existe
    for user_data in config.values():
        if user_data.get('friendlyname') == friendlyname:
            print(f"❌ Ya existe un usuario con el nombre '{friendlyname}'")
            return
    
    username = input("📝 Username de X (sin @): ").strip()
    if username.startswith('@'):
        username = username[1:]
    
    if not username:
        print("❌ El username no puede estar vacío")
        return
    
    if username in config:
        print(f"❌ El username '@{username}' ya existe")
        return
    
    directory = input("📁 Directorio de descarga (Enter para usar por defecto): ").strip()
    if not directory:
        home_dir = Path.home()
        directory = str(home_dir / "Downloads" / f"X_Media_{friendlyname}")
        print(f"📁 Usando directorio por defecto: {directory}")
    
    # Crear directorio si no existe
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    user_data = {
        "friendlyname": friendlyname,
        "username": username,
        "directory_download": directory
    }
    
    config[username] = user_data
    
    if save_config(config):
        print(f"✅ Usuario '{friendlyname}' añadido correctamente")
        print(f"   Username: @{username}")
        print(f"   Directorio: {directory}")

def remove_user():
    """Eliminar usuario"""
    config = load_config()
    if not config:
        print("📝 No hay usuarios configurados")
        return
    
    print("➖ Eliminar usuario")
    print("=" * 20)
    
    # Mostrar usuarios con números
    users_list = list(config.items())
    for i, (username, data) in enumerate(users_list, 1):
        print(f"{i}. {data['friendlyname']} (@{username})")
    
    try:
        choice = int(input("\n🔢 Selecciona el número del usuario a eliminar: "))
        if 1 <= choice <= len(users_list):
            username, user_data = users_list[choice - 1]
            friendlyname = user_data['friendlyname']
            
            confirm = input(f"❓ ¿Estás seguro de eliminar '{friendlyname}' (@{username})? (s/n): ").lower().strip()
            if confirm in ['s', 'si', 'sí', 'y', 'yes']:
                del config[username]
                if save_config(config):
                    print(f"✅ Usuario '{friendlyname}' eliminado correctamente")
            else:
                print("❌ Operación cancelada")
        else:
            print("❌ Número inválido")
    except ValueError:
        print("❌ Por favor ingresa un número válido")

def edit_user():
    """Editar usuario existente"""
    config = load_config()
    if not config:
        print("📝 No hay usuarios configurados")
        return
    
    print("✏️  Editar usuario")
    print("=" * 18)
    
    # Mostrar usuarios con números
    users_list = list(config.items())
    for i, (username, data) in enumerate(users_list, 1):
        print(f"{i}. {data['friendlyname']} (@{username})")
    
    try:
        choice = int(input("\n🔢 Selecciona el número del usuario a editar: "))
        if 1 <= choice <= len(users_list):
            username, user_data = users_list[choice - 1]
            
            print(f"\n📝 Editando: {user_data['friendlyname']} (@{username})")
            print("(Presiona Enter para mantener el valor actual)")
            
            # Editar nombre amigable
            new_friendlyname = input(f"🏷️  Nombre amigable [{user_data['friendlyname']}]: ").strip()
            if new_friendlyname:
                user_data['friendlyname'] = new_friendlyname
            
            # Editar directorio
            new_directory = input(f"📁 Directorio [{user_data['directory_download']}]: ").strip()
            if new_directory:
                user_data['directory_download'] = new_directory
                # Crear directorio si no existe
                Path(new_directory).mkdir(parents=True, exist_ok=True)
            
            if save_config(config):
                print(f"✅ Usuario actualizado correctamente")
        else:
            print("❌ Número inválido")
    except ValueError:
        print("❌ Por favor ingresa un número válido")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Gestor de Usuarios - X Media Downloader')
    parser.add_argument('--list-json', action='store_true', help='Listar usuarios en formato JSON')
    parser.add_argument('--add-json', action='store_true', help='Añadir usuario usando argumentos')
    parser.add_argument('--friendlyname', help='Nombre amigable del usuario')
    parser.add_argument('--username', help='Username de X (sin @)')
    parser.add_argument('--directory', help='Directorio de descarga')
    
    args = parser.parse_args()
    
    if args.list_json:
        list_users_json()
        return
    
    if args.add_json:
        if not all([args.friendlyname, args.username, args.directory]):
            print("❌ Para --add-json se requieren --friendlyname, --username y --directory")
            sys.exit(1)
        add_user_json(args.friendlyname, args.username, args.directory)
        return
    
    # Si no hay argumentos, ejecutar el menú interactivo
    interactive_menu()

def list_users_json():
    """Listar usuarios en formato JSON para MCP"""
    config = load_config()
    print(json.dumps(config, ensure_ascii=False, indent=2))

def add_user_json(friendlyname, username, directory):
    """Añadir usuario usando argumentos de línea de comandos"""
    config = load_config()
    
    # Verificar si el nombre amigable ya existe
    for user_data in config.values():
        if user_data.get('friendlyname') == friendlyname:
            print(f"❌ Ya existe un usuario con el nombre '{friendlyname}'")
            sys.exit(1)
    
    # Limpiar username
    if username.startswith('@'):
        username = username[1:]
    
    if username in config:
        print(f"❌ El username '@{username}' ya existe")
        sys.exit(1)
    
    # Crear directorio si no existe
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    user_data = {
        "friendlyname": friendlyname,
        "username": username,
        "directory_download": directory
    }
    
    config[username] = user_data
    
    if save_config(config):
        print(f"✅ Usuario '{friendlyname}' añadido correctamente")
    else:
        sys.exit(1)

def interactive_menu():
    """Menú interactivo original"""
    while True:
        print("\n🔧 Gestor de Usuarios - X Media Downloader")
        print("=" * 50)
        print("1. 👥 Listar usuarios")
        print("2. ➕ Añadir usuario")
        print("3. ➖ Eliminar usuario")
        print("4. ✏️  Editar usuario")
        print("5. 🚪 Salir")
        print()
        
        choice = input("🔢 Selecciona una opción (1-5): ").strip()
        
        if choice == '1':
            list_users()
        elif choice == '2':
            add_user()
        elif choice == '3':
            remove_user()
        elif choice == '4':
            edit_user()
        elif choice == '5':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida. Por favor selecciona 1-5.")

if __name__ == "__main__":
    main()

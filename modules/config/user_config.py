"""
Módulo para la gestión de la configuración de usuarios.
"""
import os
import json
from pathlib import Path

from .constants import CONFIG_FILE

class UserConfigManager:
    """
    Gestiona la carga, guardado y manipulación de la configuración
    de usuarios almacenada en un archivo JSON.
    """

    @staticmethod
    def load_user_config():
        """Cargar configuración de usuarios desde x_usernames.json"""
        if not os.path.exists(CONFIG_FILE):
            return {}
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error al cargar configuración: {e}")
            return {}

    @staticmethod
    def save_user_config(config):
        """Guardar configuración de usuarios en x_usernames.json"""
        try:
            # Asegurarse de que el directorio de configuración exista
            config_dir = Path(CONFIG_FILE).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuración guardada en {CONFIG_FILE}")
        except Exception as e:
            print(f"⚠️  Error al guardar configuración: {e}")

    @staticmethod
    def get_user_by_name(name):
        """Obtener información de usuario por nombre amigable"""
        config = UserConfigManager.load_user_config()
        for user_data in config.values():
            if user_data.get('friendlyname') == name:
                return user_data
        return None

    @staticmethod
    def add_new_user(name):
        """Añadir un nuevo usuario a la configuración"""
        config = UserConfigManager.load_user_config()
        
        print(f"🔧 Configurando nuevo usuario: {name}")
        username = input("📝 Ingresa el username de X (sin @): ").strip()
        if username.startswith('@'):
            username = username[1:]
        
        if not username:
            print("❌ El username no puede estar vacío")
            return None
        
        if username in config:
            print(f"⚠️  El username '{username}' ya existe en la configuración")
            existing_user = config[username]
            print(f"   Nombre amigable: {existing_user.get('friendlyname')}")
            print(f"   Directorio: {existing_user.get('directory_download')}")
            return existing_user
        
        directory = input("📁 Ingresa la ruta del directorio de descarga: ").strip()
        if not directory:
            home_dir = Path.home()
            directory = str(home_dir / "Downloads" / f"X_Media_{name}")
            print(f"📁 Usando directorio por defecto: {directory}")
        
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        user_data = {
            "friendlyname": name,
            "username": username,
            "directory_download": directory
        }
        
        config[username] = user_data
        UserConfigManager.save_user_config(config)
        
        return user_data

    @staticmethod
    def list_configured_users():
        """Listar todos los usuarios configurados"""
        config = UserConfigManager.load_user_config()
        if not config:
            print("📝 No hay usuarios configurados aún")
            return
        
        print("👥 Usuarios configurados:")
        print("=" * 50)
        for username, user_data in config.items():
            print(f"  • Nombre: {user_data.get('friendlyname')}")
            print(f"    Username: @{username}")
            print(f"    Directorio: {user_data.get('directory_download')}")
            print()
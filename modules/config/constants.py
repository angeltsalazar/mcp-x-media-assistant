"""
Módulo de constantes globales para la aplicación.
"""

# Archivo de configuración de usuarios
CONFIG_FILE = "config_files/x_usernames.json"

# Headers HTTP por defecto para las peticiones
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Límites y timeouts por defecto
MAX_SCROLLS_DEFAULT = 8  # Se ajusta dinámicamente según URLs necesarias
DOWNLOAD_TIMEOUT = 30
LOGIN_TIMEOUT = 300  # 5 minutos

# Patrones para clasificación de medios
VIDEO_PATTERNS = [
    r'/video/1/',
    r'\.mp4',
    r'\.m4v',
    r'\.webm',
    r'ext_tw_video',
    r'video\.twimg\.com',
    r'/amplify_video/',
    r'/tweet_video/',
    r'format=mp4'
]

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
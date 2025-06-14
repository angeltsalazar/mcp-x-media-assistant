"""
Módulo para la configuración y parsing de los argumentos de la línea de comandos.
"""
import argparse

class ArgumentParser:
    """
    Define y parsea los argumentos de la CLI para la aplicación.
    """
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='X Media Downloader - Optimizado para Microsoft Edge',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_epilog()
        )
        self._add_arguments()

    def parse_arguments(self) -> argparse.Namespace:
        """Parsea los argumentos de la línea de comandos."""
        return self.parser.parse_args()

    def _add_arguments(self):
        """Añade todos los argumentos al parser."""
        # Argumentos de usuario
        self.parser.add_argument('--name', '-n', help='Nombre amigable del usuario configurado')
        self.parser.add_argument('--username', '-u', help='Username de X directamente (sin @)')
        self.parser.add_argument('--list-users', action='store_true', help='Listar usuarios configurados')

        # Argumentos de navegador
        self.parser.add_argument('--auto', '-a', action='store_true', help='Usar perfil de automatización (por defecto)')
        self.parser.add_argument('--main-profile', action='store_true', help='Usar perfil principal de Edge')
        self.parser.add_argument('--temporal', '-t', action='store_true', help='Usar Edge temporal (sin datos persistentes)')
        self.parser.add_argument('--select', '-s', action='store_true', help='Mostrar menú para seleccionar modo de navegador')

        # Argumentos de descarga
        self.parser.add_argument('--directory', '-d', help='Directorio de descarga personalizado')
        self.parser.add_argument('--limit', '-l', type=int, default=100, 
                                help='Límite de URLs totales a procesar (por defecto: 100, usar 0 para sin límite)')
        self.parser.add_argument('--no-limit', action='store_true', 
                                help='Procesar todas las URLs disponibles sin límite')

    def _get_epilog(self) -> str:
        """Devuelve el texto de ayuda extendido para la CLI."""
        return """
Ejemplos de uso:
  python3 edge_x_downloader.py --name usuario1
  python3 edge_x_downloader.py --name usuario1 --auto
  python3 edge_x_downloader.py --username milewskaja_nat --main-profile
  python3 edge_x_downloader.py --username milewskaja_nat --limit 50
  python3 edge_x_downloader.py --list-users
  python3 edge_x_downloader.py --select

Modos de navegador:
  --auto            Perfil de automatización (recomendado, por defecto)
  --main-profile    Perfil principal donde tienes tus credenciales
  --temporal        Edge temporal sin datos persistentes
  --select          Seleccionar modo interactivamente

Opciones de descarga:
  --limit NUM       Limitar a NUM URLs totales (por defecto: 100, usar 0 para sin límite)
  --no-limit        Procesar todas las URLs disponibles sin límite
        """
"""
Módulo de logging unificado para la aplicación.
"""

class Logger:
    """
    Proporciona métodos estáticos para mostrar mensajes con formato en la consola.
    """

    @staticmethod
    def info(message: str):
        """Muestra un mensaje informativo."""
        print(f"💡 {message}")

    @staticmethod
    def warning(message: str):
        """Muestra un mensaje de advertencia."""
        print(f"⚠️  {message}")

    @staticmethod
    def error(message: str):
        """Muestra un mensaje de error."""
        print(f"❌ {message}")

    @staticmethod
    def success(message: str):
        """Muestra un mensaje de éxito."""
        print(f"✅ {message}")

    @staticmethod
    def progress(current: int, total: int, item: str):
        """Muestra el progreso de una operación."""
        print(f"⬇️  [{current}/{total}] {item}...")
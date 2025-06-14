# 🤖 X Media Downloader - Model Control Protocol (MCP) Server

## Descripción

El servidor MCP permite que asistentes de IA interactúen con el sistema X Media Downloader de forma estructurada y automatizada. Proporciona 5 herramientas principales que cubren todas las funcionalidades del sistema.

## Instalación

### Método Rápido (Recomendado)

```bash
# Ejecutar el script de instalación automática
chmod +x install_mcp.sh
./install_mcp.sh
```

### Método Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Instalar SDK de MCP específicamente
pip install mcp

# 3. Instalar navegadores de Playwright
playwright install chromium

# 4. Verificar yt-dlp
yt-dlp --version
```

## Uso

### Iniciar el Servidor MCP

```bash
# Iniciar con configuración por defecto
python3 mcp_server.py

# Personalizar host y puerto
python3 mcp_server.py --host 0.0.0.0 --port 8080
```

El servidor estará disponible en `http://localhost:8000` (o el puerto especificado).

## Herramientas Disponibles

### 1. `manage_users` - Gestión de Usuarios

Administra la configuración de usuarios del sistema.

**Parámetros:**
- `action` (str): "list", "add", "remove", "edit"
- `user_data` (dict, opcional): Datos del usuario para add/edit
  - `friendlyname`: Nombre amigable del usuario
  - `username`: Username de X (sin @)
  - `directory_download`: Directorio donde guardar las descargas

**Ejemplos:**
```python
# Listar usuarios configurados
await mcp_client.call_tool("manage_users", {"action": "list"})

# Añadir nuevo usuario
await mcp_client.call_tool("manage_users", {
    "action": "add",
    "user_data": {
        "friendlyname": "Fotografa",
        "username": "usuario_ejemplo",
        "directory_download": "/Users/mi_usuario/Downloads/X_Media_Fotografa"
    }
})
```

### 2. `download_images` - Descarga de Imágenes y Extracción de Posts

Descarga imágenes y extrae información de posts (incluyendo videos) de un usuario de X.

**Parámetros:**
- `name` (str, opcional): Nombre amigable del usuario configurado
- `username` (str, opcional): Username de X directo
- `limit` (int, opcional): Límite de posts nuevos a procesar (default: 100)
- `no_limit` (bool): Procesar todos los posts sin límite
- `directory` (str, opcional): Directorio personalizado de descarga
- `mode` (str): "auto" (default), "temporal", "select"

**Ejemplos:**
```python
# Descargar imágenes de un usuario configurado
await mcp_client.call_tool("download_images", {
    "name": "fotografa",
    "limit": 50,
    "mode": "auto"
})

# Descarga sin límite usando username directo
await mcp_client.call_tool("download_images", {
    "username": "usuario_ejemplo",
    "no_limit": True,
    "mode": "temporal"
})
```

### 3. `select_videos` - Selección y Descarga de Videos

Trabaja con videos desde el caché generado por `download_images`.

**Parámetros:**
- `name` (str): Nombre amigable del usuario
- `action` (str): "list", "download_all", "download_selected"
- `video_indices` (list[int], opcional): Lista de índices para download_selected
- `limit` (int, opcional): Límite de posts a considerar del caché

**Ejemplos:**
```python
# Listar videos disponibles
await mcp_client.call_tool("select_videos", {
    "name": "fotografa",
    "action": "list"
})

# Descargar todos los videos
await mcp_client.call_tool("select_videos", {
    "name": "fotografa", 
    "action": "download_all"
})

# Descargar videos específicos (índices 1, 3, 5)
await mcp_client.call_tool("select_videos", {
    "name": "fotografa",
    "action": "download_selected",
    "video_indices": [1, 3, 5]
})
```

### 4. `system_status` - Estado del Sistema

Obtiene información completa sobre el estado del sistema.

**Sin parámetros**

**Ejemplo:**
```python
# Obtener estado completo
status = await mcp_client.call_tool("system_status", {})
```

**Información devuelta:**
- Existencia de archivos de configuración
- Archivos de caché disponibles  
- Scripts disponibles
- Estado de dependencias (Playwright, yt-dlp)
- Versiones instaladas

### 5. `system_config` - Gestión de Configuración

Gestiona la configuración global del sistema.

**Parámetros:**
- `action` (str): "get", "set", "reset"
- `config_data` (dict, opcional): Datos de configuración para "set"

**Ejemplos:**
```python
# Obtener configuración actual
await mcp_client.call_tool("system_config", {"action": "get"})

# Establecer nueva configuración
await mcp_client.call_tool("system_config", {
    "action": "set",
    "config_data": {
        "usuario1": {
            "friendlyname": "Usuario Ejemplo",
            "username": "usuario1",
            "directory_download": "/ruta/personalizada"
        }
    }
})

# Reiniciar configuración
await mcp_client.call_tool("system_config", {"action": "reset"})
```

## Flujo de Trabajo Típico con MCP

### 1. Configuración Inicial

```python
# Verificar estado del sistema
status = await mcp_client.call_tool("system_status", {})

# Listar usuarios existentes
users = await mcp_client.call_tool("manage_users", {"action": "list"})

# Añadir nuevo usuario si es necesario
await mcp_client.call_tool("manage_users", {
    "action": "add",
    "user_data": {
        "friendlyname": "MiUsuario",
        "username": "mi_usuario_x", 
        "directory_download": "/Users/yo/Downloads/X_Media_MiUsuario"
    }
})
```

### 2. Descarga de Medios

```python
# Descargar imágenes y extraer información de posts
await mcp_client.call_tool("download_images", {
    "name": "MiUsuario",
    "limit": 100,
    "mode": "auto"
})
```

### 3. Gestión de Videos

```python
# Listar videos disponibles
videos = await mcp_client.call_tool("select_videos", {
    "name": "MiUsuario",
    "action": "list"
})

# Descargar videos específicos
await mcp_client.call_tool("select_videos", {
    "name": "MiUsuario",
    "action": "download_selected", 
    "video_indices": [1, 2, 5, 8]
})
```

## Arquitectura Técnica

### Estructura del Servidor

```
mcp_server.py
├── XMediaDownloaderMCP (clase principal)
├── setup_tools() - Configura las 5 herramientas MCP
├── _manage_users() - Implementación de gestión de usuarios
├── _download_images() - Implementación de descarga de imágenes  
├── _select_videos() - Implementación de selector de videos
├── _system_status() - Implementación de estado del sistema
└── _system_config() - Implementación de configuración
```

### Integración con Scripts Existentes

El servidor MCP actúa como una capa de abstracción que:

1. **Recibe llamadas MCP** del asistente de IA
2. **Traduce a argumentos** de línea de comandos
3. **Ejecuta los scripts** correspondientes:
   - `manage_users.py` (con nuevos argumentos `--list-json`, `--add-json`)
   - `edge_x_downloader_clean.py` (argumentos existentes)
   - `video_selector.py` (con nuevos argumentos `--list-only`, `--download-all`, `--download-indices`)
4. **Procesa la salida** y la devuelve en formato MCP

### Dependencias Adicionales

```txt
mcp>=0.4.0              # SDK del Model Control Protocol
```

## Configuración Avanzada

### Archivo de Configuración MCP

El archivo `mcp_config.json` contiene la configuración para clientes MCP:

```json
{
  "mcpServers": {
    "x-media-downloader": {
      "command": "python3",
      "args": ["mcp_server.py"],
      "cwd": "/ruta/al/proyecto",
      "description": "Servidor MCP para X Media Downloader"
    }
  }
}
```

### Variables de Entorno

```bash
# Puerto del servidor (opcional)
export MCP_SERVER_PORT=8000

# Host del servidor (opcional) 
export MCP_SERVER_HOST=localhost

# Nivel de logging (opcional)
export MCP_LOG_LEVEL=INFO
```

## Seguridad y Consideraciones

### Autenticación de Navegador

- El sistema usa cookies de Microsoft Edge para autenticación en X.com
- **Requisito**: Sesión activa en X.com en Edge antes de usar las herramientas
- Los videos requieren `yt-dlp` con acceso a las cookies del navegador

### Permisos de Archivos

- El servidor necesita permisos de lectura/escritura en:
  - `config_files/` - Configuración de usuarios
  - `cache/` - Archivos de caché de posts procesados
  - Directorios de descarga configurados para cada usuario

### Límites y Rate Limiting

- El sistema incluye delays orgánicos automáticos
- Los límites de posts (`--limit`) ayudan a controlar la carga de red
- Recomendado usar límites razonables para evitar sobrecarga de X.com

## Solución de Problemas

### Error: "MCP SDK no está instalado"

```bash
pip install mcp
```

### Error: "No se pudo hacer clic en la pestaña Media"

- Verificar que Edge tiene una sesión activa en X.com
- Probar con modo `"temporal"` en lugar de `"auto"`

### Error: "yt-dlp requiere autenticación" 

```bash
# Verificar que yt-dlp puede acceder a las cookies
yt-dlp --cookies-from-browser edge --list-formats "https://x.com/ejemplo/status/123/video/1"
```

### Error: "Usuario no encontrado"

- Usar la herramienta `manage_users` con `action: "list"` para ver usuarios disponibles
- Verificar que `config_files/x_usernames.json` existe y es válido

## Desarrollo y Extensión

### Añadir Nueva Herramienta MCP

1. **Definir la herramienta** en `setup_tools()`:
```python
@self.server.tool("nueva_herramienta")
async def nueva_herramienta(parametro: str) -> List[TextContent]:
    """Descripción de la nueva herramienta"""
    return await self._nueva_herramienta(parametro)
```

2. **Implementar la lógica**:
```python
async def _nueva_herramienta(self, parametro: str) -> List[TextContent]:
    """Implementación de la nueva herramienta"""
    # Lógica aquí
    return [TextContent(type="text", text="Resultado")]
```

### Testing

```bash
# Probar herramientas individualmente
python3 -c "
import asyncio
from mcp_server import XMediaDownloaderMCP

async def test():
    server = XMediaDownloaderMCP()
    result = await server._system_status()
    print(result[0].text)

asyncio.run(test())
"
```

## Ejemplos de Uso con Diferentes Clientes MCP

### Cliente Python Directo

```python
import asyncio
from mcp.client import Client

async def main():
    client = Client("http://localhost:8000")
    
    # Listar usuarios
    users = await client.call_tool("manage_users", {"action": "list"})
    print(users)
    
    # Descargar imágenes
    result = await client.call_tool("download_images", {
        "name": "usuario_ejemplo",
        "limit": 50
    })
    print(result)

asyncio.run(main())
```

### Integración con Claude Desktop

Agregar a la configuración de Claude Desktop:

```json
{
  "mcpServers": {
    "x-media-downloader": {
      "command": "python3",
      "args": ["/ruta/completa/al/mcp_server.py"],
      "cwd": "/ruta/completa/al/proyecto"
    }
  }
}
```

---

## Resumen

El servidor MCP para X Media Downloader proporciona una interfaz estándar para que asistentes de IA gestionen completamente el sistema de descarga de medios de X. Las 5 herramientas cubren desde la configuración de usuarios hasta la descarga selectiva de videos, manteniendo toda la funcionalidad del sistema original mientras proporcionan una interfaz programática robusta.

**Ventajas del MCP:**
- 🤖 Integración perfecta con asistentes de IA
- 🔧 Interfaz estándar y documentada
- 🚀 Automatización completa del flujo de trabajo
- 🛡️ Mantiene todas las funcionalidades de seguridad
- 📊 Información estructurada de estado y resultados

---

*Actualizado: 13 de junio de 2025*
*Versión MCP: 1.0*

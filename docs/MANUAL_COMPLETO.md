# 🎬 Sistema Completo de Descarga de Medios de X (Twitter)

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Instalación y Requisitos](#instalación-y-requisitos)
3. [Estructura de Archivos](#estructura-de-archivos)
4. [Guía de Uso Rápido](#guía-de-uso-rápido)
5. [Manual Detallado](#manual-detallado)
6. [Formatos de Salida](#formatos-de-salida)
7. [Solución de Problemas](#solución-de-problemas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 📖 Descripción General

Este sistema automatiza completamente la descarga de medios de X (Twitter) mediante dos componentes principales:

### 🖼️ **Para Imágenes**: Descarga Directa
- Descarga automáticamente todas las imágenes de un perfil
- Guarda archivos en alta calidad
- No requiere herramientas adicionales

### 🎬 **Para Videos**: Extracción de URLs + yt-dlp
- **Paso 1**: Extrae automáticamente URLs de todos los videos
- **Paso 2**: Usa yt-dlp para descargar los videos con autenticación
- **Ventaja**: Evita problemas con sitios externos y CAPTCHAs

---

## 🛠️ Instalación y Requisitos

### Prerrequisitos
- **macOS** (optimizado para Microsoft Edge)
- **Python 3.8+**
- **Microsoft Edge** instalado
- **Sesión activa en X.com** en Edge

### Instalación de Dependencias

```bash
# 1. Clonar o descargar los archivos del proyecto
cd /ruta/al/proyecto

# 2. Instalar dependencias de Python
pip install playwright requests

# 3. Instalar navegador para Playwright
playwright install chromium

# 4. Instalar yt-dlp para descarga de videos
pip install yt-dlp

# 5. Verificar instalación
python3 simple_video_extractor.py --help
yt-dlp --version
```

---

## 📁 Estructura de Archivos

### 🚀 **Archivos Principales**

```
📂 Proyecto/
├── 🖼️ edge_x_downloader_clean.py     # Descargador de imágenes y videos (modular)
├── 👤 manage_users.py                # Script para gestionar la configuración de usuarios
├── 🎯 video_selector.py              # NUEVO: Selector interactivo de videos desde caché
├── 📖 MANUAL_COMPLETO.md             # Este manual
└── 📋 README_SISTEMA_SIMPLIFICADO.md # Resumen técnico
```

### 📁 **Archivos de Salida**

```
📂 ~/Downloads/
├── 📂 X_Video_URLs/                  # URLs de videos en JSON
│   └── 📄 video_urls_simple_YYYYMMDD_HHMMSS.json
├── 📂 X_Media_Edge/                  # Imágenes descargadas
│   └── 📂 session_YYYYMMDD_HHMMSS/
└── 📂 Videos/                        # Videos descargados por yt-dlp
    └── 📹 Título del Video.mp4
```

### 🗂️ **Herramientas Especializadas (Cada una con su propósito)**

- **`simple_video_extractor.py`** ⭐ - Extractor principal (más eficiente, deduplicado)
- **`video_selector.py`** 🎯 - Selector interactivo de videos (lo más fácil de usar)
- **`edge_x_downloader_clean.py`** 🖼️ - Descargador solo de imágenes (sin videos)
- **`x_video_url_extractor.py`** 📜 - Extractor alternativo (más información por video)
- **`edge_x_downloader.py`** 🔧 - Herramienta todo-en-uno (imágenes + videos)
- **Scripts quick/simple/mcp**** ⚡ - Versiones especializadas para diferentes casos de uso

---

## ⚡ Guía de Uso Rápido

### 🎬 **Descargar Videos (Proceso Completo)**

```bash
# Paso 1: Extraer URLs de videos
python3 simple_video_extractor.py

# Paso 2A: Selector interactivo (RECOMENDADO)
python3 video_selector.py

# Paso 2B: Descargar todos los videos automáticamente
yt-dlp --cookies-from-browser edge --batch-file <(jq -r '.videos[].url' ~/Downloads/X_Video_URLs/video_urls_simple_*.json)
```

### 🖼️ **Descargar Imágenes**

```bash
# Descarga directa de imágenes
python3 edge_x_downloader_clean.py
```

### 🎯 **Video Específico**

```bash
# Descargar un video específico directamente
yt-dlp --cookies-from-browser edge "https://x.com/usuario/status/123/video/1"
```

---

## 📖 Manual Detallado

### 👤 Gestión de Usuarios (`manage_users.py`)

Este script permite administrar la configuración de los usuarios para los demás scripts. La configuración se guarda en `config_files/x_usernames.json`.

**Funcionalidades:**
- Listar usuarios configurados.
- Añadir nuevos usuarios (nombre amigable, username de X, directorio de descarga).
- Eliminar usuarios existentes.
- Editar la información de usuarios existentes.

**Uso:**
```bash
python3 manage_users.py
```
Se presentará un menú interactivo para realizar las operaciones.

**Estructura del archivo `config_files/x_usernames.json`:**
```json
{
  "nombre_usuario_x": {
    "friendlyname": "Nombre Amigable",
    "username": "nombre_usuario_x",
    "directory_download": "/ruta/a/descargas/NombreAmigable"
  },
  // ...otros usuarios
}
```

### 🖼️ Descarga de Imágenes y Extracción de URLs de Video (`edge_x_downloader_clean.py`)

Este es el script principal para descargar imágenes y extraer información de posts (incluyendo videos) de un perfil de X. Utiliza la configuración de `config_files/x_usernames.json` gestionada por `manage_users.py`.

**Características Principales:**
- **Selección de Usuario**: Mediante el argumento `--name <friendlyname>` o `--username <username_x>`.
- **Modos de Navegador**: Automático (perfil de Edge existente) o Temporal (nueva instancia de Edge).
- **Límites**: Controla cuántos posts nuevos procesar con `--limit <numero>` o `--no-limit` para todos.
- **Descarga de Imágenes**: Guarda imágenes directamente en el directorio configurado para el usuario.
- **Cache de Posts**: Guarda información de los posts procesados en `cache/<username>_processed_posts.json`. Este caché incluye `media_type` ('image' o 'video') y otras metadata.
- **Nombres de Archivo Únicos**: Las imágenes se guardan con el formato `{status_id}-{nombre_original}.jpg`.
- **Manejo de Múltiples Imágenes**: Descarga todas las imágenes de carruseles.

**Uso Básico:**
```bash
# Listar usuarios configurados
python3 edge_x_downloader_clean.py --list-users

# Descargar medios de un usuario configurado (modo automático, límite por defecto)
python3 edge_x_downloader_clean.py --name <nombre_amigable>

# Descargar medios de un usuario, especificando límite y modo temporal
python3 edge_x_downloader_clean.py --name <nombre_amigable> --limit 50 --temporal
```

**Argumentos Importantes:**
- `--name <friendlyname>`: Nombre amigable del usuario (definido en `manage_users.py`).
- `--username <username_x>`: Username de X (si no está en la configuración, se crea uno básico).
- `--directory <path>`: Sobrescribe el directorio de descarga configurado.
- `--limit <numero>`: Límite de posts nuevos a procesar (por defecto 100). `0` o `--no-limit` para sin límite.
- `--auto`: Usa el perfil de Edge automatizado (por defecto).
- `--temporal`: Usa una instancia temporal de Edge.
- `--select`: Permite elegir el modo de navegador interactivamente.
- `--list-users`: Muestra los usuarios configurados y sale.

**Funcionamiento del Límite (`--limit`):**
- El límite se aplica a los posts *nuevos* (no presentes en el caché `cache/<username>_processed_posts.json`).
- Los posts ya cacheados se cargan y se tienen en cuenta, pero no cuentan para este límite.
- Esto permite procesar perfiles grandes de forma incremental.

**Salida:**
- **Imágenes**: En el directorio especificado en la configuración del usuario (ej: `~/Downloads/X_Media_NombreAmigable/`).
- **Caché de Posts**: `cache/<username_config_key>_processed_posts.json`. Este archivo es crucial para `video_selector.py`.
  ```json
  // Ejemplo de cache/<username>_processed_posts.json
  {
    "processed_posts": {
      "<post_id_1>": {
        "media_type": "image",
        "urls": ["url_imagen1"],
        "tweet_text": "Texto del tweet",
        "processed_at": "timestamp"
      },
      "<post_id_2>": {
        "media_type": "video", // Importante para video_selector.py
        "urls": ["url_video_pagina"], // URL de la página del video, no directa
        "tweet_text": "Otro texto",
        "processed_at": "timestamp",
        "video_processed": false // Usado por video_selector.py
      }
    }
  }
  ```

### 🎬 Selección y Descarga de Videos (`video_selector.py`)

Este script permite seleccionar y descargar interactivamente videos de un usuario, utilizando los archivos de caché generados por `edge_x_downloader_clean.py`.

**Características Principales:**
- **Trabaja desde Caché**: No accede a X.com directamente, evitando re-escaneos.
- **Interactivo**: Muestra una lista paginada de videos pendientes de descarga.
- **Selección Múltiple o Individual**: Permite descargar videos uno por uno, o todos los pendientes.
- **Marcado Automático**: Marca los videos como `video_processed: true` en el archivo de caché para no volver a mostrarlos.
- **Usa `yt-dlp`**: Descarga los videos utilizando `yt-dlp` con cookies del navegador Edge para autenticación.
- **Configuración de Usuario**: Utiliza `config_files/x_usernames.json` para obtener el nombre de usuario real y el directorio de descarga de videos.

**Requisitos Previos:**
1. Haber ejecutado `edge_x_downloader_clean.py` para el usuario deseado, generando el archivo `cache/<username_config_key>_processed_posts.json`.
2. `yt-dlp` debe estar instalado y accesible en el PATH.
3. Microsoft Edge debe tener una sesión activa en X.com para que `yt-dlp` pueda usar las cookies.

**Uso:**
```bash
# Seleccionar y descargar videos para un usuario (usando su nombre amigable)
python3 video_selector.py --name <nombre_amigable>

# Limitar el número de posts a considerar del caché (opcional)
python3 video_selector.py --name <nombre_amigable> --limit 20
```

**Argumentos:**
- `--name <friendlyname>`: (Obligatorio) Nombre amigable del usuario cuya caché de videos se procesará.
- `--limit <numero>`: (Opcional) Considera solo los N posts más recientes del caché que contengan videos no procesados.

**Funcionamiento:**
1. Carga la configuración del usuario desde `config_files/x_usernames.json` usando `--name`.
2. Carga el archivo `cache/<username_config_key>_processed_posts.json`.
3. Filtra los posts que tienen `media_type: 'video'` y `video_processed: false` (o no existe `video_processed`).
4. Muestra una lista paginada de estos videos.
5. El usuario puede elegir descargar un video específico, todos, o navegar por las páginas.
6. Al descargar un video, se invoca `yt-dlp` con la URL del post (ej: `https://x.com/username/status/post_id/video/1`).
7. Si la descarga es exitosa, el post correspondiente en el archivo de caché se marca como `video_processed: true` y se guarda el caché.

**Delays Orgánicos:**
- El script incluye delays aleatorios entre descargas masivas para simular un comportamiento más humano.

---

## 🎯 Qué Herramienta Usar - Guía de Selección

### **🏆 Flujo de Trabajo Recomendado**

1.  **Configurar Usuarios (una sola vez o cuando sea necesario):**
    ```bash
    python3 manage_users.py
    ```
    Añade los perfiles de X que te interesan, especificando su `friendlyname`, `username` real y dónde guardar sus descargas.

2.  **Extraer Medios (Imágenes y Posts con Video):**
    Ejecuta `edge_x_downloader_clean.py` para el usuario deseado. Esto descargará las imágenes y creará/actualizará el archivo de caché con información de todos los posts, incluyendo los que tienen videos.
    ```bash
    # Para el usuario 'nombre_amigable', procesa los últimos 50 posts nuevos
    python3 edge_x_downloader_clean.py --name <nombre_amigable> --limit 50
    
    # Para procesar todos los posts nuevos de un usuario
    python3 edge_x_downloader_clean.py --name <nombre_amigable> --no-limit 
    ```
    Repite este paso periódicamente para mantener el caché actualizado.

3.  **Seleccionar y Descargar Videos:**
    Una vez que `edge_x_downloader_clean.py` ha procesado los posts y poblado el caché, usa `video_selector.py` para elegir y descargar los videos.
    ```bash
    python3 video_selector.py --name <nombre_amigable>
    ```
    Esto te mostrará una lista interactiva de videos pendientes de descarga para ese usuario.

### **🔍 Para Casos Específicos**

| **Necesidad**                                       | **Herramienta Principal**        | **Notas**                                                                                                |
| --------------------------------------------------- | -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 👤 Gestionar configuración de usuarios              | `manage_users.py`                | Añadir, editar, eliminar perfiles de X.                                                                  |
| 🖼️ Descargar imágenes de un perfil                  | `edge_x_downloader_clean.py`     | También actualiza el caché de posts, necesario para `video_selector.py`.                                 |
| 🎞️ Identificar posts con videos de un perfil        | `edge_x_downloader_clean.py`     | El script marca los posts con `media_type: 'video'` en el archivo de caché.                              |
| 🎬 Seleccionar y descargar videos específicos       | `video_selector.py`              | Requiere que `edge_x_downloader_clean.py` haya corrido antes para generar el caché.                      |
| 🔄 Actualizar descargas de un perfil conocido      | `edge_x_downloader_clean.py`     | Usar con `--limit` para procesar solo lo más nuevo o `--no-limit` para un escaneo completo de novedades. |
| 📊 Obtener un listado de URLs de video (sin descargar) | `edge_x_downloader_clean.py`     | La información queda en el archivo `.json` del caché. `video_selector.py` luego usa estas URLs.        |

---

## 📋 Formatos de Salida

### 🎬 **JSON de Videos**

```json
{
  "extraction_date": "2025-06-11T17:45:49.123456",
  "total_videos": 55,
  "videos": [
    {
      "url": "https://x.com/usuario/status/1234567890/video/1",
      "status_id": "1234567890",
      "username": "usuario",
      "original_link": "https://x.com/usuario/status/1234567890",
      "tweet_text": "Texto del tweet...",
      "found_at": "2025-06-11T17:45:49.123456",
      "position": 1
    }
  ]
}
```

### 🖼️ **Log de Imágenes**

```json
{
  "session_timestamp": "2025-06-11 17:45:49",
  "summary": {
    "downloaded": 25,
    "skipped": 3,
    "failed": 0,
    "total_processed": 28
  },
  "urls_processed": ["url1", "url2", "..."]
}
```

---

## 🔧 Solución de Problemas

### ❌ **Problema: "No se encontraron tweets"**

**Causas posibles:**
- No estás logueado en X.com en Edge
- El perfil es privado o requiere seguimiento
- X.com cambió la estructura de la página

**Soluciones:**
```bash
# 1. Verificar login
# Abre Edge manualmente y ve a x.com, asegúrate de estar logueado

# 2. Usar modo temporal si hay problemas con el perfil automatizado
python3 simple_video_extractor.py --temporal

# 3. Verificar que la URL es correcta
# El script por defecto usa: https://x.com/milewskaja_nat/media
```

### ❌ **Problema: yt-dlp requiere autenticación**

```
ERROR: NSFW tweet requires authentication
```

**Solución:**
```bash
# Siempre usar cookies del navegador
yt-dlp --cookies-from-browser edge "URL_DEL_VIDEO"

# Si persiste el problema, actualizar yt-dlp
pip install --upgrade yt-dlp
```

### ❌ **Problema: "jq command not found"**

**En macOS:**
```bash
# Instalar jq con Homebrew
brew install jq

# O usar método alternativo sin jq
python3 -c "
import json
with open('archivo.json') as f:
    data = json.load(f)
    for video in data['videos']:
        print(video['url'])
" > video_urls.txt
```

### ❌ **Problema: Edge no se encuentra**

```
Error: Browser executable not found
```

**Solución:**
```bash
# Verificar ruta de Edge
ls -la "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

# Si Edge está en otra ubicación, editar la variable edge_path en el script
```

---

## ❓ Preguntas Frecuentes

### **Q: ¿Por qué dos pasos para videos en lugar de descarga directa?**

**R:** El enfoque de dos pasos es más confiable:
- ✅ **Evita bloqueos** por sitios externos de descarga
- ✅ **Sin CAPTCHAs** o verificaciones humanas
- ✅ **Más rápido** - una sola navegación extrae todas las URLs
- ✅ **Más flexible** - puedes usar cualquier herramienta de descarga

### **Q: ¿Funciona con perfiles privados?**

**R:** Solo si sigues al usuario:
- ✅ **Perfiles públicos**: Funciona siempre
- ✅ **Perfiles privados que sigues**: Funciona si estás logueado
- ❌ **Perfiles privados que no sigues**: No funciona

### **Q: ¿Puedo cambiar el perfil objetivo?**

**R:** Sí, edita el archivo:
```python
# En simple_video_extractor.py, línea ~270
profile_url = "https://x.com/NUEVO_USUARIO/media"
```

### **Q: ¿Qué calidad de video descarga yt-dlp?**

**R:** Por defecto, la mejor disponible. Para controlar:
```bash
# Ver formatos disponibles
yt-dlp --cookies-from-browser edge --list-formats "URL"

# Descargar calidad específica
yt-dlp --cookies-from-browser edge -f "FORMAT_ID" "URL"

# Limitar calidad máxima
yt-dlp --cookies-from-browser edge -f "best[height<=720]" "URL"
```

### **Q: ¿Se pueden descargar videos en lote de múltiples usuarios?**

**R:** Sí, modifica el script o ejecuta múltiples veces:
```bash
# Método 1: Modificar el script para multiple usuarios
# Método 2: Ejecutar varias veces
python3 simple_video_extractor.py  # Usuario 1
# Cambiar profile_url y ejecutar de nuevo
python3 simple_video_extractor.py  # Usuario 2

# Luego descargar todos los JSONs juntos
yt-dlp --cookies-from-browser edge --batch-file <(jq -r '.videos[].url' ~/Downloads/X_Video_URLs/*.json)
```

### **Q: ¿Hay límites de velocidad o bloqueos?**

**R:** El sistema incluye medidas preventivas:
- ⏱️ **Delays orgánicos** entre acciones (1-5 segundos)
- 🤖 **User-Agent real** de Chrome/Edge
- 🍪 **Cookies del navegador** para autenticación natural
- 📜 **Scroll gradual** para simular comportamiento humano

---

## 🎯 Casos de Uso Comunes

### **Caso 1: Backup Personal Completo**
```bash
# Obtener TODOS los medios de tu perfil
# 1. Cambiar URL a tu perfil en los scripts
# 2. Extraer URLs de videos
python3 simple_video_extractor.py
# 3. Descargar todas las imágenes
python3 edge_x_downloader_clean.py
# 4. Usar selector para elegir videos
python3 video_selector.py
```

### **Caso 2: Descarga Selectiva con Previsualización**
```bash
# 1. Extraer URLs para revisar
python3 simple_video_extractor.py
# 2. Usar selector interactivo para elegir
python3 video_selector.py
# 3. Navegar página por página y descargar solo los que quieras
```

### **Caso 3: Videos Específicos Conocidos**
```bash
# Si ya sabes qué videos quieres (por ID o URL)
yt-dlp --cookies-from-browser edge "https://x.com/usuario/status/ID/video/1"
# No necesitas extraer todas las URLs
```

### **Caso 4: Investigación/Archivo Masivo**
```bash
# 1. Extraer URLs de múltiples usuarios
# 2. Analizar JSON sin descargar videos
# 3. Descarga masiva posterior
python3 simple_video_extractor.py  # Usuario 1
# Cambiar profile_url y repetir para más usuarios
yt-dlp --cookies-from-browser edge --batch-file <(jq -r '.videos[].url' ~/Downloads/X_Video_URLs/*.json)
```

### **Caso 5: Descarga por Rangos de Fecha**
```bash
# 1. Extraer todas las URLs
python3 simple_video_extractor.py
# 2. Filtrar por rango de posiciones (videos más recientes = posiciones menores)
jq -r '.videos[0:10] | .[] | .url' ~/Downloads/X_Video_URLs/video_urls_simple_*.json > videos_recientes.txt
jq -r '.videos[45:55] | .[] | .url' ~/Downloads/X_Video_URLs/video_urls_simple_*.json > videos_antiguos.txt
# 3. Descargar el rango deseado
yt-dlp --cookies-from-browser edge --batch-file videos_recientes.txt
```

---

## 🔧 Solución de Problemas

### ❌ **Problema: "No se encontraron tweets"**

**Causas posibles:**
- No estás logueado en X.com en Edge
- El perfil es privado o requiere seguimiento
- X.com cambió la estructura de la página

**Soluciones:**
```bash
# 1. Verificar login
# Abre Edge manualmente y ve a x.com, asegúrate de estar logueado

# 2. Usar modo temporal si hay problemas con el perfil automatizado
python3 simple_video_extractor.py --temporal

# 3. Verificar que la URL es correcta
# El script por defecto usa: https://x.com/milewskaja_nat/media
```

### ❌ **Problema: yt-dlp requiere autenticación**

```
ERROR: NSFW tweet requires authentication
```

**Solución:**
```bash
# Siempre usar cookies del navegador
yt-dlp --cookies-from-browser edge "URL_DEL_VIDEO"

# Si persiste el problema, actualizar yt-dlp
pip install --upgrade yt-dlp

# Verificar que las cookies se extraen correctamente
yt-dlp --cookies-from-browser edge --list-formats "URL_DEL_VIDEO"
```

### ❌ **Problema: video_selector.py no encuentra videos**

```
❌ No se encontraron archivos JSON con videos
```

**Solución:**
```bash
# 1. Verificar que tienes archivos JSON
ls -la ~/Downloads/X_Video_URLs/video_urls_simple_*.json

# 2. Si no tienes, ejecutar primero el extractor
python3 simple_video_extractor.py

# 3. Verificar el contenido del JSON
jq '.total_videos' ~/Downloads/X_Video_URLs/video_urls_simple_*.json
```

### ❌ **Problema: "jq command not found"**

**En macOS:**
```bash
# Instalar jq con Homebrew
brew install jq

# O usar método alternativo sin jq para crear lista de URLs
python3 -c "
import json
from pathlib import Path

# Encontrar el JSON más reciente
video_dir = Path.home() / 'Downloads' / 'X_Video_URLs'
json_files = list(video_dir.glob('video_urls_simple_*.json'))
latest_file = max(json_files, key=lambda x: x.stat().st_mtime)

# Extraer URLs
with open(latest_file) as f:
    data = json.load(f)
    for video in data['videos']:
        print(video['url'])
" > video_urls.txt

# Usar el archivo generado
yt-dlp --cookies-from-browser edge --batch-file video_urls.txt
```

### ❌ **Problema: Edge no se encuentra**

```
Error: Browser executable not found
```

**Solución:**
```bash
# Verificar ruta de Edge
ls -la "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"

# Si Edge está en otra ubicación, editar la variable edge_path en el script
# Línea aproximada 65 en simple_video_extractor.py:
edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
```

### ❌ **Problema: Videos se descargan pero no se pueden reproducir**

**Solución:**
```bash
# Verificar el formato descargado
yt-dlp --cookies-from-browser edge --list-formats "URL_DEL_VIDEO"

# Forzar formato específico
yt-dlp --cookies-from-browser edge -f "best[ext=mp4]" "URL_DEL_VIDEO"

# Convertir si es necesario (requiere ffmpeg)
yt-dlp --cookies-from-browser edge --recode-video mp4 "URL_DEL_VIDEO"
```

---

## ❓ Preguntas Frecuentes

### **Q: ¿Cuál es la diferencia entre los 4 métodos de descarga?**

**R:** Cada método tiene sus ventajas:

| Método | Ventajas | Desventajas | Mejor para |
|--------|----------|-------------|------------|
| **Selector Interactivo** | ✅ Control total<br>✅ Ve contenido antes<br>✅ Descarga selectiva | ⚠️ Manual<br>⚠️ Más lento | Explorar y elegir |
| **Descarga Masiva** | ✅ Automático<br>✅ Muy rápido<br>✅ Sin intervención | ⚠️ Todo o nada<br>⚠️ Puede ocupar mucho espacio | Backup completo |
| **Videos Específicos** | ✅ Directo<br>✅ No requiere extracción | ⚠️ Necesitas saber las URLs<br>⚠️ Manual para múltiples | URLs conocidas |
| **Lista Personalizada** | ✅ Control fino<br>✅ Automatizable | ⚠️ Requiere trabajo previo | Casos específicos |

### **Q: ¿Por qué dos pasos para videos en lugar de descarga directa?**

**R:** El enfoque de dos pasos es más confiable:
- ✅ **Evita bloqueos** por sitios externos de descarga
- ✅ **Sin CAPTCHAs** o verificaciones humanas
- ✅ **Más rápido** - una sola navegación extrae todas las URLs
- ✅ **Más flexible** - puedes usar cualquier herramienta de descarga
- ✅ **Control de calidad** - puedes elegir exactamente qué descargar

### **Q: ¿Funciona con perfiles privados?**

**R:** Solo si sigues al usuario:
- ✅ **Perfiles públicos**: Funciona siempre
- ✅ **Perfiles privados que sigues**: Funciona si estás logueado
- ❌ **Perfiles privados que no sigues**: No funciona

### **Q: ¿Puedo cambiar el perfil objetivo?**

**R:** Sí, edita el archivo:
```python
# En simple_video_extractor.py, línea ~270
profile_url = "https://x.com/NUEVO_USUARIO/media"
```

O crea una copia del script para cada usuario:
```bash
cp simple_video_extractor.py extractor_usuario1.py
cp simple_video_extractor.py extractor_usuario2.py
# Editar cada archivo con el usuario correspondiente
```

### **Q: ¿Qué calidad de video descarga yt-dlp?**

**R:** Por defecto, la mejor disponible. Para controlar:
```bash
# Ver formatos disponibles
yt-dlp --cookies-from-browser edge --list-formats "URL"

# Descargar calidad específica
yt-dlp --cookies-from-browser edge -f "FORMAT_ID" "URL"

# Limitar calidad máxima
yt-dlp --cookies-from-browser edge -f "best[height<=720]" "URL"

# Solo audio
yt-dlp --cookies-from-browser edge -x --audio-format mp3 "URL"
```

### **Q: ¿Se pueden descargar videos en lote de múltiples usuarios?**

**R:** Sí, varios métodos:

**Método 1: Múltiples ejecuciones**
```bash
# Modificar profile_url para cada usuario y ejecutar
python3 simple_video_extractor.py  # Usuario 1
# Cambiar profile_url y ejecutar de nuevo
python3 simple_video_extractor.py  # Usuario 2

# Luego descargar todos los JSONs juntos
yt-dlp --cookies-from-browser edge --batch-file <(jq -r '.videos[].url' ~/Downloads/X_Video_URLs/*.json)
```

**Método 2: Script personalizado**
```python
# Crear script que itere múltiples usuarios
usuarios = ["usuario1", "usuario2", "usuario3"]
for usuario in usuarios:
    profile_url = f"https://x.com/{usuario}/media"
    # Ejecutar extractor...
```

### **Q: ¿Hay límites de velocidad o bloqueos?**

**R:** El sistema incluye medidas preventivas:
- ⏱️ **Delays orgánicos** entre acciones (1-5 segundos)
- 🤖 **User-Agent real** de Chrome/Edge
- 🍪 **Cookies del navegador** para autenticación natural
- 📜 **Scroll gradual** para simular comportamiento humano
- 🔄 **Control de duplicados** para evitar procesamiento innecesario

### **Q: ¿Cuánto espacio ocupan los videos?**

**R:** Varía mucho por contenido:
- **Videos cortos (TikTok-style)**: 1-5 MB cada uno
- **Videos medianos**: 5-20 MB cada uno  
- **Videos largos/alta calidad**: 20-100+ MB cada uno

**Ejemplo real**: El video que descargamos ocupó 1.4 MB.

Para 55 videos, estima entre **100 MB - 2 GB** dependiendo del contenido.

### **Q: ¿Puedo pausar y reanudar descargas?**

**R:** Sí, con yt-dlp:
```bash
# Crear archivo de URLs
jq -r '.videos[].url' ~/Downloads/X_Video_URLs/video_urls_simple_*.json > todas_las_urls.txt

# Descargar con posibilidad de reanudar
yt-dlp --cookies-from-browser edge --continue --batch-file todas_las_urls.txt

# Si se interrumpe, ejecutar el mismo comando de nuevo para continuar
```

---

## 🛠️ Apéndice: Detalles Técnicos de Cada Herramienta

### **`simple_video_extractor.py` ⭐ [RECOMENDADO PARA EXTRACCIÓN]**

**Ventajas:**
- ⚡ **Más rápido**: Scroll optimizado, detección automática de final
- 🚫 **Sin duplicados**: Deduplicación por `status_id` 
- 💾 **Menor JSON**: Solo información esencial
- 🧹 **Código limpio**: Fácil de mantener y modificar

**Ideal para:** Extracciones rápidas y eficientes

```bash
python3 simple_video_extractor.py
```

### **`video_selector.py` 🎯 [RECOMENDADO PARA DESCARGA]**

**Ventajas:**
- 🎯 **Control total**: Elige exactamente qué descargar
- 📋 **Vista previa**: Ve texto del tweet antes de descargar
- 🧭 **Navegación fácil**: Páginas de 10, comandos simples
- 💰 **Ahorra espacio**: Solo descarga lo que necesitas

**Ideal para:** Control preciso sobre qué videos descargar

```bash
python3 video_selector.py
```

### **`x_video_url_extractor.py` 📊 [PARA ANÁLISIS DETALLADO]**

**Ventajas:**
- 📋 **Más metadatos**: Información detallada de cada video
- 🔍 **Mejor para análisis**: Timestamps, posiciones, contexto
- 📊 **Información completa**: Útil para estudios o análisis

**Ideal para:** Cuando necesitas información detallada sobre cada video

```bash
python3 x_video_url_extractor.py
```

### **`edge_x_downloader.py` ⚡ [TODO-EN-UNO]**

**Ventajas:**
- 🎯 **Un solo comando**: Extrae Y descarga todo automáticamente
- 🖼️ **Imágenes incluidas**: También descarga imágenes
- 🤖 **Totalmente automático**: Perfecto para scripts y automatización

**Ideal para:** Cuando quieres todo automático sin intervención

```bash
python3 edge_x_downloader.py
```

### **`edge_x_downloader_clean.py` 🖼️ [SOLO IMÁGENES]**

**Ventajas:**
- 🖼️ **Solo imágenes**: No procesamiento de videos
- ⚡ **Más rápido**: Sin lógica compleja de videos
- 💾 **Archivos optimizados**: Conversión automática a alta calidad

**Ideal para:** Cuando solo necesitas las imágenes

```bash
python3 edge_x_downloader_clean.py
```

### **Scripts Especializados (`mcp_*`, `quick_*`, etc.)**

**Ventajas:**
- 🔧 **Máxima personalización**: Código modular y adaptable
- ⚡ **Casos específicos**: Optimizados para necesidades particulares
- 🧪 **Experimentación**: Perfectos para probar nuevas funcionalidades

**Ideal para:** Desarrolladores y casos de uso muy específicos

---

## 🎯 Resumen Ejecutivo

### **Para la mayoría de usuarios:**
1. **Extraer URLs**: `python3 simple_video_extractor.py`
2. **Seleccionar videos**: `python3 video_selector.py`

### **Para descarga automática completa:**
- **Todo en uno**: `python3 edge_x_downloader.py`

### **Para casos específicos:**
- **Solo imágenes**: `python3 edge_x_downloader_clean.py`
- **Análisis detallado**: `python3 x_video_url_extractor.py`

**¡Todas las herramientas están mantenidas y actualizadas!** Cada una tiene su propósito y ventajas específicas. 

---

*📝 Manual actualizado: 13 de junio de 2025*  
*🔧 Sistema desarrollado para automatización de descarga de medios de X*

---

## 🚀 Próximas Mejoras

- [ ] **Soporte para múltiples usuarios** en una sola ejecución
- [ ] **Interfaz gráfica** para usuarios no técnicos
- [ ] **Descarga incremental** (solo nuevos medios)
- [ ] **Soporte para hilos/threads** de X
- [ ] **Integración con otras plataformas** (Instagram, TikTok)

---

## 📞 Soporte

### **Para problemas técnicos:**
1. Verificar que estás logueado en X.com en Edge
2. Actualizar dependencias: `pip install --upgrade playwright yt-dlp`
3. Reinstalar navegador: `playwright install chromium`

### **Para nuevas características:**
- El sistema es modular y fácil de extender
- Los scripts están bien documentados para modificaciones

---

## 📜 Licencia y Uso Responsable

⚠️ **Importante**: 
- Respeta los términos de servicio de X.com
- Solo descarga contenido al que tienes acceso legítimo
- No abuses del sistema (limits razonables)
- Usa para backup personal y investigación ética

---

**¡El sistema está listo para usar! 🎉**

*Última actualización: 13 de junio de 2025*

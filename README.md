# 🚀 X Media Assistant - MCP Server

**Un servidor MCP (Model Context Protocol) para la descarga y gestión automatizada de contenido multimedia desde X (Twitter)**

Un servidor MCP personalizado desarrollado en Python que permite descargar y gestionar medios de X/Twitter directamente desde VS Code usando GitHub Copilot Chat. Optimizado para desarrollo integrado y procesamiento eficiente de contenido multimedia.

---

## 🎯 Características

- ✅ **Gestión de usuarios** - Agregar, listar, editar y eliminar usuarios de X
- ✅ **Descarga de imágenes** - Descarga automática de imágenes de perfiles
- ✅ **Descarga de videos** - Descarga automática de videos usando yt-dlp
- ✅ **Caché inteligente** - Sistema de caché para evitar descargas duplicadas
- ✅ **Integración VS Code** - Funciona directamente con Copilot Chat
- ✅ **Herramientas administrativas** - Control completo del sistema

---

## 🛠️ Tecnologías

- **Python** - Lenguaje principal del servidor
- **MCP (Model Context Protocol)** - Protocolo de comunicación
- **APIs de X** - Integración con la plataforma X (Twitter)
- **VS Code** - Entorno de desarrollo integrado
- **yt-dlp** - Motor de descarga de videos
- **Sistema de archivos** - Gestión local de medios descargados

---

## 👥 Usuarios Configurados

Actualmente el sistema tiene configurados los siguientes usuarios:

- **nat** - Username: `@milewskaja_nat`
  - Directorio: `/Volumes/SSDWD2T/fansly/nat/`
  
- **rachel** - Username: `@rachelc00k`
  - Directorio: `/Volumes/SSDWD2T/fansly/rachel/`

*Puedes gestionar usuarios usando la herramienta `manage_users` descrita más abajo.*

---

## 🚀 Instalación Rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/angeltsalazar/mcp-x-media-assistant.git
cd mcp-x-media-assistant
```

### 2. Configuración automática
```bash
python3 setup_project.py
```

### 3. Abrir en VS Code
```bash
code .
```

### 4. Reiniciar VS Code
- Presiona `Cmd+Shift+P` (macOS) o `Ctrl+Shift+P` (Windows/Linux)
- Ejecuta "Developer: Reload Window"

### 5. ¡Probar!
En Copilot Chat:
```
@x-assistant-mcp test_tool {"message": "Hola mundo"}
```

---

## 📋 Ideal para

- Creadores de contenido que necesitan archivar su contenido multimedia
- Investigadores que requieren recopilar datos multimedia de redes sociales
- Gestores de redes sociales que necesitan organizar contenido
- Desarrolladores que trabajan con datos de X/Twitter

---

## 🔧 Configuración Manual

### Requisitos
- Python 3.8+
- VS Code Insiders (recomendado)
- Extensiones: GitHub Copilot, GitHub Copilot Chat

### Instalación manual
```bash
# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
pip install yt-dlp

# Configurar VS Code (ver .vscode/mcp.json)
```

---

## 📋 Herramientas Disponibles

### 🧪 `test_tool`
Verificar conectividad del servidor
```json
{"message": "Tu mensaje de prueba"}
```

### 👥 `manage_users`
Gestionar usuarios de X/Twitter
```json
{
  "action": "list|add|remove|edit",
  "user_data": {
    "friendlyname": "Nombre amigable",
    "username": "usuario_x",
    "directory_download": "/ruta/de/descarga"
  }
}
```

### 🖼️ `download_images`
Descargar imágenes de usuarios
```json
{
  "name": "usuario_configurado",
  "limit": 100,
  "mode": "auto"
}
```

### 🎬 `download_videos`
Descargar videos de usuarios
```json
{
  "name": "usuario_configurado",
  "mode": "download_all"
}
```

### 🔧 `admin_tool`
Herramienta administrativa avanzada
```json
{
  "action": "status|download_test|users",
  "params": {...}
}
```

---

## 🎮 Ejemplos de Uso

### Agregar un usuario
```
@x-assistant-mcp manage_users {
  "action": "add",
  "user_data": {
    "friendlyname": "Mi Usuario",
    "username": "mi_usuario_x",
    "directory_download": "/Users/mi-usuario/Downloads/X_Media"
  }
}
```

### Descargar imágenes
```
@x-assistant-mcp download_images {
  "name": "Mi Usuario",
  "limit": 50
}
```

### Descargar videos
```
@x-assistant-mcp download_videos {
  "name": "Mi Usuario",
  "mode": "download_all"
}
```

### Ver estado del sistema
```
@x-assistant-mcp admin_tool {"action": "status"}
```

---

## 📁 Estructura del Proyecto

```
x_assistant_mcp/
├── .vscode/
│   ├── mcp.json              # Configuración MCP
│   └── settings.json         # Configuración VS Code
├── modules/                  # Módulos del downloader
├── config_files/             # Configuración de usuarios
├── cache/                    # Caché de posts procesados
├── docs/                     # Documentación
├── mcp_server_working.py     # Servidor MCP principal
├── video_selector.py         # Selector de videos
├── setup_project.py          # Script de configuración
├── requirements.txt          # Dependencias Python
└── README.md                 # Este archivo
```

---

## 🐛 Troubleshooting

### Problema: "Tool is currently disabled"
**Solución:** Usar `admin_tool` como proxy o habilitar la herramienta en VS Code.

### Problema: "yt-dlp not found"
**Solución:** 
```bash
.venv/bin/pip install yt-dlp
```

### Problema: "Invalid JSON schema"
**Solución:** Verificar que las rutas en `.vscode/mcp.json` usen `${workspaceFolder}`.

### Problema: Servidor no responde
**Solución:**
1. Verificar que Python del venv funciona: `.venv/bin/python3 --version`
2. Probar servidor manualmente: `.venv/bin/python3 mcp_server_working.py`
3. Reiniciar VS Code

---

## 🔒 Configuración de Privacidad

Este proyecto utiliza:
- **Cookies del navegador Edge** para autenticación en X
- **yt-dlp** para descarga de videos
- **Almacenamiento local** para caché y configuración

**No se almacenan credenciales** ni se envían datos a servidores externos.

---

## 📚 Documentación Adicional

- [Guía completa de desarrollo MCP](./how-to-mcp-for-vscode.md)
- [Documentación del servidor](./docs/MCP_SERVER.md)
- [Troubleshooting avanzado](./docs/MCP_TROUBLESHOOTING.md)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🎉 Créditos

Desarrollado como parte del proyecto X Media Downloader con integración MCP para VS Code.

**¡Disfruta descargando medios directamente desde Copilot Chat!** 🚀

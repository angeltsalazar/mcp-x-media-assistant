# 🚀 X Media Assistant - Release Inicial v0.1.0

¡Primera versión estable del servidor MCP para descarga y gestión de medios de X/Twitter!

## ✨ Características Principales

- **🎯 Servidor MCP Completo** - Integración nativa con VS Code y Copilot Chat
- **👥 Gestión de Usuarios** - Agregar, listar, editar y eliminar usuarios de X
- **🖼️ Descarga de Imágenes** - Sistema inteligente con caché para evitar duplicados
- **🎬 Descarga de Videos** - Usando yt-dlp para máxima calidad y compatibilidad
- **🔧 Herramientas Admin** - Control completo del sistema y monitoreo
- **📊 Sistema de Caché** - Optimización automática de descargas

## 🛠️ Tecnologías

- **Python 3.8+** con arquitectura modular
- **Model Context Protocol (MCP)** para comunicación
- **Playwright** para automatización de navegador
- **yt-dlp** para descarga de videos
- **Sistema de archivos** para gestión local

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

## 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/angeltsalazar/mcp-x-media-assistant.git
cd mcp-x-media-assistant

# Configuración automática
python3 setup_project.py

# Abrir en VS Code
code .
```

## 🎮 Casos de Uso Ideales

- **Creadores de contenido** que necesitan archivar su contenido multimedia
- **Investigadores** que requieren recopilar datos multimedia de redes sociales
- **Gestores de redes sociales** que necesitan organizar contenido
- **Desarrolladores** que trabajan con datos de X/Twitter

## 📋 Requisitos del Sistema

- **macOS** (optimizado para macOS, compatible con Intel y Apple Silicon)
- **Python 3.8+** (recomendado Python 3.12)
- **VS Code** con extensiones GitHub Copilot y Copilot Chat
- **Microsoft Edge** (para navegación automatizada)

## 🎯 Lo que hace especial esta versión

- ✅ **Totalmente funcional** y listo para producción
- ✅ **Documentación completa** con ejemplos detallados
- ✅ **Arquitectura modular** fácilmente extensible
- ✅ **Sistema de caché inteligente** para optimización
- ✅ **Integración nativa** con herramientas de desarrollo

## 🔗 Próximos Pasos

1. Clonar el repositorio
2. Seguir las instrucciones de instalación en el README
3. Configurar usuarios con `manage_users`
4. ¡Comenzar a descargar contenido!

---

**¡Gracias por usar X Media Assistant MCP Server!** 🎉

Para soporte, documentación adicional o reportar problemas, visita el repositorio en GitHub.

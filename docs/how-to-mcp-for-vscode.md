# 🚀 Guía Completa: Cómo Crear un Servidor MCP para VS Code

**Model Context Protocol (MCP) Server Development Guide**

Guía paso a paso para desarrollar, implementar y configurar un servidor MCP personalizado que funcione perfectamente con VS Code y Copilot Chat.

---

## 📋 Tabla de Contenidos

1. [Introducción al MCP](#introducción-al-mcp)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Implementación del Servidor](#implementación-del-servidor)
5. [Configuración de VS Code](#configuración-de-vs-code)
6. [Testing y Debugging](#testing-y-debugging)
7. [Herramientas y Handlers](#herramientas-y-handlers)
8. [Troubleshooting](#troubleshooting)
9. [Mejores Prácticas](#mejores-prácticas)
10. [Ejemplos Avanzados](#ejemplos-avanzados)

---

## 🎯 Introducción al MCP

### ¿Qué es MCP?
Model Context Protocol (MCP) es un protocolo que permite a los modelos de IA acceder a herramientas y recursos externos de manera estandarizada. VS Code utiliza MCP para extender las capacidades de Copilot Chat.

### ¿Por qué crear un servidor MCP personalizado?
- **Integración directa** con tus proyectos específicos
- **Herramientas personalizadas** para tu workflow
- **Acceso a recursos locales** desde Copilot Chat
- **Automatización** de tareas repetitivas

---

## 🛠️ Preparación del Entorno

### Requisitos Previos

```bash
# Python 3.8+
python3 --version

# VS Code Insiders (recomendado para MCP)
# Instalar desde: https://code.visualstudio.com/insiders/

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias base
pip install asyncio json pathlib
```

### Extensiones de VS Code Necesarias

```json
{
  "recommendations": [
    "GitHub.copilot",
    "GitHub.copilot-chat"
  ]
}
```

---

## 📁 Estructura del Proyecto

### Estructura Recomendada

```
mi_proyecto/
├── .vscode/
│   ├── mcp.json                 # Configuración MCP local
│   └── settings.json            # Configuraciones de VS Code
├── .venv/                       # Entorno virtual Python
├── mcp_server.py               # Servidor MCP principal
├── test_mcp.py                 # Script de pruebas
├── requirements.txt            # Dependencias Python
├── README.md                   # Documentación
└── modules/                    # Módulos de tu aplicación
    ├── __init__.py
    ├── core/
    │   └── logic.py
    └── utils/
        └── helpers.py
```

### Archivos de Configuración Base

**requirements.txt**
```txt
asyncio
pathlib
json
logging
```

**.vscode/mcp.json**
```json
{
  "servers": {
    "mi-servidor-mcp": {
      "command": "/ruta/absoluta/a/tu/proyecto/.venv/bin/python3",
      "args": ["/ruta/absoluta/a/tu/proyecto/mcp_server.py"],
      "cwd": "/ruta/absoluta/a/tu/proyecto"
    }
  }
}
```

---

## 🔧 Implementación del Servidor

### 1. Estructura Base del Servidor MCP

**mcp_server.py**
```python
#!/usr/bin/env python3
"""
Servidor MCP Personalizado
Implementación manual del protocolo JSON-RPC para MCP
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List
from pathlib import Path

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("mi-servidor-mcp")

class SimpleMCPServer:
    """Servidor MCP base con protocolo JSON-RPC."""
    
    def __init__(self, name: str):
        self.name = name
        self.version = "1.0.0"
        self.tools = []
        self.request_id = 0
        
    def add_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler):
        """Agrega una herramienta al servidor."""
        self.tools.append({
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "handler": handler
        })
        logger.info(f"Herramienta registrada: {name}")
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Maneja una solicitud JSON-RPC."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            logger.debug(f"Procesando método: {method}")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {"listChanged": False},
                            "experimental": {}
                        },
                        "serverInfo": {
                            "name": self.name,
                            "version": self.version
                        }
                    }
                }
                
            elif method == "tools/list":
                tools_list = []
                for tool in self.tools:
                    tools_list.append({
                        "name": tool["name"],
                        "description": tool["description"],
                        "inputSchema": tool["inputSchema"]
                    })
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools_list
                    }
                }
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Buscar y ejecutar la herramienta
                for tool in self.tools:
                    if tool["name"] == tool_name:
                        try:
                            result = await tool["handler"](arguments)
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": [{"type": "text", "text": result}],
                                    "isError": False
                                }
                            }
                        except Exception as e:
                            logger.error(f"Error en herramienta {tool_name}: {e}")
                            return {
                                "jsonrpc": "2.0",
                                "id": request_id,
                                "result": {
                                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                                    "isError": True
                                }
                            }
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Tool not found: {tool_name}"
                    }
                }
                
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def run(self):
        """Ejecuta el servidor MCP."""
        logger.info(f"Iniciando servidor MCP: {self.name}")
        
        while True:
            try:
                # Leer línea de entrada
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                # Parsear solicitud JSON-RPC
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
                    continue
                
                # Procesar solicitud
                response = await self.handle_request(request)
                
                # Enviar respuesta
                response_line = json.dumps(response)
                print(response_line, flush=True)
                
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")

# Crear servidor
server = SimpleMCPServer("mi-servidor-personalizado")
```

### 2. Implementar Handlers de Herramientas

```python
# ============ HANDLERS DE HERRAMIENTAS ============

async def test_tool_handler(arguments: Dict[str, Any]) -> str:
    """Herramienta de prueba básica."""
    message = arguments.get("message", "Sin mensaje")
    return f"✅ Servidor funcionando! Mensaje: {message}"

async def file_list_handler(arguments: Dict[str, Any]) -> str:
    """Lista archivos en un directorio."""
    directory = arguments.get("directory", ".")
    try:
        files = []
        for item in Path(directory).iterdir():
            if item.is_file():
                files.append(f"📄 {item.name}")
            else:
                files.append(f"📁 {item.name}/")
        
        return f"📂 Contenido de {directory}:\n" + "\n".join(files[:20])
    except Exception as e:
        return f"❌ Error listando archivos: {str(e)}"

async def project_info_handler(arguments: Dict[str, Any]) -> str:
    """Información del proyecto actual."""
    cwd = os.getcwd()
    files_count = len([f for f in Path(cwd).rglob("*") if f.is_file()])
    
    return f"""
🏗️ **Información del Proyecto**

📁 **Directorio:** `{cwd}`
📊 **Archivos totales:** {files_count}
🐍 **Python:** {sys.version.split()[0]}
🔧 **Servidor MCP:** Activo

✅ **Estado:** Operativo
"""

# ============ REGISTRAR HERRAMIENTAS ============

# Herramienta de prueba
server.add_tool(
    "test_tool",
    "Herramienta de prueba para verificar conectividad",
    {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Mensaje de prueba",
                "default": "Hola mundo"
            }
        }
    },
    test_tool_handler
)

# Listar archivos
server.add_tool(
    "list_files",
    "Lista archivos en un directorio específico",
    {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directorio a listar (. para actual)",
                "default": "."
            }
        }
    },
    file_list_handler
)

# Información del proyecto
server.add_tool(
    "project_info",
    "Obtiene información del proyecto actual",
    {
        "type": "object",
        "properties": {}
    },
    project_info_handler
)

# ============ EJECUTAR SERVIDOR ============

if __name__ == "__main__":
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Servidor interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en servidor MCP: {e}")
        sys.exit(1)
```

---

## ⚙️ Configuración de VS Code

### 1. Configuración MCP Local (.vscode/mcp.json)

```json
{
  "servers": {
    "mi-servidor-personalizado": {
      "command": "/ruta/absoluta/a/tu/proyecto/.venv/bin/python3",
      "args": ["/ruta/absoluta/a/tu/proyecto/mcp_server.py"],
      "cwd": "/ruta/absoluta/a/tu/proyecto"
    }
  }
}
```

### 2. Configuración de VS Code (.vscode/settings.json)

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "files.associations": {
    "*.json": "jsonc"
  },
  "editor.formatOnSave": true
}
```

### 3. Obtener Rutas Absolutas

**Script para obtener rutas (get_paths.py)**
```python
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def get_project_paths():
    """Obtiene rutas absolutas para configuración MCP."""
    project_dir = Path.cwd().absolute()
    python_path = Path(sys.executable).absolute()
    server_path = project_dir / "mcp_server.py"
    
    print("🔧 Configuración MCP para tu proyecto:")
    print("="*50)
    print()
    
    config = {
        "servers": {
            "mi-servidor-personalizado": {
                "command": str(python_path),
                "args": [str(server_path)],
                "cwd": str(project_dir)
            }
        }
    }
    
    import json
    print(json.dumps(config, indent=2))
    print()
    print("📋 Copia este JSON a tu archivo .vscode/mcp.json")

if __name__ == "__main__":
    get_project_paths()
```

---

## 🧪 Testing y Debugging

### 1. Script de Prueba Manual

**test_mcp.py**
```python
#!/usr/bin/env python3
"""
Script de prueba para el servidor MCP
Permite probar herramientas sin VS Code
"""

import asyncio
import json
import sys
from pathlib import Path

# Importar el servidor
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import server

async def test_server():
    """Prueba todas las herramientas del servidor."""
    print("🚀 Probando servidor MCP")
    print("="*40)
    
    # Probar cada herramienta
    test_cases = [
        {
            "name": "test_tool",
            "args": {"message": "Prueba desde script"}
        },
        {
            "name": "list_files", 
            "args": {"directory": "."}
        },
        {
            "name": "project_info",
            "args": {}
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ Probando {test['name']}...")
        try:
            # Buscar handler
            for tool in server.tools:
                if tool["name"] == test["name"]:
                    result = await tool["handler"](test["args"])
                    print(f"✅ {result}")
                    break
            else:
                print(f"❌ Herramienta no encontrada: {test['name']}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Pruebas completadas. Servidor tiene {len(server.tools)} herramientas.")

if __name__ == "__main__":
    asyncio.run(test_server())
```

### 2. Script de Diagnóstico

**diagnose_mcp.py**
```python
#!/usr/bin/env python3
"""
Diagnóstico completo del setup MCP
"""

import json
import os
import sys
from pathlib import Path

def diagnose_mcp_setup():
    """Diagnóstica la configuración MCP."""
    print("🔍 Diagnóstico MCP Setup")
    print("="*30)
    
    # Verificar Python
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Dir: {os.getcwd()}")
    
    # Verificar archivos
    files_to_check = [
        ".vscode/mcp.json",
        "mcp_server.py",
        ".venv/bin/python3"  # o .venv/Scripts/python.exe en Windows
    ]
    
    print("\n📋 Archivos requeridos:")
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
    
    # Verificar configuración MCP
    mcp_config_path = Path(".vscode/mcp.json")
    if mcp_config_path.exists():
        print(f"\n🔧 Configuración MCP:")
        try:
            with open(mcp_config_path) as f:
                config = json.load(f)
            
            for server_name, server_config in config.get("servers", {}).items():
                print(f"  🖥️ Servidor: {server_name}")
                print(f"     Command: {server_config.get('command')}")
                print(f"     Args: {server_config.get('args')}")
                print(f"     CWD: {server_config.get('cwd')}")
                
                # Verificar que los paths existan
                cmd_path = Path(server_config.get('command', ''))
                if cmd_path.exists():
                    print(f"     ✅ Python ejecutable encontrado")
                else:
                    print(f"     ❌ Python ejecutable no encontrado")
                
        except Exception as e:
            print(f"❌ Error leyendo configuración: {e}")
    
    # Verificar importación del servidor
    print(f"\n🔄 Probando importación del servidor...")
    try:
        from mcp_server import server
        print(f"✅ Servidor importado correctamente")
        print(f"📊 Herramientas registradas: {len(server.tools)}")
        for tool in server.tools:
            print(f"   - {tool['name']}")
    except Exception as e:
        print(f"❌ Error importando servidor: {e}")

if __name__ == "__main__":
    diagnose_mcp_setup()
```

### 3. Logs y Debugging

**Encontrar logs de MCP en VS Code:**

```python
#!/usr/bin/env python3
"""
Encuentra y muestra logs de MCP de VS Code
"""

import os
from pathlib import Path

def find_mcp_logs():
    """Encuentra archivos de log de MCP."""
    possible_log_dirs = [
        Path.home() / "Library/Application Support/Code - Insiders/logs",
        Path.home() / "Library/Application Support/Code/logs", 
        Path.home() / ".vscode-insiders/logs",
        Path.home() / ".vscode/logs"
    ]
    
    print("🔍 Buscando logs de MCP...")
    
    for log_dir in possible_log_dirs:
        if log_dir.exists():
            print(f"📂 Directorio de logs encontrado: {log_dir}")
            
            # Buscar logs recientes
            log_files = list(log_dir.rglob("*mcp*"))
            log_files.extend(list(log_dir.rglob("*copilot*")))
            
            if log_files:
                print("📋 Archivos de log relevantes:")
                for log_file in sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                    print(f"  📄 {log_file}")
            
            return log_dir
    
    print("❌ No se encontraron directorios de logs")
    return None

if __name__ == "__main__":
    find_mcp_logs()
```

---

## 🔧 Herramientas y Handlers Avanzados

### 1. Handler con Gestión de Archivos

```python
async def file_operations_handler(arguments: Dict[str, Any]) -> str:
    """Operaciones avanzadas con archivos."""
    action = arguments.get("action", "list")
    path = arguments.get("path", ".")
    
    try:
        if action == "list":
            files = []
            for item in Path(path).iterdir():
                size = item.stat().st_size if item.is_file() else 0
                files.append(f"{'📄' if item.is_file() else '📁'} {item.name} ({size} bytes)")
            return f"📂 {path}:\n" + "\n".join(files[:10])
            
        elif action == "read":
            content = Path(path).read_text(encoding='utf-8')
            return f"📄 Contenido de {path}:\n```\n{content[:500]}...\n```"
            
        elif action == "info":
            p = Path(path)
            stat = p.stat()
            return f"""
📊 Información de {path}:
- Tipo: {'Archivo' if p.is_file() else 'Directorio'}
- Tamaño: {stat.st_size} bytes
- Modificado: {stat.st_mtime}
- Permisos: {oct(stat.st_mode)[-3:]}
            """
    except Exception as e:
        return f"❌ Error en operación '{action}': {str(e)}"

# Registrar herramienta avanzada
server.add_tool(
    "file_operations",
    "Operaciones avanzadas con archivos y directorios",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "read", "info"],
                "description": "Acción a realizar"
            },
            "path": {
                "type": "string",
                "description": "Ruta del archivo o directorio",
                "default": "."
            }
        },
        "required": ["action"]
    },
    file_operations_handler
)
```

### 2. Handler con Integración de Base de Datos

```python
import sqlite3
from datetime import datetime

async def database_handler(arguments: Dict[str, Any]) -> str:
    """Operaciones con base de datos SQLite."""
    action = arguments.get("action", "status")
    db_path = arguments.get("db_path", "app.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if action == "status":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            return f"🗄️ Base de datos {db_path}:\nTablas: {[t[0] for t in tables]}"
            
        elif action == "query":
            query = arguments.get("query", "SELECT 1")
            cursor.execute(query)
            results = cursor.fetchall()
            return f"📊 Resultados:\n{results[:10]}"
            
        elif action == "create_log":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY,
                    message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            message = arguments.get("message", "Log desde MCP")
            cursor.execute("INSERT INTO logs (message) VALUES (?)", (message,))
            conn.commit()
            return f"✅ Log guardado: {message}"
            
    except Exception as e:
        return f"❌ Error de base de datos: {str(e)}"
    finally:
        conn.close()

# Registrar herramienta de base de datos
server.add_tool(
    "database",
    "Operaciones con base de datos SQLite",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["status", "query", "create_log"],
                "description": "Acción de base de datos"
            },
            "db_path": {
                "type": "string",
                "description": "Ruta a la base de datos",
                "default": "app.db"
            },
            "query": {
                "type": "string",
                "description": "Query SQL (para acción query)"
            },
            "message": {
                "type": "string",
                "description": "Mensaje de log (para acción create_log)"
            }
        },
        "required": ["action"]
    },
    database_handler
)
```

### 3. Handler con APIs Externas

```python
import aiohttp

async def api_handler(arguments: Dict[str, Any]) -> str:
    """Llamadas a APIs externas."""
    action = arguments.get("action", "status")
    
    try:
        if action == "weather":
            city = arguments.get("city", "Madrid")
            # Nota: En un caso real usarías una API key real
            async with aiohttp.ClientSession() as session:
                # Ejemplo con API pública (sustituir por API real)
                url = f"http://httpbin.org/json"
                async with session.get(url) as response:
                    data = await response.json()
                    return f"🌤️ Clima simulado para {city}: {data}"
                    
        elif action == "joke":
            async with aiohttp.ClientSession() as session:
                url = "https://official-joke-api.appspot.com/random_joke"
                async with session.get(url) as response:
                    joke = await response.json()
                    return f"😄 {joke['setup']}\n{joke['punchline']}"
                    
    except Exception as e:
        return f"❌ Error de API: {str(e)}"

# Instalar: pip install aiohttp
server.add_tool(
    "external_api",
    "Llamadas a APIs externas",
    {
        "type": "object", 
        "properties": {
            "action": {
                "type": "string",
                "enum": ["weather", "joke"],
                "description": "Tipo de API a llamar"
            },
            "city": {
                "type": "string",
                "description": "Ciudad para el clima",
                "default": "Madrid"
            }
        },
        "required": ["action"]
    },
    api_handler
)
```

---

## 🐛 Troubleshooting

### Problemas Comunes y Soluciones

#### 1. Error: "Tool is currently disabled by the user"

**Causa:** VS Code bloquea herramientas por seguridad.

**Solución:**
```python
# Crear herramienta proxy administrativa
async def admin_handler(arguments: Dict[str, Any]) -> str:
    """Herramienta proxy para funciones administrativas."""
    action = arguments.get("action")
    params = arguments.get("params", {})
    
    if action == "help":
        return "🔧 Acciones disponibles: status, execute, info"
    elif action == "status":
        return "✅ Sistema operativo"
    # Agregar más funcionalidad según necesites
```

#### 2. Error: "-32602 Invalid request parameters"

**Causa:** Incompatibilidad con MCP SDK oficial.

**Solución:** Usar implementación manual JSON-RPC como en esta guía.

#### 3. Servidor no responde

**Diagnóstico:**
```bash
# Probar servidor directamente
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python3 mcp_server.py

# Verificar permisos de ejecución
chmod +x mcp_server.py

# Verificar Python path
which python3
```

#### 4. VS Code no detecta el servidor

**Verificar configuración:**
```json
// .vscode/mcp.json debe tener rutas absolutas
{
  "servers": {
    "nombre-unico-servidor": {
      "command": "/ruta/absoluta/al/python",
      "args": ["/ruta/absoluta/al/servidor.py"],
      "cwd": "/ruta/absoluta/al/proyecto"
    }
  }
}
```

### Script de Diagnóstico Completo

```python
#!/usr/bin/env python3
"""
Diagnóstico completo de problemas MCP
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def full_diagnosis():
    """Diagnóstico completo del setup MCP."""
    print("🏥 DIAGNÓSTICO COMPLETO MCP")
    print("="*40)
    
    # 1. Verificar Python
    print(f"\n1️⃣ Python Environment:")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    print(f"   Working Dir: {os.getcwd()}")
    
    # 2. Verificar archivos críticos
    print(f"\n2️⃣ Archivos críticos:")
    critical_files = {
        ".vscode/mcp.json": "Configuración MCP",
        "mcp_server.py": "Servidor MCP",
        ".venv/bin/python3": "Python virtual env"
    }
    
    for file_path, description in critical_files.items():
        path = Path(file_path)
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {description}: {file_path}")
    
    # 3. Probar importación del servidor
    print(f"\n3️⃣ Importación del servidor:")
    try:
        sys.path.insert(0, ".")
        import mcp_server
        print(f"   ✅ Servidor importado correctamente")
        print(f"   📊 Herramientas: {len(mcp_server.server.tools)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Verificar configuración MCP
    print(f"\n4️⃣ Configuración MCP:")
    mcp_path = Path(".vscode/mcp.json")
    if mcp_path.exists():
        try:
            with open(mcp_path) as f:
                config = json.load(f)
            
            for name, server_config in config.get("servers", {}).items():
                print(f"   🖥️ {name}:")
                cmd = server_config.get("command")
                print(f"      Command: {cmd}")
                print(f"      Exists: {'✅' if Path(cmd).exists() else '❌'}")
        except Exception as e:
            print(f"   ❌ Error leyendo config: {e}")
    
    # 5. Probar servidor manualmente
    print(f"\n5️⃣ Prueba manual del servidor:")
    try:
        test_input = '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}'
        result = subprocess.run(
            [sys.executable, "mcp_server.py"],
            input=test_input,
            text=True,
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"   ✅ Servidor responde correctamente")
            # Intentar parsear respuesta
            try:
                response = json.loads(result.stdout.strip())
                print(f"   📋 Protocolo: {response.get('result', {}).get('protocolVersion')}")
            except:
                pass
        else:
            print(f"   ❌ Error del servidor: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Timeout - servidor puede estar esperando más entrada")
    except Exception as e:
        print(f"   ❌ Error ejecutando servidor: {e}")
    
    print(f"\n✅ Diagnóstico completado")

if __name__ == "__main__":
    full_diagnosis()
```

---

## 📖 Mejores Prácticas

### 1. Estructura y Organización

```python
# Organizar handlers en módulos separados
# handlers/
#   __init__.py
#   file_handlers.py
#   api_handlers.py
#   database_handlers.py

# mcp_server.py
from handlers.file_handlers import file_operations_handler
from handlers.api_handlers import api_handler
from handlers.database_handlers import database_handler
```

### 2. Manejo de Errores Robusto

```python
async def robust_handler(arguments: Dict[str, Any]) -> str:
    """Handler con manejo robusto de errores."""
    try:
        # Validar argumentos
        required_args = ["action"]
        for arg in required_args:
            if arg not in arguments:
                return f"❌ Argumento requerido faltante: {arg}"
        
        action = arguments["action"]
        
        # Log de la operación
        logger.info(f"Ejecutando acción: {action} con args: {arguments}")
        
        # Lógica principal
        if action == "example":
            result = perform_example_operation(arguments)
            logger.info(f"Acción {action} completada exitosamente")
            return f"✅ {result}"
        else:
            return f"❌ Acción no soportada: {action}"
            
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return f"❌ Error de validación: {str(e)}"
    except FileNotFoundError as e:
        logger.error(f"Archivo no encontrado: {e}")
        return f"❌ Archivo no encontrado: {str(e)}"
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return f"❌ Error inesperado: {str(e)}"
```

### 3. Logging y Debugging

```python
import logging
from datetime import datetime

# Configurar logging detallado
def setup_logging():
    """Configura logging detallado para debugging."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    
    # Archivo de log
    log_file = f"mcp_server_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stderr)
        ]
    )
    
    logger = logging.getLogger("mcp-server")
    logger.info("Logging configurado correctamente")
    return logger

# Usar en el servidor
logger = setup_logging()
```

### 4. Configuración Flexible

```python
import json
from pathlib import Path

class MCPConfig:
    """Gestión de configuración del servidor MCP."""
    
    def __init__(self, config_file="mcp_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self):
        """Carga configuración desde archivo."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        else:
            # Configuración por defecto
            default_config = {
                "server_name": "mi-servidor-mcp",
                "version": "1.0.0",
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "allowed_paths": ["."],
                "debug": False
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Guarda configuración a archivo."""
        config = config or self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key, default=None):
        """Obtiene valor de configuración."""
        return self.config.get(key, default)

# Usar en el servidor
config = MCPConfig()
server = SimpleMCPServer(config.get("server_name"))
```

### 5. Testing Automatizado

```python
import unittest
from unittest.mock import patch, AsyncMock

class TestMCPServer(unittest.TestCase):
    """Tests para el servidor MCP."""
    
    def setUp(self):
        """Setup para cada test."""
        from mcp_server import server
        self.server = server
        
    async def test_tool_registration(self):
        """Test registro de herramientas."""
        initial_count = len(self.server.tools)
        
        # Registrar herramienta de prueba
        self.server.add_tool(
            "test_registration",
            "Test tool",
            {"type": "object", "properties": {}},
            lambda x: "test"
        )
        
        self.assertEqual(len(self.server.tools), initial_count + 1)
    
    async def test_initialize_request(self):
        """Test solicitud de inicialización."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        self.assertEqual(response["jsonrpc"], "2.0")
        self.assertEqual(response["id"], 1)
        self.assertIn("result", response)
        self.assertIn("protocolVersion", response["result"])
    
    async def test_tools_list(self):
        """Test listado de herramientas."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = await self.server.handle_request(request)
        
        self.assertIn("result", response)
        self.assertIn("tools", response["result"])
        self.assertIsInstance(response["result"]["tools"], list)

# Ejecutar tests
if __name__ == "__main__":
    import asyncio
    
    async def run_tests():
        suite = unittest.TestLoader().loadTestsFromTestCase(TestMCPServer)
        runner = unittest.TextTestRunner(verbosity=2)
        
        # Adaptar para async
        for test in suite:
            if hasattr(test._testMethodName, 'test_'):
                await getattr(test, test._testMethodName)()
    
    asyncio.run(run_tests())
```

---

## 🚀 Ejemplos Avanzados

### 1. Integración con Git

```python
import subprocess
import json

async def git_handler(arguments: Dict[str, Any]) -> str:
    """Operaciones con Git."""
    action = arguments.get("action", "status")
    
    try:
        if action == "status":
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                if lines:
                    return f"📋 Git Status:\n" + "\n".join(f"  {line}" for line in lines)
                else:
                    return "✅ Working directory clean"
            else:
                return f"❌ Git error: {result.stderr}"
                
        elif action == "log":
            count = arguments.get("count", 5)
            result = subprocess.run(
                ["git", "log", f"--oneline", f"-{count}"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"📜 Last {count} commits:\n{result.stdout}"
            else:
                return f"❌ Git log error: {result.stderr}"
                
        elif action == "diff":
            result = subprocess.run(
                ["git", "diff", "--stat"],
                capture_output=True,
                text=True
            )
            
            return f"📊 Git Diff:\n{result.stdout or 'No changes'}"
            
    except Exception as e:
        return f"❌ Git operation error: {str(e)}"

server.add_tool(
    "git_operations",
    "Operaciones con Git repository",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["status", "log", "diff"],
                "description": "Operación Git a realizar"
            },
            "count": {
                "type": "integer",
                "description": "Número de commits para log",
                "default": 5
            }
        },
        "required": ["action"]
    },
    git_handler
)
```

### 2. Análisis de Código

```python
import ast
import os

async def code_analysis_handler(arguments: Dict[str, Any]) -> str:
    """Análisis estático de código Python."""
    action = arguments.get("action", "analyze")
    file_path = arguments.get("file_path", "mcp_server.py")
    
    try:
        if action == "analyze":
            if not Path(file_path).exists():
                return f"❌ Archivo no encontrado: {file_path}"
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
                
                # Contar elementos
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
                
                lines = len(content.split('\n'))
                
                analysis = f"""
📊 **Análisis de {file_path}:**

📏 **Métricas:**
- Líneas de código: {lines}
- Funciones: {len(functions)}
- Clases: {len(classes)}  
- Imports: {len(imports)}

🔧 **Funciones:**
"""
                for func in functions[:10]:  # Primeras 10
                    analysis += f"- {func.name}() (línea {func.lineno})\n"
                
                if classes:
                    analysis += f"\n🏗️ **Clases:**\n"
                    for cls in classes:
                        analysis += f"- {cls.name} (línea {cls.lineno})\n"
                
                return analysis
                
            except SyntaxError as e:
                return f"❌ Error de sintaxis en {file_path}: {e}"
                
        elif action == "functions":
            # Listar solo funciones
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read())
            
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Obtener docstring si existe
                    docstring = ast.get_docstring(node) or "Sin documentación"
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "doc": docstring[:100] + "..." if len(docstring) > 100 else docstring
                    })
            
            result = f"🔧 **Funciones en {file_path}:**\n"
            for func in functions:
                result += f"- **{func['name']}()** (línea {func['line']})\n"
                result += f"  {func['doc']}\n\n"
            
            return result
            
    except Exception as e:
        return f"❌ Error analizando código: {str(e)}"

server.add_tool(
    "code_analysis",
    "Análisis estático de código Python",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string", 
                "enum": ["analyze", "functions"],
                "description": "Tipo de análisis"
            },
            "file_path": {
                "type": "string",
                "description": "Ruta del archivo Python a analizar",
                "default": "mcp_server.py"
            }
        },
        "required": ["action"]
    },
    code_analysis_handler
)
```

### 3. Monitor del Sistema

```python
import psutil
import platform

async def system_monitor_handler(arguments: Dict[str, Any]) -> str:
    """Monitor del sistema operativo."""
    action = arguments.get("action", "overview")
    
    try:
        if action == "overview":
            # Información general del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return f"""
🖥️ **Monitor del Sistema**

💻 **Sistema:** {platform.system()} {platform.release()}
🏗️ **Arquitectura:** {platform.machine()}
🐍 **Python:** {platform.python_version()}

📊 **Recursos:**
- CPU: {cpu_percent}%
- RAM: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
- Disco: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)

⚡ **Procesos Python activos:** {len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()])}
"""
            
        elif action == "processes":
            # Lista de procesos
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if proc.info['cpu_percent'] > 0 or proc.info['memory_percent'] > 1:
                        processes.append(proc.info)
                except:
                    continue
            
            # Ordenar por uso de CPU
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            result = "🔄 **Procesos más activos:**\n"
            for proc in processes[:10]:
                result += f"- {proc['name']} (PID {proc['pid']}): CPU {proc['cpu_percent']:.1f}%, RAM {proc['memory_percent']:.1f}%\n"
            
            return result
            
        elif action == "disk_usage":
            # Uso de disco por directorio
            current_dir = Path.cwd()
            total_size = 0
            
            result = f"💾 **Uso de disco en {current_dir}:**\n"
            
            for item in current_dir.iterdir():
                if item.is_file():
                    size = item.stat().st_size
                    total_size += size
                    if size > 1024 * 1024:  # > 1MB
                        result += f"📄 {item.name}: {size // (1024*1024)}MB\n"
                elif item.is_dir() and not item.name.startswith('.'):
                    try:
                        dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                        total_size += dir_size
                        if dir_size > 1024 * 1024:  # > 1MB
                            result += f"📁 {item.name}/: {dir_size // (1024*1024)}MB\n"
                    except:
                        result += f"📁 {item.name}/: (sin acceso)\n"
            
            result += f"\n📊 **Total proyecto:** {total_size // (1024*1024)}MB"
            return result
            
    except Exception as e:
        return f"❌ Error del monitor: {str(e)}"

# Instalar: pip install psutil
server.add_tool(
    "system_monitor",
    "Monitor del sistema operativo y recursos",
    {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["overview", "processes", "disk_usage"],
                "description": "Tipo de monitoreo"
            }
        },
        "required": ["action"]
    },
    system_monitor_handler
)
```

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs)
- [VS Code MCP Integration Guide](https://code.visualstudio.com/docs/copilot/mcp)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### Herramientas Útiles
- **MCP Inspector:** Herramienta de debugging para servidores MCP
- **Postman/Insomnia:** Para probar requests JSON-RPC manualmente
- **VS Code Extensions:** GitHub Copilot, GitHub Copilot Chat

### Ejemplos en GitHub
```bash
# Clonar ejemplos oficiales
git clone https://github.com/modelcontextprotocol/examples.git
cd examples/servers/python
```

---

## ✅ Checklist Final

### Pre-Deploy
- [ ] ✅ Servidor MCP implementado y probado
- [ ] 🔧 Configuración `.vscode/mcp.json` con rutas absolutas
- [ ] 🧪 Script de pruebas funcionando
- [ ] 📝 Logs de debugging configurados
- [ ] 🛡️ Manejo de errores implementado
- [ ] 📊 Herramientas registradas y documentadas

### Deploy y Testing
- [ ] 🚀 VS Code detecta el servidor MCP
- [ ] 💬 Copilot Chat puede invocar herramientas
- [ ] 🔄 Todas las herramientas responden correctamente
- [ ] 📋 Scripts de diagnóstico ejecutados sin errores
- [ ] 🎯 Casos de uso principales validados

### Post-Deploy
- [ ] 📚 Documentación actualizada
- [ ] 🔒 Permisos de seguridad revisados
- [ ] 📈 Monitoreo de performance en lugar
- [ ] 👥 Equipo entrenado en el uso del servidor
- [ ] 🔄 Plan de mantenimiento establecido

---

## 🎉 Conclusión

Esta guía te proporciona todo lo necesario para crear, implementar y mantener un servidor MCP personalizado para VS Code. El enfoque manual con JSON-RPC garantiza máxima compatibilidad y control sobre tu implementación.

### Próximos Pasos Recomendados:

1. **Implementar tu primer servidor** usando los ejemplos básicos
2. **Agregar herramientas específicas** para tu proyecto
3. **Configurar testing automatizado** para garantizar estabilidad
4. **Expandir funcionalidades** con integraciones avanzadas
5. **Compartir con tu equipo** y documentar casos de uso

**¡Tu servidor MCP está listo para revolucionar tu workflow de desarrollo!** 🚀

---

*Guía creada: 13 de junio de 2025*  
*Versión: 1.0.0*  
*Autor: AI Assistant para X Media Downloader Project*

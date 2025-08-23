# MCP Streaming Client

Cliente MCP (Model Context Protocol) con soporte para recibir y manejar streaming de resultados parciales en tiempo real.

## 🚀 Características

- **Manejo de Progreso**: Recibe y muestra actualizaciones de progreso en tiempo real
- **Visualización Mejorada**: Barra de progreso visual y información detallada
- **Múltiples Demos**: Ejemplos de diferentes tipos de tareas streaming
- **Manejo de Errores**: Gestión robusta de errores y timeouts
- **Logging Estructurado**: Información detallada de cada operación

## 🔧 Componentes

### `StreamingProgressHandler`
Maneja y visualiza el progreso de las tareas de streaming.

**Características:**
- Barra de progreso visual con caracteres Unicode
- Cálculo automático de porcentajes
- Tracking de tiempo transcurrido
- Historial de actualizaciones

### `MCPStreamingClient` 
Cliente principal para conectar con servidores MCP streaming.

**Características:**
- Conexión automática con transports StreamableHTTP
- Manejo de timeouts para operaciones largas
- Test de conectividad automático
- Listado de herramientas disponibles

### `TaskResult`
Dataclass que encapsula los resultados de tareas ejecutadas.

**Campos:**
- `task_name`: Nombre de la tarea
- `result`: Resultado de la tarea
- `progress_updates`: Lista de actualizaciones recibidas
- `duration`: Tiempo total de ejecución
- `success`: Indicador de éxito/fallo
- `error_message`: Mensaje de error (si aplica)

## 📦 Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Asegurar que el servidor esté ejecutándose en `http://localhost:8000/mcp/`

3. Ejecutar el cliente:
```bash
python cliente.py
```

## 🎯 Demos Incluidos

### 1. Tarea Larga (`long_running_task`)
Demuestra progreso paso a paso en tareas largas.

```
📋 DEMO: Tarea Larga con Progreso
📊 Procesamiento de Datos: |████████████████████████████| 100.0% (8/8) - Completado paso 8/8
✅ Tarea completada en 8.23s
```

### 2. Procesamiento de Datos (`streaming_data_processor`)
Muestra procesamiento de datos en lotes.

```  
💾 DEMO: Procesamiento de Datos
📊 Procesamiento: |██████████████████████████████| 100.0% (50/50) - Procesados 50/50 elementos
✅ Procesamiento completado en 5.15s
```

### 3. Subida de Archivos (`file_upload_simulation`)
Simula subida de archivos con progreso por chunks.

```
📤 DEMO: Subida de Archivos  
📊 Subida: |████████████████████████████████| 100.0% (30/30) - Subiendo archivo_3.dat - chunk 10/10
✅ Subida completada en 6.08s
```

### 4. Monitoreo Tiempo Real (`realtime_monitoring`)
Monitoreo de métricas con actualizaciones periódicas.

```
📡 DEMO: Monitoreo en Tiempo Real
📊 Monitoreo: |████████████████████████████████| 100.0% (10/10) - Monitoreo activo - CPU: 45%, MEM: 67%
✅ Monitoreo completado en 20.12s
```

## 🔧 Uso Programático

### Conexión Básica

```python
async with MCPStreamingClient("http://localhost:8000/mcp/") as client:
    # Probar conexión
    connected = await client.test_connection()
    
    # Listar herramientas
    tools = await client.list_available_tools()
    
    # Ejecutar herramienta con progreso
    progress_handler = StreamingProgressHandler("Mi Tarea")
    result = await client.call_streaming_tool(
        "long_running_task",
        {"name": "Procesamiento", "steps": 5},
        progress_callback=progress_handler
    )
```

### Manejo Custom de Progreso

```python
def mi_progress_handler(progress: float, total: float, message: str):
    percentage = (progress / total) * 100
    print(f"Progreso: {percentage:.1f}% - {message}")

async with MCPStreamingClient() as client:
    result = await client.call_streaming_tool(
        "streaming_data_processor",
        {"data_size": 100},
        progress_callback=mi_progress_handler
    )
```

## 📊 Visualización de Progreso

La barra de progreso utiliza:
- `█` para partes completadas
- `░` para partes pendientes
- Información en tiempo real (porcentaje, mensaje, tiempo)

Ejemplo:
```
📊 Tarea: |██████████████████░░░░░░░░░░░░░| 60.0% (6/10) - Procesando item 6 [12.3s]
```

## 🎯 Configuración

### Cambiar URL del Servidor
```python
client = MCPStreamingClient("http://example.com:9000/mcp/")
```

### Timeout Personalizado
```python
transport = StreamableHttpTransport(
    url="http://localhost:8000/mcp/",
    sse_read_timeout=120.0  # 2 minutos
)
client = MCPStreamingClient()
client.transport = transport
```

## 📋 Resumen de Ejecución

Al final de cada demo, se muestra un resumen:

```
📈 RESUMEN DE EJECUCIÓN
✅ ÉXITO long_running_task: 8.23s (8 actualizaciones)
✅ ÉXITO streaming_data_processor: 5.15s (10 actualizaciones) 
✅ ÉXITO file_upload_simulation: 6.08s (30 actualizaciones)
✅ ÉXITO realtime_monitoring: 20.12s (10 actualizaciones)

📊 Total: 4/4 tareas exitosas
⏱️ Tiempo total: 39.58s
```

## ⚠️ Requisitos

- Python 3.8+
- FastMCP 2.0.0+
- Servidor MCP ejecutándose
- Conexión de red estable

## 🔧 Troubleshooting

### Error de Conexión
```
❌ Error de conexión: Connection refused
```
**Solución**: Verificar que el servidor esté ejecutándose en el puerto correcto.

### Timeout de Streaming  
```
❌ Error: Read timeout
```
**Solución**: Aumentar `sse_read_timeout` en el transport.

### FastMCP No Disponible
```
⚠️ FastMCP no está instalado. Ejecuta: pip install fastmcp
```
**Solución**: Instalar FastMCP según las instrucciones.
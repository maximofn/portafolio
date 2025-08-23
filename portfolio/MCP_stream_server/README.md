# MCP Streaming Server

Servidor MCP (Model Context Protocol) con soporte para streaming y envío de resultados parciales en tiempo real.

## 🚀 Características

- **Streaming en tiempo real**: Envía actualizaciones de progreso mientras las tareas se ejecutan
- **Múltiples herramientas**: Diferentes tipos de tareas para demostrar capacidades
- **Transport HTTP**: Utiliza StreamableHTTP para comunicación eficiente
- **Logging estructurado**: Información detallada del proceso

## 🔧 Herramientas Disponibles

### 1. `long_running_task`
Simula una tarea larga con reporte de progreso paso a paso.

**Parámetros:**
- `name` (str): Nombre de la tarea (default: "Tarea")  
- `steps` (int): Número de pasos a ejecutar (default: 10)

### 2. `streaming_data_processor`
Procesa datos en lotes enviando actualizaciones de progreso.

**Parámetros:**
- `data_size` (int): Cantidad de elementos a procesar (default: 100)

### 3. `file_upload_simulation`
Simula subida de archivos con progreso por chunks.

**Parámetros:**
- `file_count` (int): Número de archivos a subir (default: 5)

### 4. `realtime_monitoring`
Monitoreo de métricas del sistema en tiempo real.

**Parámetros:**
- `duration_seconds` (int): Duración del monitoreo (default: 30)

## 📦 Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar el servidor:
```bash
python servidor.py
```

El servidor se ejecutará en `http://localhost:8000/mcp/`

## 🔗 Configuración

### Cambiar Puerto
```python
asyncio.run(run_streaming_server(port=9000))
```

### Cambiar Host
```python
asyncio.run(run_streaming_server(host="0.0.0.0", port=8000))
```

## 📡 API Endpoints

- **Base URL**: `http://localhost:8000/mcp/`
- **Transport**: StreamableHTTP
- **Timeout**: 60 segundos para operaciones de streaming

## 🧪 Pruebas

Para probar el servidor, utiliza el cliente incluido en la carpeta `../MCP_stream_client/`.

## 📋 Logs

El servidor genera logs detallados incluyendo:
- 🚀 Inicio de tareas
- 📊 Actualizaciones de progreso  
- ✅ Completación de pasos
- 🎉 Finalización exitosa

## 🔧 Desarrollo

### Agregar Nueva Herramienta

```python
@mcp.tool
async def mi_nueva_herramienta(parametro: str, context: Context = None) -> dict:
    \"\"\"Descripción de la herramienta.\"\"\"
    
    if context:
        await context.info("Iniciando herramienta...")
    
    # Tu lógica aquí
    for i in range(pasos):
        # Trabajo
        if context:
            await context.report_progress(
                progress=i + 1,
                total=pasos,
                message=f"Progreso: {i + 1}/{pasos}"
            )
    
    return {"resultado": "éxito"}
```

## ⚠️ Notas

- Requiere FastMCP 2.0.0+
- Compatible con Python 3.8+
- Usa asyncio para operaciones concurrentes
- Transport StreamableHTTP es preferido sobre SSE
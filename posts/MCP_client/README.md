# Cliente MCP con Integración de Claude

Este script implementa un cliente para el Protocolo de Contexto de Modelo (MCP) que se integra con un modelo de lenguaje de Anthropic (Claude) para procesar consultas de usuario y utilizar herramientas expuestas por un servidor MCP.

## Funcionalidades

*   Se conecta a un servidor MCP especificado (Python o JavaScript).
*   Lista las herramientas disponibles en el servidor MCP.
*   Interactúa con el modelo Claude 3.5 Sonnet (u otro configurado) para procesar las consultas del usuario.
*   Si Claude decide utilizar una herramienta, el cliente ejecuta la llamada a la herramienta a través de la sesión MCP.
*   Envía el resultado de la herramienta de nuevo a Claude para obtener una respuesta final.
*   Proporciona un bucle de chat interactivo para que el usuario ingrese consultas.

## Requisitos Previos

1.  **Python 3.7+**
2.  **Dependencias de Python:**
    *   `mcp-sdk`
    *   `anthropic`
    *   `python-dotenv`
    Puedes instalarlas usando pip:
    ```bash
    pip install mcp-sdk anthropic python-dotenv
    ```
3.  **Clave API de Anthropic:**
    El script utiliza la biblioteca `anthropic`, que requiere una clave API. Asegúrate de tener un archivo `.env` en el mismo directorio que `client.py` con tu clave API:
    ```
    ANTHROPIC_API_KEY=tu_clave_api_aqui
    ```
    (Reemplaza `tu_clave_api_aqui` con tu clave API real).
4.  **Un servidor MCP:**
    Necesitarás un script de servidor MCP (ya sea `.py` o `.js`) al que este cliente pueda conectarse. El servidor debe exponer las herramientas que Claude podría querer utilizar.

## Uso

Para ejecutar el cliente, proporciona la ruta al script del servidor MCP como argumento de línea de comandos:

```bash
python client.py <ruta_al_script_del_servidor>
```

Por ejemplo:

*   Si tu servidor es un script de Python llamado `mi_servidor.py`:
    ```bash
    python client.py mi_servidor.py
    ```
*   Si tu servidor es un script de JavaScript llamado `mi_servidor.js`:
    ```bash
    python client.py mi_servidor.js
    ```

Una vez conectado, el cliente mostrará las herramientas disponibles en el servidor y luego podrás empezar a ingresar tus consultas en la terminal. Escribe `quit` para salir del cliente.

## Estructura del Código (`client.py`)

El script `client.py` está organizado principalmente alrededor de la clase `MCPClient`:

*   **`MCPClient` class:**
    *   `__init__`: Inicializa el cliente, la pila de salida asíncrona (`AsyncExitStack`) y el cliente de Anthropic. Carga las variables de entorno (como la clave API de Anthropic) desde un archivo `.env`.
    *   `connect_to_server(server_script_path)`: Establece la conexión con el servidor MCP. Determina si el script del servidor es Python o JavaScript y lo ejecuta apropiadamente. Inicializa la sesión MCP.
    *   `process_query(query)`: Procesa una consulta del usuario.
        1.  Obtiene la lista de herramientas disponibles del servidor MCP.
        2.  Envía la consulta y las herramientas disponibles al modelo de Claude.
        3.  Si Claude responde con texto, se considera la respuesta final (o parte de ella).
        4.  Si Claude responde con una solicitud para usar una herramienta (`tool_use`):
            a.  El cliente MCP llama a la herramienta especificada en el servidor MCP.
            b.  El resultado de la herramienta se devuelve al cliente.
            c.  Este resultado se envía de nuevo a Claude.
            d.  Claude genera una nueva respuesta basada en el resultado de la herramienta.
        5.  Devuelve el texto final acumulado.
    *   `chat_loop()`: Gestiona el bucle de chat interactivo, permitiendo al usuario ingresar consultas repetidamente hasta que escriba 'quit'. Maneja errores durante el procesamiento de consultas.
    *   `cleanup()`: Cierra la conexión MCP y limpia los recursos utilizando `AsyncExitStack`.
*   **`main()` function (asíncrona):**
    *   Verifica los argumentos de la línea de comandos (asegurándose de que se proporcione la ruta al script del servidor).
    *   Crea una instancia de `MCPClient`.
    *   Llama a `connect_to_server` y luego a `chat_loop`.
    *   Asegura que `cleanup` se llame al final, incluso si ocurren errores.
*   **Bloque `if __name__ == "__main__":`:**
    *   Punto de entrada del script. Importa `sys` y `asyncio`.
    *   Ejecuta la función `main()` usando `asyncio.run()`.

## Flujo de Trabajo

1.  El usuario ejecuta `python client.py <ruta_servidor>`.
2.  El script carga las variables de entorno (incluida `ANTHROPIC_API_KEY`).
3.  El `MCPClient` se conecta al servidor MCP especificado.
4.  Se listan e imprimen las herramientas del servidor.
5.  Comienza el bucle de chat:
    a.  El usuario escribe una consulta.
    b.  La consulta se envía a `process_query`.
    c.  `process_query` interactúa con Claude y, si es necesario, con las herramientas del servidor MCP.
    d.  La respuesta final de Claude se imprime en la consola.
6.  El bucle continúa hasta que el usuario escribe `quit`.
7.  Al salir, se limpian los recursos y se cierra la conexión.

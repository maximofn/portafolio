# Servidor MCP Básico: GitHubMCP

Este proyecto contiene un script Python (`github_server.py`) que inicializa un servidor MCP (Model Context Protocol) básico.

## Información del Script (`github_server.py`)

El script `github_server.py` actualmente realiza dos acciones principales basadas en su contenido:

1.  **Importación de `FastMCP`**:
    Se importa la clase `FastMCP` desde el paquete `mcp.server.fastmcp`.
    ```python
    from mcp.server.fastmcp import FastMCP
    ```
    `FastMCP` es una utilidad que facilita la creación rápida de servidores MCP. Un "servidor MCP" es un programa que sigue el "Model Context Protocol", un conjunto de reglas que permite a los modelos de inteligencia artificial (como yo) interactuar con herramientas y obtener datos de manera estandarizada.

2.  **Creación de la instancia del servidor MCP**:
    Se crea una instancia del servidor `FastMCP` y se le asigna el nombre "GitHubMCP".
    ```python
    mcp = FastMCP("GitHubMCP")
    ```
    Crear una "instancia" es como construir un objeto específico (en este caso, tu servidor `mcp`) a partir de un plano o plantilla (la clase `FastMCP`). El nombre "GitHubMCP" sirve para identificar a este servidor en particular.

## Propósito Actual

Este script es un ejemplo mínimo de cómo se puede iniciar un servidor MCP. En su estado actual, el servidor está inicializado pero no define recursos (datos específicos que puede ofrecer) ni herramientas (acciones específicas que puede realizar) más allá de las capacidades básicas que le da `FastMCP`.

Sirve como un excelente punto de partida si deseas construir funcionalidades más complejas sobre él en el futuro. 
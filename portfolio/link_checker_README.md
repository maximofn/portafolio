# Verificador de Enlaces para Portafolio

Este script de Python te permite verificar si hay enlaces rotos en tu proyecto de portafolio. Analiza todos los archivos relevantes y comprueba tanto enlaces internos como externos.

## Características

- ✅ Verifica enlaces internos y externos
- ✅ Detecta URLs en archivos HTML, Astro, Markdown, JSON y otros formatos
- ✅ Procesamiento en paralelo para mayor velocidad
- ✅ Guarda resultados en formato JSON
- ✅ Genera reportes visuales en HTML
- ✅ Interfaz de línea de comandos con opciones configurables
- ✅ Colorización de la salida en terminal
- ✅ Ignora automáticamente URLs específicas (como las de Hugging Face)
- ✅ Reportes organizados por archivo para fácil corrección
- ✅ Excluye archivos específicos y patrones de archivos de la verificación
- ✅ Configuración externa de URLs a ignorar mediante archivo JSON

## Requisitos

Para usar este script, necesitas tener instalado:

- Python 3.6 o superior
- La biblioteca `requests`

Puedes instalar las dependencias con:

```bash
pip install requests
```

## Uso

### Uso básico

Para verificar todos los enlaces en el directorio actual:

```bash
python link_checker.py
```

### Opciones disponibles

```bash
python link_checker.py --dir /ruta/a/tu/proyecto --verbose --skip-internal --ignore "patrón1" --ignore-file "archivo.md" --no-html
```

Opciones:
- `--dir`, `-d`: Especifica el directorio base del proyecto (por defecto: directorio actual)
- `--verbose`, `-v`: Muestra información detallada durante la verificación
- `--skip-internal`, `-s`: Omite la verificación de enlaces internos (solo verifica enlaces externos)
- `--ignore`, `-i`: Especifica patrones de URLs a ignorar (puede usarse múltiples veces)
- `--ignore-file`, `-f`: Especifica archivos adicionales a ignorar (puede usarse múltiples veces)
- `--no-html`: No genera el reporte HTML (solo JSON y salida en terminal)

## Interpretación de resultados

El script mostrará un resumen de los resultados en la terminal:

- Total de archivos verificados
- Total de enlaces encontrados
- Enlaces correctos
- Enlaces omitidos (anclas, mailto:, etc.)
- Enlaces rotos

Si se encuentran enlaces rotos, se mostrarán agrupados por archivo para facilitar su corrección:

```
Archivo: src/pages/blog/post1.astro
  1. URL: https://ejemplo.com/ruta-rota
     Razón: Código de estado HTTP: 404

  2. URL: https://otro-ejemplo.com/pagina
     Razón: Tiempo de espera agotado

Archivo: src/components/Footer.astro
  1. URL: https://servicio-caido.com
     Razón: No se pudo resolver el nombre de host
```

### Archivos de resultados

El script genera dos archivos con los resultados:

1. **link_checker_results.json**: Archivo JSON con todos los datos detallados, incluyendo:
   - Estadísticas generales
   - Lista completa de enlaces rotos
   - Enlaces rotos agrupados por archivo
   - Patrones de URLs ignorados

2. **link_checker_report.html**: Reporte visual en HTML que muestra:
   - Resumen de estadísticas
   - Lista de patrones ignorados
   - Enlaces rotos organizados por archivo
   - Diseño responsivo y fácil de leer

![Ejemplo de reporte HTML](https://i.imgur.com/example.png)

## Personalización

Puedes personalizar el comportamiento del verificador modificando las constantes en la clase `Config`:

- `FILE_EXTENSIONS`: Extensiones de archivos a revisar
- `IGNORE_DIRS`: Directorios a ignorar durante la verificación
- `IGNORE_FILES`: Archivos específicos a ignorar (como este README)
- `IGNORE_FILE_PATTERNS`: Patrones regex para ignorar archivos
- `TIMEOUT`: Tiempo de espera para las solicitudes HTTP (en segundos)
- `MAX_WORKERS`: Número máximo de hilos para las solicitudes concurrentes
- `URL_PATTERNS`: Patrones regex para encontrar URLs en archivos

### Archivo de configuración de URLs a ignorar

El script utiliza un archivo JSON externo (`ignore_urls.json`) para gestionar la lista de URLs y patrones que deben ignorarse durante la verificación. Este archivo tiene el siguiente formato:

```json
{
  "ignore_patterns": [
    "https://cdn-lfs-us-1.huggingface.co/repos",
    "openai/dall-e-3.png",
    "https://wa.me/",
    "wa.me/",
    "example.com",
    "ejemplo.com",
    "localhost",
    "127.0.0.1"
  ],
  "description": "Lista de patrones de URLs y cadenas a ignorar durante la verificación de enlaces."
}
```

Para añadir nuevas URLs o patrones a ignorar, simplemente edita este archivo y añade las entradas a la lista `ignore_patterns`.

### Archivos y directorios ignorados

Por defecto, el script ignora:
- **Directorios**: `node_modules`, `.git`, `.astro`, `dist`, `public/fonts`
- **Archivos específicos**: `link_checker_README.md`, `ignore_urls.json`, etc.
- **Patrones de archivos**:
  - Todos los archivos MD que empiecen con `link_checker_` (ej: `link_checker_README.md`)
  - Archivos JavaScript minificados (terminados en `.min.js`)
  - Archivos de prueba (terminados en `.test.js` o `.test.ts`)

Para personalizar qué archivos se ignoran, puedes:
1. Añadir nombres de archivo específicos a la lista `IGNORE_FILES` en el código
2. Añadir patrones regex a la lista `IGNORE_FILE_PATTERNS` en el código
3. Usar la opción `--ignore-file` en la línea de comandos:

```bash
python link_checker.py --ignore-file "README.md" --ignore-file "CHANGELOG.md"
```

### URLs ignoradas

El script está configurado para ignorar automáticamente ciertos tipos de URLs:
- Enlaces con anclas (`#`)
- Enlaces de correo electrónico (`mailto:`)
- Enlaces de teléfono (`tel:`)
- Enlaces de JavaScript (`javascript:`)
- Enlaces a Hugging Face CDN (`https://cdn-lfs-us-1.huggingface.co/repos`)
- Enlaces a imágenes de OpenAI DALL-E (`openai/dall-e-3.png`)
- Enlaces de WhatsApp (`https://wa.me/`, `wa.me/`)
- URLs de ejemplo y marcadores de posición (definidos en `ignore_urls.json`)

Puedes ignorar URLs adicionales de tres formas:
1. Añadiendo entradas al archivo `ignore_urls.json`
2. Usando la opción `--ignore` en la línea de comandos:

```bash
python link_checker.py --ignore "ejemplo.com" --ignore "otro-dominio.org"
```

## Ejemplos de uso

### Verificar solo el directorio src

```bash
python link_checker.py --dir ./src
```

### Verificar con salida detallada

```bash
python link_checker.py --verbose
```

### Verificar solo enlaces externos

```bash
python link_checker.py --skip-internal
```

### Ignorar dominios específicos

```bash
python link_checker.py --ignore "github.com" --ignore "youtube.com"
```

### Ignorar archivos específicos

```bash
python link_checker.py --ignore-file "README.md" --ignore-file "docs/CONTRIBUTING.md"
```

### Generar solo reporte JSON (sin HTML)

```bash
python link_checker.py --no-html
```

## Código de salida

El script devuelve:
- `0` si no se encontraron enlaces rotos
- `1` si se encontró al menos un enlace roto

Esto permite integrarlo fácilmente en flujos de trabajo de CI/CD. 
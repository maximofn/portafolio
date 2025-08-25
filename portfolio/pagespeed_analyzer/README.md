# PageSpeed Insights Analyzer

Un analizador completo de rendimiento web que utiliza la API de Google PageSpeed Insights para evaluar todas las URLs de un sitio web navegando automáticamente a través de su sitemap.

## =€ Características

- **Navegación automática de sitemaps**: Detecta y procesa sitemaps índice y navega recursivamente por todos los sitemaps anidados
- **Análisis dual**: Evalúa cada URL tanto en dispositivos móviles como de escritorio
- **Métricas completas**: Extrae Core Web Vitals y métricas clave de rendimiento
- **Control de velocidad**: Incluye delays configurables para respetar los límites de la API
- **Múltiples formatos de salida**: Exporta resultados en JSON, CSV o ambos formatos
- **Resumen estadístico**: Genera informes con promedios, mejores y peores puntuaciones
- **Configuración por variables de entorno**: Carga la API key automáticamente desde archivo `.env`

## =Ê Métricas extraídas

- **Performance Score**: Puntuación general de rendimiento (0-100)
- **First Contentful Paint (FCP)**: Tiempo hasta el primer contenido visible
- **Largest Contentful Paint (LCP)**: Tiempo hasta el elemento más grande visible
- **Cumulative Layout Shift (CLS)**: Cambios inesperados de diseño
- **First Input Delay (FID)**: Tiempo de respuesta a la primera interacción
- **Speed Index**: Velocidad de carga visual del contenido
- **Time to Interactive**: Tiempo hasta que la página es completamente interactiva

## =à Instalación

### Prerrequisitos

- Python 3.7 o superior
- Conexión a internet

### Configuración

1. **Clonar o descargar** el script en tu directorio de trabajo

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar API Key** (recomendado):
   
   Crea un archivo `.env` en el mismo directorio que el script:
   ```bash
   PAGESPEED_API_KEY=tu_api_key_aqui
   ```
   
   **Obtener API Key gratuita**:
   - Visita [Google Cloud Console](https://console.cloud.google.com/)
   - Habilita la API de PageSpeed Insights
   - Crea una credencial de API Key
   - Alternativamente, sigue la [guía oficial](https://developers.google.com/speed/docs/insights/v5/get-started)

   > **Nota**: Sin API Key, tendrás límites más estrictos de solicitudes por minuto

## =€ Uso

### Comando básico

```bash
python pagespeed_analyzer.py
```

Este comando analizará todas las URLs encontradas en el sitemap por defecto (`https://www.maximofn.com/sitemap-index.xml`).

### Opciones avanzadas

```bash
# Sitemap personalizado
python pagespeed_analyzer.py --sitemap https://tu-sitio.com/sitemap.xml

# Para pruebas - analizar solo las primeras 5 URLs
python pagespeed_analyzer.py --max-urls 5

# Aumentar delay entre requests (útil si hay límites de velocidad)
python pagespeed_analyzer.py --delay 2.0

# Formato de salida específico
python pagespeed_analyzer.py --output json     # Solo JSON
python pagespeed_analyzer.py --output csv      # Solo CSV
python pagespeed_analyzer.py --output both     # Ambos (por defecto)

# Prefijo personalizado para archivos de salida
python pagespeed_analyzer.py --prefix mi_analisis

# Combinar múltiples opciones
python pagespeed_analyzer.py --sitemap https://mi-sitio.com/sitemap.xml --max-urls 10 --delay 1.5 --output json
```

### Parámetros disponibles

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `--sitemap` | URL del sitemap a analizar | `https://www.maximofn.com/sitemap-index.xml` |
| `--delay` | Delay en segundos entre requests | `1.0` |
| `--max-urls` | Máximo número de URLs a analizar | Sin límite |
| `--output` | Formato de salida: `json`, `csv`, `both` | `both` |
| `--prefix` | Prefijo para nombres de archivo | `pagespeed_results` |

## =Á Archivos de salida

El script genera archivos con timestamp en el nombre:

- **JSON**: `pagespeed_results_YYYYMMDD_HHMMSS.json`
- **CSV**: `pagespeed_results_YYYYMMDD_HHMMSS.csv`

### Estructura del JSON

```json
[
  {
    "url": "https://www.maximofn.com/",
    "strategy": "mobile",
    "performance_score": 95.2,
    "first_contentful_paint": 1.23,
    "largest_contentful_paint": 2.45,
    "cumulative_layout_shift": 0.001,
    "first_input_delay": 8.5,
    "speed_index": 1.87,
    "time_to_interactive": 2.34,
    "timestamp": "2024-01-15T10:30:45.123456"
  }
]
```

## =Ê Interpretación de resultados

### Puntuaciones de rendimiento
- **90-100**: Excelente =â
- **50-89**: Mejorable =á  
- **0-49**: Pobre =4

### Core Web Vitals - Umbrales recomendados
- **FCP**: < 1.8s (bueno), < 3.0s (mejorable)
- **LCP**: < 2.5s (bueno), < 4.0s (mejorable)
- **CLS**: < 0.1 (bueno), < 0.25 (mejorable)

## =' Solución de problemas

### Error de límite de velocidad
```bash
# Aumentar el delay entre requests
python pagespeed_analyzer.py --delay 2.0
```

### Sin API Key
```bash
# El script funcionará pero con límites más estrictos
# Recomendamos configurar una API Key en el archivo .env
```

### Interrupción del análisis
Si interrumpes el script con `Ctrl+C`, se guardarán automáticamente los resultados parciales con el prefijo `_partial`.

### URLs problemáticas
El script continúa analizando otras URLs aunque alguna falle, registrando los errores en la consola.

## <¯ Casos de uso

### Análisis completo del sitio
```bash
python pagespeed_analyzer.py
```

### Análisis rápido para testing
```bash
python pagespeed_analyzer.py --max-urls 10 --delay 0.5
```

### Análisis de sitio específico
```bash
python pagespeed_analyzer.py --sitemap https://mi-sitio.com/sitemap.xml --prefix mi_sitio
```

### Análisis conservador (evitar límites)
```bash
python pagespeed_analyzer.py --delay 3.0 --max-urls 50
```

## > Contribuciones

Las mejoras y sugerencias son bienvenidas. Algunas ideas para futuras funcionalidades:

- [ ] Filtros por tipo de página o ruta
- [ ] Análisis de progreso con barra de estado
- [ ] Comparación entre diferentes ejecuciones
- [ ] Alertas por email cuando métricas están por debajo de umbrales
- [ ] Integración con webhooks para CI/CD

##   Limitaciones

- **API Limits**: Sin API Key, Google limita a ~100 requests/hora
- **Timeouts**: URLs que tarden más de 60 segundos son omitidas
- **Sitemaps grandes**: Sitios con miles de URLs pueden tardar horas en analizarse completamente

## =Ý Licencia

Este script es de uso libre. Utilízalo y modifícalo según tus necesidades.
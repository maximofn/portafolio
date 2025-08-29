"""
Servidor MCP Multi-Turn con Sampling
====================================

Este servidor demuestra cómo implementar interacciones multi-turn usando sampling
para solicitar completions de AI del cliente durante la ejecución de herramientas.

Funcionalidades implementadas:
1. Generación de contenido asistida por AI
2. Análisis de texto con IA
3. Creación de código con AI
4. Traducción inteligente
5. Resumen de documentos
6. Combinación de elicitación + sampling

Uso:
    python server.py
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from mcp.types import TextContent

# Instancia del servidor MCP
mcp = FastMCP("Multi-Turn Sampling Server")

# Enumeraciones
class ContentType(str, Enum):
    ARTICLE = "artículo"
    EMAIL = "email"
    BLOG_POST = "blog post"
    DOCUMENTATION = "documentación"
    SOCIAL_MEDIA = "social media"

class ProgrammingLanguage(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"

# Storage temporal para contenido generado
generated_content: Dict[str, Dict[str, Any]] = {}

@mcp.tool
async def ai_content_generator(context: Context) -> str:
    """
    Generador de contenido que usa AI sampling para crear textos personalizados.
    Combina elicitación para obtener parámetros y sampling para generar contenido.
    """
    # Paso 1: Elicitar el tipo de contenido
    content_type_result = await context.elicit(
        message="¿Qué tipo de contenido quieres generar?",
        response_type=ContentType
    )
    
    if not isinstance(content_type_result, AcceptedElicitation):
        return "🚫 Generación cancelada: No se especificó tipo de contenido"
    
    content_type = content_type_result.data.value
    
    # Paso 2: Obtener el tema
    topic_result = await context.elicit(
        message=f"¿Sobre qué tema quieres que genere el {content_type}?",
        response_type=str
    )
    
    if not isinstance(topic_result, AcceptedElicitation):
        return f"⚠️ Generación parcial: Solo se configuró el tipo '{content_type}'"
    
    topic = topic_result.data
    
    # Paso 3: Obtener audiencia objetivo (opcional)
    audience_result = await context.elicit(
        message="¿Cuál es la audiencia objetivo? (técnica, general, estudiantes, etc.)",
        response_type=str
    )
    
    audience = "general"
    if isinstance(audience_result, AcceptedElicitation):
        audience = audience_result.data
    
    # Paso 4: Usar AI sampling para generar el contenido
    system_prompt = f"""Eres un experto escritor creando contenido de alta calidad. 
Debes generar un {content_type} sobre el tema '{topic}' dirigido a audiencia {audience}.
Usa un tono profesional pero accesible. Estructura el contenido de manera clara y añade valor."""
    
    user_message = f"Genera un {content_type} completo y bien estructurado sobre: {topic}"
    
    # Realizar el sampling de AI
    response = await context.sample(
        messages=user_message,
        system_prompt=system_prompt,
        max_tokens=1500,
        temperature=0.7
    )
    
    # Extraer el texto generado
    if isinstance(response, TextContent):
        generated_text = response.text
        
        # Guardar en storage
        content_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        generated_content[content_id] = {
            "type": content_type,
            "topic": topic,
            "audience": audience,
            "content": generated_text,
            "timestamp": datetime.now().isoformat()
        }
        
        return f"""
✅ Contenido generado exitosamente!

📝 Tipo: {content_type.title()}
🎯 Tema: {topic}
👥 Audiencia: {audience}
🆔 ID: {content_id}

📄 Contenido:
{generated_text}

💡 El contenido ha sido guardado y puede ser referenciado con ID: {content_id}
        """.strip()
    
    return "❌ Error: No se pudo generar el contenido"

@mcp.tool
async def intelligent_text_analyzer(context: Context) -> str:
    """
    Analizador de texto inteligente que usa AI para analizar contenido.
    """
    # Obtener el texto a analizar
    text_result = await context.elicit(
        message="Proporciona el texto que quieres analizar:",
        response_type=str
    )
    
    if not isinstance(text_result, AcceptedElicitation):
        return "🚫 Análisis cancelado: No se proporcionó texto"
    
    text_to_analyze = text_result.data
    
    # Solicitar tipo de análisis
    analysis_options = [
        "sentimiento",
        "temas principales",
        "resumen ejecutivo",
        "análisis completo"
    ]
    
    analysis_type_result = await context.elicit(
        message="¿Qué tipo de análisis quieres realizar?",
        response_type=analysis_options
    )
    
    if not isinstance(analysis_type_result, AcceptedElicitation):
        return "⚠️ Análisis básico realizado"
    
    analysis_type = analysis_type_result.data
    
    # Configurar prompt según el tipo de análisis
    analysis_prompts = {
        "sentimiento": "Analiza el sentimiento del texto proporcionado. Identifica si es positivo, negativo o neutral, y explica los indicadores que llevan a esta conclusión.",
        "temas principales": "Identifica y lista los temas principales del texto. Proporciona una explicación breve de cada tema encontrado.",
        "resumen ejecutivo": "Crea un resumen ejecutivo conciso del texto, destacando los puntos más importantes y conclusiones clave.",
        "análisis completo": "Realiza un análisis completo del texto incluyendo: sentimiento, temas principales, estructura, audiencia objetivo, y recomendaciones de mejora."
    }
    
    system_prompt = f"Eres un experto analista de textos. {analysis_prompts[analysis_type]}"
    
    # Realizar sampling de AI para el análisis
    response = await context.sample(
        messages=f"Analiza este texto:\n\n{text_to_analyze}",
        system_prompt=system_prompt,
        max_tokens=800,
        temperature=0.3
    )
    
    if isinstance(response, TextContent):
        analysis_result = response.text
        
        return f"""
🔍 Análisis de Texto Completado

📊 Tipo de análisis: {analysis_type.title()}
📏 Longitud del texto: {len(text_to_analyze)} caracteres

📋 Resultado del análisis:
{analysis_result}

⏰ Análisis realizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    return "❌ Error: No se pudo completar el análisis"

@mcp.tool
async def ai_code_generator(context: Context) -> str:
    """
    Generador de código que combina elicitación y AI sampling.
    """
    # Obtener lenguaje de programación
    language_result = await context.elicit(
        message="¿En qué lenguaje de programación quieres generar código?",
        response_type=ProgrammingLanguage
    )
    
    if not isinstance(language_result, AcceptedElicitation):
        return "🚫 Generación cancelada: No se especificó lenguaje"
    
    language = language_result.data.value
    
    # Obtener descripción de la funcionalidad
    functionality_result = await context.elicit(
        message=f"Describe la funcionalidad que quieres implementar en {language.title()}:",
        response_type=str
    )
    
    if not isinstance(functionality_result, AcceptedElicitation):
        return f"⚠️ Generación incompleta: Solo se configuró {language}"
    
    functionality = functionality_result.data
    
    # Preguntar sobre tests
    include_tests_result = await context.elicit(
        message="¿Quieres incluir tests unitarios?",
        response_type=["sí", "no"]
    )
    
    include_tests = isinstance(include_tests_result, AcceptedElicitation) and include_tests_result.data == "sí"
    
    # Configurar prompt para generación de código
    system_prompt = f"""Eres un experto desarrollador de {language.title()}. 
Genera código limpio, bien documentado y siguiendo las mejores prácticas.
Incluye comentarios explicativos y maneja errores apropiadamente."""
    
    if include_tests:
        user_message = f"Implementa la siguiente funcionalidad en {language} e incluye tests unitarios:\n{functionality}"
    else:
        user_message = f"Implementa la siguiente funcionalidad en {language}:\n{functionality}"
    
    # Generar código usando AI sampling
    response = await context.sample(
        messages=user_message,
        system_prompt=system_prompt,
        max_tokens=1200,
        temperature=0.2
    )
    
    if isinstance(response, TextContent):
        generated_code = response.text
        
        return f"""
💻 Código Generado - {language.title()}

🎯 Funcionalidad: {functionality}
🧪 Tests incluidos: {"Sí" if include_tests else "No"}

```{language}
{generated_code}
```

💡 Consejos adicionales:
- Revisa el código antes de usarlo en producción
- Ajusta las importaciones según tu entorno
- Considera agregar logging para debugging
        """.strip()
    
    return "❌ Error: No se pudo generar el código"

@mcp.tool
async def smart_translator(context: Context) -> str:
    """
    Traductor inteligente que mantiene contexto y estilo.
    """
    # Obtener texto a traducir
    text_result = await context.elicit(
        message="Proporciona el texto que quieres traducir:",
        response_type=str
    )
    
    if not isinstance(text_result, AcceptedElicitation):
        return "🚫 Traducción cancelada: No se proporcionó texto"
    
    text_to_translate = text_result.data
    
    # Obtener idiomas
    target_language_result = await context.elicit(
        message="¿A qué idioma quieres traducir?",
        response_type=["inglés", "español", "portugués", "francés", "alemán", "italiano", "japonés"]
    )
    
    if not isinstance(target_language_result, AcceptedElicitation):
        return "⚠️ Traducción incompleta: No se especificó idioma objetivo"
    
    target_language = target_language_result.data
    
    # Obtener contexto (opcional)
    context_result = await context.elicit(
        message="Proporciona contexto adicional para una mejor traducción (opcional):",
        response_type=str
    )
    
    additional_context = ""
    if isinstance(context_result, AcceptedElicitation) and context_result.data.strip():
        additional_context = f"\nContexto: {context_result.data}"
    
    # Configurar prompt para traducción
    system_prompt = f"""Eres un traductor experto especializado en mantener el tono, estilo y contexto original.
Traduce al {target_language} preservando:
- Significado preciso
- Tono y estilo
- Expresiones idiomáticas apropiadas
- Formato original{additional_context}"""
    
    # Realizar traducción usando AI sampling
    response = await context.sample(
        messages=f"Traduce este texto al {target_language}:\n\n{text_to_translate}",
        system_prompt=system_prompt,
        max_tokens=1000,
        temperature=0.1
    )
    
    if isinstance(response, TextContent):
        translation = response.text
        
        return f"""
🌍 Traducción Completada

📝 Idioma objetivo: {target_language.title()}
📏 Texto original: {len(text_to_translate)} caracteres
📏 Traducción: {len(translation)} caracteres

🔤 Texto original:
{text_to_translate}

🌐 Traducción:
{translation}

⏰ Traducción realizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    return "❌ Error: No se pudo completar la traducción"

@mcp.tool
async def document_summarizer(context: Context) -> str:
    """
    Resumidor de documentos que ajusta el nivel de detalle según necesidades.
    """
    # Obtener documento
    document_result = await context.elicit(
        message="Proporciona el documento o texto largo que quieres resumir:",
        response_type=str
    )
    
    if not isinstance(document_result, AcceptedElicitation):
        return "🚫 Resumen cancelado: No se proporcionó documento"
    
    document = document_result.data
    
    # Obtener tipo de resumen
    summary_types = [
        "ejecutivo (1-2 párrafos)",
        "detallado (3-5 párrafos)",
        "puntos clave (lista)",
        "abstracto académico"
    ]
    
    summary_type_result = await context.elicit(
        message="¿Qué tipo de resumen necesitas?",
        response_type=summary_types
    )
    
    if not isinstance(summary_type_result, AcceptedElicitation):
        return "⚠️ Resumen básico generado"
    
    summary_type = summary_type_result.data
    
    # Configurar prompt según tipo de resumen
    summary_prompts = {
        "ejecutivo (1-2 párrafos)": "Crea un resumen ejecutivo conciso en 1-2 párrafos que capture lo más importante para tomadores de decisiones.",
        "detallado (3-5 párrafos)": "Genera un resumen detallado en 3-5 párrafos que cubra todos los puntos importantes manteniendo la estructura lógica.",
        "puntos clave (lista)": "Extrae los puntos clave más importantes y preséntalos como una lista numerada clara y organizada.",
        "abstracto académico": "Crea un abstracto académico estructurado con objetivo, metodología, resultados principales y conclusiones."
    }
    
    system_prompt = f"Eres un experto en síntesis de información. {summary_prompts[summary_type]} Mantén precisión y claridad."
    
    # Generar resumen usando AI sampling
    response = await context.sample(
        messages=f"Resume este documento:\n\n{document}",
        system_prompt=system_prompt,
        max_tokens=600,
        temperature=0.3
    )
    
    if isinstance(response, TextContent):
        summary = response.text
        
        return f"""
📄 Resumen de Documento Generado

📊 Tipo de resumen: {summary_type}
📏 Documento original: {len(document)} caracteres  
📏 Resumen: {len(summary)} caracteres
📉 Reducción: {((len(document) - len(summary)) / len(document) * 100):.1f}%

📋 Resumen:
{summary}

⏰ Resumen generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    return "❌ Error: No se pudo generar el resumen"

@mcp.tool
async def creative_writing_assistant(context: Context) -> str:
    """
    Asistente de escritura creativa que combina elicitación y sampling
    para generar contenido creativo personalizado.
    """
    # Paso 1: Obtener género/estilo
    genres = [
        "ficción científica",
        "fantasía",
        "misterio/thriller",
        "romance",
        "drama",
        "comedia",
        "terror"
    ]
    
    genre_result = await context.elicit(
        message="¿En qué género quieres escribir?",
        response_type=genres
    )
    
    if not isinstance(genre_result, AcceptedElicitation):
        return "🚫 Escritura cancelada: No se especificó género"
    
    genre = genre_result.data
    
    # Paso 2: Obtener elementos de la historia
    elements_result = await context.elicit(
        message="Describe elementos clave para la historia (personajes, situación, tema, etc.):",
        response_type=str
    )
    
    if not isinstance(elements_result, AcceptedElicitation):
        return f"⚠️ Escritura incompleta: Solo se configuró género '{genre}'"
    
    elements = elements_result.data
    
    # Paso 3: Longitud deseada
    lengths = [
        "cuento corto (500-1000 palabras)",
        "historia mediana (1000-2000 palabras)", 
        "solo el inicio (200-400 palabras)",
        "outline/esquema"
    ]
    
    length_result = await context.elicit(
        message="¿Qué longitud prefieres?",
        response_type=lengths
    )
    
    length = "cuento corto (500-1000 palabras)"
    if isinstance(length_result, AcceptedElicitation):
        length = length_result.data
    
    # Configurar prompt para escritura creativa
    system_prompt = f"""Eres un escritor creativo experto en {genre}. 
Crea contenido original, envolvente y bien estructurado.
Desarrolla personajes interesantes, diálogos naturales y descripciones vívidas.
Mantén consistencia en tono y estilo apropiados para el género."""
    
    user_message = f"""Escribe una {length} en género {genre} incorporando estos elementos:
{elements}

Asegúrate de crear una narrativa envolvente con:
- Personajes bien desarrollados
- Conflicto interesante  
- Desarrollo de trama coherente
- Final satisfactorio (si aplica)"""
    
    # Generar contenido creativo usando AI sampling
    response = await context.sample(
        messages=user_message,
        system_prompt=system_prompt,
        max_tokens=1800,
        temperature=0.8  # Mayor temperatura para creatividad
    )
    
    if isinstance(response, TextContent):
        creative_content = response.text
        
        return f"""
✍️ Contenido Creativo Generado

🎭 Género: {genre.title()}
📏 Longitud: {length}
🎯 Elementos incorporados: {elements[:100]}...

📚 Historia:
{creative_content}

💡 Sugerencias para continuar:
- Desarrolla más los personajes secundarios
- Explora subtemas interesantes
- Considera diferentes perspectivas narrativas
        """.strip()
    
    return "❌ Error: No se pudo generar el contenido creativo"

@mcp.tool
async def get_generated_content_list(context: Context) -> str:
    """
    Muestra lista de todo el contenido generado en esta sesión.
    """
    if not generated_content:
        return "📭 No hay contenido generado en esta sesión"
    
    content_list = ["📋 Contenido Generado en Esta Sesión:", "=" * 45]
    
    for content_id, data in generated_content.items():
        content_list.append(f"\n🆔 {content_id}")
        content_list.append(f"   Tipo: {data['type']}")
        content_list.append(f"   Tema: {data['topic']}")
        content_list.append(f"   Creado: {data['timestamp']}")
        content_list.append(f"   Longitud: {len(data['content'])} caracteres")
    
    return "\n".join(content_list)

if __name__ == "__main__":
    print("🚀 Iniciando Servidor MCP Multi-Turn con Sampling...")
    print("=" * 55)
    print("Funcionalidades disponibles:")
    print("1. 📝 ai_content_generator - Generador de contenido con AI")
    print("2. 🔍 intelligent_text_analyzer - Analizador de texto inteligente")
    print("3. 💻 ai_code_generator - Generador de código con AI")
    print("4. 🌍 smart_translator - Traductor inteligente")
    print("5. 📄 document_summarizer - Resumidor de documentos")
    print("6. ✍️ creative_writing_assistant - Asistente de escritura creativa")
    print("7. 📋 get_generated_content_list - Ver contenido generado")
    print("=" * 55)
    
    mcp.run()
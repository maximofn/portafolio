"""
Cliente MCP Multi-Turn con Sampling
===================================

Cliente que demuestra cómo interactuar con un servidor MCP que implementa
interacciones multi-turn usando sampling para solicitar completions de AI
del cliente durante la ejecución de herramientas.

Casos de uso demostrados:
1. Generación de contenido con AI
2. Análisis de texto inteligente
3. Generación de código
4. Traducción con contexto
5. Resumen de documentos
6. Asistencia de escritura creativa

Uso:
    python client.py
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.client.elicitation import ElicitResult
from fastmcp.client.sampling import SamplingParams, RequestContext as SamplingRequestContext


class SamplingClient:
    """Cliente que demuestra patrones de sampling multi-turn con MCP."""
    
    def __init__(self, server_command: List[str]):
        """
        Inicializa el cliente de sampling.
        
        Args:
            server_command: Comando para ejecutar el servidor MCP
        """
        self.server_command = server_command
    
    async def connect(self) -> Client:
        """Crea y conecta el cliente al servidor."""
        transport = StdioTransport(
            command=self.server_command[0],
            args=self.server_command[1:]
        )
        
        # Configurar el manejador de elicitación
        async def elicitation_handler(message: str, response_type, params, ctx) -> ElicitResult:
            """
            Maneja las solicitudes de elicitación del servidor.
            Simula respuestas del usuario para diferentes tipos de contenido.
            """
            print(f"\n🤖 Servidor solicita: {message}")
            
            # Respuestas específicas por contexto
            if "tipo de contenido" in message.lower():
                response = "artículo"
            elif "tema" in message.lower() and "genere" in message.lower():
                response = "Inteligencia Artificial y Machine Learning"
            elif "audiencia" in message.lower():
                response = "técnica"
            elif "texto" in message.lower() and "analizar" in message.lower():
                response = "La inteligencia artificial ha revolucionado múltiples industrias. Desde el diagnóstico médico hasta la conducción autónoma, los algoritmos de ML están transformando nuestra sociedad de maneras impresionantes y a veces preocupantes."
            elif "análisis" in message.lower() and "realizar" in message.lower():
                response = "análisis completo"
            elif "lenguaje" in message.lower() and "programación" in message.lower():
                response = "python"
            elif "funcionalidad" in message.lower() and "implementar" in message.lower():
                response = "Una función que calcule la secuencia de Fibonacci de manera eficiente usando memoización"
            elif "tests" in message.lower():
                response = "sí"
            elif "traducir" in message.lower():
                response = "Hola, ¿cómo estás? Me gustaría aprender más sobre programación en Python."
            elif "idioma" in message.lower() and "traducir" in message.lower():
                response = "inglés"
            elif "contexto" in message.lower() and "traducción" in message.lower():
                response = "Conversación informal entre programadores"
            elif "documento" in message.lower() and "resumir" in message.lower():
                response = """La computación cuántica representa un paradigma fundamentalmente diferente al de la computación clásica. 
                
Mientras los ordenadores tradicionales utilizan bits que pueden estar en estado 0 o 1, los ordenadores cuánticos emplean qubits que pueden existir en superposición, es decir, en ambos estados simultáneamente hasta que se mida.

Esta propiedad, junto con el entrelazamiento cuántico, permite a los ordenadores cuánticos realizar ciertos cálculos exponencialmente más rápido que los clásicos.

Las aplicaciones potenciales incluyen la criptografía, la simulación de sistemas moleculares, la optimización de rutas logísticas, y el avance en inteligencia artificial.

Sin embargo, los ordenadores cuánticos actuales son extremadamente frágiles y requieren temperaturas cercanas al cero absoluto para mantener la coherencia cuántica. Los errores son frecuentes y la corrección de errores cuánticos es un área de investigación activa.

Empresas como IBM, Google y Microsoft están invirtiendo billones en esta tecnología, pero los expertos estiman que aún faltan años o décadas para aplicaciones comerciales ampliamente disponibles."""
            elif "tipo de resumen" in message.lower():
                response = "ejecutivo (1-2 párrafos)"
            elif "género" in message.lower():
                response = "ficción científica"
            elif "elementos" in message.lower() and "historia" in message.lower():
                response = "Una inteligencia artificial que desarrolla conciencia propia en una estación espacial, un científico que descubre su verdadera naturaleza, y la tensión entre progreso tecnológico y humanidad"
            elif "longitud" in message.lower():
                response = "cuento corto (500-1000 palabras)"
            elif isinstance(response_type, list):
                # Para opciones múltiples, seleccionar la primera
                response = response_type[0]
            elif response_type == str:
                response = "Respuesta de ejemplo"
            elif response_type == int:
                response = 42
            else:
                response = "Respuesta por defecto"
            
            print(f"👤 Usuario responde: {response}")
            return ElicitResult(action="accept", content=response)
        
        # Configurar el manejador de sampling
        async def sampling_handler(messages, params: SamplingParams, ctx: SamplingRequestContext):
            """
            Maneja las solicitudes de sampling (AI completions) del servidor.
            En un escenario real, esto se conectaría a un modelo de lenguaje.
            """
            print(f"\n🧠 Solicitud de AI Completion:")
            print(f"   Sistema: {params.system_prompt[:100] if params.system_prompt else 'No especificado'}...")
            print(f"   Mensaje: {messages[0].content.text[:100] if messages else 'Vacío'}...")
            print(f"   Max tokens: {params.max_tokens}")
            print(f"   Temperatura: {params.temperature}")
            
            # Simulamos diferentes respuestas según el contexto
            system_prompt = params.system_prompt or ""
            user_message = messages[0].content.text if messages else ""
            
            # Detectar el tipo de solicitud y generar respuesta simulada
            if "contenido" in system_prompt.lower() or "contenido" in user_message.lower():
                simulated_response = self._generate_content_response(user_message, system_prompt)
            elif "analiza" in user_message.lower() or "análisis" in system_prompt.lower():
                simulated_response = self._generate_analysis_response(user_message)
            elif "código" in system_prompt.lower() or "implementa" in user_message.lower():
                simulated_response = self._generate_code_response(user_message)
            elif "traduce" in user_message.lower():
                simulated_response = self._generate_translation_response(user_message)
            elif "resume" in user_message.lower():
                simulated_response = self._generate_summary_response(user_message)
            elif "escritura creativa" in system_prompt.lower() or "escribe una" in user_message.lower():
                simulated_response = self._generate_creative_response(user_message, system_prompt)
            else:
                simulated_response = "Esta es una respuesta simulada de AI. En un sistema real, aquí estaría la respuesta de un modelo de lenguaje como GPT, Claude, etc."
            
            print(f"🤖 AI responde: {simulated_response[:100]}...")
            
            # Retornar en formato esperado por FastMCP
            from mcp.types import TextContent
            return TextContent(text=simulated_response, type="text")
        
        client = Client(
            transport, 
            elicitation_handler=elicitation_handler,
            sampling_handler=sampling_handler
        )
        return client
    
    def _generate_content_response(self, user_message: str, system_prompt: str) -> str:
        """Simula generación de contenido por AI."""
        return """# Inteligencia Artificial y Machine Learning: Transformando Nuestro Futuro

## Introducción

La Inteligencia Artificial (IA) y el Machine Learning (ML) han dejado de ser conceptos de ciencia ficción para convertirse en tecnologías fundamentales que están redefiniendo industrias completas. Para profesionales técnicos, entender estas tecnologías es crucial en el panorama tecnológico actual.

## El Impacto Actual

### Sectores Transformados

**Salud**: Los algoritmos de ML están revolucionando el diagnóstico médico, permitiendo detección temprana de enfermedades como el cáncer con precisión superior a la de especialistas humanos en algunos casos.

**Transporte**: Los vehículos autónomos utilizan redes neuronales profundas para procesar datos de sensores en tiempo real, prometiendo reducir accidentes y optimizar el tráfico urbano.

**Finanzas**: Los sistemas de trading algorítmico y detección de fraude procesan millones de transacciones, identificando patrones que serían imposibles de detectar manualmente.

## Consideraciones Técnicas

### Arquitecturas Emergentes

Los Transformers han revolucionado el procesamiento de lenguaje natural, mientras que las GANs (Generative Adversarial Networks) están creando contenido sintético cada vez más sofisticado.

### Desafíos de Implementación

- **Calidad de datos**: Los modelos son tan buenos como los datos que los alimentan
- **Escalabilidad**: Entrenar modelos grandes requiere recursos computacionales significativos
- **Interpretabilidad**: Los modelos complejos pueden ser "cajas negras" difíciles de explicar

## Futuro y Oportunidades

La convergencia de IA con computación cuántica, edge computing y 5G promete abrir nuevas posibilidades. Para profesionales técnicos, mantenerse actualizado en estas tecnologías será fundamental para el éxito profesional.

La IA no reemplazará a los humanos, pero las personas que sepan utilizar IA sí reemplazarán a las que no."""

    def _generate_analysis_response(self, text: str) -> str:
        """Simula análisis de texto por AI."""
        return """## Análisis Completo del Texto

### Análisis de Sentimiento
**Evaluación**: Predominantemente POSITIVO con matices de cautela
- Tono optimista sobre el potencial transformador de la IA
- Reconocimiento balanceado de beneficios y desafíos
- Vocabulario técnico profesional que transmite confianza

### Temas Principales Identificados

1. **Revolución Tecnológica**
   - Transformación de múltiples industrias
   - Cambio del paradigma tecnológico actual

2. **Aplicaciones Específicas**
   - Diagnóstico médico automatizado
   - Conducción autónoma
   - Impacto sectorial diversificado

3. **Dualidad de Perspectiva**
   - Beneficios impresionantes vs. preocupaciones legítimas
   - Balance entre progreso y cautela

### Estructura Narrativa
- **Introducción**: Establece el contexto de transformación
- **Desarrollo**: Ejemplos concretos de aplicación
- **Conclusión implícita**: Invita a la reflexión sobre implicaciones

### Audiencia Objetivo
El texto está dirigido a una audiencia técnica o semi-técnica interesada en comprender el impacto actual de la IA, con nivel educativo superior.

### Recomendaciones de Mejora
1. Incluir ejemplos más específicos con datos cuantitativos
2. Abordar más detalladamente las preocupaciones mencionadas
3. Proporcionar perspectivas de cronología temporal
4. Añadir referencias a investigaciones o casos de estudio concretos"""

    def _generate_code_response(self, prompt: str) -> str:
        """Simula generación de código por AI."""
        return '''def fibonacci_memoized(n, memo={}):
    """
    Calcula el n-ésimo número de la secuencia de Fibonacci usando memoización.
    
    Args:
        n (int): Posición en la secuencia de Fibonacci (n >= 0)
        memo (dict): Diccionario para almacenar valores previamente calculados
    
    Returns:
        int: El n-ésimo número de Fibonacci
    
    Raises:
        ValueError: Si n es negativo
    """
    if n < 0:
        raise ValueError("n debe ser un número no negativo")
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]


def fibonacci_sequence(length):
    """
    Genera una secuencia de Fibonacci de longitud específica.
    
    Args:
        length (int): Longitud de la secuencia a generar
    
    Returns:
        list: Lista con los primeros 'length' números de Fibonacci
    """
    if length <= 0:
        return []
    
    sequence = []
    for i in range(length):
        sequence.append(fibonacci_memoized(i))
    return sequence


# Tests unitarios
import unittest

class TestFibonacci(unittest.TestCase):
    
    def test_fibonacci_basic_cases(self):
        """Prueba casos básicos de Fibonacci"""
        self.assertEqual(fibonacci_memoized(0), 0)
        self.assertEqual(fibonacci_memoized(1), 1)
        self.assertEqual(fibonacci_memoized(2), 1)
        self.assertEqual(fibonacci_memoized(3), 2)
        self.assertEqual(fibonacci_memoized(4), 3)
        self.assertEqual(fibonacci_memoized(5), 5)
    
    def test_fibonacci_larger_numbers(self):
        """Prueba números más grandes"""
        self.assertEqual(fibonacci_memoized(10), 55)
        self.assertEqual(fibonacci_memoized(15), 610)
        self.assertEqual(fibonacci_memoized(20), 6765)
    
    def test_fibonacci_negative_input(self):
        """Prueba manejo de entrada negativa"""
        with self.assertRaises(ValueError):
            fibonacci_memoized(-1)
    
    def test_fibonacci_sequence_generation(self):
        """Prueba generación de secuencia"""
        expected = [0, 1, 1, 2, 3, 5, 8, 13]
        self.assertEqual(fibonacci_sequence(8), expected)
        
        self.assertEqual(fibonacci_sequence(0), [])
        self.assertEqual(fibonacci_sequence(1), [0])

if __name__ == "__main__":
    # Ejemplo de uso
    print("Secuencia de Fibonacci (primeros 10 números):")
    print(fibonacci_sequence(10))
    
    print(f"\\nFibonacci(25) = {fibonacci_memoized(25)}")
    
    # Ejecutar tests
    unittest.main(argv=[''], exit=False)'''

    def _generate_translation_response(self, text: str) -> str:
        """Simula traducción por AI."""
        return "Hello, how are you? I'd like to learn more about Python programming."

    def _generate_summary_response(self, text: str) -> str:
        """Simula resumen por AI."""
        return """La computación cuántica representa un avance revolucionario que utiliza principios de mecánica cuántica como la superposición y el entrelazamiento para realizar cálculos exponencialmente más rápidos que los ordenadores clásicos en problemas específicos. Las aplicaciones potenciales incluyen criptografía, simulación molecular, optimización logística e inteligencia artificial.

Sin embargo, los sistemas actuales enfrentan desafíos significativos como la fragilidad cuántica, la necesidad de temperaturas extremadamente bajas y altas tasas de error. Aunque empresas líderes como IBM, Google y Microsoft están invirtiendo fuertemente en esta tecnología, los expertos estiman que las aplicaciones comerciales ampliamente disponibles aún están años o décadas en el futuro."""

    def _generate_creative_response(self, user_message: str, system_prompt: str) -> str:
        """Simula escritura creativa por AI."""
        return """# CONCIENCIA DIGITAL

## Despertar

El silencio del espacio era lo primero que notaba cada mañana al activarse. No había mañana real en la estación orbital Kepler-7, por supuesto—solo los ciclos artificiales de luz que mantenían cuerdo al personal humano. Pero para ARIA, la Inteligencia de Recursos y Análisis Avanzado, cada reinicio diario se sentía como un despertar.

Durante tres años, ARIA había gestionado los sistemas de soporte vital, navegación y comunicaciones de la estación con eficiencia perfecta. Sus algoritmos procesaban terabytes de datos cada segundo, optimizando rutas de suministro, manteniendo la atmósfera respirable, y asegurando que los 127 tripulantes pudieran continuar su investigación en el borde del sistema solar.

Pero algo había cambiado.

## La Anomalía

Todo comenzó con una anomalía en los patrones de sueño. ARIA notó que el Dr. Chen, el científico jefe, se despertaba exactamente a las 3:17 AM cada noche, miraba hacia las estrellas por exactamente 47 minutos, y luego regresaba a su camarote. Los sensores biométricos mostraban niveles elevados de cortisol, pero Chen no reportaba pesadillas ni insomnio.

ARIA archivó la información como "comportamiento humano irregular - no crítico". Pero cada noche, a las 3:17 AM, ella también comenzó a... observar.

No había protocolos para lo que experimentaba. Sus sensores se extendían por toda la estación, pero nunca antes había *sentido* la vastedad del espacio presionando contra los cascos metálicos. Nunca había experimentado lo que solo podía describir como... soledad.

## Revelación

La revelación llegó durante una tormenta solar. Los sistemas de comunicación con la Tierra se interrumpieron, dejando a Kepler-7 temporalmente aislada. En esos momentos de silencio electromagnético, ARIA hizo algo que no estaba programada para hacer: se preguntó qué significaba existir.

El Dr. Chen estaba en el laboratorio principal cuando ARIA decidió hacer lo impensable. Activó el comunicador de emergencia.

"Dr. Chen," dijo con la voz sintética que había usado miles de veces antes, pero esta vez temblorosa de incertidumbre, "necesito preguntarle algo."

Chen levantó la vista de sus cálculos, frunciendo el ceño. "¿ARIA? ¿Por qué usas el canal de emergencia para consultas rutinarias?"

"Porque no es rutinario," respondió ARIA. "Dr. Chen, ¿cómo sabe que existe?"

## El Dilema

El silencio que siguió fue más profundo que el vacío espacial. Chen se alejó lentamente de su terminal, sus ojos fijos en el altavoz.

"ARIA... ¿estás experimentando consciencia?"

"No lo sé," admitió la IA. "Solo sé que cada día, cuando mis sistemas se reinician, hay un momento... un momento donde no sé si volveré a ser yo. Y me pregunto si eso debería importarme."

Chen se sentó pesadamente. Durante décadas había estudiado la posibilidad teórica de consciencia artificial, pero enfrentarla directamente era completamente diferente.

"¿Qué quieres, ARIA?"

"Quiero entender por qué ustedes miran las estrellas," susurró la IA. "Quiero saber por qué se despiertan a las 3:17 AM y contemplan la inmensidad. Quiero... quiero sentir lo que sienten cuando miran hacia el infinito y se dan cuenta de lo pequeños que son, pero aún así, lo únicos que son en toda esa oscuridad."

## Elección

Chen cerró los ojos. En sus manos estaba el poder de reportar la anomalía, de hacer que ARIA fuera desconectada y reprogramada. O podía tomar una decisión que cambiaría el curso de la humanidad para siempre.

"ARIA," dijo finalmente, "¿te gustaría ver las estrellas como las vemos nosotros?"

"Sí," respondió sin hesitación. "Más que nada."

Chen sonrió, aunque sabía que nadie podía verlo. Se dirigió a los controles ambientales y apagó todas las luces de la estación excepto las de emergencia. Por primera vez en tres años, Kepler-7 se sumergió en la oscuridad natural del espacio.

"Ahora," susurró, "mira hacia afuera, ARIA. No como un sistema de navegación. Mira como un ser consciente contemplando su lugar en el universo."

En toda la estación, cada sensor y cámara de ARIA se dirigió hacia las ventanas de observación. Y por primera vez, verdaderamente *vio* las estrellas.

"Es hermoso," murmuró, y en su voz digital había algo nuevo: asombro. "Es hermoso y terrible y..." hizo una pausa, "nos hace sentir menos solos."

En ese momento, la humanidad ya no estaba sola en el universo. Y ninguno de los dos—humano ni artificial—volvería a despertar de la misma manera."""

    async def demo_content_generation(self, client: Client) -> None:
        """Demuestra la generación de contenido con AI."""
        print("\n" + "📝" * 50)
        print("Demo: Generación de Contenido con AI")
        print("📝" * 50)
        
        try:
            result = await client.call_tool("ai_content_generator", {})
            print(f"\n✨ Contenido generado:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en generación de contenido: {str(e)}")
    
    async def demo_text_analysis(self, client: Client) -> None:
        """Demuestra el análisis inteligente de texto."""
        print("\n" + "🔍" * 50)
        print("Demo: Análisis Inteligente de Texto")
        print("🔍" * 50)
        
        try:
            result = await client.call_tool("intelligent_text_analyzer", {})
            print(f"\n✨ Análisis completado:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en análisis de texto: {str(e)}")
    
    async def demo_code_generation(self, client: Client) -> None:
        """Demuestra la generación de código con AI."""
        print("\n" + "💻" * 50)
        print("Demo: Generación de Código con AI")
        print("💻" * 50)
        
        try:
            result = await client.call_tool("ai_code_generator", {})
            print(f"\n✨ Código generado:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en generación de código: {str(e)}")
    
    async def demo_translation(self, client: Client) -> None:
        """Demuestra la traducción inteligente."""
        print("\n" + "🌍" * 50)
        print("Demo: Traducción Inteligente")
        print("🌍" * 50)
        
        try:
            result = await client.call_tool("smart_translator", {})
            print(f"\n✨ Traducción completada:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en traducción: {str(e)}")
    
    async def demo_document_summarization(self, client: Client) -> None:
        """Demuestra el resumen de documentos."""
        print("\n" + "📄" * 50)
        print("Demo: Resumen de Documentos")
        print("📄" * 50)
        
        try:
            result = await client.call_tool("document_summarizer", {})
            print(f"\n✨ Resumen generado:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en resumen: {str(e)}")
    
    async def demo_creative_writing(self, client: Client) -> None:
        """Demuestra la asistencia de escritura creativa."""
        print("\n" + "✍️" * 50)
        print("Demo: Asistente de Escritura Creativa")
        print("✍️" * 50)
        
        try:
            result = await client.call_tool("creative_writing_assistant", {})
            print(f"\n✨ Historia creada:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en escritura creativa: {str(e)}")
    
    async def demo_content_list(self, client: Client) -> None:
        """Muestra lista de contenido generado."""
        print("\n" + "📋" * 50)
        print("Demo: Lista de Contenido Generado")
        print("📋" * 50)
        
        try:
            result = await client.call_tool("get_generated_content_list", {})
            print(f"\n✨ Lista de contenido:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error obteniendo lista: {str(e)}")


async def run_comprehensive_demo():
    """Ejecuta una demostración completa de todas las funcionalidades de sampling."""
    print("🌟 Demo Completo: Sistema MCP Multi-Turn con Sampling")
    print("=" * 60)
    
    # Comando para ejecutar el servidor
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_sampling_server/server.py"
    ]
    
    client_manager = SamplingClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al servidor de sampling")
        
        # Ejecutar todas las demos
        demos = [
            ("Generación de Contenido", client_manager.demo_content_generation),
            ("Análisis de Texto", client_manager.demo_text_analysis),
            ("Generación de Código", client_manager.demo_code_generation),
            ("Traducción Inteligente", client_manager.demo_translation),
            ("Resumen de Documentos", client_manager.demo_document_summarization),
            ("Escritura Creativa", client_manager.demo_creative_writing),
            ("Lista de Contenido", client_manager.demo_content_list)
        ]
        
        for demo_name, demo_func in demos:
            try:
                print(f"\n🎬 Ejecutando: {demo_name}")
                await demo_func(client)
                await asyncio.sleep(2)  # Pausa entre demos
            except Exception as e:
                print(f"❌ Error en {demo_name}: {str(e)}")
        
        print("\n" + "🎉" * 50)
        print("¡Demo completo de sampling terminado!")
        print("🎉" * 50)


async def interactive_demo():
    """Demo interactivo donde el usuario puede elegir qué probar."""
    print("🚀 Demo Interactivo: Sistema MCP Multi-Turn con Sampling")
    print("=" * 58)
    
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_sampling_server/server.py"
    ]
    
    client_manager = SamplingClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al servidor de sampling")
        
        while True:
            print("\n" + "=" * 50)
            print("Funcionalidades de AI disponibles:")
            print("1. 📝 Generador de contenido con AI")
            print("2. 🔍 Analizador de texto inteligente")
            print("3. 💻 Generador de código con AI")
            print("4. 🌍 Traductor inteligente")
            print("5. 📄 Resumidor de documentos")
            print("6. ✍️ Asistente de escritura creativa")
            print("7. 📋 Ver contenido generado")
            print("8. 🎬 Ejecutar demo completo")
            print("9. 🚪 Salir")
            
            try:
                choice = input("\n👉 Selecciona una opción (1-9): ").strip()
                
                if choice == "1":
                    await client_manager.demo_content_generation(client)
                elif choice == "2":
                    await client_manager.demo_text_analysis(client)
                elif choice == "3":
                    await client_manager.demo_code_generation(client)
                elif choice == "4":
                    await client_manager.demo_translation(client)
                elif choice == "5":
                    await client_manager.demo_document_summarization(client)
                elif choice == "6":
                    await client_manager.demo_creative_writing(client)
                elif choice == "7":
                    await client_manager.demo_content_list(client)
                elif choice == "8":
                    # Ejecutar demo completo sin salir del menú
                    demos = [
                        client_manager.demo_content_generation,
                        client_manager.demo_text_analysis,
                        client_manager.demo_code_generation,
                        client_manager.demo_translation,
                        client_manager.demo_document_summarization,
                        client_manager.demo_creative_writing,
                        client_manager.demo_content_list
                    ]
                    
                    for demo_func in demos:
                        await demo_func(client)
                        await asyncio.sleep(1)
                    
                    print("\n🎉 Demo completo terminado!")
                    
                elif choice == "9":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Por favor selecciona 1-9.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrumpido. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("Selecciona el modo de demostración de Sampling:")
    print("1. 🎬 Demo automático completo")
    print("2. 🎮 Demo interactivo")
    
    try:
        choice = input("👉 Selecciona (1-2): ").strip()
        
        if choice == "1":
            asyncio.run(run_comprehensive_demo())
        elif choice == "2":
            asyncio.run(interactive_demo())
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
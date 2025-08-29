"""
Cliente MCP Multi-Turn Combinado (Elicitación + Sampling)
=========================================================

Cliente que demuestra el uso combinado de elicitación y sampling
en un agente de reserva de viajes inteligente.

Demuestra:
1. Elicitación para decisiones críticas del usuario
2. Sampling para generar recomendaciones personalizadas con AI
3. Flujo completo de reserva con confirmaciones
4. Manejo de respuestas complejas (aceptar/rechazar/modificar)
5. Integración fluida entre inputs humanos y AI completions

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


class CombinedTravelClient:
    """Cliente que demuestra patrones combinados de elicitación + sampling."""
    
    def __init__(self, server_command: List[str]):
        """
        Inicializa el cliente combinado.
        
        Args:
            server_command: Comando para ejecutar el servidor MCP
        """
        self.server_command = server_command
        self.user_scenario = None  # None = modo interactivo real, o especificar escenario para simular
    
    def set_user_scenario(self, scenario: str):
        """
        Configura el escenario de usuario a simular.
        
        Args:
            scenario: 'business', 'family', 'budget', 'luxury', 'interactive' o None para modo interactivo real
        """
        self.user_scenario = scenario
    
    def set_interactive_mode(self):
        """Habilita el modo interactivo real donde el usuario debe introducir respuestas."""
        self.user_scenario = None
    
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
            Si user_scenario es None, pide input real al usuario.
            Si tiene un escenario configurado, simula respuestas automáticas.
            """
            print(f"\n🤖 Agente solicita: {message}")
            
            # Si no hay escenario configurado, pedir input real del usuario
            if self.user_scenario is None or self.user_scenario == "interactive":
                # Mostrar opciones si response_type es una lista
                if isinstance(response_type, list):
                    print("Opciones disponibles:")
                    for i, option in enumerate(response_type, 1):
                        print(f"  {i}. {option}")
                    while True:
                        try:
                            choice = input(f"👤 Tu respuesta (1-{len(response_type)}): ").strip()
                            choice_idx = int(choice) - 1
                            if 0 <= choice_idx < len(response_type):
                                response = response_type[choice_idx]
                                break
                            else:
                                print(f"❌ Por favor selecciona un número del 1 al {len(response_type)}")
                        except ValueError:
                            print("❌ Por favor ingresa un número válido")
                else:
                    # Para otros tipos, pedir input directo
                    response_hint = ""
                    if response_type == int:
                        response_hint = " (número entero)"
                    elif response_type == str:
                        response_hint = " (texto)"
                    
                    response = input(f"👤 Tu respuesta{response_hint}: ").strip()
                    
                    # Convertir al tipo correcto si es necesario
                    if response_type == int:
                        try:
                            response = int(response)
                        except ValueError:
                            print("⚠️ Usando valor por defecto: 1")
                            response = 1
            else:
                # Modo simulación automática
                if "RESUMEN DE TU VIAJE" in message:
                    print(f"🔍 DEBUG: Detectada solicitud de confirmación - Escenario: {self.user_scenario}")
                
                # Respuestas según escenario de usuario
                if self.user_scenario == "business":
                    response = self._get_business_response(message, response_type)
                elif self.user_scenario == "family":
                    response = self._get_family_response(message, response_type)
                elif self.user_scenario == "budget":
                    response = self._get_budget_response(message, response_type)
                elif self.user_scenario == "luxury":
                    response = self._get_luxury_response(message, response_type)
                else:
                    response = self._get_default_response(message, response_type)
                
                print(f"👤 Usuario ({self.user_scenario}) responde: {response}")
            
            # FastMCP espera un objeto JSON (dict), no string directo
            if isinstance(response, str):
                return ElicitResult(action="accept", content={"value": response})
            elif isinstance(response, (int, float)):
                return ElicitResult(action="accept", content={"value": response})
            else:
                return ElicitResult(action="accept", content=response)
        
        # Configurar el manejador de sampling
        async def sampling_handler(messages, params: SamplingParams, ctx: SamplingRequestContext):
            """
            Maneja las solicitudes de sampling (AI completions).
            Simula respuestas de diferentes modelos de AI según el contexto.
            """
            print(f"\n🧠 Solicitud AI para {self._detect_ai_task(messages, params)}:")
            print(f"   📝 Sistema: {params.system_prompt[:80]}..." if params.system_prompt else "   📝 Sistema: No especificado")
            print(f"   💬 Usuario: {messages[0].content.text[:80]}..." if messages else "   💬 Usuario: Vacío")
            
            # Generar respuesta simulada según el tipo de tarea
            task_type = self._detect_ai_task(messages, params)
            simulated_response = self._generate_ai_response(task_type, messages, params)
            
            print(f"🤖 AI responde: {simulated_response[:100]}...")
            
            from mcp.types import TextContent
            return TextContent(text=simulated_response, type="text")
        
        client = Client(
            transport, 
            elicitation_handler=elicitation_handler,
            sampling_handler=sampling_handler
        )
        return client
    
    def _detect_ai_task(self, messages, params: SamplingParams) -> str:
        """Detecta el tipo de tarea AI basado en el contexto."""
        if not messages:
            return "unknown"
        
        message_text = messages[0].content.text.lower()
        system_prompt = (params.system_prompt or "").lower()
        
        if "destino" in message_text and "analiza" in message_text:
            return "destination_analysis"
        elif "itinerario" in message_text or "itinerario" in system_prompt:
            return "itinerary_generation"
        elif "confirmación" in message_text or "confirmación" in system_prompt:
            return "confirmation_message"
        else:
            return "general_travel_ai"
    
    def _generate_ai_response(self, task_type: str, messages, params: SamplingParams) -> str:
        """Genera respuesta AI simulada según el tipo de tarea."""
        responses = {
            "destination_analysis": self._generate_destination_analysis(),
            "itinerary_generation": self._generate_itinerary(),
            "confirmation_message": self._generate_confirmation(),
            "general_travel_ai": self._generate_general_travel_response()
        }
        
        return responses.get(task_type, "Respuesta AI simulada para tarea no reconocida.")
    
    def _generate_destination_analysis(self) -> str:
        """Simula análisis de destino por AI."""
        return """{"name": "Roma, Italia", "base_price": 750, "highlights": ["Coliseo", "Vaticano", "Fontana di Trevi", "Gastronomía auténtica"], "best_season": "Primavera/Otoño (Abril-Junio, Septiembre-Octubre)", "travel_time": "8-10 horas desde América del Norte"}"""
    
    def _generate_itinerary(self) -> str:
        """Simula generación de itinerario personalizado."""
        if self.user_scenario == "business":
            return """🏢 ITINERARIO EJECUTIVO - ROMA (4 días)

DÍA 1: Llegada y orientación
- Mañana: Check-in hotel business (zona EUR)
- Tarde: Centro histórico - Pantheon, Piazza Navona
- Noche: Cena ejecutiva en Il Pagliaccio (Michelin ⭐)

DÍA 2: Roma Clásica Eficiente
- 08:00: Tour privado Coliseo y Foro Romano (2h)
- 11:00: Break reunión virtual (WiFi hotel)
- 14:00: Almuerzo rápido Checchino dal 1887
- 16:00: Museos Vaticanos + Capilla Sixtina (entrada prioritaria)

DÍA 3: Networking y Cultura
- Mañana: Disponible para meetings/calls
- 14:00: Villa Borghese y Galleria
- 18:00: Aperitivo networking - Hotel de Russie
- 20:30: Cena en Piperno (especialidad carciofi)

DÍA 4: Último día
- 10:00: Fontana di Trevi y shopping Via del Corso
- 13:00: Almuerzo ligero antes del vuelo
- Transfer aeropuerto

💰 COSTOS ADICIONALES ESTIMADOS:
- Comidas: $400-600 USD
- Tours privados: $300 USD  
- Transport local: $100 USD
- Compras/souvenirs: $200 USD

✈️ CONSEJOS EJECUTIVOS:
- Hotel con centro business 24/7
- SIM card local para datos ilimitados
- Apps: Citymapper, Google Translate offline
- Vestuario: Business casual, zapatos cómodos para caminar"""
        
        elif self.user_scenario == "family":
            return """👨‍👩‍👧‍👦 ITINERARIO FAMILIAR - ROMA (5 días)

DÍA 1: Llegada suave
- Mañana: Llegada, check-in apartamento familiar
- Tarde: Exploración barrio Trastevere (kid-friendly)
- Noche: Pizza en Da Enzo al 29 (auténtica, ambiente casual)

DÍA 2: Roma Antigua para niños
- 09:00: Coliseo con audio-guía para niños
- 11:30: Foro Romano - juego "busca el tesoro histórico"
- 14:00: Pausa pranzo en parque Villa Celimontana
- 16:00: Gelato en Giolitti (desde 1900!)

DÍA 3: Vaticano Familiar
- 08:00: Desayuno tranquilo
- 10:00: Museos Vaticanos (tour familia 2.5h max)
- 14:00: Picnic en Jardines Vaticanos
- 16:00: Subida a Cúpula San Pedro (si niños >8 años)
- 18:00: Paseo Castel Sant'Angelo

DÍA 4: Diversión y Descubrimiento
- 09:00: Villa Borghese - alquiler bicicletas familiares
- 11:00: Zoo de Roma (Bioparco)
- 15:00: Fontana di Trevi - lanzar monedas (tradición!)
- 17:00: Escalinata Española y shopping souvenirs

DÍA 5: Último día relajado
- 10:00: Mercado Campo de' Fiori con niños
- 12:00: Última pasta en Roma - Checchino dal 1887
- 14:00: Preparar maletas, descanso
- 16:00: Transfer al aeropuerto

💰 COSTOS FAMILIA (4 personas):
- Alimentos: $600-800 USD (incluye mucho gelato!)
- Actividades: $400 USD
- Transporte: $150 USD
- Souvenirs: $300 USD

👨‍👩‍👧‍👦 CONSEJOS FAMILIARES:
- Apartamento > hotel (cocina, lavandería)
- Llevar snacks y agua siempre
- Apps: Rome for Kids, iDiscover Rome
- Horarios: salidas temprano, siesta tarde"""
        
        else:  # Default business-focused
            return """🎯 ITINERARIO PERSONALIZADO - DESTINO PRINCIPAL

Basado en tus preferencias, he creado un plan equilibrado que combina los imperdibles con experiencias auténticas locales.

📅 PLANIFICACIÓN POR DÍAS:
DÍA 1: Orientación y primeras impresiones
DÍA 2-3: Atracciones principales y cultura local  
DÍA 4: Experiencias únicas y gastronomía
DÍA 5: Compras y preparación de regreso

🍽️ RECOMENDACIONES GASTRONÓMICAS:
- Restaurantes locales auténticos
- Especialidades regionales imperdibles
- Opciones para diferentes presupuestos

💡 CONSEJOS PRÁCTICOS:
- Mejor época para visitar
- Qué llevar en la maleta
- Apps útiles para el destino
- Precauciones de seguridad

Los costos adicionales estimados varían según tu presupuesto seleccionado."""
    
    def _generate_confirmation(self) -> str:
        """Simula mensaje de confirmación personalizado."""
        return """🎉 ¡Felicitaciones! Tu aventura está oficialmente confirmada.

Has tomado una excelente decisión eligiendo este destino. Nuestro equipo está emocionado de ser parte de tu próximo viaje y ya estamos trabajando para asegurar que cada detalle sea perfecto.

✅ QUÉ VIENE AHORA:
- Recibirás documentación completa por email en 24h
- Te contactaremos 48h antes del viaje con detalles finales
- Tienes soporte 24/7 durante todo tu viaje
- Acceso a nuestra app móvil con itinerario interactivo

🎁 BONOS INCLUIDOS:
- Guía digital personalizada del destino
- Lista de frases útiles en el idioma local
- Mapa offline con puntos de interés marcados
- Contactos de emergencia locales

Tu inversión en experiencias vale cada centavo. ¡Prepárate para crear recuerdos inolvidables!"""
    
    def _generate_general_travel_response(self) -> str:
        """Respuesta AI general para viajes."""
        return "Basado en las preferencias indicadas, puedo ofrecerte recomendaciones personalizadas que optimicen tu experiencia de viaje, considerando factores como presupuesto, tiempo disponible, y tipo de actividades preferidas."
    
    def _get_business_response(self, message: str, response_type) -> str:
        """Respuestas para viajero de negocios."""
        # Priorizar confirmación antes que otras respuestas
        if "confirmas" in message.lower() or "RESUMEN DE TU VIAJE" in message:
            return "confirmar"
        elif "tipo de viaje" in message.lower():
            return "negocios"
        elif "destino" in message.lower() and "RESUMEN" not in message:
            return "Nueva York"
        elif "cuándo" in message.lower():
            return "2024-03-15"
        elif "cuántas personas" in message.lower():
            return 1
        elif "presupuesto" in message.lower():
            return "lujo"
        elif isinstance(response_type, list):
            return response_type[0]
        else:
            return "Sí"
    
    def _get_family_response(self, message: str, response_type) -> str:
        """Respuestas para viaje familiar."""
        # Priorizar confirmación antes que otras respuestas
        if "confirmas" in message.lower() or "RESUMEN DE TU VIAJE" in message:
            return "confirmar"
        elif "tipo de viaje" in message.lower():
            return "familiar"
        elif "destino" in message.lower() and "RESUMEN" not in message:
            return "París"
        elif "cuándo" in message.lower():
            return "vacaciones de verano"
        elif "cuántas personas" in message.lower():
            return 4
        elif "presupuesto" in message.lower():
            return "medio"
        elif isinstance(response_type, list):
            return response_type[0]
        else:
            return "Sí"
    
    def _get_budget_response(self, message: str, response_type) -> str:
        """Respuestas para viajero con presupuesto ajustado."""
        # Priorizar confirmación antes que otras respuestas
        if "confirmas" in message.lower() or "RESUMEN DE TU VIAJE" in message:
            return "ver opciones más baratas"
        elif "aceptas" in message.lower():
            return "aceptar"
        elif "tipo de viaje" in message.lower():
            return "placer"
        elif "destino" in message.lower() and "RESUMEN" not in message:
            return "Bali"
        elif "cuándo" in message.lower():
            return "temporada baja"
        elif "cuántas personas" in message.lower():
            return 2
        elif "presupuesto" in message.lower():
            return "económico"
        elif isinstance(response_type, list):
            return response_type[0]
        else:
            return "Sí"
    
    def _get_luxury_response(self, message: str, response_type) -> str:
        """Respuestas para viajero de lujo."""
        # Priorizar confirmación antes que otras respuestas
        if "confirmas" in message.lower() or "RESUMEN DE TU VIAJE" in message:
            return "confirmar"
        elif "tipo de viaje" in message.lower():
            return "placer"
        elif "destino" in message.lower() and "RESUMEN" not in message:
            return "Tokio"
        elif "cuándo" in message.lower():
            return "primavera 2024"
        elif "cuántas personas" in message.lower():
            return 2
        elif "presupuesto" in message.lower():
            return "lujo"
        elif isinstance(response_type, list):
            return response_type[0]
        else:
            return "Excelente"
    
    def _get_default_response(self, message: str, response_type) -> str:
        """Respuestas por defecto."""
        if isinstance(response_type, list):
            return response_type[0]
        elif response_type == int:
            return 2
        else:
            return "Sí"
    
    async def demo_business_traveler(self, client: Client) -> None:
        """Demuestra reserva para viajero de negocios."""
        print("\n" + "💼" * 50)
        print("Demo: Viajero de Negocios - Nueva York")
        print("💼" * 50)
        
        self.set_user_scenario("business")
        
        try:
            result = await client.call_tool("intelligent_travel_booking_agent", {})
            print(f"\n✨ Resultado de reserva ejecutiva:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva de negocios: {str(e)}")
    
    async def demo_family_traveler(self, client: Client) -> None:
        """Demuestra reserva para familia."""
        print("\n" + "👨‍👩‍👧‍👦" * 50)
        print("Demo: Viaje Familiar - París")
        print("👨‍👩‍👧‍👦" * 50)
        
        self.set_user_scenario("family")
        
        try:
            result = await client.call_tool("intelligent_travel_booking_agent", {})
            print(f"\n✨ Resultado de reserva familiar:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva familiar: {str(e)}")
    
    async def demo_budget_traveler(self, client: Client) -> None:
        """Demuestra reserva con presupuesto ajustado."""
        print("\n" + "💰" * 50)
        print("Demo: Viajero Económico - Bali")
        print("💰" * 50)
        
        self.set_user_scenario("budget")
        
        try:
            result = await client.call_tool("intelligent_travel_booking_agent", {})
            print(f"\n✨ Resultado de reserva económica:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva económica: {str(e)}")
    
    async def demo_luxury_traveler(self, client: Client) -> None:
        """Demuestra reserva de lujo."""
        print("\n" + "✨" * 50)
        print("Demo: Viajero de Lujo - Tokio")
        print("✨" * 50)
        
        self.set_user_scenario("luxury")
        
        try:
            result = await client.call_tool("intelligent_travel_booking_agent", {})
            print(f"\n✨ Resultado de reserva de lujo:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva de lujo: {str(e)}")
    
    async def demo_booking_management(self, client: Client) -> None:
        """Demuestra gestión de reservas."""
        print("\n" + "📋" * 50)
        print("Demo: Gestión de Reservas")
        print("📋" * 50)
        
        try:
            # Listar todas las reservas
            result = await client.call_tool("list_all_bookings", {})
            print(f"\n📋 Lista de reservas:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en gestión de reservas: {str(e)}")
    
    async def demo_interactive_booking(self, client: Client) -> None:
        """Demostración interactiva real - el usuario introduce sus propias respuestas."""
        print("\n" + "🎮" * 50)
        print("Demo: Reserva Interactiva Real")
        print("🎮" * 50)
        print("\n🎯 En este modo TÚ introduces las respuestas")
        print("💡 El agente te preguntará y esperará tu input real")
        
        self.set_interactive_mode()  # Activar modo interactivo
        
        try:
            result = await client.call_tool("intelligent_travel_booking_agent", {})
            print(f"\n✨ Resultado de tu reserva interactiva:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva interactiva: {str(e)}")


async def run_comprehensive_demo():
    """Ejecuta demo completo de todos los tipos de viajero."""
    print("🌟 Demo Completo: Agente de Viajes Inteligente (Elicitación + AI)")
    print("=" * 70)
    
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_combined_server/server.py"
    ]
    
    client_manager = CombinedTravelClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al agente de viajes inteligente")
        
        # Ejecutar demos de diferentes tipos de viajero
        demos = [
            ("Viajero de Negocios", client_manager.demo_business_traveler),
            ("Familia Vacacionando", client_manager.demo_family_traveler),
            ("Viajero Económico", client_manager.demo_budget_traveler),
            ("Viajero de Lujo", client_manager.demo_luxury_traveler),
            ("Gestión de Reservas", client_manager.demo_booking_management)
        ]
        
        for demo_name, demo_func in demos:
            try:
                print(f"\n🎬 Ejecutando: {demo_name}")
                await demo_func(client)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"❌ Error en {demo_name}: {str(e)}")
        
        print("\n" + "🎉" * 50)
        print("¡Demo completo del agente inteligente terminado!")
        print("Casos demostrados: Elicitación + AI Sampling")
        print("🎉" * 50)


async def interactive_demo():
    """Demo interactivo donde el usuario elige el tipo de viajero."""
    print("🚀 Demo Interactivo: Agente de Viajes Inteligente")
    print("=" * 55)
    
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_combined_server/server.py"
    ]
    
    client_manager = CombinedTravelClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al agente de viajes inteligente")
        
        while True:
            print("\n" + "=" * 50)
            print("Opciones disponibles:")
            print("1. 🎮 RESERVA INTERACTIVA REAL (tú introduces respuestas)")
            print("2. 💼 Demo automático: Viajero de negocios (Nueva York)")
            print("3. 👨‍👩‍👧‍👦 Demo automático: Familia vacacionando (París)")
            print("4. 💰 Demo automático: Viajero económico (Bali)")
            print("5. ✨ Demo automático: Viajero de lujo (Tokio)")
            print("6. 📋 Gestionar reservas existentes")
            print("7. 🎬 Ejecutar demo completo automático")
            print("8. 🚪 Salir")
            
            try:
                choice = input("\n👉 Selecciona una opción (1-8): ").strip()
                
                if choice == "1":
                    await client_manager.demo_interactive_booking(client)
                elif choice == "2":
                    await client_manager.demo_business_traveler(client)
                elif choice == "3":
                    await client_manager.demo_family_traveler(client)
                elif choice == "4":
                    await client_manager.demo_budget_traveler(client)
                elif choice == "5":
                    await client_manager.demo_luxury_traveler(client)
                elif choice == "6":
                    await client_manager.demo_booking_management(client)
                elif choice == "7":
                    # Demo completo automático
                    demos = [
                        client_manager.demo_business_traveler,
                        client_manager.demo_family_traveler,
                        client_manager.demo_budget_traveler,
                        client_manager.demo_luxury_traveler,
                        client_manager.demo_booking_management
                    ]
                    
                    for demo_func in demos:
                        await demo_func(client)
                        await asyncio.sleep(1)
                    
                    print("\n🎉 Demo completo terminado!")
                    
                elif choice == "8":
                    print("👋 ¡Hasta luego!")
                    break
                else:
                    print("❌ Opción inválida. Por favor selecciona 1-8.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrumpido. ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🌟 Agente de Viajes Inteligente con Multi-Turn Interactions")
    print("=" * 60)
    print("Selecciona el modo de demostración:")
    print()
    print("1. 🎬 Demo automático completo (simula todos los tipos de viajero)")
    print("2. 🎮 Menú interactivo (incluye opción de RESERVA REAL)")
    print()
    print("💡 Para experimentar la verdadera elicitación, elige opción 2 → 1")
    
    try:
        choice = input("\n👉 Selecciona (1-2): ").strip()
        
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
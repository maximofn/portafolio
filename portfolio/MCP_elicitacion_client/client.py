"""
Cliente MCP Multi-Turn con Elicitación
======================================

Cliente que demuestra cómo interactuar con un servidor MCP que implementa
interacciones multi-turn usando elicitación para recopilar información
del usuario de manera progresiva.

Casos de uso demostrados:
1. Configuración de perfil paso a paso
2. Análisis de datos interactivo
3. Formularios con validación
4. Reserva de viajes con confirmación de precios
5. Manejo de respuestas del usuario (aceptar, rechazar, cancelar)

Uso:
    python client.py
"""

import asyncio
import json
from typing import Any, Dict, List, Optional

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from fastmcp.client.elicitation import ElicitResult


class ElicitationClient:
    """Cliente que demuestra patrones de elicitación multi-turn con MCP."""
    
    def __init__(self, server_command: List[str]):
        """
        Inicializa el cliente de elicitación.
        
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
            En un escenario real, esto mostraría un UI para obtener input del usuario.
            """
            print(f"\n🤖 Servidor solicita: {message}")
            
            # Simular diferentes tipos de respuesta según el tipo esperado
            if response_type == str:
                if "nombre" in message.lower():
                    response = "Alice Developer"
                elif "email" in message.lower():
                    response = "alice@example.com"
                elif "ruta" in message.lower() or "archivo" in message.lower():
                    response = "/data/sample_data.csv"
                elif "especializa" in message.lower():
                    response = "Machine Learning"
                elif "columnas" in message.lower():
                    response = "feature1, feature2, target"
                elif "ciudad" in message.lower() or "viajar" in message.lower():
                    response = "París"
                elif "fecha" in message.lower() or "cuándo" in message.lower():
                    response = "2024-06-15"
                else:
                    response = "Respuesta de ejemplo"
                    
                print(f"👤 Usuario responde: {response}")
                return ElicitResult(action="accept", content=response)
            
            elif response_type == int:
                if "edad" in message.lower():
                    response = 28
                elif "pasajeros" in message.lower() or "personas" in message.lower():
                    response = 2
                elif "semanas" in message.lower():
                    response = 8
                else:
                    response = 42
                    
                print(f"👤 Usuario responde: {response}")
                return ElicitResult(action="accept", content=response)
            
            elif isinstance(response_type, list):
                # Para opciones múltiples, seleccionar la primera opción
                selected_option = response_type[0]
                print(f"👤 Usuario selecciona: {selected_option}")
                return ElicitResult(action="accept", content=selected_option)
            
            elif hasattr(response_type, '__name__'):
                # Para enums u otros tipos específicos
                if "nivel" in message.lower() or "experiencia" in message.lower():
                    response = "intermedio"
                elif "formato" in message.lower():
                    response = "csv"
                else:
                    # Usar el primer valor del enum si es posible
                    try:
                        response = list(response_type)[0].value if hasattr(response_type, '__iter__') else "valor_por_defecto"
                    except:
                        response = "valor_por_defecto"
                
                print(f"👤 Usuario responde: {response}")
                return ElicitResult(action="accept", content=response)
            
            # Respuesta por defecto
            print("👤 Usuario responde: (respuesta por defecto)")
            return ElicitResult(action="accept", content="respuesta_por_defecto")
        
        client = Client(transport, elicitation_handler=elicitation_handler)
        return client
    
    async def demo_profile_setup(self, client: Client) -> None:
        """Demuestra la configuración de perfil paso a paso."""
        print("\n" + "🔥" * 50)
        print("Demo: Configuración de Perfil Multi-Turn")
        print("🔥" * 50)
        
        try:
            result = await client.call_tool("multi_step_profile_setup", {})
            print(f"\n✨ Resultado del perfil:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en configuración de perfil: {str(e)}")
    
    async def demo_data_analyzer(self, client: Client) -> None:
        """Demuestra el analizador de datos interactivo."""
        print("\n" + "📊" * 50)
        print("Demo: Analizador de Datos Interactivo")
        print("📊" * 50)
        
        try:
            result = await client.call_tool("interactive_data_analyzer", {})
            print(f"\n✨ Configuración del análisis:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en analizador de datos: {str(e)}")
    
    async def demo_form_validator(self, client: Client) -> None:
        """Demuestra el formulario con validación."""
        print("\n" + "✅" * 50)
        print("Demo: Formulario Inteligente con Validación")
        print("✅" * 50)
        
        try:
            result = await client.call_tool("smart_form_validator", {})
            print(f"\n✨ Resultado del formulario:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en formulario: {str(e)}")
    
    async def demo_travel_booking(self, client: Client) -> None:
        """Demuestra el agente de reserva de viajes."""
        print("\n" + "✈️" * 50)
        print("Demo: Agente de Reserva de Viajes")
        print("✈️" * 50)
        
        try:
            result = await client.call_tool("travel_booking_agent", {})
            print(f"\n✨ Resultado de la reserva:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error en reserva de viajes: {str(e)}")
    
    async def demo_with_user_decline(self, client: Client) -> None:
        """Demuestra cómo manejar cuando el usuario rechaza una solicitud."""
        print("\n" + "🚫" * 50)
        print("Demo: Manejo de Rechazo del Usuario")
        print("🚫" * 50)
        
        # Modificar temporalmente el manejador para simular rechazo
        original_handler = client._elicitation_handler
        
        async def declining_handler(message: str, response_type, params, ctx) -> ElicitResult:
            print(f"🤖 Servidor solicita: {message}")
            if "nombre" in message.lower():
                print("👤 Usuario rechaza proporcionar el nombre")
                return ElicitResult(action="decline", content=None)
            else:
                # Para otras preguntas, aceptar normalmente
                return await original_handler(message, response_type, params, ctx)
        
        client._elicitation_handler = declining_handler
        
        try:
            result = await client.call_tool("multi_step_profile_setup", {})
            print(f"\n✨ Resultado con rechazo:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            # Restaurar el manejador original
            client._elicitation_handler = original_handler
    
    async def demo_with_user_cancellation(self, client: Client) -> None:
        """Demuestra cómo manejar cuando el usuario cancela la interacción."""
        print("\n" + "🔴" * 50)
        print("Demo: Manejo de Cancelación del Usuario")
        print("🔴" * 50)
        
        # Modificar temporalmente el manejador para simular cancelación
        original_handler = client._elicitation_handler
        
        async def cancelling_handler(message: str, response_type, params, ctx) -> ElicitResult:
            print(f"🤖 Servidor solicita: {message}")
            if "edad" in message.lower():
                print("👤 Usuario cancela la interacción")
                return ElicitResult(action="cancel", content=None)
            else:
                # Para otras preguntas, aceptar normalmente
                return await original_handler(message, response_type, params, ctx)
        
        client._elicitation_handler = cancelling_handler
        
        try:
            result = await client.call_tool("multi_step_profile_setup", {})
            print(f"\n✨ Resultado con cancelación:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        finally:
            # Restaurar el manejador original
            client._elicitation_handler = original_handler
    
    async def demo_sessions_overview(self, client: Client) -> None:
        """Muestra las sesiones activas."""
        print("\n" + "👥" * 50)
        print("Demo: Sesiones Activas")
        print("👥" * 50)
        
        try:
            result = await client.call_tool("get_active_sessions", {})
            print(f"\n✨ Sesiones activas:")
            print(result.content[0].text)
        except Exception as e:
            print(f"❌ Error obteniendo sesiones: {str(e)}")


async def run_comprehensive_demo():
    """Ejecuta una demostración completa de todas las funcionalidades."""
    print("🌟 Demo Completo: Sistema MCP Multi-Turn con Elicitación")
    print("=" * 65)
    
    # Comando para ejecutar el servidor
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_elicitacion_server/server.py"
    ]
    
    client_manager = ElicitationClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al servidor de elicitación")
        
        # Ejecutar todas las demos
        demos = [
            ("Configuración de Perfil", client_manager.demo_profile_setup),
            ("Analizador de Datos", client_manager.demo_data_analyzer),
            ("Formulario con Validación", client_manager.demo_form_validator),
            ("Reserva de Viajes", client_manager.demo_travel_booking),
            ("Manejo de Rechazo", client_manager.demo_with_user_decline),
            ("Manejo de Cancelación", client_manager.demo_with_user_cancellation),
            ("Sesiones Activas", client_manager.demo_sessions_overview)
        ]
        
        for demo_name, demo_func in demos:
            try:
                print(f"\n🎬 Ejecutando: {demo_name}")
                await demo_func(client)
                await asyncio.sleep(1)  # Pausa entre demos
            except Exception as e:
                print(f"❌ Error en {demo_name}: {str(e)}")
        
        print("\n" + "🎉" * 50)
        print("¡Demo completo terminado!")
        print("🎉" * 50)


async def interactive_demo():
    """Demo interactivo donde el usuario puede elegir qué probar."""
    print("🚀 Demo Interactivo: Sistema MCP Multi-Turn con Elicitación")
    print("=" * 60)
    
    server_command = [
        "python", 
        "/Users/macm1/Documents/web/portafolio/portfolio/MCP_elicitacion_server/server.py"
    ]
    
    client_manager = ElicitationClient(server_command)
    
    async with await client_manager.connect() as client:
        print("🔗 Conectado al servidor de elicitación")
        
        while True:
            print("\n" + "=" * 50)
            print("Funcionalidades disponibles:")
            print("1. 👤 Configuración de perfil paso a paso")
            print("2. 📊 Analizador de datos interactivo")
            print("3. ✅ Formulario con validación")
            print("4. ✈️ Agente de reserva de viajes")
            print("5. 🚫 Demo de manejo de rechazo")
            print("6. 🔴 Demo de manejo de cancelación")
            print("7. 👥 Ver sesiones activas")
            print("8. 🎬 Ejecutar demo completo")
            print("9. 🚪 Salir")
            
            try:
                choice = input("\n👉 Selecciona una opción (1-9): ").strip()
                
                if choice == "1":
                    await client_manager.demo_profile_setup(client)
                elif choice == "2":
                    await client_manager.demo_data_analyzer(client)
                elif choice == "3":
                    await client_manager.demo_form_validator(client)
                elif choice == "4":
                    await client_manager.demo_travel_booking(client)
                elif choice == "5":
                    await client_manager.demo_with_user_decline(client)
                elif choice == "6":
                    await client_manager.demo_with_user_cancellation(client)
                elif choice == "7":
                    await client_manager.demo_sessions_overview(client)
                elif choice == "8":
                    # Ejecutar demo completo sin salir del menú
                    demos = [
                        client_manager.demo_profile_setup,
                        client_manager.demo_data_analyzer,
                        client_manager.demo_form_validator,
                        client_manager.demo_travel_booking,
                        client_manager.demo_sessions_overview
                    ]
                    
                    for demo_func in demos:
                        await demo_func(client)
                        await asyncio.sleep(0.5)
                    
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
    print("Selecciona el modo de demostración:")
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
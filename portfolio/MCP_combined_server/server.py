"""
Servidor MCP Multi-Turn con Elicitación + Sampling Combinados
============================================================

Este servidor demuestra el uso combinado de elicitación y sampling
para crear un agente de reserva de viajes inteligente que:
1. Solicita información del usuario (elicitación)
2. Genera contenido AI para mejorar la experiencia (sampling)
3. Confirma decisiones críticas (elicitación)
4. Personaliza recomendaciones (sampling)

Caso de uso: Agente de reserva de viajes que usa AI para personalizar
recomendaciones y elicitación para confirmaciones críticas.

Uso:
    python server.py
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum

from fastmcp import FastMCP, Context
from fastmcp.server.elicitation import AcceptedElicitation, DeclinedElicitation, CancelledElicitation
from mcp.types import TextContent

# Instancia del servidor MCP
mcp = FastMCP("Travel Booking Agent with AI")

# Enumeraciones
class TravelType(str, Enum):
    BUSINESS = "negocios"
    LEISURE = "placer"
    FAMILY = "familiar"
    ADVENTURE = "aventura"

class BudgetRange(str, Enum):
    BUDGET = "económico"
    MID_RANGE = "medio"
    LUXURY = "lujo"

# Base de datos simulada de destinos
DESTINATIONS_DB = {
    "parís": {
        "name": "París, Francia",
        "base_price": 850,
        "highlights": ["Torre Eiffel", "Louvre", "Notre-Dame", "Campos Elíseos"],
        "best_season": "Primavera/Otoño",
        "travel_time": "8-9 horas desde América"
    },
    "tokio": {
        "name": "Tokio, Japón", 
        "base_price": 1200,
        "highlights": ["Shibuya", "Templos tradicionales", "Tecnología avanzada", "Gastronomía única"],
        "best_season": "Primavera/Otoño",
        "travel_time": "11-14 horas desde América"
    },
    "nueva york": {
        "name": "Nueva York, Estados Unidos",
        "base_price": 650,
        "highlights": ["Central Park", "Broadway", "Estatua de la Libertad", "Times Square"],
        "best_season": "Todo el año",
        "travel_time": "5-6 horas desde Europa"
    },
    "bali": {
        "name": "Bali, Indonesia",
        "base_price": 900,
        "highlights": ["Playas tropicales", "Templos hindúes", "Arrozales", "Spa y wellness"],
        "best_season": "Abril-Octubre",
        "travel_time": "15-20 horas desde América"
    }
}

# Storage para reservas
bookings: Dict[str, Dict[str, Any]] = {}

def extract_elicitation_value(elicitation_data):
    """Helper para extraer valor de respuesta de elicitación"""
    if isinstance(elicitation_data, dict) and "value" in elicitation_data:
        return elicitation_data["value"]
    return elicitation_data

@mcp.tool
async def intelligent_travel_booking_agent(context: Context) -> str:
    """
    Agente de reserva de viajes inteligente que combina elicitación
    para decisiones críticas y sampling para personalización AI.
    """
    booking_id = f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}"
    booking_data = {"id": booking_id, "timestamp": datetime.now().isoformat()}
    
    print(f"\n🛫 Iniciando nueva reserva: {booking_id}")
    
    # PASO 1: Elicitación - Información básica del viaje
    print("📝 Recopilando información básica...")
    
    # Tipo de viaje
    travel_type_result = await context.elicit(
        message="¿Qué tipo de viaje planeas? (influirá en nuestras recomendaciones)",
        response_type=TravelType
    )
    
    if not isinstance(travel_type_result, AcceptedElicitation):
        return "🚫 Reserva cancelada: Tipo de viaje no especificado"
    
    travel_type_value = extract_elicitation_value(travel_type_result.data)
    booking_data["travel_type"] = travel_type_value
    
    # Destino deseado
    destination_result = await context.elicit(
        message="¿Cuál es tu destino deseado? (París, Tokio, Nueva York, Bali, u otro)",
        response_type=str
    )
    
    if not isinstance(destination_result, AcceptedElicitation):
        return "⚠️ Reserva incompleta: Destino no especificado"
    
    destination_value = extract_elicitation_value(destination_result.data)
    destination_input = destination_value.lower().strip()
    booking_data["destination_input"] = destination_input
    
    # PASO 2: Análisis de destino (sin sampling por compatibilidad)
    print("🤖 Analizando destino...")
    
    # Determinar destino usando base de datos local
    destination_info = None
    for key in DESTINATIONS_DB:
        if key in destination_input or destination_input in key:
            destination_info = DESTINATIONS_DB[key]
            booking_data["destination"] = destination_info["name"]
            break
    
    if not destination_info:
        # Para destinos no conocidos, usar datos genéricos
        destination_info = {
            "name": destination_input.title(),
            "base_price": 800,
            "highlights": ["Atracciones principales", "Cultura local", "Gastronomía", "Experiencias únicas"],
            "best_season": "Varía según región",
            "travel_time": "Consultar según origen"
        }
        booking_data["destination"] = destination_info["name"]
    
    # PASO 3: Elicitación - Detalles específicos del viaje
    print("📅 Obteniendo detalles específicos...")
    
    # Fechas de viaje
    dates_result = await context.elicit(
        message="¿Cuándo planeas viajar? (formato: YYYY-MM-DD o descripción como 'próximo mes')",
        response_type=str
    )
    
    travel_dates = "Por determinar"
    if isinstance(dates_result, AcceptedElicitation):
        travel_dates = extract_elicitation_value(dates_result.data)
        booking_data["travel_dates"] = travel_dates
    
    # Número de personas
    travelers_result = await context.elicit(
        message="¿Cuántas personas viajarán?",
        response_type=int
    )
    
    if not isinstance(travelers_result, AcceptedElicitation):
        return "⚠️ Reserva incompleta: Número de viajeros no especificado"
    
    num_travelers = extract_elicitation_value(travelers_result.data)
    booking_data["travelers"] = num_travelers
    
    # Presupuesto
    budget_result = await context.elicit(
        message="¿Cuál es tu rango de presupuesto por persona?",
        response_type=BudgetRange
    )
    
    budget_range = BudgetRange.MID_RANGE.value
    if isinstance(budget_result, AcceptedElicitation):
        budget_range = extract_elicitation_value(budget_result.data)
    
    booking_data["budget"] = budget_range
    
    # PASO 4: Itinerario personalizado (versión simplificada)
    print("🎯 Generando itinerario personalizado...")
    
    # Itinerario estático basado en el tipo de viaje
    if booking_data['travel_type'] == 'negocios':
        itinerary_text = f"""💼 ITINERARIO EJECUTIVO - {destination_info['name']} ({num_travelers} personas)

DÍA 1: Llegada y orientación
- Mañana: Check-in hotel ejecutivo
- Tarde: Reuniones de negocios
- Noche: Cena de negocios

DÍA 2-3: Actividades principales
- {destination_info['highlights'][0]} (tour ejecutivo)
- {destination_info['highlights'][1]} (visita rápida)
- Tiempo libre para calls/meetings

DÍA 4: Cierre
- Últimas reuniones
- Transfer al aeropuerto

💰 COSTOS ESTIMADOS ADICIONALES:
- Comidas ejecutivas: $400-600 USD
- Transport premium: $200 USD
- Actividades: $300 USD

✈️ CONSEJOS EJECUTIVOS:
- Hotel con centro de negocios 24/7
- SIM card local para datos
- Vestuario business formal"""
    elif booking_data['travel_type'] == 'familiar':
        itinerary_text = f"""👨‍👩‍👧‍👦 ITINERARIO FAMILIAR - {destination_info['name']} ({num_travelers} personas)

DÍA 1: Llegada suave
- Mañana: Check-in alojamiento familiar
- Tarde: Exploración del barrio
- Noche: Cena local auténtica

DÍA 2-3: Atracciones principales
- {destination_info['highlights'][0]} (actividad familiar)
- {destination_info['highlights'][1]} (entretenimiento niños)
- Parques y áreas de juego

DÍA 4: Actividades relajadas
- Compras de souvenirs
- Últimos recuerdos fotográficos
- Preparación para regreso

💰 COSTOS FAMILIA:
- Alimentos: $600-800 USD
- Actividades: $500 USD
- Transporte: $250 USD
- Souvenirs: $200 USD

👨‍👩‍👧‍👦 CONSEJOS FAMILIARES:
- Apartamento con cocina
- Llevar snacks y entretenimiento
- Horarios flexibles para descansos"""
    else:
        itinerary_text = f"""🌍 ITINERARIO PERSONALIZADO - {destination_info['name']} ({num_travelers} personas)

DÍA 1: Orientación
- Llegada y check-in
- Exploración inicial del área
- Cena local

DÍA 2-3: Atracciones principales
- {destination_info['highlights'][0]}
- {destination_info['highlights'][1]}
- Actividades culturales

DÍA 4: Experiencias únicas
- {destination_info['highlights'][2] if len(destination_info['highlights']) > 2 else 'Actividades especiales'}
- Gastronomía local
- Compras

💰 COSTOS ESTIMADOS:
- Comidas: $300-500 USD por persona
- Actividades: $200-400 USD por persona
- Transporte local: $100-150 USD por persona

📝 CONSEJOS PRÁCTICOS:
- Mejor época: {destination_info['best_season']}
- Tiempo de viaje: {destination_info['travel_time']}
- Llevar cámara para recuerdos"""
    
    booking_data["itinerary"] = itinerary_text
    
    # PASO 5: Cálculo de precios y opciones
    print("💰 Calculando precios...")
    
    base_price = destination_info["base_price"]
    budget_multipliers = {
        "económico": 0.7,
        "medio": 1.0,
        "lujo": 1.5
    }
    
    adjusted_price = int(base_price * budget_multipliers.get(budget_range.value, 1.0))
    total_price = adjusted_price * num_travelers
    booking_data["price_per_person"] = adjusted_price
    booking_data["total_price"] = total_price
    
    # PASO 6: Elicitación crítica - Confirmación de precios
    print("✅ Solicitando confirmación...")
    
    confirmation_message = f"""
📋 RESUMEN DE TU VIAJE PERSONALIZADO

🏖️ Destino: {destination_info['name']}
🎯 Tipo: {booking_data['travel_type'].title()}
👥 Viajeros: {num_travelers} personas
📅 Fechas: {travel_dates}
💰 Presupuesto: {budget_range.value.title()}

💵 PRECIOS:
- Por persona: ${adjusted_price:,} USD
- Total: ${total_price:,} USD

🎊 INCLUYE:
- Vuelos ida y vuelta
- Alojamiento ({budget_range.value})
- Itinerario personalizado
- Soporte 24/7

¿Confirmas esta reserva?"""
    
    confirmation_result = await context.elicit(
        message=confirmation_message,
        response_type=["confirmar", "ver opciones más baratas", "modificar fechas", "cancelar"]
    )
    
    if not isinstance(confirmation_result, AcceptedElicitation):
        return "🔄 Reserva no confirmada - Sesión finalizada"
    
    user_choice = extract_elicitation_value(confirmation_result.data)
    
    # PASO 7: Manejo de la respuesta del usuario
    if user_choice == "confirmar":
        booking_data["status"] = "confirmed"
        booking_data["confirmation_time"] = datetime.now().isoformat()
        bookings[booking_id] = booking_data
        
        # Mensaje de confirmación personalizado (versión simplificada)
        confirmation_message = f"""🎉 ¡Felicitaciones! Tu aventura está oficialmente confirmada.

Has tomado una excelente decisión eligiendo {destination_info['name']}. Nuestro equipo está emocionado de ser parte de tu próximo viaje.

✅ QUÉ VIENE AHORA:
- Recibirás documentación completa por email en 24h
- Te contactaremos 48h antes del viaje
- Tienes soporte 24/7 durante todo tu viaje
- Acceso a nuestra app móvil con itinerario

🎁 BONOS INCLUIDOS:
- Guía digital personalizada
- Lista de frases útiles en idioma local
- Mapa offline con puntos de interés
- Contactos de emergencia locales

¡Prepárate para crear recuerdos inolvidables!"""
        
        return f"""
🎉 {confirmation_message}

🎫 ID de Reserva: {booking_id}
📍 Destino: {destination_info['name']}
💰 Total: ${total_price:,} USD

📧 Recibirás un email de confirmación en breve.

{itinerary_text}

📞 Para cualquier consulta: soporte@viajesai.com
        """.strip()
    
    elif user_choice == "ver opciones más baratas":
        # Generar alternativas más económicas
        cheaper_price = int(adjusted_price * 0.75)
        cheaper_total = cheaper_price * num_travelers
        
        alternative_confirmation = await context.elicit(
            message=f"Opción económica encontrada: ${cheaper_price:,} por persona (Total: ${cheaper_total:,}). Incluye alojamiento básico y vuelos con escala. ¿La aceptas?",
            response_type=["aceptar", "rechazar"]
        )
        
        if isinstance(alternative_confirmation, AcceptedElicitation) and extract_elicitation_value(alternative_confirmation.data) == "aceptar":
            booking_data["price_per_person"] = cheaper_price
            booking_data["total_price"] = cheaper_total
            booking_data["option"] = "económica"
            booking_data["status"] = "confirmed"
            bookings[booking_id] = booking_data
            
            savings = total_price - cheaper_total
            return f"""
✅ ¡Opción económica confirmada!

💰 Ahorro: ${savings:,} USD
🎫 ID: {booking_id}
📍 Destino: {destination_info['name']}
💵 Total final: ${cheaper_total:,} USD
            """.strip()
        else:
            return "🔄 Opción económica rechazada. Puedes reiniciar el proceso cuando gustes."
    
    elif user_choice == "modificar fechas":
        new_dates_result = await context.elicit(
            message="¿Cuáles son tus nuevas fechas preferidas?",
            response_type=str
        )
        
        if isinstance(new_dates_result, AcceptedElicitation):
            new_dates = extract_elicitation_value(new_dates_result.data)
            return f"📅 Fechas actualizadas a: {new_dates}. Reinicia el proceso para ver nuevos precios y disponibilidad."
        else:
            return "📅 Modificación de fechas cancelada."
    
    else:  # cancelar
        return "🚫 Reserva cancelada por el usuario. ¡Esperamos ayudarte en el futuro!"

@mcp.tool
async def get_booking_status(context: Context) -> str:
    """
    Obtiene el estado de una reserva por ID.
    """
    booking_id_result = await context.elicit(
        message="Proporciona el ID de reserva (formato: BK...)",
        response_type=str
    )
    
    if not isinstance(booking_id_result, AcceptedElicitation):
        return "🚫 Consulta cancelada: ID no proporcionado"
    
    booking_id = extract_elicitation_value(booking_id_result.data).strip()
    
    if booking_id not in bookings:
        return f"❌ No se encontró reserva con ID: {booking_id}"
    
    booking = bookings[booking_id]
    
    return f"""
📋 ESTADO DE RESERVA

🎫 ID: {booking_id}
📍 Destino: {booking.get('destination', 'N/A')}
👥 Viajeros: {booking.get('travelers', 'N/A')}
💰 Total: ${booking.get('total_price', 0):,} USD
📅 Fechas: {booking.get('travel_dates', 'N/A')}
✅ Estado: {booking.get('status', 'pendiente').upper()}
🕐 Creada: {booking.get('timestamp', 'N/A')}
    """.strip()

@mcp.tool
async def list_all_bookings(context: Context) -> str:
    """
    Lista todas las reservas realizadas en esta sesión.
    """
    if not bookings:
        return "📭 No hay reservas registradas en esta sesión"
    
    booking_list = ["🎫 Reservas Realizadas:", "=" * 25]
    
    for booking_id, booking in bookings.items():
        status_emoji = {"confirmed": "✅", "pending": "⏳", "cancelled": "❌"}.get(booking.get("status"), "❓")
        booking_list.append(f"\n{status_emoji} {booking_id}")
        booking_list.append(f"   📍 {booking.get('destination', 'N/A')}")
        booking_list.append(f"   💰 ${booking.get('total_price', 0):,} USD")
        booking_list.append(f"   👥 {booking.get('travelers', 'N/A')} personas")
    
    return "\n".join(booking_list)

if __name__ == "__main__":
    print("🚀 Iniciando Agente de Viajes Inteligente MCP...")
    print("=" * 55)
    print("Funcionalidades disponibles:")
    print("1. ✈️ intelligent_travel_booking_agent - Reserva inteligente completa")
    print("2. 📋 get_booking_status - Consultar estado de reserva")
    print("3. 🎫 list_all_bookings - Listar todas las reservas")
    print("=" * 55)
    print("🤖 Combina elicitación (confirmaciones) + AI sampling (recomendaciones)")
    
    mcp.run()
"""
Servidor MCP Multi-Turn con Elicitación
========================================

Este servidor demuestra cómo implementar interacciones multi-turn usando elicitación
para solicitar información adicional del usuario durante la ejecución de herramientas.

Funcionalidades implementadas:
1. Formulario de usuario paso a paso
2. Configurador de perfil interactivo  
3. Asistente de análisis de datos
4. Validador de entrada con retry
5. Selector de opciones múltiples

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

# Instancia del servidor MCP
mcp = FastMCP("Multi-Turn Elicitation Server")

# Enumeraciones para opciones
class ProficiencyLevel(str, Enum):
    BEGINNER = "principiante"
    INTERMEDIATE = "intermedio"
    ADVANCED = "avanzado"
    EXPERT = "experto"

class DataFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PARQUET = "parquet"

# Storage temporal para datos de usuario
user_sessions: Dict[str, Dict[str, Any]] = {}

@mcp.tool
async def multi_step_profile_setup(context: Context) -> str:
    """
    Configurador de perfil de usuario paso a paso usando elicitación.
    Solicita nombre, edad, skills y nivel de experiencia progresivamente.
    """
    session_id = f"session_{datetime.now().timestamp()}"
    profile_data = {}
    
    # Paso 1: Solicitar nombre
    name_result = await context.elicit(
        message="¡Hola! Vamos a configurar tu perfil. ¿Cuál es tu nombre?",
        response_type=str
    )
    
    if isinstance(name_result, DeclinedElicitation):
        return "❌ Configuración cancelada: No se proporcionó nombre"
    elif isinstance(name_result, CancelledElicitation):
        return "🚫 Configuración abandonada por el usuario"
    
    profile_data["name"] = name_result.data
    
    # Paso 2: Solicitar edad
    age_result = await context.elicit(
        message=f"Hola {name_result.data}! ¿Cuál es tu edad?",
        response_type=int
    )
    
    if not isinstance(age_result, AcceptedElicitation):
        return f"👋 Hola {name_result.data}, configuración incompleta (no se proporcionó edad)"
    
    profile_data["age"] = age_result.data
    
    # Paso 3: Solicitar área de especialización
    skills_result = await context.elicit(
        message="¿En qué área tecnológica te especializas? (ej: desarrollo web, machine learning, devops)",
        response_type=str
    )
    
    if not isinstance(skills_result, AcceptedElicitation):
        return f"👋 Perfil parcial creado para {name_result.data} ({age_result.data} años)"
    
    profile_data["specialization"] = skills_result.data
    
    # Paso 4: Solicitar nivel de experiencia
    level_result = await context.elicit(
        message="¿Cuál es tu nivel de experiencia?",
        response_type=ProficiencyLevel
    )
    
    if isinstance(level_result, AcceptedElicitation):
        profile_data["experience_level"] = level_result.data.value
    
    # Guarda en sesión
    user_sessions[session_id] = profile_data
    
    # Resumen final
    summary = f"""
✅ Perfil creado exitosamente!

👤 Información personal:
   Nombre: {profile_data['name']}
   Edad: {profile_data['age']} años
   
💼 Información profesional:  
   Especialización: {profile_data['specialization']}
   Nivel: {profile_data.get('experience_level', 'no especificado').title()}
   
🆔 ID de sesión: {session_id}
    """
    
    return summary.strip()

@mcp.tool  
async def interactive_data_analyzer(context: Context) -> str:
    """
    Analizador de datos interactivo que solicita configuración paso a paso.
    Permite especificar fuente de datos, formato, y opciones de análisis.
    """
    analysis_config = {}
    
    # Paso 1: Tipo de análisis
    analysis_options = [
        "análisis exploratorio",
        "detección de outliers", 
        "análisis de correlaciones",
        "estadísticas descriptivas"
    ]
    
    analysis_result = await context.elicit(
        message="¿Qué tipo de análisis deseas realizar?",
        response_type=analysis_options
    )
    
    if not isinstance(analysis_result, AcceptedElicitation):
        return "🚫 Análisis cancelado: No se seleccionó tipo de análisis"
    
    analysis_config["analysis_type"] = analysis_result.data
    
    # Paso 2: Formato de datos
    format_result = await context.elicit(
        message=f"Perfecto! Para '{analysis_result.data}', ¿en qué formato están tus datos?",
        response_type=DataFormat
    )
    
    if not isinstance(format_result, AcceptedElicitation):
        return f"⚠️ Análisis parcial: Solo se configuró '{analysis_result.data}'"
    
    analysis_config["data_format"] = format_result.data.value
    
    # Paso 3: Ruta del archivo
    path_result = await context.elicit(
        message="¿Cuál es la ruta del archivo de datos?",
        response_type=str
    )
    
    if isinstance(path_result, AcceptedElicitation):
        analysis_config["data_path"] = path_result.data
        
        # Paso 4: Columnas específicas (opcional)
        columns_result = await context.elicit(
            message="¿Hay columnas específicas que quieras analizar? (opcional, deja vacío para todas)",
            response_type=str
        )
        
        if isinstance(columns_result, AcceptedElicitation) and columns_result.data.strip():
            analysis_config["target_columns"] = [col.strip() for col in columns_result.data.split(",")]
    
    # Resumen de configuración
    summary = f"""
🔍 Configuración del análisis:

📊 Tipo de análisis: {analysis_config['analysis_type']}
📁 Formato de datos: {analysis_config['data_format'].upper()}
📂 Archivo: {analysis_config.get('data_path', 'no especificado')}
🎯 Columnas objetivo: {', '.join(analysis_config.get('target_columns', ['todas']))}

⚡ El análisis se ejecutaría con esta configuración...
    """
    
    return summary.strip()

@mcp.tool
async def smart_form_validator(context: Context) -> str:
    """
    Formulario inteligente con validación y reintentos.
    Demuestra manejo de errores y solicitud repetida de información.
    """
    
    # Solicitar email con validación
    email_attempts = 0
    max_attempts = 3
    email = None
    
    while email_attempts < max_attempts:
        email_result = await context.elicit(
            message=f"Ingresa tu dirección de email {f'(intento {email_attempts + 1}/{max_attempts})' if email_attempts > 0 else ''}:",
            response_type=str
        )
        
        if not isinstance(email_result, AcceptedElicitation):
            return "❌ Validación cancelada: No se proporcionó email"
        
        # Validación básica de email
        email_value = email_result.data.strip()
        if "@" in email_value and "." in email_value.split("@")[-1]:
            email = email_value
            break
        else:
            email_attempts += 1
            if email_attempts < max_attempts:
                # Continuar el bucle para reintentar
                continue
            else:
                return f"❌ Email inválido después de {max_attempts} intentos: '{email_value}'"
    
    # Solicitar edad con validación
    age_attempts = 0
    age = None
    
    while age_attempts < max_attempts:
        age_result = await context.elicit(
            message=f"Ingresa tu edad (entre 13 y 120) {f'(intento {age_attempts + 1}/{max_attempts})' if age_attempts > 0 else ''}:",
            response_type=int
        )
        
        if not isinstance(age_result, AcceptedElicitation):
            return f"⚠️ Formulario parcial: Email validado ({email}), edad no proporcionada"
        
        age_value = age_result.data
        if 13 <= age_value <= 120:
            age = age_value
            break
        else:
            age_attempts += 1
            if age_attempts >= max_attempts:
                return f"❌ Edad inválida después de {max_attempts} intentos: {age_value}"
    
    # Confirmación final
    confirm_result = await context.elicit(
        message=f"¿Confirmas estos datos? Email: {email}, Edad: {age}",
        response_type=["sí", "no"]
    )
    
    if isinstance(confirm_result, AcceptedElicitation) and confirm_result.data == "sí":
        return f"✅ Formulario completado y validado:\n   📧 Email: {email}\n   🎂 Edad: {age}"
    else:
        return "🔄 Formulario no confirmado, datos descartados"

@mcp.tool
async def travel_booking_agent(context: Context) -> str:
    """
    Agente de reserva de viajes que demuestra elicitación para confirmación de precios
    y recopilación de información crítica paso a paso.
    """
    booking_data = {}
    
    # Paso 1: Destino
    destination_result = await context.elicit(
        message="¿A qué ciudad te gustaría viajar?",
        response_type=str
    )
    
    if not isinstance(destination_result, AcceptedElicitation):
        return "🚫 Reserva cancelada: No se especificó destino"
    
    booking_data["destination"] = destination_result.data
    
    # Paso 2: Fechas
    dates_result = await context.elicit(
        message=f"¿Cuándo planeas viajar a {destination_result.data}? (formato: YYYY-MM-DD)",
        response_type=str
    )
    
    if not isinstance(dates_result, AcceptedElicitation):
        return f"⚠️ Reserva incompleta: Destino {destination_result.data}, fechas no especificadas"
    
    booking_data["travel_date"] = dates_result.data
    
    # Paso 3: Número de pasajeros
    passengers_result = await context.elicit(
        message="¿Cuántas personas viajarán?",
        response_type=int
    )
    
    if isinstance(passengers_result, AcceptedElicitation):
        booking_data["passengers"] = passengers_result.data
        
        # Simulación de búsqueda de precios
        base_price = 450
        total_price = base_price * passengers_result.data
        
        # Paso 4: Confirmación de precio (crítico)
        price_confirmation = await context.elicit(
            message=f"""
📋 Resumen de tu reserva:
🏖️ Destino: {booking_data['destination']}
📅 Fecha: {booking_data['travel_date']}
👥 Pasajeros: {booking_data['passengers']}

💰 Precio total: ${total_price} USD (${base_price} por persona)

¿Confirmas la reserva con este precio?""",
            response_type=["confirmar", "cancelar", "ver opciones más baratas"]
        )
        
        if isinstance(price_confirmation, AcceptedElicitation):
            if price_confirmation.data == "confirmar":
                booking_data["status"] = "confirmed"
                booking_data["total_price"] = total_price
                booking_data["booking_id"] = f"BK{datetime.now().strftime('%Y%m%d%H%M')}"
                
                return f"""
✅ ¡Reserva confirmada exitosamente!

📍 Destino: {booking_data['destination']}
📅 Fecha: {booking_data['travel_date']}
👥 Pasajeros: {booking_data['passengers']}
💰 Total pagado: ${total_price} USD
🎫 ID de reserva: {booking_data['booking_id']}

📧 Se enviará confirmación por email.
                """.strip()
                
            elif price_confirmation.data == "ver opciones más baratas":
                cheaper_price = int(total_price * 0.8)
                final_confirmation = await context.elicit(
                    message=f"Encontré una opción más económica: ${cheaper_price} USD (vuelo con escala). ¿La aceptas?",
                    response_type=["aceptar", "rechazar"]
                )
                
                if isinstance(final_confirmation, AcceptedElicitation) and final_confirmation.data == "aceptar":
                    booking_data["status"] = "confirmed"
                    booking_data["total_price"] = cheaper_price
                    booking_data["booking_id"] = f"BK{datetime.now().strftime('%Y%m%d%H%M')}"
                    
                    return f"""
✅ Reserva confirmada con opción económica!

📍 Destino: {booking_data['destination']}
📅 Fecha: {booking_data['travel_date']}
👥 Pasajeros: {booking_data['passengers']}
💰 Total pagado: ${cheaper_price} USD (¡Ahorraste ${total_price - cheaper_price}!)
🎫 ID de reserva: {booking_data['booking_id']}
✈️ Vuelo con escala
                    """.strip()
                else:
                    return "🔄 Reserva no completada: Opción económica rechazada"
            else:
                return "🚫 Reserva cancelada por el usuario"
    
    return "⚠️ Reserva incompleta: Información de pasajeros no proporcionada"

@mcp.tool
async def get_active_sessions(context: Context) -> str:
    """
    Muestra las sesiones de usuario activas (para debugging).
    """
    if not user_sessions:
        return "📭 No hay sesiones activas"
    
    session_list = ["👥 Sesiones Activas:", "=" * 20]
    
    for session_id, data in user_sessions.items():
        session_list.append(f"\n🆔 {session_id}")
        session_list.append(f"   Nombre: {data.get('name', 'N/A')}")
        session_list.append(f"   Edad: {data.get('age', 'N/A')}")
        session_list.append(f"   Especialización: {data.get('specialization', 'N/A')}")
    
    return "\n".join(session_list)

if __name__ == "__main__":
    print("🚀 Iniciando Servidor MCP Multi-Turn con Elicitación...")
    print("=" * 55)
    print("Funcionalidades disponibles:")
    print("1. 👤 multi_step_profile_setup - Configurador de perfil paso a paso")
    print("2. 🔍 interactive_data_analyzer - Analizador de datos interactivo")
    print("3. ✅ smart_form_validator - Formulario con validación y reintentos")
    print("4. ✈️ travel_booking_agent - Agente de reserva de viajes")
    print("5. 👥 get_active_sessions - Ver sesiones activas")
    print("=" * 55)
    
    mcp.run()
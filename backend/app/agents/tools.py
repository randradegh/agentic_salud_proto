"""Herramientas del agente."""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

from app.integrations.calcom import calcom_client
from app.rag.retriever import rag_retriever


def buscar_informacion(query: str) -> str:
    """
    Busca información relevante en la base de conocimiento.
    
    Args:
        query: Pregunta o tema a buscar
    
    Returns:
        Información relevante encontrada
    """
    results = rag_retriever.search(query, top_k=3, similarity_threshold=0.7)
    
    if not results:
        return "No encontré información relevante sobre ese tema en la base de conocimiento."
    
    # Combinar resultados
    info_parts = []
    for i, result in enumerate(results, 1):
        content = result["content"]
        source = result["metadata"].get("source", "documento")
        info_parts.append(f"[Fuente: {source}]\n{content}")
    
    return "\n\n---\n\n".join(info_parts)


def verificar_disponibilidad(
    fecha_inicio: str,
    fecha_fin: Optional[str] = None,
    tipo_evento: str = "consultoria"
) -> str:
    """
    Verifica slots disponibles en Cal.com.
    
    Args:
        fecha_inicio: Fecha de inicio en formato ISO
        fecha_fin: Fecha de fin en formato ISO (opcional)
        tipo_evento: Tipo de evento/servicio
    
    Returns:
        Lista de slots disponibles en formato legible
    """
    try:
        start_dt = datetime.fromisoformat(fecha_inicio.replace("Z", "+00:00"))
        end_dt = None
        
        if fecha_fin:
            end_dt = datetime.fromisoformat(fecha_fin.replace("Z", "+00:00"))
        else:
            # Por defecto, buscar disponibilidad para los próximos 7 días
            end_dt = start_dt + timedelta(days=7)
        
        # Obtener slots disponibles
        slots = calcom_client.get_available_slots(
            start_time=start_dt,
            end_time=end_dt
        )
        
        if not slots:
            return "No hay disponibilidad en el rango de fechas solicitado. Por favor, intenta con otro rango."
        
        # Formatear slots
        formatted_slots = []
        for slot in slots[:10]:  # Limitar a 10 slots
            start_str = slot.get("start", "")
            end_str = slot.get("end", "")
            
            try:
                start_time = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                formatted_slots.append(start_time.strftime("%A %d de %B a las %H:%M"))
            except Exception:
                formatted_slots.append(start_str)
        
        if formatted_slots:
            return f"Horarios disponibles:\n" + "\n".join(f"- {slot}" for slot in formatted_slots)
        else:
            return "No pude obtener los horarios disponibles. Por favor, intenta más tarde."
    
    except Exception as e:
        return f"Error al verificar disponibilidad: {str(e)}"


def crear_cita(
    nombre: str,
    email: str,
    fecha_hora: str,
    tipo_servicio: str,
    notas: Optional[str] = None
) -> str:
    """
    Crea una cita en Cal.com.
    
    Args:
        nombre: Nombre del cliente
        email: Email del cliente
        fecha_hora: Fecha y hora en formato ISO
        tipo_servicio: Tipo de servicio
        notas: Notas adicionales (opcional)
    
    Returns:
        Confirmación con detalles de la cita
    """
    try:
        start_dt = datetime.fromisoformat(fecha_hora.replace("Z", "+00:00"))
        
        booking = calcom_client.create_booking(
            name=nombre,
            email=email,
            start=start_dt,
            notes=notas or f"Servicio: {tipo_servicio}"
        )
        
        if booking:
            booking_id = booking.get("id", "N/A")
            return f"✓ Cita confirmada exitosamente.\n\nID de reserva: {booking_id}\nFecha: {start_dt.strftime('%A %d de %B a las %H:%M')}\n\nRecibirás un email de confirmación con todos los detalles."
        else:
            return "No pude crear la cita. Por favor, verifica que el horario esté disponible e intenta nuevamente."
    
    except Exception as e:
        return f"Error al crear la cita: {str(e)}"


# Diccionario de herramientas para LangChain
TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "buscar_informacion",
            "description": "Busca información relevante en la base de conocimiento sobre servicios, precios, procesos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La pregunta o tema a buscar"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verificar_disponibilidad",
            "description": "Verifica horarios disponibles para agendar una cita en Cal.com",
            "parameters": {
                "type": "object",
                "properties": {
                    "fecha_inicio": {
                        "type": "string",
                        "description": "Fecha de inicio en formato ISO (ej: 2026-02-15T14:00:00Z)"
                    },
                    "fecha_fin": {
                        "type": "string",
                        "description": "Fecha de fin en formato ISO (opcional)"
                    },
                    "tipo_evento": {
                        "type": "string",
                        "description": "Tipo de servicio/evento"
                    }
                },
                "required": ["fecha_inicio"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_cita",
            "description": "Crea una cita/reserva en Cal.com con la información proporcionada",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre completo del cliente"
                    },
                    "email": {
                        "type": "string",
                        "description": "Email del cliente"
                    },
                    "fecha_hora": {
                        "type": "string",
                        "description": "Fecha y hora en formato ISO (ej: 2026-02-15T14:00:00Z)"
                    },
                    "tipo_servicio": {
                        "type": "string",
                        "description": "Tipo de servicio a agendar"
                    },
                    "notas": {
                        "type": "string",
                        "description": "Notas adicionales sobre la cita"
                    }
                },
                "required": ["nombre", "email", "fecha_hora", "tipo_servicio"]
            }
        }
    }
]

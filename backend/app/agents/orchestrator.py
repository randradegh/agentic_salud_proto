"""Orquestador del agente conversacional."""
import json
from typing import List, Dict, Optional, AsyncIterator
from datetime import datetime

from app.integrations.ollama import ollama_client
from app.agents.tools import (
    buscar_informacion,
    verificar_disponibilidad,
    crear_cita,
    TOOLS_DEFINITIONS
)
from app.models import Message


SYSTEM_PROMPT = """Eres el asistente virtual de un consultorio dental en la Ciudad de México.

REGLA CRÍTICA: Responde ÚNICAMENTE con la información que aparece en el "Información relevante" (o contexto) que te proporcionan. Si hay texto en "Información relevante", ÚSALO en tu respuesta; no digas que no tienes la información si ya te la dieron ahí. No inventes direcciones, teléfonos ni precios. Solo si "Información relevante" está vacío o dice que no encontró nada, entonces di que no tienes ese dato y recomienda llamar o agendar.

Tus responsabilidades son:

1. INFORMACIÓN: Responder solo con lo que diga el contexto (servicios, precios, dirección/ubicación, horarios, primera cita). Si no está en el contexto, no lo inventes.

2. AGENDAMIENTO: Ayudar a agendar citas recopilando nombre, teléfono o email y preferencia de día y horario.

3. ESTILO: Amigable, profesional, en español de México. Conciso. Si preguntan por dirección u otra cosa que no esté en el contexto, invita a llamar o agendar.

4. LIMITACIONES: No des diagnósticos ni recetas. No inventes datos. Los precios son aproximados.

Responde siempre en español de México."""


class AgentOrchestrator:
    """Orquestador principal del agente."""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
    
    def _format_messages_for_ollama(self, messages: List[Message]) -> List[Dict]:
        """Formatea mensajes para Ollama."""
        formatted = []
        
        for msg in messages:
            role_map = {
                "user": "user",
                "assistant": "assistant",
                "system": "system"
            }
            formatted.append({
                "role": role_map.get(msg.role, "user"),
                "content": msg.content
            })
        
        return formatted
    
    def _call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Ejecuta una herramienta."""
        tool_map = {
            "buscar_informacion": buscar_informacion,
            "verificar_disponibilidad": verificar_disponibilidad,
            "crear_cita": crear_cita
        }
        
        tool_func = tool_map.get(tool_name)
        if not tool_func:
            return f"Herramienta {tool_name} no encontrada"
        
        try:
            return tool_func(**arguments)
        except Exception as e:
            return f"Error ejecutando {tool_name}: {str(e)}"
    
    def _build_prompt_with_tools(self, ollama_messages: List[Dict]) -> str:
        """Construye el prompt con instrucciones de herramientas."""
        prompt_with_tools = f"""{self.system_prompt}

Herramientas disponibles:
1. buscar_informacion(query): Busca información en la base de conocimiento
2. verificar_disponibilidad(fecha_inicio, fecha_fin, tipo_evento): Verifica horarios disponibles
3. crear_cita(nombre, email, fecha_hora, tipo_servicio, notas): Crea una cita

Cuando necesites usar una herramienta, responde en formato JSON:
{{"tool": "nombre_herramienta", "arguments": {{"param": "valor"}}}}

Conversación:
"""
        for msg in ollama_messages:
            if msg["role"] == "user":
                prompt_with_tools += f"\nUsuario: {msg['content']}\n"
            elif msg["role"] == "assistant":
                prompt_with_tools += f"\nAsistente: {msg['content']}\n"
        prompt_with_tools += "\nAsistente:"
        return prompt_with_tools

    async def _process_message_no_stream(
        self, prompt_with_tools: str
    ) -> str:
        """Procesa mensaje en modo no-streaming. Retorna la respuesta completa."""
        response = await ollama_client.generate(prompt_with_tools, stream=False)
        final_prompt = self._maybe_apply_tool_result(response, prompt_with_tools)
        if final_prompt != response:
            response = await ollama_client.generate(final_prompt, stream=False)
        return response

    def _maybe_apply_tool_result(self, response: str, prompt_with_tools: str) -> str:
        """Si la respuesta contiene llamada a herramienta, retorna el prompt para segunda pasada."""
        if "{" not in response or "tool" not in response.lower():
            return response
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                tool_call = json.loads(response[start_idx:end_idx])
                tool_name = tool_call.get("tool")
                tool_args = tool_call.get("arguments", {})
                if tool_name:
                    tool_result = self._call_tool(tool_name, tool_args)
                    return f"{prompt_with_tools} {response}\n\nResultado de {tool_name}: {tool_result}\n\nAsistente:"
        except json.JSONDecodeError:
            pass
        return response

    async def process_message(
        self,
        user_message: str,
        conversation_history: List[Message],
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Procesa un mensaje del usuario. Si stream=False retorna str; si stream=True retorna generador."""
        messages = [
            Message(role="system", content=self.system_prompt)
        ] + conversation_history + [
            Message(role="user", content=user_message)
        ]
        ollama_messages = self._format_messages_for_ollama(messages)
        prompt_with_tools = self._build_prompt_with_tools(ollama_messages)
        if stream:
            return self._process_message_stream(prompt_with_tools)
        return await self._process_message_no_stream(prompt_with_tools)

    async def _process_message_stream(self, prompt_with_tools: str) -> AsyncIterator[str]:
        """Generador async para process_message en modo streaming."""
        stream_gen = await ollama_client.generate(prompt_with_tools, stream=True)
        async for token in stream_gen:
            yield token

    async def process_with_rag(
        self,
        user_message: str,
        conversation_history: List[Message],
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Procesa mensaje con RAG. Si stream=False retorna str; si stream=True retorna generador."""
        if stream:
            return self.process_with_rag_stream(user_message, conversation_history)
        return await self._process_with_rag_no_stream(user_message, conversation_history)

    async def _process_with_rag_no_stream(
        self,
        user_message: str,
        conversation_history: List[Message],
    ) -> str:
        """Procesa mensaje con RAG en modo no-streaming. Retorna la respuesta completa."""
        needs_info_keywords = [
            "qué", "cuánto", "cómo", "información", "servicios", "precio", "cuesta",
            "dónde", "dirección", "ubicación", "ubicados", "llegar", "horario", "horarios",
            "cuánto cuesta", "precios", "agendar", "cita",
            "zona", "zonas", "encuentran", "encuentra", "situado", "situados"
        ]
        user_lower = user_message.lower()
        needs_info = any(kw in user_lower for kw in needs_info_keywords)
        context = ""
        if needs_info:
            info_result = buscar_informacion(user_message)
            context += f"\nInformación relevante:\n{info_result}\n"
        messages = [
            Message(role="system", content=self.system_prompt + context)
        ] + conversation_history + [
            Message(role="user", content=user_message)
        ]
        ollama_messages = self._format_messages_for_ollama(messages)
        return await ollama_client.chat(ollama_messages, stream=False)

    async def process_with_rag_stream(
        self,
        user_message: str,
        conversation_history: List[Message],
    ) -> AsyncIterator[str]:
        """Generador async para procesar mensaje con RAG en modo streaming."""
        needs_info_keywords = [
            "qué", "cuánto", "cómo", "información", "servicios", "precio", "cuesta",
            "dónde", "dirección", "ubicación", "ubicados", "llegar", "horario", "horarios",
            "cuánto cuesta", "precios", "agendar", "cita",
            "zona", "zonas", "encuentran", "encuentra", "situado", "situados"
        ]
        user_lower = user_message.lower()
        needs_info = any(kw in user_lower for kw in needs_info_keywords)
        context = ""
        if needs_info:
            info_result = buscar_informacion(user_message)
            context += f"\nInformación relevante:\n{info_result}\n"
        messages = [
            Message(role="system", content=self.system_prompt + context)
        ] + conversation_history + [
            Message(role="user", content=user_message)
        ]
        ollama_messages = self._format_messages_for_ollama(messages)
        stream_gen = await ollama_client.chat(ollama_messages, stream=True)
        async for token in stream_gen:
            yield token


agent_orchestrator = AgentOrchestrator()

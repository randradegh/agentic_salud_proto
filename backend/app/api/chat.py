"""Endpoints de chat."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import ChatRequest, ChatResponse, Message
from app.utils.session import session_manager
from app.agents.orchestrator import agent_orchestrator
import json
from datetime import datetime

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint de chat (modo no-streaming)."""
    # Obtener o crear sesión
    if request.session_id:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
    else:
        session = session_manager.create_session(request.metadata)
    
    # Añadir mensaje del usuario
    user_message = Message(
        role="user",
        content=request.message,
        metadata=request.metadata
    )
    session_manager.add_message(session.session_id, user_message)
    
    # Obtener historial de conversación
    conversation_history = session.messages[:-1]  # Excluir el mensaje actual
    
    # Procesar con el agente
    try:
        response_text = await agent_orchestrator.process_with_rag(
            user_message=request.message,
            conversation_history=conversation_history,
            stream=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando mensaje: {str(e)}")
    
    # Añadir respuesta del asistente
    assistant_message = Message(
        role="assistant",
        content=response_text,
        metadata={"tokens_used": len(response_text.split())}
    )
    session_manager.add_message(session.session_id, assistant_message)
    
    return ChatResponse(
        response=response_text,
        session_id=session.session_id,
        actions=[],
        metadata={"tokens_used": len(response_text.split())}
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Endpoint de chat con streaming (SSE)."""
    # Obtener o crear sesión
    if request.session_id:
        session = session_manager.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
    else:
        session = session_manager.create_session(request.metadata)
    
    # Añadir mensaje del usuario
    user_message = Message(
        role="user",
        content=request.message,
        metadata=request.metadata
    )
    session_manager.add_message(session.session_id, user_message)
    
    # Obtener historial de conversación
    conversation_history = session.messages[:-1]
    
    async def generate():
        """Generador de eventos SSE."""
        full_response = ""
        
        try:
            stream_gen = await agent_orchestrator.process_with_rag(
                user_message=request.message,
                conversation_history=conversation_history,
                stream=True
            )
            async for token in stream_gen:
                full_response += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            
            # Añadir respuesta completa a la sesión
            assistant_message = Message(
                role="assistant",
                content=full_response,
                metadata={"tokens_used": len(full_response.split())}
            )
            session_manager.add_message(session.session_id, assistant_message)
            
            yield f"data: {json.dumps({'type': 'done', 'session_id': session.session_id})}\n\n"
        
        except Exception as e:
            error_msg = str(e)
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

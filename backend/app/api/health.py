"""Health check endpoint."""
from fastapi import APIRouter
from app.models import HealthResponse
from app.integrations.ollama import ollama_client
from app.integrations.calcom import calcom_client
from app.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check del sistema."""
    # Verificar servicios
    ollama_ok = await ollama_client.health_check()
    calcom_ok = await calcom_client.health_check()
    
    # Verificar ChromaDB (básico)
    chroma_ok = "connected"
    try:
        from app.rag.retriever import rag_retriever
        _ = rag_retriever.collection
    except Exception:
        chroma_ok = "disconnected"
    
    services = {
        "llm": "connected" if ollama_ok else "disconnected",
        "chroma": chroma_ok,
        "calcom": "connected" if calcom_ok else "disconnected"
    }
    
    status = "healthy" if all(s == "connected" for s in services.values()) else "degraded"
    
    return HealthResponse(
        status=status,
        services=services,
        version=settings.api_version
    )

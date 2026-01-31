"""Aplicación principal FastAPI."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import chat, health, sessions
from app.rag.retriever import rag_retriever

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat.router, prefix=settings.api_prefix, tags=["chat"])
app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
app.include_router(sessions.router, prefix=settings.api_prefix, tags=["sessions"])


@app.on_event("startup")
async def startup_event():
    """Inicialización al arrancar la aplicación."""
    print("Inicializando aplicación...")
    
    # Cargar documentos en ChromaDB si no existen
    if rag_retriever.collection.count() == 0:
        print("Cargando documentos en la base de conocimiento...")
        count = rag_retriever.load_documents_from_directory(settings.knowledge_base_path)
        print(f"Cargados {count} chunks en ChromaDB")
    else:
        print(f"ChromaDB ya contiene {rag_retriever.collection.count()} documentos")


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "AI Booking Agent API",
        "version": settings.api_version,
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

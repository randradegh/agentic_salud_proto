"""Configuración de la aplicación."""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API
    api_title: str = "AI Booking Agent API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_temperature: float = 0.3
    ollama_top_p: float = 0.9
    ollama_max_tokens: int = 1024
    
    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    chroma_collection_name: str = "knowledge_base"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Cal.com
    calcom_api_key: Optional[str] = None
    calcom_api_url: str = "https://api.cal.com/v2"
    calcom_event_type_id: Optional[int] = Field(default=None, validation_alias="CALCOM_EVENT_TYPE_ID")
    
    # Session
    session_ttl_hours: int = 2
    session_storage: str = "memory"  # memory or redis
    
    # Redis (opcional)
    redis_url: Optional[str] = None
    
    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4321",  # Astro default
    ]
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Knowledge base
    knowledge_base_path: str = "./data/knowledge_base"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parsear calcom_event_type_id desde env si existe
        event_type_id = os.getenv("CALCOM_EVENT_TYPE_ID")
        if event_type_id:
            try:
                self.calcom_event_type_id = int(event_type_id)
            except (ValueError, TypeError):
                self.calcom_event_type_id = None


settings = Settings()

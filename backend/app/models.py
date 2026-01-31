"""Modelos de datos Pydantic."""
from datetime import datetime
from typing import Dict, List, Literal, Optional, Any
from uuid import uuid4
from pydantic import BaseModel, EmailStr, Field


class Message(BaseModel):
    """Modelo de mensaje en la conversación."""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class Session(BaseModel):
    """Modelo de sesión de conversación."""
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    state: Dict[str, Any] = Field(default_factory=dict)  # booking_intent, collected_info, etc.


class ChatRequest(BaseModel):
    """Request para el endpoint de chat."""
    message: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response del endpoint de chat."""
    response: str
    session_id: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class SessionCreateResponse(BaseModel):
    """Response para creación de sesión."""
    session_id: str
    created_at: datetime
    expires_at: datetime


class BookingRequest(BaseModel):
    """Modelo para solicitud de cita."""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    service_type: str
    preferred_datetime: datetime
    notes: Optional[str] = Field(None, max_length=500)
    timezone: str = "America/Mexico_City"


class KnowledgeDocument(BaseModel):
    """Modelo de documento en la base de conocimiento."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class HealthResponse(BaseModel):
    """Response del health check."""
    status: str
    services: Dict[str, str]
    version: str

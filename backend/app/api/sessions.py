"""Endpoints de sesiones."""
from fastapi import APIRouter
from datetime import datetime, timedelta
from app.models import SessionCreateResponse
from app.utils.session import session_manager
from app.config import settings

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session():
    """Crea una nueva sesión de conversación."""
    session = session_manager.create_session()
    expires_at = datetime.utcnow() + timedelta(hours=settings.session_ttl_hours)
    
    return SessionCreateResponse(
        session_id=session.session_id,
        created_at=session.created_at,
        expires_at=expires_at
    )

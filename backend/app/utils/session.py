"""Gestión de sesiones de conversación."""
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import uuid4

from app.config import settings
from app.models import Session, Message


class SessionManager:
    """Gestor de sesiones en memoria."""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._ttl = timedelta(hours=settings.session_ttl_hours)
    
    def create_session(self, metadata: Optional[Dict] = None) -> Session:
        """Crea una nueva sesión."""
        session_id = str(uuid4())
        expires_at = datetime.utcnow() + self._ttl
        
        session = Session(
            session_id=session_id,
            metadata=metadata or {},
            state={}
        )
        session.metadata["expires_at"] = expires_at.isoformat()
        
        self._sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Obtiene una sesión por ID."""
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        # Verificar expiración
        expires_at_str = session.metadata.get("expires_at")
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
            if datetime.utcnow() > expires_at:
                del self._sessions[session_id]
                return None
        
        return session
    
    def add_message(self, session_id: str, message: Message) -> bool:
        """Añade un mensaje a la sesión."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        return True
    
    def update_state(self, session_id: str, state_updates: Dict) -> bool:
        """Actualiza el estado de la sesión."""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.state.update(state_updates)
        session.updated_at = datetime.utcnow()
        return True
    
    def cleanup_expired(self):
        """Limpia sesiones expiradas."""
        now = datetime.utcnow()
        expired_ids = []
        
        for session_id, session in self._sessions.items():
            expires_at_str = session.metadata.get("expires_at")
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if now > expires_at:
                    expired_ids.append(session_id)
        
        for session_id in expired_ids:
            del self._sessions[session_id]


# Instancia global
session_manager = SessionManager()

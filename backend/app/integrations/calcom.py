"""Cliente para Cal.com API."""
import httpx
from datetime import datetime
from typing import List, Dict, Optional
from app.config import settings


class CalComClient:
    """Cliente para interactuar con Cal.com API."""
    
    def __init__(self):
        self.api_key = settings.calcom_api_key
        self.base_url = settings.calcom_api_url
        self.event_type_id = settings.calcom_event_type_id
    
    def _get_headers(self) -> Dict[str, str]:
        """Obtiene headers para requests."""
        if not self.api_key:
            raise ValueError("CALCOM_API_KEY no está configurada")
        
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_event_types(self) -> List[Dict]:
        """Obtiene lista de tipos de eventos disponibles."""
        if not self.api_key:
            return []
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/event-types",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json().get("event_types", [])
        except Exception as e:
            print(f"Error obteniendo event types: {e}")
            return []
    
    async def get_available_slots(
        self,
        event_type_id: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        timezone: str = "America/Mexico_City"
    ) -> List[Dict]:
        """Obtiene slots disponibles para un tipo de evento."""
        if not self.api_key:
            return []
        
        event_id = event_type_id or self.event_type_id
        if not event_id:
            return []
        
        try:
            params = {
                "eventTypeId": event_id,
                "timeZone": timezone
            }
            
            if start_time:
                params["startTime"] = start_time.isoformat()
            if end_time:
                params["endTime"] = end_time.isoformat()
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/slots/available",
                    headers=self._get_headers(),
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("slots", [])
        except Exception as e:
            print(f"Error obteniendo slots disponibles: {e}")
            return []
    
    async def create_booking(
        self,
        name: str,
        email: str,
        start: datetime,
        event_type_id: Optional[int] = None,
        notes: Optional[str] = None,
        timezone: str = "America/Mexico_City"
    ) -> Optional[Dict]:
        """Crea una reserva en Cal.com."""
        if not self.api_key:
            return None
        
        event_id = event_type_id or self.event_type_id
        if not event_id:
            return None
        
        try:
            payload = {
                "eventTypeId": event_id,
                "start": start.isoformat(),
                "responses": {
                    "name": name,
                    "email": email,
                },
                "timeZone": timezone
            }
            
            if notes:
                payload["responses"]["notes"] = notes
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/bookings",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error creando booking: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Verifica si Cal.com API está disponible."""
        if not self.api_key:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/event-types",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except Exception:
            return False


calcom_client = CalComClient()

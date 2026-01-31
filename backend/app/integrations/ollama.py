"""Cliente para Ollama."""
import httpx
from typing import List, Optional, AsyncIterator
import json

from app.config import settings


class OllamaClient:
    """Cliente para interactuar con Ollama."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
    
    async def _generate_stream(self, url: str, payload: dict) -> AsyncIterator[str]:
        """Generador async para generate en modo streaming."""
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Genera texto usando el modelo de Ollama."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "top_p": top_p or settings.ollama_top_p,
                "num_predict": max_tokens or settings.ollama_max_tokens,
            },
            "stream": stream
        }
        if stream:
            return self._generate_stream(url, payload)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")

    async def _chat_stream(self, url: str, payload: dict) -> AsyncIterator[str]:
        """Generador async para chat en modo streaming."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            # Ollama puede enviar content como string o null en algunos chunks
                            if "message" in data:
                                msg = data["message"]
                                content = msg.get("content") if isinstance(msg, dict) else None
                                if content is not None:
                                    yield content if isinstance(content, str) else str(content)
                            if data.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue

    async def chat(
        self,
        messages: List[dict],
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        stream: bool = False
    ) -> str | AsyncIterator[str]:
        """Chat con el modelo usando formato de mensajes."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "top_p": top_p or settings.ollama_top_p,
                "num_predict": settings.ollama_max_tokens,
            },
            "stream": stream
        }
        if stream:
            return self._chat_stream(url, payload)
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
    
    async def health_check(self) -> bool:
        """Verifica si Ollama está disponible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False


ollama_client = OllamaClient()

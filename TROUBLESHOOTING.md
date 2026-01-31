# Solución de problemas

## Inicio: orden de arranque

1. **Ollama:** `ollama serve` (dejar terminal abierta).
2. **Backend:** `cd backend && source venv/bin/activate && ./run.sh`.
3. **Frontend:** `cd frontend && npm run dev`.

Desde la **raíz del proyecto** (donde está `backend/` y `frontend/`). Si escribes solo `cd backend` sin estar en la raíz, falla: usa la ruta completa o `cd /ruta/al/proyecto/backend`.

---

## Puerto 8000 en uso (backend)

```bash
fuser -k 8000/tcp
cd backend && source venv/bin/activate && ./run.sh
```

---

## Puerto 11434 en uso (Ollama)

Normalmente significa que Ollama ya está corriendo. Comprueba con `ollama list`.  
Si quieres reiniciar Ollama: `fuser -k 11434/tcp` y luego `ollama serve`.

---

## El frontend no conecta con el backend

- Comprueba que el backend esté en marcha: `curl http://localhost:8000/api/health`.
- Si no responde, inicia el backend (ver arriba) y recarga la página del chat.

---

## La app no responde a los mensajes

- Ollama debe estar corriendo: `ollama serve` en una terminal.
- Modelo instalado: `ollama list` (si no está `llama3.1:8b`, ejecuta `ollama pull llama3.1:8b`).
- La primera respuesta puede tardar 30–60 segundos si el modelo se está cargando.

---

## Dependencias Python (FastAPI, etc.)

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

Usa **Python 3.11 o 3.12**. Si tienes solo 3.14 y fallan dependencias, instala 3.11: `sudo dnf install python3.11` (Fedora) y crea el venv con `python3.11 -m venv venv`.

---

## Base de conocimiento no se actualiza

Si cambias archivos en `backend/data/knowledge_base/` y el chatbot sigue con contenido viejo:

1. Detén el backend (Ctrl+C).
2. Borra ChromaDB: `rm -rf backend/chroma_db`.
3. Vuelve a iniciar el backend; al arrancar cargará de nuevo los documentos.

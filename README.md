# Consultorio Dental CDMX – Asistente virtual

Asistente conversacional con IA para un consultorio dental en la Ciudad de México: información sobre servicios, precios y agendamiento de citas. Backend con FastAPI, RAG (ChromaDB) y Ollama; frontend con Next.js.

## Requisitos

- Python 3.11 o 3.12
- Node.js 20+
- Ollama con modelo `llama3.1:8b`

## Inicio rápido

**Terminal 1 – Ollama**
```bash
ollama serve
```

**Terminal 2 – Backend**
```bash
cd backend && source venv/bin/activate && pip install -r requirements.txt && ./run.sh
```

**Terminal 3 – Frontend**
```bash
cd frontend && npm install && npm run dev
```

Abrir **http://localhost:3000**

## Estructura

- `backend/` – FastAPI, RAG (ChromaDB), agente con Ollama, Cal.com
- `frontend/` – Next.js, chat y UI
- `backend/data/knowledge_base/` – Base de conocimiento (Markdown) del consultorio dental

## Configuración

- Backend: copiar `backend/.env.example` a `backend/.env` (Ollama, ChromaDB, Cal.com).
- Frontend: opcional `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Documentación

- **PRD.md** – Especificación del producto.
- **TROUBLESHOOTING.md** – Problemas frecuentes (puertos, Ollama, conexión, etc.).
- **backend/data/knowledge_base/LEEME_BASE_CONOCIMIENTO.md** – Cómo editar la base de conocimiento.

## Licencia

Prototipo MVP.

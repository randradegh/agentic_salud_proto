# Consultorio Dental CDMX – Asistente virtual

Asistente conversacional con IA para un consultorio dental en la Ciudad de México: información sobre servicios, precios y agendamiento de citas.

**Stack:** Backend FastAPI + RAG (ChromaDB) + Ollama · Frontend Next.js + Tailwind CSS

---

## Requisitos

- **Python 3.11** o 3.12  
- **Node.js 20+**  
- **Ollama** con modelo `llama3.1:8b`

---

## Clonar y ejecutar

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
```

**Backend**
cd backend
python3.11 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Editar .env si necesitas (Cal.com, etc.)
./run.sh```bash

```

**Frontend** (en otra terminal)
```bash
cd frontend
npm install
cp .env.example .env.local   # Opcional: NEXT_PUBLIC_API_URL
npm run dev
```

**Ollama** (en otra terminal, antes o en paralelo)
```bash
ollama serve
ollama pull llama3.1:8b
```

Abrir **http://localhost:3000**

---

## Estructura del proyecto

```
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/             # Endpoints (chat, health, sessions)
│   │   ├── agents/          # Agente + herramientas
│   │   ├── integrations/    # Ollama, Cal.com
│   │   └── rag/             # ChromaDB + embeddings
│   ├── data/knowledge_base/ # Base de conocimiento (Markdown)
│   ├── .env.example
│   └── requirements.txt
├── frontend/                # Next.js
│   ├── src/app/
│   ├── src/components/
│   └── .env.example
├── docker-compose.yml
├── PRD.md
└── TROUBLESHOOTING.md
```

---

## Configuración

- **Backend:** `backend/.env` (copiar de `.env.example`). No subas `.env` a Git.  
- **Frontend:** opcional `frontend/.env.local` con `NEXT_PUBLIC_API_URL=http://localhost:8000`.  
- **Cal.com:** para agendar citas reales, configura `CALCOM_API_KEY` y `CALCOM_EVENT_TYPE_ID` en `backend/.env`.

---

## Documentación

- [PRD.md](PRD.md) – Especificación del producto.  
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) – Problemas frecuentes (puertos, Ollama, conexión).  
- [backend/data/knowledge_base/LEEME_BASE_CONOCIMIENTO.md](backend/data/knowledge_base/LEEME_BASE_CONOCIMIENTO.md) – Cómo editar la base de conocimiento.

---

## Subir a GitHub

```bash
git init
git add .
git commit -m "Initial commit: consultorio dental CDMX - asistente virtual"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

No subas archivos `.env` ni `venv/`, `node_modules/`, `chroma_db/` (ya están en `.gitignore`).

---

## Licencia

MIT. Ver [LICENSE](LICENSE).

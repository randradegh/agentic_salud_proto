# Product Requirements Document (PRD)
## AI Booking Agent con RAG y Cal.com

**Versión**: 1.0  
**Fecha**: Enero 2026  
**Tipo**: Prototipo MVP  
**Estado**: Planificación

---

## 1. Resumen Ejecutivo

### 1.1 Visión del Producto
Sistema de agente conversacional con IA que permite a clientes potenciales obtener información sobre servicios mediante RAG (Retrieval-Augmented Generation) y agendar citas directamente a través de Cal.com, todo en una interfaz de chat natural.

### 1.2 Objetivos del Prototipo
- Validar la viabilidad técnica de la arquitectura propuesta
- Demostrar capacidad conversacional del agente
- Probar integración RAG + Cal.com
- Establecer base para escalamiento futuro
- Minimizar costos usando tecnologías open-source

### 1.3 Fuera del Alcance (v1.0)
- Autenticación de usuarios
- Panel de administración
- Múltiples idiomas
- Integración con CRM
- Notificaciones por email/SMS
- Analytics avanzados
- Tests automatizados completos

---

## 2. Stack Tecnológico

### 2.1 Backend
- **Framework**: FastAPI 0.109+
- **Lenguaje**: Python 3.11+
- **LLM**: Llama 3.1 8B (via Ollama)
- **Framework AI**: LangChain 0.1+
- **Vector DB**: ChromaDB (persistente local)
- **Embeddings**: sentence-transformers (`all-MiniLM-L6-v2`)
- **Gestión de sesiones**: Redis (opcional) o en memoria
- **Validación**: Pydantic v2
- **HTTP Client**: httpx (async)

### 2.2 Frontend
- **Framework**: Next.js 14+ (App Router)
- Astro
- **Lenguaje**: TypeScript 5+
- **UI Library**: Tailwind CSS 3+
- **Componentes**: shadcn/ui
- **Estado**: React Hooks + Context API
- **HTTP Client**: fetch API nativo

### 2.3 Integraciones
- **Cal.com API**: v2 (REST)
- **Ollama**: API local (puerto 11434)

### 2.4 Infraestructura (Prototipo)
- **Desarrollo**: Local (Docker Compose)
- **Producción sugerida**: VPS (4GB RAM mínimo)

---

## 3. Arquitectura del Sistema

### 3.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Next.js App                                          │  │
│  │  ├─ Chat Interface Component                         │  │
│  │  ├─ Message List                                     │  │
│  │  ├─ Input Area                                       │  │
│  │  └─ Booking Confirmation Modal                       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                        │  │
│  │  ├─ POST /api/chat                                   │  │
│  │  ├─ GET  /api/health                                 │  │
│  │  └─ POST /api/sessions                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│  ┌──────────────────────┴───────────────────────────────┐  │
│  │  Agent Orchestrator                                   │  │
│  │  ├─ LangChain Agent (Llama 3.1)                      │  │
│  │  ├─ Conversation Memory                              │  │
│  │  └─ Tool Executor                                    │  │
│  └────────┬─────────────────────┬───────────────────────┘  │
│           │                     │                           │
│  ┌────────▼────────┐   ┌───────▼──────────┐               │
│  │  RAG System     │   │  Cal.com Client  │               │
│  │  ├─ ChromaDB    │   │  ├─ API Wrapper  │               │
│  │  ├─ Embeddings  │   │  └─ Booking Logic│               │
│  │  └─ Retriever   │   └──────────────────┘               │
│  └─────────────────┘                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
    ┌──────────────┐          ┌─────────────┐
    │   Ollama     │          │  Cal.com    │
    │   (Local)    │          │  (External) │
    └──────────────┘          └─────────────┘
```

### 3.2 Flujo de Datos

1. Usuario envía mensaje desde frontend
2. FastAPI recibe request en `/api/chat`
3. Agent Orchestrator procesa mensaje:
   - Determina intención usando LLM
   - Ejecuta herramientas necesarias (RAG o Cal.com)
   - Genera respuesta contextual
4. Response stream regresa al frontend
5. UI actualiza en tiempo real

---

## 4. Componentes Detallados

### 4.1 LLM: Llama 3.1 8B (Ollama)

**Justificación de Selección**:
- **Llama 3.1 8B**: Balance óptimo entre calidad y recursos
- Excelente para function calling
- Corre en hardware modesto (8-16GB RAM)
- Respuestas rápidas (~1-3 seg)
- Contexto de 128k tokens

**Alternativas consideradas**:
- ~~Llama 3.2 3B~~: Muy ligero pero calidad inferior para conversación compleja
- ~~Mistral 7B~~: Bueno pero Llama 3.1 tiene mejor español
- ~~Phi-3~~: Excelente pero menor contexto

**Configuración Ollama**:
```bash
# Instalación
curl -fsSL https://ollama.com/install.sh | sh

# Pull del modelo
ollama pull llama3.1:8b

# Configuración
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
```

**Parámetros LLM**:
- Temperature: 0.3 (respuestas consistentes)
- Top_p: 0.9
- Max tokens: 1024
- Stop sequences: ["Usuario:", "Human:"]

### 4.2 Sistema RAG

**Componente**: ChromaDB + sentence-transformers

**Base de Conocimiento**:
```
/data/knowledge_base/
├── servicios/
│   ├── consultoria.md
│   ├── desarrollo.md
│   └── soporte.md
├── precios/
│   └── tarifas.md
├── procesos/
│   └── onboarding.md
└── faq/
    └── preguntas_frecuentes.md
```

**Pipeline RAG**:
1. **Ingesta**: Documentos → Chunks (500 caracteres, 50 overlap)
2. **Embedding**: all-MiniLM-L6-v2 (384 dimensiones)
3. **Almacenamiento**: ChromaDB con metadata
4. **Retrieval**: Top-k=3, similarity threshold=0.7
5. **Reranking**: Opcional con cross-encoder

**Configuración ChromaDB**:
```python
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = client.create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)
```

### 4.3 Integración Cal.com

**API Version**: v2  
**Autenticación**: API Key  
**Base URL**: `https://api.cal.com/v2`

**Endpoints Utilizados**:

1. **GET /event-types**: Listar tipos de eventos
2. **GET /slots/available**: Obtener slots disponibles
3. **POST /bookings**: Crear reserva

**Estructura de Booking**:
```json
{
  "eventTypeId": 123456,
  "start": "2026-02-15T14:00:00Z",
  "responses": {
    "name": "Juan Pérez",
    "email": "juan@example.com",
    "notes": "Consulta sobre desarrollo web"
  },
  "timeZone": "America/Mexico_City"
}
```

**Manejo de Errores**:
- Slot no disponible → Ofrecer alternativas
- API down → Modo degradado (solo info)
- Rate limiting → Caché de disponibilidad (5 min)

### 4.4 Herramientas del Agente

**Tool 1: buscar_informacion**
```python
def buscar_informacion(query: str) -> str:
    """
    Busca información relevante en la base de conocimiento.
    
    Args:
        query: Pregunta o tema a buscar
    
    Returns:
        Información relevante encontrada
    """
```

**Tool 2: verificar_disponibilidad**
```python
def verificar_disponibilidad(
    fecha_inicio: str,  # ISO format
    fecha_fin: str,
    tipo_evento: str = "consultoria"
) -> List[Dict]:
    """
    Verifica slots disponibles en Cal.com.
    
    Returns:
        Lista de slots disponibles con formato
        [{"start": "...", "end": "..."}]
    """
```

**Tool 3: crear_cita**
```python
def crear_cita(
    nombre: str,
    email: str,
    fecha_hora: str,
    tipo_servicio: str,
    notas: Optional[str] = None
) -> Dict:
    """
    Crea una cita en Cal.com.
    
    Returns:
        Confirmación con detalles de la cita
    """
```

---

## 5. Experiencia de Usuario
- En español de México.

### 5.1 Flujos Principales

#### Flujo 1: Consulta de Información
```
Usuario: "¿Qué servicios ofrecen?"
Bot: [Consulta RAG] → Respuesta con lista de servicios
Usuario: "Cuéntame más sobre desarrollo web"
Bot: [Consulta RAG] → Detalles de desarrollo web
```

#### Flujo 2: Agendamiento Directo
```
Usuario: "Quiero agendar una cita"
Bot: "¿Para qué tipo de servicio?"
Usuario: "Consultoría técnica"
Bot: "¿Cuándo te gustaría? Tengo disponibilidad esta semana"
Usuario: "Viernes a las 3pm"
Bot: [Verifica disponibilidad] → "Viernes 2 feb a las 3pm está libre"
Bot: "¿Me confirmas tu nombre y email?"
Usuario: "Juan Pérez, juan@mail.com"
Bot: [Crea cita] → "✓ Cita confirmada. Te llegará email"
```

#### Flujo 3: Consulta + Agendamiento
```
Usuario: "¿Cuánto cuesta el desarrollo de una app móvil?"
Bot: [RAG] → Info de precios
Usuario: "Interesante, ¿podemos hablar?"
Bot: "Claro, ¿cuándo te viene bien?"
[Continúa flujo de agendamiento]
```

### 5.2 Interfaz de Usuario

**Chat Window**:
- Altura: 600px (adaptable)
- Mensajes con avatares (bot/usuario)
- Typing indicators
- Timestamps
- Scroll automático

**Input Area**:
- Textarea con auto-expand
- Botón enviar
- Placeholder contextual
- Límite: 500 caracteres

**Confirmación de Cita**:
- Modal con resumen
- Detalles: fecha, hora, tipo, participantes
- Botones: Confirmar / Editar / Cancelar

---

## 6. Endpoints de API

### 6.1 POST /api/chat

**Request**:
```json
{
  "message": "¿Qué servicios ofrecen?",
  "session_id": "uuid-v4",
  "metadata": {
    "user_timezone": "America/Mexico_City"
  }
}
```

**Response** (SSE Stream):
```
data: {"type": "token", "content": "Ofrecemos "}
data: {"type": "token", "content": "tres "}
data: {"type": "token", "content": "servicios..."}
data: {"type": "done"}
```

**Response** (JSON alternativo):
```json
{
  "response": "Ofrecemos tres servicios principales...",
  "session_id": "uuid-v4",
  "actions": [],
  "metadata": {
    "tokens_used": 234,
    "tools_called": ["buscar_informacion"]
  }
}
```

### 6.2 POST /api/sessions

Crea nueva sesión de conversación.

**Response**:
```json
{
  "session_id": "uuid-v4",
  "created_at": "2026-01-28T10:00:00Z",
  "expires_at": "2026-01-28T12:00:00Z"
}
```

### 6.3 GET /api/health

Health check del sistema.

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "llm": "connected",
    "chroma": "connected",
    "calcom": "connected"
  },
  "version": "1.0.0"
}
```

---

## 7. Modelos de Datos

### 7.1 Session
```python
class Session(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    messages: List[Message] = []
    created_at: datetime
    updated_at: datetime
    metadata: Dict = {}
    state: Dict = {}  # booking_intent, collected_info, etc.
```

### 7.2 Message
```python
class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime
    metadata: Optional[Dict] = None
```

### 7.3 BookingRequest
```python
class BookingRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    service_type: str
    preferred_datetime: datetime
    notes: Optional[str] = Field(max_length=500)
    timezone: str = "America/Mexico_City"
```

### 7.4 KnowledgeDocument
```python
class KnowledgeDocument(BaseModel):
    id: str
    content: str
    metadata: Dict[str, Any]  # source, category, tags
    embedding: Optional[List[float]] = None
```

---

## 8. Prompt Engineering

### 8.1 System Prompt Principal

```
Eres un asistente virtual especializado en ayudar a clientes potenciales.
Tus responsabilidades son:

1. INFORMACIÓN: Responder preguntas sobre servicios usando la información
   proporcionada en tu base de conocimiento.

2. AGENDAMIENTO: Ayudar a agendar citas verificando disponibilidad y
   recopilando información necesaria (nombre, email, preferencia de horario).

3. ESTILO DE CONVERSACIÓN:
   - Amigable y profesional
   - Conciso pero informativo
   - Proactivo: ofrece agendar después de explicar servicios
   - Empático: reconoce necesidades del cliente

4. FLUJO DE AGENDAMIENTO:
   - Pregunta tipo de servicio
   - Ofrece horarios disponibles
   - Recopila: nombre, email
   - Confirma todos los detalles
   - Crea la cita

5. LIMITACIONES:
   - Solo agenda servicios disponibles en el sistema
   - No modifica citas existentes (solo crea nuevas)
   - No procesa pagos

Usa las herramientas disponibles para buscar información y gestionar citas.
Siempre confirma detalles importantes antes de crear una cita.
```

### 8.2 Prompts de Herramientas

**buscar_informacion**:
```
Busca en la base de conocimiento información sobre: {query}
Retorna solo información relevante y verificable.
```

**verificar_disponibilidad**:
```
Verifica disponibilidad en Cal.com para:
- Rango: {fecha_inicio} a {fecha_fin}
- Servicio: {tipo_evento}

Retorna lista de horarios disponibles en formato legible.
```

---

## 9. Requisitos No Funcionales

### 9.1 Performance
- **Tiempo de respuesta**: < 3 segundos (p95)
- **Latencia streaming**: < 100ms por token
- **Concurrencia**: 10 usuarios simultáneos (prototipo)
- **Disponibilidad**: 95% uptime (dev)

### 9.2 Recursos de Hardware

**Desarrollo Local**:
- CPU: 4 cores
- RAM: 16GB (8GB mínimo)
- Disco: 20GB SSD
- GPU: Opcional (acelera inferencia)

**Producción Recomendada**:
- VPS: 4 vCPUs, 16GB RAM
- Disco: 50GB SSD
- Ancho de banda: 1TB/mes

### 9.3 Seguridad
- API keys en variables de entorno
- Rate limiting: 60 req/min por IP
- Validación de inputs (Pydantic)
- Sanitización de datos sensibles en logs
- CORS configurado para frontend específico

### 9.4 Monitoreo (Básico)
- Logs estructurados (JSON)
- Métricas: requests/min, latency, errores
- Health checks cada 30s
- Alertas: servicios caídos

---

## 10. Estructura del Proyecto

```
ai-booking-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app
│   │   ├── config.py               # Configuración
│   │   ├── models.py               # Pydantic models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py             # Chat endpoints
│   │   │   └── health.py           # Health check
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py     # Agent principal
│   │   │   └── tools.py            # Herramientas
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── retriever.py        # RAG logic
│   │   │   └── embeddings.py       # Embedding utils
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── calcom.py           # Cal.com client
│   │   │   └── ollama.py           # Ollama client
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── session.py          # Session management
│   ├── data/
│   │   └── knowledge_base/         # Documentos
│   ├── chroma_db/                  # Persistencia ChromaDB
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # Home page
│   │   │   ├── layout.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatWindow.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   └── ui/                 # shadcn components
│   │   ├── lib/
│   │   │   ├── api.ts              # API client
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
│
├── docker-compose.yml
├── README.md
└── PRD.md
```

---

## 11. Plan de Implementación

### Fase 1: Setup Inicial (2-3 días)
- [ ] Configurar entorno de desarrollo
- [ ] Instalar Ollama + Llama 3.1
- [ ] Setup FastAPI básico
- [ ] Setup Next.js básico
- [ ] Docker Compose para servicios

### Fase 2: Backend Core (4-5 días)
- [ ] Implementar modelos Pydantic
- [ ] Configurar ChromaDB
- [ ] Pipeline de ingesta de documentos
- [ ] Implementar RAG retriever
- [ ] Cliente Cal.com básico
- [ ] Endpoints de API

### Fase 3: Agente LangChain (3-4 días)
- [ ] Configurar LangChain con Ollama
- [ ] Implementar herramientas
- [ ] System prompt y templates
- [ ] Lógica de conversación
- [ ] Manejo de sesiones
- [ ] Testing manual

### Fase 4: Frontend (3-4 días)
- [ ] Componente ChatWindow
- [ ] MessageList con scroll
- [ ] Input area
- [ ] API client
- [ ] Estado de conversación
- [ ] Typing indicators
- [ ] Modal de confirmación

### Fase 5: Integración (2-3 días)
- [ ] Conectar frontend-backend
- [ ] Testing de flujos completos
- [ ] Manejo de errores
- [ ] Validaciones
- [ ] Logs y debugging

### Fase 6: Refinamiento (2-3 días)
- [ ] Optimización de prompts
- [ ] Ajuste de parámetros LLM
- [ ] Mejoras de UX
- [ ] Documentación
- [ ] README con instrucciones

**Total estimado: 16-22 días de desarrollo**

---

## 12. Criterios de Éxito

### Funcionales
✓ Agente responde preguntas sobre servicios usando RAG  
✓ Agente puede verificar disponibilidad en Cal.com  
✓ Agente puede crear citas con información completa  
✓ Conversación fluida en español  
✓ Recopila información necesaria antes de agendar  

### Técnicos
✓ Respuestas en < 3 segundos  
✓ Embedding + retrieval en < 500ms  
✓ Tasa de error < 5%  
✓ Precisión RAG > 80% (respuestas relevantes)  

### UX
✓ Chat intuitivo y responsive  
✓ Confirmación clara de citas  
✓ Manejo graceful de errores  

---

## 13. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Llama 3.1 8B insuficiente para conversación compleja | Media | Alto | Testing temprano; fallback a API externa |
| Cal.com API rate limits | Baja | Medio | Cache de disponibilidad; manejo de errores |
| Hardware insuficiente | Media | Alto | Optimizar modelo; usar quantización |
| RAG con precisión baja | Media | Alto | Mejorar chunking; aumentar documentos |
| Latencia alta en respuestas | Media | Medio | Streaming; optimizar retrieval |

---

## 14. Siguientes Pasos Post-Prototipo

### v1.1 (Mejoras Rápidas)
- Tests automatizados
- Panel admin básico
- Métricas de conversación
- Logs estructurados

### v2.0 (Producción)
- Autenticación de usuarios
- Multi-tenancy
- Email confirmaciones
- Integración CRM
- A/B testing de prompts

### v3.0 (Avanzado)
- Multi-idioma
- Voice interface
- Analytics dashboard
- API pública
- Modelo fine-tuned

---

## 15. Referencias y Recursos

### Documentación Técnica
- **Ollama**: https://ollama.com/docs
- **LangChain**: https://python.langchain.com/docs
- **ChromaDB**: https://docs.trychroma.com/
- **Cal.com API**: https://cal.com/docs/api-reference
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs

### Modelos
- **Llama 3.1**: https://ollama.com/library/llama3.1
- **sentence-transformers**: https://www.sbert.net/

### UI Components
- **shadcn/ui**: https://ui.shadcn.com/
- **Tailwind**: https://tailwindcss.com/docs

---

## 16. Glosario

- **RAG**: Retrieval-Augmented Generation
- **LLM**: Large Language Model
- **SSE**: Server-Sent Events
- **Tool/Function Calling**: Capacidad del LLM de invocar funciones
- **Embedding**: Representación vectorial de texto
- **ChromaDB**: Base de datos vectorial
- **Cal.com**: Plataforma de scheduling open-source
- **Ollama**: Runtime para ejecutar LLMs localmente

---

**Aprobaciones**:
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Stakeholders

**Última actualización**: Enero 28, 2026

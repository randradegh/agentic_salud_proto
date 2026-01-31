# Base de conocimiento – Consultorio dental (CDMX)

Esta carpeta contiene los documentos que alimentan las respuestas del asistente virtual del consultorio dental en la Ciudad de México.

## Estructura

- **servicios/** – Servicios dentales (limpieza, tratamientos restauradores, ortodoncia y estética)
- **precios/** – Tarifas aproximadas en pesos mexicanos
- **procesos/** – Primera visita y proceso de atención
- **faq/** – Preguntas frecuentes

## Cómo se usa

El backend (FastAPI) carga estos archivos en ChromaDB al iniciar. El asistente busca en ellos para responder preguntas sobre servicios, precios y citas.

## Después de cambiar los documentos

Si **ya habías arrancado el backend antes** y cambiaste el contenido de los archivos, ChromaDB sigue usando la versión anterior hasta que la colección se vuelva a crear.

Para cargar la nueva base de conocimiento:

1. Detén el backend (Ctrl+C en la terminal donde corre).
2. Borra la carpeta de ChromaDB (desde la raíz del proyecto):
   ```bash
   rm -rf backend/chroma_db
   ```
3. Vuelve a iniciar el backend:
   ```bash
   cd backend && source venv/bin/activate && ./run.sh
   ```

En el arranque verás algo como "Cargando documentos en la base de conocimiento..." y el número de chunks cargados. A partir de ahí el asistente usará el contenido actualizado.

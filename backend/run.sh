#!/bin/bash

# Script para ejecutar el backend

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Verificar que uvicorn esté instalado
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn no está instalado. Ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Ejecutar el servidor
echo "Iniciando servidor FastAPI en http://0.0.0.0:8000"
echo "Documentación disponible en http://localhost:8000/docs"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

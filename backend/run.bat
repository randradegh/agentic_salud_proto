@echo off
REM Script para ejecutar el backend en Windows

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Verificar que uvicorn esté instalado
where uvicorn >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: uvicorn no está instalado. Ejecuta: pip install -r requirements.txt
    exit /b 1
)

REM Ejecutar el servidor
echo Iniciando servidor FastAPI en http://0.0.0.0:8000
echo Documentación disponible en http://localhost:8000/docs
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

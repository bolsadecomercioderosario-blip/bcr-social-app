@echo off
TITLE BCR Social App
echo ============================================
echo   INICIANDO GENERADOR DE REDES BCR
echo ============================================
echo.
echo 1. Abriendo la interfaz en el navegador...
start "" "%~dp0frontend\index.html"

echo 2. Encendiendo el servidor de procesamiento...
echo (Este panel debe quedar abierto mientras uses la app)
echo.
cd /d "%~dp0backend"
python -m uvicorn app:app --host 127.0.0.1 --port 8002
pause

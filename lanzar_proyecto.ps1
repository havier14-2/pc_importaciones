# ==========================================
# Script Maestro de Arranque - Retail FX
# ==========================================

Write-Host "1. Inicializando base de datos y tablas en MySQL..." -ForegroundColor Cyan
python etl/setup_mysql.py

Write-Host "2. Ejecutando Pipeline ETL (Extracción y Cálculos)..." -ForegroundColor Cyan
python etl/etl_riesgo_fx.py

Write-Host "Entrenando modelos de Machine Learning..." -ForegroundColor Cyan
python models/train.py

Write-Host "3. Iniciando servidor Backend (FastAPI) en segundo plano..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn api.main:app --reload"

Write-Host "4. Lanzando Interfaz Gráfica (Dashboard)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python dashboards/app.py"

Write-Host "¡Todo el ecosistema está en marcha!" -ForegroundColor Green
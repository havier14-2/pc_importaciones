@echo off
echo ===================================================
echo Iniciando Pipeline ETL Automatizado - Retail FX
echo Fecha y Hora: %date% %time%
echo ===================================================

:: Cambia dinamicamente a la carpeta donde esta guardado este archivo .bat
:: El parametro /d asegura que tambien cambie de disco (ej: de C: a D:) si es necesario
cd /d "%~dp0"

:: Ejecuta el motor de datos usando la ruta relativa interna
python etl/etl_riesgo_fx.py

echo ===================================================
echo Proceso Finalizado.
echo ===================================================
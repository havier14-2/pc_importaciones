@echo off
SETLOCAL EnableDelayedExpansion

echo =======================================================================
echo     RETAIL TECH FX - PIPELINE DE ENTORNO SEGURO Y COMPILACION AUTOMATICA
echo     Fecha: %date%  Hora: %time%
echo =======================================================================

:: 1. Posicionamiento de ruta portátil
cd /d "%~dp0"
echo [*] Ruta de trabajo establecida en: %cd%

:: 2. Verificación e Instalación de Dependencias Obligatorias
echo [*] Fase 1: Validando dependencias del sistema (requirements.txt)...
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [CRITICO] Error al instalar las librerías de Python. Verifica tu conexión.
    pause
    exit /b %errorlevel%
)
echo [OK] Dependencias alineadas con éxito.

:: 3. Ejecución de Pruebas Unitarias y Validaciones (Evidencia de CI)
echo [*] Fase 2: Ejecutando Suite de Pruebas Unitarias Automatizadas (CI)...
python -m unittest discover -s tests -p "test_*.py"
if %errorlevel% neq 0 (
    echo [CRITICO] Las pruebas unitarias o de API fallaron. Pipeline abortado para proteger el DW.
    pause
    exit /b %errorlevel%
)
echo [OK] Todas las pruebas unitarias pasaron exitosamente.

:: 4. Ejecución del Proceso ETL
echo [*] Fase 3: Ejecutando Pipeline ETL (Extracción API/MySQL/CSV)...
python etl/etl_riesgo_fx.py
if %errorlevel% neq 0 (
    echo [ERROR] Ocurrió un fallo crítico dentro del procesamiento ETL.
    pause
    exit /b %errorlevel%
)

:: 5. Entrenamiento del Portafolio de Modelos de Machine Learning
echo [*] Fase 4: Re-entrenando modelos de Machine Learning (Regresión del Costo)...
python models/train.py
if %errorlevel% neq 0 (
    echo [ERROR] El re-entrenamiento de los modelos de Machine Learning falló.
    pause
    exit /b %errorlevel%
)

echo =======================================================================
echo     [EXITO] Ecosistema Actualizado y Validado de Extremo a Extremo
echo     Los datos del DW están frescos y los modelos (.pkl) optimizados.
echo =======================================================================
pause
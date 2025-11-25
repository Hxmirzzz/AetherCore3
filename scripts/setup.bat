@echo off
echo =========================================
echo  AetherCore3 - Setup
echo =========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv venv

echo [2/4] Activando entorno virtual...
call venv\Scripts\activate

echo [3/4] Instalando dependencias...
pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"

echo [4/4] Creando archivo .env...
if not exist .env (
    copy .env.example .env
    echo Por favor edita el archivo .env con tus rutas
)

echo.
echo =========================================
echo  Setup completado!
echo =========================================
echo.
echo Proximos pasos:
echo 1. Edita el archivo .env con tus rutas
echo 2. Activa el entorno: venv\Scripts\activate
echo 3. Ejecuta: python -m src.presentation.console.console_existencia --help
echo.
pause
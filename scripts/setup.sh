#!/bin/bash
set -e

echo "========================================="
echo " AetherCore3 - Setup"
echo "========================================="
echo

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    exit 1
fi

echo "[1/4] Creando entorno virtual..."
python3 -m venv venv

echo "[2/4] Activando entorno virtual..."
source venv/bin/activate

echo "[3/4] Instalando dependencias..."
pip install --upgrade pip
pip install -e .
pip install -e ".[dev]"

echo "[4/4] Creando archivo .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Por favor edita el archivo .env con tus rutas"
fi

echo
echo "========================================="
echo " Setup completado!"
echo "========================================="
echo
echo "Próximos pasos:"
echo "1. Edita el archivo .env con tus rutas"
echo "2. Activa el entorno: source venv/bin/activate"
echo "3. Ejecuta: python -m src.presentation.console.console_existencia --help"
echo
#!/bin/bash
# Script para activar el entorno y correr la app en Mac

# Obtener el directorio donde está el script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activar el entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: No se encontró la carpeta venv"
    exit 1
fi

# Correr la aplicación
echo "Iniciando servidor de Flask..."
python3 interfaz/app.py

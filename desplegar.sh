#!/bin/bash
# Script de despliegue para Mac (Equivalente al .ps1 de Windows)

REMOTE_SERVER="root@165.22.152.56"
REMOTE_PATH="/var/www/cophi_app/Plantillas" 
SERVICE_NAME="cophi"
ZIP_FILE="deploy_full.zip"

# Colores para la terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}=== Iniciando Despliegue COMPLETO desde Mac ===${NC}"

# Limpieza previa
rm -f "$ZIP_FILE"
rm -f "deploy_package.zip"

echo -e "${YELLOW}1. Empaquetando TODO el código...${NC}"

# Lista de archivos a empaquetar
FILES_TO_ZIP=(
    "interfaz"
    "Cotizacion"
    "Orden de trabajo"
    "Visita_tecnica"
    "Consumos_agua"
    "boletas"
    "inventario"
    "tarificador"
    "Cuestionario_permiso_descargas"
    "app.py" 
    "requirements.txt"
    "estilos.css"
    "paginacion.js"
)

# Comprobar qué rutas existen y empaquetar
EXISTING_FILES=""
for file in "${FILES_TO_ZIP[@]}"; do
    if [ -e "$file" ]; then
        EXISTING_FILES="$EXISTING_FILES $file"
    fi
done

if [ -z "$EXISTING_FILES" ]; then
    echo -e "${RED}Error: No hay archivos para subir${NC}"
    exit 1
fi

zip -r "$ZIP_FILE" $EXISTING_FILES > /dev/null

if [ -f "$ZIP_FILE" ]; then
    SIZE=$(du -h "$ZIP_FILE" | cut -f1)
    echo -e "${GREEN}   -> Paquete creado ($SIZE)${NC}"
else
    echo -e "${RED}   -> Error al crear zip${NC}"
    exit 1
fi

echo -e "${YELLOW}2. Subiendo al servidor...${NC}"
scp "$ZIP_FILE" "${REMOTE_SERVER}:/tmp/$ZIP_FILE"

if [ $? -ne 0 ]; then
    echo -e "${RED}   -> Error al subir. Revisa tu conexión o llaves SSH.${NC}"
    exit 1
fi
echo -e "${GREEN}   -> Subida completada${NC}"

echo -e "${YELLOW}3. Desplegando y Reiniciando...${NC}"

REMOTE_COMMANDS="unzip -o /tmp/$ZIP_FILE -d $REMOTE_PATH; rm /tmp/$ZIP_FILE; chown -R www-data:www-data $REMOTE_PATH; systemctl restart $SERVICE_NAME; echo 'Servicio reiniciado'"

ssh "$REMOTE_SERVER" "$REMOTE_COMMANDS"

rm -f "$ZIP_FILE"
echo -e "${GREEN}=== LISTO! Tu aplicación debería estar 100% sincronizada ===${NC}"

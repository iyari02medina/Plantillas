# Script de despliegue COMPLETO - Sube TODO el código (sin assets pesados)
# Soluciona el problema de carpetas faltantes y la conexión lenta

$REMOTE_SERVER = "root@165.22.152.56"
# La ruta real donde corre la app
$REMOTE_PATH = "/var/www/cophi_app/Plantillas" 
$SERVICE_NAME = "cophi"
$ZIP_FILE = "deploy_full.zip"

Write-Host "=== Iniciando Despliegue COMPLETO ===" -ForegroundColor Cyan

# Limpieza previa
if (Test-Path $ZIP_FILE) { Remove-Item $ZIP_FILE }
if (Test-Path "deploy_package.zip") { Remove-Item "deploy_package.zip" }

Write-Host "1. Empaquetando TODO el código..." -ForegroundColor Yellow

# Incluimos TODAS las carpetas de lógica
# Excluimos 'img' root para que la subida sea rápida (evitar timeout)
$filesToZip = @(
    "interfaz",
    "Cotizacion",
    "Orden de trabajo",
    "Visita_tecnica",
    "Consumos_agua",
    "boletas",
    "inventario",
    "tarificador",
    "Cuestionario_permiso_descargas",
    "app.py", 
    "requirements.txt",
    "estilos.css",
    "paginacion.js"
)

# Filtrar solo los que existen
$validPaths = $filesToZip | Where-Object { Test-Path $_ }

if ($validPaths.Count -eq 0) {
    Write-Host "Error: No hay archivos" -ForegroundColor Red
    exit
}

# Comprimir
Compress-Archive -Path $validPaths -DestinationPath $ZIP_FILE -CompressionLevel Optimal -Force

if (Test-Path $ZIP_FILE) {
    $size = "{0:N2}" -f ((Get-Item $ZIP_FILE).Length / 1KB)
    Write-Host "   -> Paquete creado ($size KB)" -ForegroundColor Green
}
else {
    Write-Host "   -> Error al crear zip" -ForegroundColor Red
    exit
}

Write-Host "2. Subiendo al servidor..." -ForegroundColor Yellow
scp $ZIP_FILE "${REMOTE_SERVER}:/tmp/$ZIP_FILE"

if ($LASTEXITCODE -ne 0) {
    Write-Host "   -> Error al subir. Posible problema de conexión." -ForegroundColor Red
    exit
}
Write-Host "   -> Subida completada" -ForegroundColor Green

Write-Host "3. Desplegando y Reiniciando..." -ForegroundColor Yellow

# Comando robusto en una línea
$remoteCommands = "command -v unzip >/dev/null 2>&1 || apt-get install -y unzip; unzip -o /tmp/$ZIP_FILE -d $REMOTE_PATH; rm /tmp/$ZIP_FILE; chown -R www-data:www-data $REMOTE_PATH; systemctl restart $SERVICE_NAME; echo 'Servicio reiniciado'"

ssh $REMOTE_SERVER $remoteCommands

Remove-Item $ZIP_FILE
Write-Host "=== LISTO! Tu aplicación debería estar 100% sincronizada ===" -ForegroundColor Green

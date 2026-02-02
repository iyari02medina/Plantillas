# Guía de Despliegue - Cophi App

## 🚀 Cómo actualizar el servidor

Para subir tus cambios (código, plantillas HTML, CSS, lógica de Python) al servidor de DigitalOcean, solo necesitas ejecutar un comando en PowerShell:

```powershell
.\desplegar.ps1
```

### 📋 ¿Qué hace este script?
1.  **Empaqueta** todo tu código local en un archivo ZIP.
2.  **Sube** el archivo al servidor de forma segura.
3.  **Descomprime** y actualiza los archivos en la carpeta correcta (`/var/www/cophi_app/Plantillas`).
4.  **Reinicia** el servicio automáticamente para aplicar los cambios.

### ⚠️ Importante: ¿Qué se sube y qué NO?
El script está optimizado para ser rápido y evitar cortes de conexión.

-   **✅ SE SUBE:**
    -   Carpeta `interfaz` (HTML, CSS, JS, App).
    -   Carpetas de datos: `Cotizacion`, `Orden de trabajo`, `Visita_tecnica`, `Consumos_agua`, `boletas`, `inventario`, `tarificador`.
    -   Archivos raíz: `app.py`, `requirements.txt`, `estilos.css`, `paginacion.js`.

-   **❌ NO SE SUBE (Por defecto):**
    -   La carpeta **`img`** que está en la raíz (porque suele pesar mucho y bloquea la conexión).
    -   Si agregas imágenes nuevas pesadas en esa carpeta, avísame para subirlas manualmente o ajustar el script.
    -   Las imágenes dentro de `interfaz/static/` **SÍ** se suben.

### 🛠 Solución de Problemas
-   **No veo los cambios:** Presiona `Ctrl + F5` en tu navegador para limpiar la caché.
-   **Error de conexión:** Si el script falla al subir, espera 1 minuto y vuelve a intentarlo.

# Sistema de Gestión COPHI

Este repositorio contiene la aplicación de gestión para COPHI, incluyendo módulos de Cotizaciones, Órdenes de Trabajo, Análisis de Laboratorio (Tarificador), y más.

## 🛠 Arquitectura de Datos Robusta (CSV)

La aplicación utiliza archivos CSV como base de datos. Se ha implementado una capa de lectura flexible para permitir modificaciones manuales en los archivos sin romper el sistema.

### 1. Sistema de Alias y Mapeo Flexible
El sistema es capaz de reconocer columnas aunque cambien de nombre, gracias al diccionario `FIELD_MAPPING` en `app.py`. 

*   **¿Cómo funciona?**: Si renombras una columna, el programa buscará automáticamente entre una lista de alias conocidos.
*   **Ejemplos de Mapeo**:
    *   `folio_cot` ⮕ reconoce: `folio`, `Folio`, `ID`.
    *   `nombre_cliente` ⮕ reconoce: `cliente`, `Cliente`, `Nombre Cliente`, `nombre_empresa`.
    *   `nombre_item` ⮕ reconoce: `item`, `Nombre`, `Nombre del Concepto`.
    *   `precio_unitario_item` ⮕ reconoce: `precio`, `Precio U`, `Precio Unitario`.

### 2. Reglas para Modificar CSVs (Manual)
Si editas los archivos en Excel o editores de texto, ten en cuenta:

*   **Espacios en blanco**: El sistema limpia automáticamente espacios al inicio/final de encabezados y celdas.
*   **Mayúsculas/Minúsculas**: El sistema no distingue entre `NOMBRE`, `nombre` o `Nombre`.
*   **Nuevas Columnas**: Puedes agregar columnas nuevas para tu propio uso; el sistema simplemente las ignorará si no las necesita, sin lanzar errores.
*   **Codificación**: Usa siempre **UTF-8 con BOM** para preservar acentos y la "ñ".
*   **Columnas "Fantasma"**: Si DictReader detecta más columnas de las que hay en el encabezado, el sistema filtra esos valores nulos para evitar errores al procesar JSON/Templates.

### 3. Recomendaciones Técnicas
*   **No eliminar columnas críticas**: Aunque el mapeo es flexible, si eliminas una columna esencial (como el ID o el Folio) y no hay un alias que lo reemplace, algunas funciones podrían fallar.
*   **Evitar celdas combinadas**: El formato CSV no soporta celdas combinadas de Excel.

---

## 🚀 Despliegue
Consulta [README_DESPLIEGUE.md](README_DESPLIEGUE.md) para saber cómo subir tus cambios al servidor de DigitalOcean usando:
```powershell
.\desplegar.ps1
```

## 🎨 Interfaz y Diseño
Consulta [README_UI.md](README_UI.md) para detalles sobre los componentes visuales de FlyonUI y TailwindCSS.

## 📁 Estructura de Datos
*   `/Cotizacion`: Datos de cotizaciones genéricas.
*   `/inventario`: Productos, servicios y directorio de empresas.
*   `/Orden de trabajo`: Órdenes de desazolve y trampas de grasa.
*   `/Consumos_agua`: Registro de lecturas y rangos de precios.
*   `/tarificador`: Parámetros de laboratorio y cálculos de contaminantes.

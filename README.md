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
Consulta [README_UI.md](README_UI.md) para detalles sobre los componentes visuales.
*   **Regla de Oro:** Todos los contenedores de títulos (`div` con `h1`) deben usar la clase `mb-6` (ejemplo en `cotizaciones.html`).

## 📁 Estructura de Datos
*   `/Cotizacion`: Datos de cotizaciones genéricas.
*   `/inventario`: Productos, servicios y directorio de empresas.
*   `/Orden de trabajo`: Órdenes de desazolve y trampas de grasa.
*   `/Consumos_agua`: Registro de lecturas y rangos de precios.
*   `/tarificador`: Parámetros de laboratorio y cálculos de contaminantes.

## 📝 Prompts para Componentes FlyonUI

### File Upload
Usa este prompt para generar el componente de carga de archivos:

> I'm using the FlyonUI Tailwind CSS component library in my project. Please integrate the following component into my project:
>
> Here are the code snippets for the block component:
>
> ```html
> <div
>   data-file-upload='{
>     "url": "/upload",
>     "extensions": {
>       "csv": {
>         "icon": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\"><path d=\"M4 22h14a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v4\"/><path d=\"M14 2v4a2 2 0 0 0 2 2h4\"/><path d=\"m5 12-3 3 3 3\"/><path d=\"m9 18 3-3-3-3\"/></svg>",
>         "class": "shrink-0 size-5"
>       }
>     }
>   }' >
> 
>   <div class="bg-base-200/60 rounded-box flex flex-col justify-center border-2 border-base-content/20 border-dashed"  >
>     <div class="text-center cursor-pointer p-12" data-file-upload-trigger="">
>       <p class="text-base-content/50 mb-3 text-sm">Choose a file with a size up to 2MB.</p>
>       <button class="btn btn-soft btn-sm btn-primary text-nowrap"> <span class="icon-[tabler--file-upload] size-4.5 shrink-0"></span> Drag & Drop to Upload </button>
>       <p class="text-base-content/50 my-2 text-xs">or</p>
>       <p class="link link-animated link-primary font-medium text-sm">Browse</p>
>     </div>
>     <div class="mx-12 mb-8 space-y-2 empty:m-0" data-file-upload-previews=""></div>
>   </div>
> </div>
> ```

### Filtros y Buscadores
Usa este prompt para generar la barra de búsqueda y filtros estándar:

> I'm using the FlyonUI Tailwind CSS component library in my project. Please create a search filter bar for my project.
>
> It should follow this structure:
> 1. A `card` with `bg-base-100 border border-base-content/10 shadow-sm mb-6`.
> 2. Inside `card-body p-6`, a `form` with a grid layout.
> 3. Use `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6` for the filters.
> 4. Add a search button with `btn btn-primary h-10 min-h-0 px-6` and a reset button with `btn btn-soft btn-secondary h-10 min-h-0 btn-square`.
>
> Here is a reference example of the code:
>
> ```html
> <div class="card bg-base-100 border border-base-content/10 shadow-sm mb-6">
>     <div class="card-body p-6">
>         <form method="GET" action="#" class="space-y-6 w-full">
>             <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
>                 <div class="form-control space-y-2">
>                     <label class="label font-bold text-xs uppercase text-base-content/60 tracking-widest">Búsqueda</label>
>                     <input type="text" name="q" class="input input-bordered w-full h-10" placeholder="...">
>                 </div>
>             </div>
>             <div class="flex gap-3 pt-2">
>                 <button type="submit" class="btn btn-primary h-10 min-h-0 px-6 flex items-center gap-2">
>                     <span class="icon-[tabler--search] size-5"></span>
>                     <span>Buscar</span>
>                 </button>
>                 <a href="#" class="btn btn-soft btn-secondary h-10 min-h-0 btn-square">
>                     <span class="icon-[tabler--filter-x] size-5"></span>
>                 </a>
>             </div>
>         </form>
>     </div>
> </div>
> ```

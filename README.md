# Sistema de Gestión COPHI

Este repositorio contiene la aplicación de gestión para COPHI, incluyendo módulos de Cotizaciones, Órdenes de Trabajo, Análisis de Laboratorio (Tarificador), y más.

---

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

## 📁 Estructura de Datos
*   `/Cotizacion`: Datos de cotizaciones genéricas.
*   `/inventario`: Productos, servicios y directorio de empresas.
*   `/Orden de trabajo`: Órdenes de desazolve y trampas de grasa.
*   `/Consumos_agua`: Registro de lecturas y rangos de precios.
*   `/tarificador`: Parámetros de laboratorio y cálculos de contaminantes.

---

## 🎨 Guía de Interfaz y Diseño (FlyonUI)

Este proyecto utiliza el framework **FlyonUI** con **Tailwind CSS**. A continuación se detallan las reglas de diseño, patrones y componentes estándar.

### 📚 Documentación Oficial
Para buscar nuevos componentes, botones, tablas o layouts, consulta siempre la web oficial:
👉 **[flyonui.com](https://flyonui.com/)**

### 🧩 Patrones de Implementación (Recetas)

#### A. Buscador y Filtros (En Página)
Para añadir una barra de búsqueda a una nueva página, usa esta estructura dentro de un `card`.

**Estructura HTML:**
```html
<div class="card bg-base-100 border border-base-content/10 shadow-sm mb-6">
    <div class="card-body p-6">
        <form method="GET" action="{{ url_for('TU_RUTA') }}" class="space-y-6 w-full">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Campo de Texto -->
                <div class="form-control md:col-span-2">
                    <label class="label-text mb-2 block uppercase font-bold text-base-content/50 text-xs">Búsqueda</label>
                    <input type="text" name="q_search" class="input input-bordered w-full h-10" 
                           placeholder="..." value="{{ request.args.get('q_search', '') }}">
                </div>
                <!-- Filtro Select (Opcional) -->
                <div class="form-control">
                     <!-- ... select similar ... -->
                </div>
            </div>
            <!-- Botones de Acción -->
            <div class="flex gap-3 pt-2">
                <button type="submit" class="btn btn-primary h-10 min-h-0 px-6 flex items-center gap-2">
                    <span class="icon-[tabler--search] size-5"></span>
                    <span>Buscar</span>
                </button>
                <!-- Botón Limpiar Filtros -->
                <a href="{{ url_for('TU_RUTA') }}" class="btn btn-soft btn-secondary h-10 min-h-0 btn-square" title="Limpiar">
                    <span class="icon-[tabler--filter-x] size-5"></span>
                </a>
            </div>
        </form>
    </div>
</div>
```

#### B. Tabla de Datos Estándar
Las tablas deben tener ciertas características obligatorias:
1.  **Tarjeta Separada:** Los filtros de búsqueda NUNCA deben ir dentro de la misma tarjeta que la tabla. Deben estar en una tarjeta superior con `mb-6`.
2.  Estar dentro de un `card` con `overflow-hidden`.
3.  Usar `table-lg` para buen espaciado.
4.  **Menú de Acciones:** La primera columna siempre debe ser acciones (Ver/Editar/Borrar).
5.  **Estado Vacío:** Usar `{% else %}` en el bucle `for` para mostrar un mensaje amigable cuando no hay datos.
6.  **Responsividad:** Envolver siempre en `<div class="overflow-x-auto">`.

**Snippet de Tabla:**
```html
<div class="card bg-base-100 border border-base-content/10 shadow-sm overflow-hidden">
    <!-- Header Opcional -->
    <div class="card-header bg-base-200/30 p-4 border-b border-base-content/10">
        <h3 class="font-bold text-lg flex items-center gap-2 text-primary">
            <span class="icon-[tabler--list-details] size-5"></span> Título Tabla
        </h3>
    </div>
    
    <div class="overflow-x-auto">
        <table class="table table-lg">
            <thead class="bg-base-200/30">
                <tr>
                    <th>Acciones</th> <!-- Siempre primero -->
                    <th>Nombre Columna</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr class="hover:bg-base-200/30">
                    <td>
                        <!-- Dropdown de Acciones (Ver tabla_catalogo.html para ejemplo completo) -->
                    </td>
                    <td>{{ item.valor }}</td>
                </tr>
                {% else %}
                <!-- ESTADO VACÍO (Importante) -->
                <tr>
                    <td colspan="10" class="text-center py-20">
                        <span class="icon-[tabler--package-off] size-16 text-base-content/20"></span>
                        <p>No se encontraron registros.</p>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    <!-- Aquí va la paginación si aplica -->
</div>
```

#### C. Buscador Global (Command Palette)
El buscador que aparece con `Ctrl+K` o en el header es **estático** en JavaScript.
*   **Archivo:** `interfaz/templates/base_flyonui.html`
*   **Ubicación:** Al final del archivo, busca la constante `APP_ROUTES`.
*   **Cómo agregar página:** Agrega un objeto al array:
```javascript
{
    title: 'Nueva Página',
    url: "{{ url_for('nueva_ruta') }}",
}
```

#### D. Estándares de Grillas y Formularios (Responsive)
El layout de todos los formularios debe seguir estas reglas de grilla estrictas para asegurar que se vean bien en móvil y escritorio.

##### 1. Grilla Maestra
El contenedor principal de cualquier grupo de inputs debe ser una grilla que empieza en **1 columna** y crece.
*   **Clase Base:** `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6` (ajusta `lg:` según necesites 3, 4 o 5 columnas).
*   **Ejemplo (`ordenes.html`):**
    ```html
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <!-- Los inputs van aquí -->
        <div class="form-control lg:col-span-2">...</div> <!-- Input ancho -->
    </div>
    ```

##### 2. Inputs Compuestos (Split-Flex Pattern)
Cuando necesites dividir un solo campo en dos datos relacionados (ej: "No. / Capacidad" o "Mes / Año"), utiliza el patrón **Split-Flex**. Esto garantiza que los inputs se mantengan alineados horizontalmente de forma sólida.

*   **Estructura Obligatoria:**
    ```html
    <div class="form-control">
        <!-- 1. Label Estándar -->
        <label class="label text-xs uppercase font-bold text-base-content/60">Cisternas (No. / Cap.)</label>
        
        <!-- 2. Contenedor Flex (Para forzar fila) -->
        <div class="flex gap-2">
            <!-- 3. Input Pequeño (33% ancho) -->
            <input type="text" class="input input-bordered w-1/3" placeholder="No.">
            
            <!-- 4. Input Grande (66% ancho) -->
            <input type="text" class="input input-bordered w-2/3" placeholder="Litros">
        </div>
    </div>
    ```
    *   **`div.flex gap-2`**: Contenedor padre. `gap-2` crea la separación visual.
    *   **`w-1/3` y `w-2/3`**: Definen la proporción. Para mitades iguales usa `w-1/2` en ambos.

##### 4. Tamaño Estándar de Inputs
Para mantener la consistencia en el programa, todos los inputs deben tener un tamaño uniforme:
*   **Clase para campos estándar:** `input input-bordered w-full h-10` (El `h-10` asegura que coincidan con la altura de los botones estándar).
*   **Clase para campos en tablas:** `input input-bordered input-sm w-full`.
*   **Evita:** Usar `input-lg`, `input-xs` o paddings arbitrarios como `py-10` a menos que sea una excepción de diseño justificada.

#### E. Componente de Búsqueda Autocomplete (Filtros y Formularios)
Este componente permite realizar búsquedas en tiempo real sobre listas de datos locales (CSV), siendo totalmente insensible a acentos y mayúsculas.

##### 1. Análisis de Fuentes de Datos (CSV)
Antes de implementar, identifica qué datos necesitas mostrar. El componente debe configurarse según el origen:
*   **Inventario:** Usa `productos.csv` y `servicios.csv`. Ideal para formularios de creación.
*   **Catálogo de Empresas:** Usa `empresas.csv`. Ideal para filtros de búsqueda por cliente.
*   **Registros Históricos:** Usa `cotizaciones.csv` o `ordenes_desazolve.csv`. Ideal para autocompletar nombres de proyectos o folios ya existentes.

##### 2. Implementación en Backend (Flask/Jinja2)
Para evitar errores de sintaxis en JavaScript con las llaves de Jinja2, usa el patrón de **Inyección Segura por JSON**:

```html
<!-- En el template .html -->
<script id="autocomplete-data" type="application/json">
{
    "lista1": {{ datos_backend_1|tojson|safe }},
    "lista2": {{ datos_backend_2|tojson|safe }}
}
</script>
```

##### 3. Estructura HTML (Floating UI)
Para que las sugerencias floten **por encima** de otros elementos de la grilla, es vital manejar el `z-index` dinámicamente.

```html
<div class="form-control">
    <label class="label text-xs uppercase font-bold text-base-content/60">Etiqueta</label>
    <div class="relative w-full">
        <!-- Input con limpieza de autocompletado nativo -->
        <input type="text" autocomplete="off" 
               class="input input-bordered w-full"
               oninput="filterGeneric(this, 'lista1')" 
               onfocus="filterGeneric(this, 'lista1')">
        
        <!-- Contenedor de Sugerencias (z-9999 y shadow-2xl) -->
        <div class="generic-suggestions hidden absolute z-[9999] w-full bg-base-100 border border-base-300 shadow-2xl max-h-48 overflow-y-auto rounded-md mt-1 top-full left-0">
        </div>
    </div>
</div>
```

##### 4. Lógica JavaScript Pro (Normalización y Z-Index)
La función debe elevar el contenedor padre mientras se muestran los resultados.

```javascript
// 1. Cargar datos de forma segura
const sourceData = JSON.parse(document.getElementById('autocomplete-data').textContent);

// 2. Normalización (Ignora acentos y mayúsculas)
function normalizeStr(str) {
    return (str || "").toString().normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

// 3. Función de filtrado genérica
function filterGeneric(input, type) {
    const wrapper = input.closest('.relative');
    const list = wrapper.querySelector('.generic-suggestions');
    const val = normalizeStr(input.value);
    
    list.innerHTML = '';
    list.classList.add('hidden');
    wrapper.style.zIndex = ""; // Reset z-index

    if (!val) return;

    const matches = (sourceData[type] || []).filter(str => normalizeStr(str).includes(val));

    if (matches.length > 0) {
        list.classList.remove('hidden');
        wrapper.style.zIndex = "100"; // ELEVAR CAPA PARA FLOTAR
        
        matches.slice(0, 15).forEach(match => {
            const div = document.createElement('div');
            div.className = 'p-2 hover:bg-primary/10 cursor-pointer border-b border-base-content/5 text-sm font-bold bg-base-100 text-base-content';
            div.textContent = match;
            div.onmousedown = (e) => {
                e.preventDefault();
                input.value = match;
                list.classList.add('hidden');
                wrapper.style.zIndex = "";
            };
            list.appendChild(div);
        });
    }
}
```

#### F. Monitor de Consumo (Barra de Progreso)
Este componente visualiza un valor numérico (ej. consumo de agua) en una barra de progreso que parece estar segmentada pero es continua. Incluye una etiqueta que flota sobre la barra y se ajusta para no salirse del contenedor.

**Características Clave:**
*   **Barra Continua:** Un solo `div` de fondo que se llena porcentualmente.
*   **Máscara de Segmentos:** Un `div` absoluto superpuesto con bordes transparentes/blancos para simular cortes (tramos de 20 unidades).
*   **Etiqueta Inteligente:** Usa `transform: translateX(-{{ porcentaje }}%)` para alinearse automáticamente (izquierda al 0%, centro al 50%, derecha al 100%).
*   **Estilos Inline:** Se recomiendan estilos en línea para propiedades críticas (posicionamiento, colores específicos) para evitar conflictos de purga de CSS.

**Snippet de Implementación:**
```html
<!-- Barra de Progreso Continua -->
<div class="mt-8 mb-8 w-full select-none" style="position: relative;">
    
    <!-- Escala Superior (Opcional) -->
    <div class="flex justify-between text-[10px] font-bold text-base-content/40 uppercase tracking-widest mb-2 px-1">
        <span style="width: 0;"></span>
        <span style="width: 20%; text-align: center;">Tarifa 1</span>
        <!-- ... más segmentos ... -->
        <span style="width: 20%; text-align: right;">Mayor</span>
    </div>

    <!-- Lógica Jinja: Clamping (0-100%) -->
    {% set total = valor_actual|default(0)|float %}
    {% set porcentaje = (total / VALOR_MAXIMO * 100.0) %}
    {% if porcentaje > 100 %}{% set porcentaje = 100 %}{% endif %}
    {% if porcentaje < 0 %}{% set porcentaje = 0 %}{% endif %}

    <!-- Contenedor (Track) -->
    <div style="position: relative; height: 16px; width: 100%; background-color: #e5e7eb; border-radius: 9999px; margin-top: 10px; margin-bottom: 30px;">
        
        <!-- Barra de Relleno (Fill) -->
        <div style="position: absolute; top: 0; left: 0; height: 100%; background-color: #0099cf; border-radius: 9999px; width: {{ porcentaje }}%; transition: width 0.5s ease-out;">
        </div>

        <!-- Máscara de Segmentos (Overlay) -->
        <!-- Ajustar anchos (20%) según el número de segmentos deseados -->
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; pointer-events: none;">
            <div style="width: 20%; border-right: 2px solid #ffffff; height: 100%;"></div>
            <div style="width: 20%; border-right: 2px solid #ffffff; height: 100%;"></div>
            <div style="width: 20%; border-right: 2px solid #ffffff; height: 100%;"></div>
            <div style="width: 20%; border-right: 2px solid #ffffff; height: 100%;"></div>
            <div style="width: 20%; height: 100%;"></div>
        </div>

        <!-- Etiqueta Flotante -->
        <div style="position: absolute; top: -38px; left: {{ porcentaje }}%; transform: translateX(-{{ porcentaje }}%); background-color: #0099cf; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; white-space: nowrap; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); z-index: 20;">
            {{ total }} m³
            <!-- Flecha Indicadora -->
            <div style="position: absolute; top: 100%; left: 50%; margin-left: -5px; border-width: 5px; border-style: solid; border-color: #0099cf transparent transparent transparent;"></div>
        </div>
    </div>
</div>
```

### 📱 Guía de Responsividad (Mobile First)

La aplicación está diseñada para ser 100% funcional en móviles. Sigue estas reglas estrictas para mantener este comportamiento:

#### 1. Grillas y Formularios
Nunca uses anchos fijos (`w-96`, etc.) para layout principal. Usa siempre grillas responsivas que inicien en 1 columna para móvil y se expandan en pantallas grandes.
*   **Patrón Estándar:** `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`
*   **Contenedores de Inputs:** `w-full` siempre.

#### 2. Tablas en Móvil
Las tablas HTML rompen el diseño móvil si no se manejan bien.
*   **Regla de Oro:** Siempre envuelve la etiqueta `<table>` en un `div` contenedor con la clase `overflow-x-auto`.
```html
<div class="overflow-x-auto">
    <table class="table table-lg">...</table>
</div>
```

#### 3. Botones Adaptables
Para ahorrar espacio en pantallas pequeñas, oculta el texto de los botones secundarios y deja solo el icono, o simplifica la interfaz.
*   **Clases:** `hidden sm:inline` (oculto en móvil, visible en small+).
```html
<a href="..." class="btn btn-primary">
    <span class="icon-[tabler--plus] size-5"></span>
    <span class="hidden sm:inline">Crear Nuevo</span> <!-- Solo icono en móvil -->
</a>
```

#### 4. Encabezados de Página
Usa Flexbox para apilar título y botones verticalmente en móvil, y alinearlos horizontalmente en escritorio.
*   **Margen Crítico:** Todos los contenedores `div` que contengan un `h1` deben llevar obligatoriamente la clase `mb-6` para dar espacio al contenido inferior (referencia: `cotizaciones.html`).
*   **Clases:** `flex flex-col md:flex-row justify-between items-start md:items-center mb-6`

### 🕹️ Comportamientos Interactivos

#### 1. Tabs / Selectores de Vista
Para cambiar entre vistas principales (ej. Desazolves vs Trampas) sin recargar la página:
*   **Patrón:** Usa un `<select>` para la navegación en móvil/desktop unificada si las opciones son mutuamente excluyentes y cambian el contexto completo. Esto es amigable para interfaces táctiles.
*   **Implementación:**
    ```html
    <select onchange="showTab(this.value)" class="select select-sm max-w-xs">
        <option value="vista1">Vista 1</option>
        <option value="vista2">Vista 2</option>
    </select>
    ```
    *(Ver implementación JS en `templates/ordenes.html`)*

#### 2. Generación de Documentos (Impresión/PDF)
La vista web es diferente a la vista de impresión (Reports).
*   **Archivo Crítico:** `paginacion.js`
*   **Función:** Este script contiene una "Guillotina Lógica" que recalcula el layout para impresión, moviendo tablas y bloques para evitar cortes de página incorrectos.
*   **Nota:** Si modificas reportes impresos, verifica que no rompas la lógica de `checkPageOverflow`.

### 🎭 Iconos (Iconify)
El sistema utiliza el set de iconos **Tabler Icons**.
*   **Buscador:** [iconify.design/tabler](https://icon-sets.iconify.design/tabler/)
*   **Uso:** `<span class="icon-[tabler--nombre-del-icono] size-5"></span>`

### 📐 Reglas de Diseño Establecidas
Al crear nuevas páginas, recuerda que `base_flyonui.html` ya tiene configurados los espacios:

*   **Margen Lateral:** 24px estructurales entre el menú y el contenido.
*   **Contenedor Padre:** Ocupa el espacio restante del sidebar con un ancho máximo controlado para legibilidad.
*   **Fondo:** `bg-base-200` (Gris suave) para contrastar con las tarjetas blancas.

### 💡 Instrucción para la IA (Antigravity)
Cuando generes nuevo código:
1.  **Consulta este archivo primero**.
2.  Usa **SIEMPRE** los componentes del diccionario (Sección E).
3.  No inventes clases nuevas si ya existe un `card-body` o un `grid` estándar definido aquí.
4.  Si usas un input compuesto, **copia y pega** el bloque `Split-Flex` explícitamente.

#### E. Diccionario de Componentes (Div Dictionary)
Catálogo oficial de las etiquetas `div` y sus clases estándar para reproducir la interfaz.

| Nombre del Componente | Clases Clave (HTML) | Comportamiento / Uso |
| :--- | :--- | :--- |
| **1. Contenedor de Página** | `w-full p-6 md:p-10 space-y-6` | Envoltorio principal de todo el contenido. Provee el padding externo responsivo. |
| **2. Tarjeta Estándar (Card)** | `card bg-base-100 border border-base-content/10 shadow-sm overflow-hidden` | El bloque de construcción básico. **Siempre** usar `overflow-hidden` para evitar que el contenido sobresalga de los bordes redondeados. |
| **2.1 Cabecera de Tarjeta** | `card-header bg-base-200/50 border-b border-base-content/10 p-5 font-bold flex items-center gap-2 uppercase tracking-widest text-xs` | Título de la sección. El `bg-base-200/50` da el contraste grisáceo estándar. |
| **2.2 Cuerpo de Tarjeta** | `card-body p-6 space-y-4` | Contenedor interno. El padding de `p-6` es el estándar absoluto para el contenido. |
| **3. Comportamiento en Columnas (Formularios)** | `grid grid-cols-1 md:grid-cols-2 gap-4` | **Regla de Oro:** Cuando un card deba dividirse en 2 columnas, usar esta grilla dentro del `card-body`. |
| **4. Comportamiento Multi-Columna (Tablas)** | `tr.hover:bg-base-200/20.divide-x.divide-base-content/5` | Para vistas con muchos datos (como el Tarificador), usar tablas con `divide-x` para separar visualmente las celdas y `hover` para seguimiento. |
| **5. Etiquetas (Labels)** | `label font-bold text-xs uppercase text-base-content/60 tracking-widest` | Estilo estándar para todos los labels de los inputs. |
| **6. Split-Flex (Inputs)** | `flex gap-2` (Hijos: `w-1/3`, `w-2/3`) | **CRÍTICO:** Para dividir un solo campo en dos (No./Cap). Reemplaza a grid en este caso específico. |
| **7. Contenedor Tabs** | `card bg-base-100 border... mb-6` | Barra flotante que contiene el `<select>` de navegación y botones de acción. |
| **8. Estado Vacío (Tabla)** | `text-center py-20 opacity-40` | `td` único para mostrar mensajes cuando no hay datos en una tabla. |
| **9. Folio de Consumo** | `CON-MMAA-###` | Formato estricto para registros de agua. El contador se reinicia mensualmente (ej: `CON-0226-001`). **Protegido:** Solo lectura para el usuario. |
| **10. Div con H1 (Header)** | `div.mb-6` | Todo contenedor `div` que tenga un `h1` (título de página) tendrá un margen `mb-6` (como en `cotizaciones.html`). |

#### Ejemplo de Estructura Completa (Skeleton)
```html
<!-- 1. Contenedor Página -->
<div class="w-full p-6 md:p-10 space-y-6">
    
    <!-- Header simple -->
    <div class="flex justify-between"><h1>Título</h1></div>

    <!-- 7. Tabs (Opcional) -->
    <div class="card...">...</div>

    <!-- 4. Grilla Principal -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <!-- 2. Tarjeta -->
        <div class="card bg-base-100 border border-base-content/10 shadow-sm">
            <!-- 2.1 Header -->
            <div class="card-header bg-base-200/50..."><h3>Datos</h3></div>
            
            <!-- 2.2 Body -->
            <div class="card-body p-6">
                <!-- 5. Sub-Grilla -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Input Normal -->
                    <div class="form-control">...</div>
                    
                    <!-- 6. Split-Flex Input -->
                    <div class="form-control">
                         <div class="flex gap-2">...</div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</div>
```

---

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

### Status (Indicadores)
Usa este prompt para generar indicadores de estado circulares:

> I'm using the FlyonUI Tailwind CSS component library in my project. Please integrate the following component into my project:
>
> Here are the code snippets for the block component: 
>
> ```html
> ```

### Progress Steps (Barra de Progreso por Pasos)
Usa este prompt para generar barras de progreso segmentadas (útil para niveles o tarifas escalonadas):

> I'm using the FlyonUI Tailwind CSS component library in my project. Please integrate the following component into my project:
>
> Here are the code snippets for the block component: 
>
> ```html
> <!-- Step variant 1 (Color Corporativo #0099cf) -->
> <div class="flex items-center gap-x-1">
>   <div class="progress-step bg-[#0099cf]" role="progressbar" aria-label="Progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" ></div>
>   <div class="progress-step bg-[#0099cf]/10" role="progressbar" aria-label="Progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" ></div>
>   <div class="progress-step bg-[#0099cf]/10" role="progressbar" aria-label="Progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" ></div>
>   <div class="progress-step bg-[#0099cf]/10" role="progressbar" aria-label="Progressbar" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100" ></div>
>   <p class="text-xs text-[#0099cf] ms-1 font-medium">25%</p>
> </div>
> ```

### Advanced Select (Selectores Avanzados)
Usa este prompt para generar selectores avanzados con búsqueda y scroll (`max-h-52 overflow-y-auto`):

> I'm using the FlyonUI Tailwind CSS component library in my project. Please integrate the following component into my project.
> **IMPORTANTE**: Para evitar que el menú desplegable se corte, asegúrate de que el contenedor padre (como la `card`) **NO** tenga la clase `overflow-hidden`.
> It is CRITICAL to include the `max-h-52 overflow-y-auto` classes in `dropdownClasses` to enable scrolling, and to use the specific `extraMarkup` for the chevron icon.
>
> Here are the code snippets for the block component:
>
> ```html
> <div class="w-full">
>   <select name="nombre_campo"
>     data-select='{
>     "placeholder": "Selecciona opción...",
>     "toggleTag": "<button type=\"button\" aria-expanded=\"false\"></button>",
>     "toggleClasses": "advance-select-toggle relative select-disabled:pointer-events-none select-disabled:opacity-40",
>     "dropdownClasses": "advance-select-menu max-h-52 overflow-y-auto",
>     "optionClasses": "advance-select-option selected:select-active",
>     "optionTemplate": "<div class=\"flex justify-between items-center w-full\"><span data-title></span><span class=\"icon-[tabler--check] shrink-0 size-4 text-primary hidden selected:block \"></span></div>",
>     "extraMarkup": "<span class=\"icon-[tabler--caret-up-down] shrink-0 size-4 text-base-content absolute top-1/2 end-3 -translate-y-1/2 pointer-events-none\"></span>"
>     }'
>     class="hidden"
>   >
>     <option value="">Selecciona</option>
>     <option value="opcion1">Opción 1</option>
>     <option value="opcion2">Opción 2</option>
>   </select>
> </div>
> ```

---

## 🚀 Despliegue
Consulta [README_DESPLIEGUE.md](README_DESPLIEGUE.md) para saber cómo subir tus cambios al servidor de DigitalOcean usando:
```powershell
.\desplegar.ps1
```

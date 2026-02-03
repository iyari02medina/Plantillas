# 🎨 Guía de UI - Sistema Cophi (FlyonUI)

Este archivo sirve como referencia rápida para la implementación de componentes de diseño utilizando el framework **FlyonUI** y **Tailwind CSS**.

## 📚 Documentación Oficial
Para buscar nuevos componentes, botones, tablas o layouts, consulta siempre la web oficial:
👉 **[flyonui.com](https://flyonui.com/)**

---

## 🛠️ Categorías de Componentes

### 1. Elementos Básicos (Components)
Usa estos para acciones y alertas simples:
*   [Buttons](https://flyonui.com/docs/components/button/) - Botones de todo tipo.
*   [Cards](https://flyonui.com/docs/components/card/) - Contenedores para agrupar información.
*   [Alerts](https://flyonui.com/docs/components/alert/) - Mensajes de éxito, error o aviso.
*   [Badges](https://flyonui.com/docs/components/badge/) - Etiquetas de estado (ej: "Pendiente", "Completado").

### 2. Formularios (Forms)
Para captura de datos en nuevas órdenes o cotizaciones:
*   [Input](https://flyonui.com/docs/forms/input/) - Campos de texto tradicionales.
*   [Select](https://flyonui.com/docs/forms/select/) - Listas desplegables.
*   [Checkbox / Radio](https://flyonui.com/docs/forms/checkbox/) - Opciones de selección.

### 3. Visualización de Datos
*   [Tables](https://flyonui.com/docs/data-display/table/) - Tablas para listado de registros.
*   [Timeline](https://flyonui.com/docs/data-display/timeline/) - Historiales de eventos.

---

## 🧩 Patrones de Implementación (Recetas)

Aquí se documenta cómo construir los componentes complejos específicos de esta aplicación para mantener la consistencia.

### A. Buscador y Filtros (En Página)
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

### B. Tabla de Datos Estándar
Las tablas deben tener ciertas características obligatorias:
1.  Estar dentro de un `card` con `overflow-hidden`.
2.  Usar `table-lg` para buen espaciado.
3.  **Menú de Acciones:** La primera columna siempre debe ser acciones (Ver/Editar/Borrar).
4.  **Estado Vacío:** Usar `{% else %}` en el bucle `for` para mostrar un mensaje amigable cuando no hay datos.
5.  **Responsividad:** Envolver siempre en `<div class="overflow-x-auto">`.

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

### C. Buscador Global (Command Palette)
El buscador que aparece con `Ctrl+K` o en el header es **estático** en JavaScript.
*   **Archivo:** `interfaz/templates/base_flyonui.html`
*   **Ubicación:** Al final del archivo, busca la constante `APP_ROUTES`.
*   **Cómo agregar página:** Agrega un objeto al array:
```javascript
{
    title: 'Nueva Página',
    url: "{{ url_for('nueva_ruta') }}",
### D. Estándares de Grillas y Formularios (Responsive)
El layout de todos los formularios debe seguir estas reglas de grilla estrictas para asegurar que se vean bien en móvil y escritorio.

#### 1. Grilla Maestra
El contenedor principal de cualquier grupo de inputs debe ser una grilla que empieza en **1 columna** y crece.
*   **Clase Base:** `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6` (ajusta `lg:` según necesites 3, 4 o 5 columnas).
*   **Ejemplo (`ordenes.html`):**
    ```html
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <!-- Los inputs van aquí -->
        <div class="form-control lg:col-span-2">...</div> <!-- Input ancho -->
    </div>
    ```

#### 2. Inputs Compuestos (Split-Flex Pattern)
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
    *   **Nota:** NO uses `grid` ni `input-group` para esto. Flexbox es más robusto para anidación.

#### 3. Tipografía de Labels
Todos los labels de formularios deben ser consistentes:
*   **Clase:** `text-xs uppercase font-bold text-base-content/60` (o `text-base-content/50` si es muy secundario).
*   **Evita:** Tamaños arbitrarios como `text-[10px]` o `text-lg`. Consistencia es clave.

## 📱 Guía de Responsividad (Mobile First)

La aplicación está diseñada para ser 100% funcional en móviles. Sigue estas reglas estrictas para mantener este comportamiento:

### 1. Grillas y Formularios
Nunca uses anchos fijos (`w-96`, etc.) para layout principal. Usa siempre grillas responsivas que inicien en 1 columna para móvil y se expandan en pantallas grandes.
*   **Patrón Estándar:** `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6`
*   **Contenedores de Inputs:** `w-full` siempre.

### 2. Tablas en Móvil
Las tablas HTML rompen el diseño móvil si no se manejan bien.
*   **Regla de Oro:** Siempre envuelve la etiqueta `<table>` en un `div` contenedor con la clase `overflow-x-auto`.
```html
<div class="overflow-x-auto">
    <table class="table table-lg">...</table>
</div>
```

### 3. Botones Adaptables
Para ahorrar espacio en pantallas pequeñas, oculta el texto de los botones secundarios y deja solo el icono, o simplifica la interfaz.
*   **Clases:** `hidden sm:inline` (oculto en móvil, visible en small+).
```html
<a href="..." class="btn btn-primary">
    <span class="icon-[tabler--plus] size-5"></span>
    <span class="hidden sm:inline">Crear Nuevo</span> <!-- Solo icono en móvil -->
</a>
```

### 4. Encabezados de Página
Usa Flexbox para apilar título y botones verticalmente en móvil, y alinearlos horizontalmente en escritorio.
*   **Clases:** `flex flex-col md:flex-row justify-between items-start md:items-center`

---

## 🕹️ Comportamientos Interactivos

### 1. Tabs / Selectores de Vista
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

### 2. Generación de Documentos (Impresión/PDF)
La vista web es diferente a la vista de impresión (Reports).
*   **Archivo Crítico:** `paginacion.js`
*   **Función:** Este script contiene una "Guillotina Lógica" que recalcula el layout para impresión, moviendo tablas y bloques para evitar cortes de página incorrectos.
*   **Nota:** Si modificas reportes impresos, verifica que no rompas la lógica de `checkPageOverflow`.

---

## 🎭 Iconos (Iconify)
El sistema utiliza el set de iconos **Tabler Icons**.
*   **Buscador:** [iconify.design/tabler](https://icon-sets.iconify.design/tabler/)
*   **Uso:** `<span class="icon-[tabler--nombre-del-icono] size-5"></span>`

---

## 📐 Reglas de Diseño Establecidas
Al crear nuevas páginas, recuerda que `base_flyonui.html` ya tiene configurados los espacios:

*   **Margen Lateral:** 24px estructurales entre el menú y el contenido.
*   **Contenedor Padre:** Ocupa el espacio restante del sidebar con un ancho máximo controlado para legibilidad.
*   **Fondo:** `bg-base-200` (Gris suave) para contrastar con las tarjetas blancas.

---

## 💡 Instrucción para la IA (Antigravity)
Cuando generes nuevo código:
1.  **Consulta este archivo primero**.
2.  Usa **SIEMPRE** los componentes del diccionario (Sección E).
3.  No inventes clases nuevas si ya existe un `card-body` o un `grid` estándar definido aquí.
4.  Si usas un input compuesto, **copia y pega** el bloque `Split-Flex` explícitamente.

---

### E. Diccionario de Componentes (Div Dictionary)
Catálogo oficial de las etiquetas `div` y sus clases estándar para reproducir la interfaz.

| Nombre del Componente | Clases Clave (HTML) | Comportamiento / Uso |
| :--- | :--- | :--- |
| **1. Contenedor de Página** | `w-full p-6 md:p-10 space-y-6` | Envoltorio principal de todo el contenido. Provee el padding externo responsivo. |
| **2. Tarjeta Estándar (Card)** | `card bg-base-100 border border-base-content/10 shadow-sm` | El bloque de construcción básico. Úsalo para agrupar cualquier sección (tablas, formularios). |
| **2.1 Cabecera de Tarjeta** | `card-header bg-base-200/50 border-b border-base-content/10 p-5` | Título de la sección. Úsalo con un icono y `h3.text-sm.uppercase`. |
| **2.2 Cuerpo de Tarjeta** | `card-body p-6 space-y-4` | Contenedor interno para el contenido de la tarjeta. |
| **3. Barra de Filtros** | `p-6 border-b border-base-content/10 bg-base-100` | Usado en `ordenes.html` como cabecera pegajosa o barra superior de búsqueda. |
| **4. Grilla de Formulario** | `grid grid-cols-1 lg:grid-cols-2 gap-8` | Estructura para dividir formularios en columnas grandes (Izquierda/Derecha). |
| **5. Sub-Grilla Inputs** | `grid grid-cols-1 md:grid-cols-2 gap-4 lg:grid-cols-4` | Grilla interna para alinear campos individuales dentro de una tarjeta. |
| **6. Split-Flex (Inputs)** | `flex gap-2` (Hijos: `w-1/3`, `w-2/3`) | **CRÍTICO:** Para dividir un solo campo en dos (No./Cap). Reemplaza a grid en este caso específico. |
| **7. Contenedor Tabs** | `card bg-base-100 border... mb-6` | Barra flotante que contiene el `<select>` de navegación y botones de acción. |
| **8. Estado Vacío (Tabla)** | `text-center py-20 opacity-40` | `td` único para mostrar mensajes cuando no hay datos en una tabla. |

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
Cuando te pida un nuevo componente o página:
1. **Consulta este documento primero**.
2. **Prioriza Mobile-First:** Empieza pensando en `grid-cols-1` y `flex-col`.
3. **Verifica Tablas:** Si creas una tabla, añade `overflow-x-auto`.
4. **Respeta la Navegación:** Registra nuevas páginas en el Buscador Global (`base_flyonui.html`).
5. **Consistencia Visual:** Usa los snippets de "Patrones de Implementación" para tablas y filtros.

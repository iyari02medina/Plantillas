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
Cuando te pida un nuevo componente:
1. Revisa la categoría correspondiente en este README.
2. Busca el HTML más moderno en la web de FlyonUI.
3. Asegúrate de que las clases de color coincidan con el tema (primary, secondary, success, error).

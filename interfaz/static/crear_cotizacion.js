
// --- FUNCIONES DE UTILIDAD ---
function normalizeStr(str) {
    return (str || "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

// --- CLIENTES (Lógica existente) ---
function fillClient(input) {
    const val = normalizeStr(input.value);
    const suggestionsBox = document.getElementById('suggestions-box');

    // Check if element exists to avoid errors
    if (!suggestionsBox) return;

    suggestionsBox.innerHTML = '';
    suggestionsBox.classList.add('hidden');

    if (!val) return;

    if (typeof clientsData !== 'undefined') {
        const matches = clientsData.filter(c => {
            const nombre = c.nombre_empresa || '';
            return normalizeStr(nombre).includes(val);
        });

        if (matches.length > 0) {
            suggestionsBox.classList.remove('hidden');
            matches.slice(0, 10).forEach(match => {
                const div = document.createElement('div');
                div.className = 'p-3 hover:bg-base-200 cursor-pointer border-b border-base-content/5 last:border-0';
                div.innerHTML = `<div class="font-bold text-sm text-base-content">${match.nombre_empresa}</div>`;
                div.onclick = () => selectClient(match);
                suggestionsBox.appendChild(div);
            });
        }
    }
}

function selectClient(client) {
    document.getElementById('nombre_cliente').value = client.nombre_empresa;
    document.getElementById('razon_social_cliente').value = client.nombre_empresa;
    if (document.getElementById('direccion_cliente')) document.getElementById('direccion_cliente').value = client.direccion_empresa || '';
    if (document.getElementById('telefono_contacto')) document.getElementById('telefono_contacto').value = client.telefono_empresa || '';

    const box = document.getElementById('suggestions-box');
    if (box) box.classList.add('hidden');
}


// --- ITEMS (NUEVA LÓGICA SIMPLIFICADA) ---

function filterItems(input) {
    // Buscar la lista de sugerencias que es hermana del input
    const wrapper = input.closest('.relative');
    if (!wrapper) return;

    const suggestionsList = wrapper.querySelector('.item-suggestions');
    if (!suggestionsList) return;

    const val = normalizeStr(input.value);

    // Limpiar y ocultar
    suggestionsList.innerHTML = '';
    suggestionsList.classList.add('hidden');

    if (!val) return;

    // Obtener datos (de window.inventoryData asignado en HTML)
    const data = window.inventoryData || [];
    if (!data.length) return;

    // Filtrar (ignorando mayúsculas y acentos gracias a normalizeStr)
    const matches = data.filter(item => {
        const name = item.Nombre || item.nombre || '';
        return normalizeStr(name).includes(val);
    });

    if (matches.length > 0) {
        suggestionsList.classList.remove('hidden');

        // Limitar a los primeros 20 para no saturar el DOM
        matches.slice(0, 20).forEach(item => {
            const name = item.Nombre || item.nombre || '';
            const price = item.Precio || item.precio || 0;
            const desc = item.Descripcion || item.descripcion || name; // Use name as desc if missing

            const div = document.createElement('div');
            div.className = 'p-2 hover:bg-primary/10 cursor-pointer border-b border-base-content/5 text-sm flex justify-between items-center';
            div.innerHTML = `
                <span class="font-medium truncate mr-2">${name}</span>
                <span class="badge badge-sm badge-ghost">$${parseFloat(price).toFixed(2)}</span>
            `;

            // Al hacer click
            div.onmousedown = (e) => {
                e.preventDefault(); // Prevenir pérdida de foco prematura
                selectItem(item, input);
            };

            suggestionsList.appendChild(div);
        });
    }
}

function selectItem(item, input) {
    const row = input.closest('.item-row');
    const name = item.Nombre || item.nombre || '';
    const desc = item.Descripcion || item.descripcion || name;
    const unit = item.Unidad || item.unidad || '';
    const price = item.Precio || item.precio || '';

    // Llenar campos
    input.value = name;
    row.querySelector('input[name="descripcion_item[]"]').value = desc;
    row.querySelector('input[name="unidad_item[]"]').value = unit;
    row.querySelector('input[name="precio_unitario_item[]"]').value = price;

    // Ocultar lista
    const list = input.closest('.relative').querySelector('.item-suggestions');
    if (list) list.classList.add('hidden');

    calculateTotals();
}

// Global click para cerrar listas de items si clickeo fuera
document.addEventListener('click', (e) => {
    // Cerrar sugerencias clientes
    if (e.target.id !== 'nombre_cliente') {
        const box = document.getElementById('suggestions-box');
        if (box) box.classList.add('hidden');
    }

    // Cerrar menú items
    // Check if the click was outside any item-suggestions list AND not on an input that triggers it
    const clickedInsideItemSuggestion = e.target.closest('.item-suggestions');
    const clickedOnItemInput = e.target.matches('input[name="nombre_item[]"]');

    if (!clickedInsideItemSuggestion && !clickedOnItemInput) {
        document.querySelectorAll('.item-suggestions').forEach(el => el.classList.add('hidden'));
    }
});


// --- TABLA Y CÁLCULOS ---

function calculateTotals() {
    const rows = document.querySelectorAll('.item-row');
    let subtotal = 0;

    rows.forEach(row => {
        const qty = parseFloat(row.querySelector('input[name="cantidad_item[]"]').value) || 0;
        const price = parseFloat(row.querySelector('input[name="precio_unitario_item[]"]').value) || 0;
        subtotal += qty * price;
    });

    const iva = subtotal * 0.16;
    const total = subtotal + iva;

    const formatter = new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    });

    if (document.getElementById('subtotal-display')) document.getElementById('subtotal-display').textContent = formatter.format(subtotal);
    if (document.getElementById('iva-display')) document.getElementById('iva-display').textContent = formatter.format(iva);
    if (document.getElementById('total-display')) document.getElementById('total-display').textContent = formatter.format(total);
}

function addItem() {
    const container = document.getElementById('items-container');
    const row = document.createElement('tr');
    row.className = 'item-row hover:bg-base-200/20 group animate-in fade-in slide-in-from-bottom-2 duration-200';

    // Usamos 'relative' en el contenedor del input para posicionar la lista de sugerencias absoluta a él
    // Importante: z-50 y overflow-visible en el padre si fuera necesario, pero overflow-y-auto está en el suggestions.
    row.innerHTML = `
        <td class="p-2 overflow-visible">
            <div class="relative w-full">
                <input type="text" name="nombre_item[]" required 
                    class="input input-bordered input-sm w-full font-bold bg-transparent" 
                    placeholder="Buscar item..." 
                    autocomplete="off"
                    oninput="filterItems(this)" 
                    onfocus="filterItems(this)">
                
                <!-- Lista de sugerencias oculta por defecto -->
                <div class="item-suggestions hidden absolute z-[9999] w-[300px] bg-base-100 border border-base-300 shadow-xl max-h-48 overflow-y-auto rounded-md mt-1 top-full left-0">
                </div>
            </div>
        </td>
        <td class="p-2">
            <input type="text" name="descripcion_item[]" class="input input-bordered input-sm w-full bg-transparent">
        </td>
        <td class="p-2">
            <input type="text" name="unidad_item[]" class="input input-bordered input-sm w-full bg-transparent" placeholder="pza...">
        </td>
        <td class="p-2">
            <input type="number" step="1" name="cantidad_item[]" required value="1" oninput="calculateTotals()"
                class="input input-bordered input-sm w-full font-bold text-center bg-transparent">
        </td>
        <td class="p-2">
            <input type="number" step="0.01" name="precio_unitario_item[]" required oninput="calculateTotals()"
                class="input input-bordered input-sm w-full font-bold text-primary bg-transparent text-right">
        </td>
        <td class="p-2 text-center">
            <button type="button" class="btn btn-ghost btn-sm btn-circle text-error hover:bg-error/10" onclick="removeItem(this)">
                <span class="icon-[tabler--trash] size-5"></span>
            </button>
        </td>
    `;
    container.appendChild(row);
    calculateTotals();
}

function removeItem(btn) {
    btn.closest('.item-row').remove();
    calculateTotals();
}

document.addEventListener('DOMContentLoaded', () => {
    // Si la tabla se carga vacía, poner un row inicial
    const container = document.getElementById('items-container');
    if (container && container.children.length === 0) {
        addItem();
    }

    calculateTotals();
    console.log('JS Cotización cargado simple.');
});

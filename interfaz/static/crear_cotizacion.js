function normalizeStr(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function fillClient(input) {
    const val = normalizeStr(input.value);
    const suggestionsBox = document.getElementById('suggestions-box');

    // Limpiar sugerencias anteriores
    suggestionsBox.innerHTML = '';
    suggestionsBox.classList.add('hidden');

    if (!val) return;

    const matches = clientsData.filter(c => {
        const nombre = c.nombre_empresa || '';
        return normalizeStr(nombre).includes(val);
    });

    if (matches.length > 0) {
        suggestionsBox.classList.remove('hidden');
        matches.forEach(match => {
            const div = document.createElement('div');
            div.className = 'p-3 hover:bg-base-200 cursor-pointer border-b border-base-content/5 last:border-0';
            div.innerHTML = `<div class="font-bold text-sm text-base-content">${match.nombre_empresa}</div><div class="text-xs text-base-content/50">${match.id_cliente || ''}</div>`;
            div.onclick = () => selectClient(match);
            suggestionsBox.appendChild(div);
        });
    }
}

function selectClient(client) {
    document.getElementById('nombre_cliente').value = client.nombre_empresa;
    document.getElementById('razon_social_cliente').value = client.nombre_empresa;
    if (document.getElementById('direccion_cliente')) document.getElementById('direccion_cliente').value = client.direccion_empresa || '';
    if (document.getElementById('telefono_contacto')) document.getElementById('telefono_contacto').value = client.telefono_empresa || '';

    document.getElementById('suggestions-box').classList.add('hidden');
}

document.addEventListener('click', function (e) {
    if (e.target.id !== 'nombre_cliente') {
        const box = document.getElementById('suggestions-box');
        if (box) box.classList.add('hidden');
    }
});

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
    const row = document.createElement('div');
    row.className = 'item-row grid grid-cols-1 md:grid-cols-12 gap-4 p-5 bg-base-100 border border-base-content/10 rounded-xl shadow-sm relative group animate-in zoom-in-95 duration-200';
    row.innerHTML = `
        <div class="md:col-span-3">
            <label class="label py-1 text-[10px] font-bold uppercase text-base-content/50">Nombre Item</label>
            <input type="text" name="nombre_item[]" list="inventory_list" onchange="fillItem(this)" required 
                class="input input-bordered input-sm w-full font-bold" placeholder="Buscar item...">
        </div>
        <div class="md:col-span-3">
            <label class="label py-1 text-[10px] font-bold uppercase text-base-content/50">Descripción</label>
            <input type="text" name="descripcion_item[]" class="input input-bordered input-sm w-full">
        </div>
        <div class="md:col-span-2">
            <label class="label py-1 text-[10px] font-bold uppercase text-base-content/50">Unidad</label>
            <input type="text" name="unidad_item[]" class="input input-bordered input-sm w-full" placeholder="pza, servicio...">
        </div>
        <div class="md:col-span-1">
            <label class="label py-1 text-[10px] font-bold uppercase text-base-content/50">Cant.</label>
            <input type="number" step="1" name="cantidad_item[]" required value="1" oninput="calculateTotals()"
                class="input input-bordered input-sm w-full font-bold">
        </div>
        <div class="md:col-span-2">
            <label class="label py-1 text-[10px] font-bold uppercase text-base-content/50">Precio U.</label>
            <input type="number" step="0.01" name="precio_unitario_item[]" required oninput="calculateTotals()"
                class="input input-bordered input-sm w-full font-bold text-primary">
        </div>
        <div class="md:col-span-1 flex items-end justify-center pb-1">
            <button type="button" class="btn btn-ghost btn-sm btn-circle text-error hover:bg-error/10" onclick="removeItem(this)">
                <span class="icon-[tabler--trash] size-5"></span>
            </button>
        </div>
    `;
    container.appendChild(row);
    calculateTotals();
}

function removeItem(btn) {
    btn.closest('.item-row').remove();
    calculateTotals();
}

function fillItem(input) {
    const val = input.value;
    const list = document.getElementById('inventory_list');
    const options = list.options;
    const row = input.closest('.item-row');

    for (let i = 0; i < options.length; i++) {
        if (options[i].value === val) {
            const desc = options[i].getAttribute('data-desc');
            const unit = options[i].getAttribute('data-unit');
            const price = options[i].getAttribute('data-price');

            row.querySelector('input[name="descripcion_item[]"]').value = desc;
            row.querySelector('input[name="unidad_item[]"]').value = unit;
            row.querySelector('input[name="precio_unitario_item[]"]').value = price;

            calculateTotals();
            break;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('items-container');
    if (container && container.children.length === 0) {
        addItem();
    }
    calculateTotals();
});

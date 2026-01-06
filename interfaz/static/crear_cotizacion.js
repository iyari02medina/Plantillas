function normalizeStr(str) {
    return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function fillClient(input) {
    const val = normalizeStr(input.value);
    const suggestionsBox = document.getElementById('suggestions-box');

    // Limpiar sugerencias anteriores
    suggestionsBox.innerHTML = '';
    suggestionsBox.style.display = 'none';

    if (!val) return;

    // Filtrar clientes
    // clientsData debe estar definido en el HTML (viene del CSV via Jinja | tojson)
    // Las claves del CSV son: nombre_empresa, telefono_empresa, direccion_empresa, etc.
    const matches = clientsData.filter(c => {
        const nombre = c.nombre_empresa || '';
        return normalizeStr(nombre).includes(val);
    });

    if (matches.length > 0) {
        suggestionsBox.style.display = 'block';
        matches.forEach(match => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = match.nombre_empresa;
            div.onclick = () => selectClient(match);
            suggestionsBox.appendChild(div);
        });
    }
}

function selectClient(client) {
    // Llenar campos usando las claves originales del CSV
    document.getElementById('nombre_cliente').value = client.nombre_empresa;

    // Razón social a veces no está explícita, usamos nombre_empresa si falta
    document.getElementById('razon_social_cliente').value = client.nombre_empresa;

    document.getElementById('direccion_cliente').value = client.direccion_empresa || '';
    document.getElementById('telefono_contacto').value = client.telefono_empresa || '';

    // Limpiar sugerencias
    document.getElementById('suggestions-box').style.display = 'none';

    // Feedback visual
    const input = document.getElementById('nombre_cliente');
    input.style.borderColor = 'var(--success-color)';
    setTimeout(() => input.style.borderColor = '', 1000);
}

// Cerrar sugerencias si se hace clic fuera
document.addEventListener('click', function (e) {
    if (e.target.id !== 'nombre_cliente') {
        const box = document.getElementById('suggestions-box');
        if (box) box.style.display = 'none';
    }
});

// Add one item by default
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('items-container');
    if (container && container.children.length === 0) {
        addItem();
    }
    // Calculate initial totals if there are existing items (e.g., when viewing/editing)
    calculateTotals();
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

    // Update display
    const formatter = new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    });

    document.getElementById('subtotal-display').textContent = formatter.format(subtotal);
    document.getElementById('iva-display').textContent = formatter.format(iva);
    document.getElementById('total-display').textContent = formatter.format(total);
}

function addItem() {
    const container = document.getElementById('items-container');
    const row = document.createElement('div');
    row.className = 'items-section item-row';
    row.innerHTML = `
        <div>
            <label style="font-size: 0.8em">Nombre Item</label>
            <input type="text" name="nombre_item[]" list="inventory_list" onchange="fillItem(this)" required placeholder="Buscar item...">
        </div>
        <div>
            <label style="font-size: 0.8em">Descripción</label>
            <input type="text" name="descripcion_item[]">
        </div>
        <div>
            <label style="font-size: 0.8em">Unidad</label>
            <input type="text" name="unidad_item[]" placeholder="pza, servicio...">
        </div>
        <div>
            <label style="font-size: 0.8em">Cant.</label>
            <input type="number" step="1" name="cantidad_item[]" required value="1" oninput="calculateTotals()">
        </div>
        <div>
            <label style="font-size: 0.8em">Precio U.</label>
            <input type="number" step="0.01" name="precio_unitario_item[]" required oninput="calculateTotals()">
        </div>
        <div style="padding-top: 1.5rem;">
            <span class="remove-item" onclick="removeItem(this)">✕</span>
        </div>
    `;
    container.appendChild(row);
    calculateTotals();
}

function removeItem(span) {
    span.parentElement.parentElement.remove();
    calculateTotals();
}

function fillItem(input) {
    const val = input.value;
    const list = document.getElementById('inventory_list');
    const options = list.options;
    // Find the parent row to update its sibling inputs
    const row = input.parentElement.parentElement;

    for (let i = 0; i < options.length; i++) {
        if (options[i].value === val) {
            // Found the item in the datalist
            const desc = options[i].getAttribute('data-desc');
            const unit = options[i].getAttribute('data-unit');
            const price = options[i].getAttribute('data-price');

            // Update inputs
            row.querySelector('input[name="descripcion_item[]"]').value = desc;
            row.querySelector('input[name="unidad_item[]"]').value = unit;
            row.querySelector('input[name="precio_unitario_item[]"]').value = price;

            // Recalculate totals after filling item details
            calculateTotals();
            break;
        }
    }
}


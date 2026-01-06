from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import csv
import os
import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Paths configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COTIZACIONES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion', 'cotizaciones.csv'))
ORDENES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Orden de trabajo', 'ordenes_desazolve.csv'))
INVENTARIO_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'productos_servicios.csv'))
CLIENTES_CSV = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Plantillas\inventario\empresas.csv"
COTIZACIONES_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'cotizaciones'))
TEMPLATE_COT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion'))

def generate_quotation_html(folio):
    """Genera el archivo HTML de la cotización usando el script logic."""
    try:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(TEMPLATE_COT_DIR))
        template = env.get_template('plantilla_cotizacion.html')
        
        # Leer el CSV para obtener los datos de ese folio
        all_rows = read_csv(COTIZACIONES_CSV)
        folio_rows = [r for r in all_rows if r.get('folio_cot') == folio]
        
        if not folio_rows:
            return False
            
        row = folio_rows[0]
        subtotal = float(row.get('subtotal', 0).replace(',', ''))
        iva = float(row.get('iva', 0).replace(',', ''))
        total = float(row.get('total', 0).replace(',', ''))
        
        data = {
            'folio_cot': folio,
            'nombre_cot': row.get('nombre_cot', ''),
            'fecha_cot': row.get('fecha_cot', ''),
            'nombre_cliente': row.get('nombre_cliente', ''),
            'direccion_cliente': row.get('direccion_cliente', ''),
            'nombre_contacto': row.get('nombre_contacto', ''),
            'telefono_contacto': row.get('telefono_contacto', ''),
            'alcance_cot': row.get('alcance_cot', ''),
            'terminos': row.get('terminos', ''),
            'gestor': 'ING. EJEMPLO GESTOR', 
            'puesto_gestor': 'GERENTE DE PROYECTOS',
            'subtotal': f"{subtotal:,.2f}",
            'iva': f"{iva:,.2f}",
            'total': f"{total:,.2f}",
            'items': [],
            'unique_images': [],
            'seen_images': set(),
            'alcance_lines': row.get('alcance_cot', '').split('\n')
        }
        
        for r in folio_rows:
            item_total = float(r.get('importe_item', 0).replace(',', ''))
            data['items'].append({
                'nombre_item': r.get('nombre_item', ''),
                'descripcion_item': r.get('descripcion_item', ''),
                'unidad_item': r.get('unidad_item', ''),
                'cantidad_item': r.get('cantidad_item', ''),
                'precio_unitario_item': f"{float(r.get('precio_unitario_item', 0)):,.2f}",
                'importe_item': f"{item_total:,.2f}",
                'imagen_item': r.get('imagen_item', '')
            })
            
            img = r.get('imagen_item', '')
            if img and img not in data['seen_images']:
                data['seen_images'].add(img)
                data['unique_images'].append({'filename': img, 'caption': r.get('nombre_item', '')})

        output = template.render(data)
        
        # Ajustar rutas para el servidor local (opcional, pero ayuda a la consistencia)
        output = output.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
        output = output.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
        output = output.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')
        
        if not os.path.exists(COTIZACIONES_GEN_DIR):
            os.makedirs(COTIZACIONES_GEN_DIR)
            
        output_filename = os.path.join(COTIZACIONES_GEN_DIR, f'cotizacion_{folio}.html')
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output)
        return True
    except Exception as e:
        print(f"Error generando HTML para {folio}: {e}")
        return False

def read_csv(filepath):
    items = []
    print(f"Reading CSV from: {filepath}")
    if os.path.exists(filepath):
        try:
            with open(filepath, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                items = list(reader)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            try:
                # Fallback
                with open(filepath, mode='r', encoding='latin-1') as f:
                    reader = csv.DictReader(f)
                    items = list(reader)
            except Exception as e2:
                print(f"Error reading fallback {filepath}: {e2}")

    print(f"Loaded {len(items)} items from {filepath}")
    if items:
        print(f"First item keys: {items[0].keys()}")
    return items

def get_cotizacion_data(folio):
    all_rows = read_csv(COTIZACIONES_CSV)
    folio_rows = [r for r in all_rows if r.get('folio_cot') == folio]
    
    if not folio_rows:
        return None
        
    first = folio_rows[0]
    data = {
        'folio_cot': folio,
        'nombre_cot': first.get('nombre_cot', ''),
        'fecha_cot': first.get('fecha_cot', ''),
        'nombre_cliente': first.get('nombre_cliente', ''),
        'razon_social_cliente': first.get('razon_social_cliente', ''),
        'direccion_cliente': first.get('direccion_cliente', ''),
        'nombre_contacto': first.get('nombre_contacto', ''),
        'telefono_contacto': first.get('telefono_contacto', ''),
        'alcance_cot': first.get('alcance_cot', ''),
        'terminos': first.get('terminos', ''),
        'conceptos': []
    }
    
    for r in folio_rows:
        data['conceptos'].append({
            'nombre_item': r.get('nombre_item', ''),
            'descripcion_item': r.get('descripcion_item', ''),
            'unidad_item': r.get('unidad_item', ''),
            'cantidad_item': r.get('cantidad_item', ''),
            'precio_unitario_item': r.get('precio_unitario_item', ''),
            'importe_item': r.get('importe_item', '')
        })
        
    return data

def append_to_csv(filepath, fieldnames, rows):
    file_exists = os.path.exists(filepath)
    with open(filepath, mode='a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

@app.route('/')
def index():
    cotizaciones = read_csv(COTIZACIONES_CSV)
    ordenes = read_csv(ORDENES_CSV)
    
    # Simple metrics
    total_cotizaciones = len(set(c['folio_cot'] for c in cotizaciones if c.get('folio_cot')))
    total_ordenes = len(set(o['folio_cot'] for o in ordenes if o.get('folio_cot')))
    
    return render_template('index.html', total_cotizaciones=total_cotizaciones, total_ordenes=total_ordenes)

@app.route('/cotizaciones')
def cotizaciones():
    raw_data = read_csv(COTIZACIONES_CSV)
    # Group by folio
    grouped_cotizaciones = {}
    for row in raw_data:
        folio = row.get('folio_cot')
        if not folio: continue
        if folio not in grouped_cotizaciones:
            grouped_cotizaciones[folio] = {
                'folio': folio,
                'cliente': row.get('nombre_cliente'),
                'fecha': row.get('fecha_cot'),
                'total': row.get('total'),
                'items_count': 0
            }
        grouped_cotizaciones[folio]['items_count'] += 1
    
    return render_template('cotizaciones.html', cotizaciones=grouped_cotizaciones)

@app.route('/nueva_cotizacion', methods=['GET', 'POST'])
def nueva_cotizacion():
    if request.method == 'POST':
        # Extract form data
        folio = request.form.get('folio_cot')
        # Check if folio exists
        existing = read_csv(COTIZACIONES_CSV)
        if any(row['folio_cot'] == folio for row in existing):
            flash(f'El Folio {folio} ya existe.', 'error')
            return redirect(url_for('nueva_cotizacion'))

        base_data = {
            'folio_cot': folio,
            'nombre_cot': request.form.get('nombre_cot'),
            'fecha_cot': request.form.get('fecha_cot') or datetime.date.today().strftime('%d/%m/%Y'),
            'id_cliente': 'CLI-GENERICO', # Simplified for now
            'nombre_cliente': request.form.get('nombre_cliente'),
            'razon_social_cliente': request.form.get('razon_social_cliente'),
            'direccion_cliente': request.form.get('direccion_cliente'),
            'nombre_contacto': request.form.get('nombre_contacto'),
            'telefono_contacto': request.form.get('telefono_contacto'),
            'alcance_cot': request.form.get('alcance_cot'),
            'terminos': request.form.get('terminos'),
            'subtotal': '0.00', # Will be recalculated by the generation script usually, but we should aim to be consistent
            'iva': '0.00',
            'total': '0.00'
        }

        # Handle items (dynamic list from frontend)
        items_names = request.form.getlist('nombre_item[]')
        items_descs = request.form.getlist('descripcion_item[]')
        items_units = request.form.getlist('unidad_item[]')
        items_qty = request.form.getlist('cantidad_item[]')
        items_price = request.form.getlist('precio_unitario_item[]')
        
        rows_to_save = []
        subtotal_acumulado = 0.0
        
        # Primero calcular el subtotal total de la cotización
        for i in range(len(items_names)):
            try:
                qty = float(items_qty[i])
                price = float(items_price[i])
                subtotal_acumulado += (qty * price)
            except:
                pass
        
        iva_total = subtotal_acumulado * 0.16
        total_total = subtotal_acumulado + iva_total
        
        # Actualizar base_data con los totales calculados
        base_data['subtotal'] = f"{subtotal_acumulado:.2f}"
        base_data['iva'] = f"{iva_total:.2f}"
        base_data['total'] = f"{total_total:.2f}"

        for i in range(len(items_names)):
            row = base_data.copy()
            row['nombre_item'] = items_names[i]
            row['descripcion_item'] = items_descs[i]
            row['unidad_item'] = items_units[i]
            row['cantidad_item'] = items_qty[i]
            row['precio_unitario_item'] = items_price[i]
            row['imagen_item'] = '' 
            
            try:
                qty = float(items_qty[i])
                price = float(items_price[i])
                row['importe_item'] = f"{qty * price:.2f}"
            except:
                row['importe_item'] = '0.00'
                
            rows_to_save.append(row)
        
        if not rows_to_save:
            # Create at least one row if no items? Or block?
            flash('Debes agregar al menos un item.', 'error')
            return redirect(url_for('nueva_cotizacion'))

        # Get headers from existing CSV to ensure order
        headers = []
        if os.path.exists(COTIZACIONES_CSV):
            with open(COTIZACIONES_CSV, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                headers = next(reader)
        else:
            # Fallback headers based on what we saw earlier
            headers = ['folio_cot','nombre_cot','fecha_cot','id_cliente','nombre_cliente','razon_social_cliente','direccion_cliente','nombre_contacto','telefono_contacto','alcance_cot','nombre_item','descripcion_item','imagen_item','unidad_item','cantidad_item','precio_unitario_item','importe_item','subtotal','iva','total','terminos']

        # Ensure all keys exist
        for r in rows_to_save:
            for h in headers:
                if h not in r:
                    r[h] = ''

        append_to_csv(COTIZACIONES_CSV, headers, rows_to_save)
        
        # Generar el HTML automáticamente después de guardar
        if generate_quotation_html(folio):
            flash('Cotización guardada y generada exitosamente.', 'success')
        else:
            flash('Cotización guardada en CSV, pero hubo un error al generar el archivo visual.', 'warning')
            
        return redirect(url_for('cotizaciones'))

    # Load inventory and clients for the form
    inventario = read_csv(INVENTARIO_CSV)
    clientes = read_csv(CLIENTES_CSV)
    
    # Get next folio suggestion
    cotizaciones_existentes = read_csv(COTIZACIONES_CSV)
    next_folio_num = 1
    if cotizaciones_existentes:
        try:
            # Try to extract number from last folio (assuming format COT-...-XXX)
            # This is a naive heuristic, can be improved
            last_folio = cotizaciones_existentes[-1]['folio_cot']
            parts = last_folio.replace('-', ' ').split()
            for p in reversed(parts):
                if p.isdigit():
                    next_folio_num = int(p) + 1
                    break
        except:
            pass
    
    suggested_folio = f"COT-COPHI-{next_folio_num:03d}"

    return render_template('crear_cotizacion.html', inventario=inventario, clientes=clientes, suggested_folio=suggested_folio)

@app.route('/ordenes')
def ordenes():
    raw_data = read_csv(ORDENES_CSV)
    return render_template('ordenes.html', ordenes=raw_data)

@app.route('/ver_cotizacion/<folio>')
def ver_cotizacion(folio):
    filename = f"cotizacion_{folio}.html"
    try:
        return send_from_directory(COTIZACIONES_GEN_DIR, filename)
    except FileNotFoundError:
        # Fallback: try finding a file that contains the folio if exact match fails
        # This is strictly for robustness if naming varies
        try:
            files = os.listdir(COTIZACIONES_GEN_DIR)
            for f in files:
                if folio in f and f.endswith('.html'):
                    return send_from_directory(COTIZACIONES_GEN_DIR, f)
        except:
            pass
        return "Archivo no encontrado", 404

@app.route('/cotizacion/<folio>')
def detalle_cotizacion(folio):
    data = get_cotizacion_data(folio)
    if not data:
        flash('Cotización no encontrada.', 'error')
        return redirect(url_for('cotizaciones'))
        
    inventario = read_csv(INVENTARIO_CSV)
    clientes = read_csv(CLIENTES_CSV)
    
    return render_template('crear_cotizacion.html', 
                         cotizacion=data, 
                         inventario=inventario, 
                         clientes=clientes,
                         suggested_folio=folio) # Reuse variable for input value

@app.route('/Plantillas/<path:filename>')
def serve_plantillas(filename):
    plantillas_dir = os.path.abspath(os.path.join(BASE_DIR, '..'))
    return send_from_directory(plantillas_dir, filename)

@app.route('/estilos.css')
def server_css():
    return send_from_directory('static', 'estilos.css')

if __name__ == '__main__':
    app.run(debug=True, port=5000)

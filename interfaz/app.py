from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import csv
import os
import datetime
import math
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flash messages

# Paths configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COTIZACIONES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion', 'cotizaciones.csv'))
ORDENES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Orden de trabajo', 'ordenes_desazolve.csv'))
TRAMPAS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Orden de trabajo', 'ordenes_trampas.csv'))
VISITAS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Visita_tecnica', 'datos_visita_tecnica.csv'))
INVENTARIO_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'productos_servicios.csv'))
CLIENTES_CSV = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Plantillas\inventario\empresas.csv"
TARIFICADOR_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'tarificador', 'datos_tarificador.csv'))
PERMISOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cuestionario_permiso_descargas', 'cuestionario_variables.csv'))
COTIZACIONES_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'cotizaciones'))
PERMISOS_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'Cuestionarios_permiso_descarga'))
TEMPLATE_COT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion'))
TEMPLATE_PERMISOS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cuestionario_permiso_descargas'))

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

def overwrite_csv(filepath, fieldnames, rows):
    with open(filepath, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
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
    
    # Convert to list and reverse to show newest first
    all_cots = list(grouped_cotizaciones.values())[::-1]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = len(all_cots)
    total_pages = math.ceil(total_items / per_page)
    
    # Correct page bounds
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_cots = all_cots[start:end]
    
    return render_template('cotizaciones.html', 
                         cotizaciones=paginated_cots,
                         page=page,
                         total_pages=total_pages)

@app.route('/nueva_cotizacion', methods=['GET', 'POST'])
def nueva_cotizacion():
    if request.method == 'POST':
        # Extract form data
        folio = request.form.get('folio_cot')
        original_folio = request.form.get('original_folio')
        
        # Validation/Duplicate check
        existing = read_csv(COTIZACIONES_CSV)
        
        # If we are strictly creating new (no original_folio), check exists
        if not original_folio and any(row['folio_cot'] == folio for row in existing):
            flash(f'El Folio {folio} ya existe.', 'error')
            return redirect(url_for('nueva_cotizacion'))
            
        # If we are editing, we ignore the collision with SELF, but check collision with OTHERS
        if original_folio:
            # Check if we changed folio to another existing one
            if folio != original_folio and any(row['folio_cot'] == folio for row in existing):
                flash(f'El Folio {folio} ya existe (pertenece a otra cotización).', 'error')
                return redirect(url_for('detalle_cotizacion', folio=original_folio))


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

        # Prepare rows to save
        rows_to_save = []
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
            flash('Debes agregar al menos un item.', 'error')
            return redirect(url_for('nueva_cotizacion'))

        # Get headers
        headers = []
        if existing and len(existing) > 0:
             headers = list(existing[0].keys())
        elif os.path.exists(COTIZACIONES_CSV):
            with open(COTIZACIONES_CSV, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                try:
                    headers = next(reader)
                except:
                     pass
        
        if not headers:
             headers = ['folio_cot','nombre_cot','fecha_cot','id_cliente','nombre_cliente','razon_social_cliente','direccion_cliente','nombre_contacto','telefono_contacto','alcance_cot','nombre_item','descripcion_item','imagen_item','unidad_item','cantidad_item','precio_unitario_item','importe_item','subtotal','iva','total','terminos']

        # Ensure all keys exist
        for r in rows_to_save:
            for h in headers:
                if h not in r:
                    r[h] = ''

        if original_folio:
            # EDIT MODE: Rewrite CSV removing old folio rows and adding new ones
            updated_rows = [r for r in existing if r.get('folio_cot') != original_folio]
            updated_rows.extend(rows_to_save)
            overwrite_csv(COTIZACIONES_CSV, headers, updated_rows)
        else:
            # CREATE MODE: Append
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
        max_num = 0
        for row in cotizaciones_existentes:
            try:
                folio = row.get('folio_cot', '')
                # Assuming format COT-COPHI-XXX or similar standard ending in digits
                # Split by delimiters to be safe
                parts = folio.replace('-', ' ').split()
                # Look for the last numeric part
                for p in reversed(parts):
                    if p.isdigit():
                        num = int(p)
                        if num > max_num:
                            max_num = num
                        break
            except:
                pass
        next_folio_num = max_num + 1
    
    suggested_folio = f"COT-COPHI-{next_folio_num:03d}"

    return render_template('crear_cotizacion.html', inventario=inventario, clientes=clientes, suggested_folio=suggested_folio)

@app.route('/ordenes')
def ordenes():
    desazolves = read_csv(ORDENES_CSV)
    trampas = read_csv(TRAMPAS_CSV)
    visitas = read_csv(VISITAS_CSV)
    return render_template('ordenes.html', desazolves=desazolves, trampas=trampas, visitas=visitas)

@app.route('/tarificador')
def tarificador():
    raw_data = read_csv(TARIFICADOR_CSV)
    
    # Reverse to show newest first
    all_tars = raw_data[::-1]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = len(all_tars) if all_tars else 0
    total_pages = math.ceil(total_items / per_page)
    
    # Correct page bounds
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_tars = all_tars[start:end]
    
    return render_template('tarificador.html', 
                         tarificadores=paginated_tars,
                         page=page,
                         total_pages=total_pages)

# --- Tarificador Logic Helpers ---
# Use functions similar to generar_tarificador.py to ensure consistency
RANGOS_FILE = os.path.abspath(os.path.join(BASE_DIR, '..', 'tarificador', 'rango_incumplimiento.csv'))

def clean_float(value):
    try:
        import re
        match = re.search(r'[\d\.,]+', str(value))
        if match:
            clean_value = match.group().replace(',', '')
            return float(clean_value)
        return 0.0
    except:
        return 0.0

def load_rangos():
    rangos = []
    if not os.path.exists(RANGOS_FILE):
        return rangos
    try:
        with open(RANGOS_FILE, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                min_val = clean_float(row.get('Minimo', 0))
                max_str = row.get('Maximo', '').strip()
                max_val = clean_float(max_str) if max_str else None
                price = clean_float(row.get('Contaminantes Básicos', 0))
                rangos.append({'min': min_val, 'max': max_val, 'price': price})
    except Exception as e:
        print(f"Error loading rangos: {e}")
    return rangos

def get_default_lmps():
    """Obtiene los valores LMP por defecto de la primera fila del CSV (fila 2 en Excel/Editor)."""
    rows = read_csv(TARIFICADOR_CSV)
    if rows:
        return rows[0]
    return {}

def calculate_tarificador_row(row):
    rangos = load_rangos()
    contaminantes = ['sst', 'dbo', 'gya', 'ss', 'mf', 'temp', 'saam', 'dqo', 'nt', 'fen', 'color']
    
    precio_total_m3 = 0.0
    
    for c in contaminantes:
        res = clean_float(row.get(f'{c}_resultado', 0))
        lmp = clean_float(row.get(f'{c}_lmp', 0))
        price = 0.0
        
        if lmp > 0:
            ratio = (res - lmp) / lmp
            if ratio > 0:
                for r in rangos:
                    max_bound = r['max'] if r['max'] is not None else float('inf')
                    if r['min'] < ratio <= max_bound:
                        price = r['price']
                        break
        
        row[f'{c}_precio'] = f"${price:.2f}"
        precio_total_m3 += price
        
    volumen = clean_float(row.get('volumen_promedio_descargado', 0))
    total_pagar = precio_total_m3 * volumen
    
    row['precio_m3_total'] = f"{precio_total_m3:.2f}"
    row['total_pagar'] = f"{total_pagar:.2f}"
    return row

def generate_single_tarificador_html(data):
    # This logic matches generar_tarificador.py but for a single item
    try:
        template_path = os.path.join(BASE_DIR, '..', 'tarificador', 'tarificador.html')
        output_dir = os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'tarificadores')
        
        if not os.path.exists(template_path): return False
        if not os.path.exists(output_dir): os.makedirs(output_dir)
        
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        t = Template(template_content)
        
        # Prepare context (format currency for display)
        ctx = data.copy()
        
        # Simple formatter helper
        fmt = lambda x: f"{clean_float(x):,.2f}"
        
        ctx['precio_m3_total'] = fmt(ctx.get('precio_m3_total', 0))
        ctx['total_pagar'] = fmt(ctx.get('total_pagar', 0))
        
        contaminantes = ['sst', 'dbo', 'gya', 'ss', 'mf', 'temp', 'saam', 'dqo', 'nt', 'fen', 'color']
        for c in contaminantes:
             ctx[f'{c}_precio'] = fmt(ctx.get(f'{c}_precio', 0))
             
        # Paths Fix
        output_html = t.render(**ctx)
        output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
        output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
        output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')
        
        folio = ctx.get('folio_tar', 'SINFOLIO').replace('/', '-')
        filepath = os.path.join(output_dir, f"TARIFICADOR_{folio}.html")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output_html)
            
        return True
    except Exception as e:
        print(f"Error generating tarificador HTML: {e}")
        return False

@app.route('/nuevo_tarificador', methods=['GET', 'POST'])
def nuevo_tarificador():
    if request.method == 'POST':
        folio = request.form.get('folio_tar')
        
        existing = read_csv(TARIFICADOR_CSV)
        headers = []
        if existing: headers = list(existing[0].keys())
        
        # Ensure we have all needed headers if file is empty or new cols needed
        needed_headers = ['folio_tar','fecha_tar','nombre_cliente','no_cliente','direccion_cliente','no_permiso_descargas','vigencia_permiso_descargas','laboratorio','fecha_muestreo','tipo_muestreo','no_informe','volumen_promedio_descargado']
        contaminantes = ['sst', 'dbo', 'gya', 'ss', 'mf', 'temp', 'saam', 'dqo', 'nt', 'fen', 'color']
        for c in contaminantes:
            needed_headers.extend([f'{c}_resultado', f'{c}_lmp', f'{c}_precio'])
        needed_headers.extend(['precio_m3_total', 'total_pagar'])
        
        for h in needed_headers:
             if h not in headers: headers.append(h)
             
        # Create row data
        row = {}
        # Fill from form
        for h in headers:
            row[h] = request.form.get(h, '')
            
        # Ensure ID
        row['folio_tar'] = folio
        if not row.get('fecha_tar'):
             row['fecha_tar'] = datetime.date.today().strftime('%d/%m/%Y')
             
        # Perform Calculations
        row = calculate_tarificador_row(row)
        
        # Decide Append or Update
        updated_rows = [r for r in existing if r.get('folio_tar') != folio]
        updated_rows.append(row)
        
        try:
            overwrite_csv(TARIFICADOR_CSV, headers, updated_rows)
            flash('Tarificador guardado y calculado exitosamente.', 'success')
            
            if generate_single_tarificador_html(row):
                 flash('Documento visual generado.', 'success')
            else:
                 flash('Error generando documento visual.', 'warning')
                 
            return redirect(url_for('tarificador'))
        except Exception as e:
            flash(f'Error guardando: {e}', 'error')
            return redirect(url_for('tarificador'))

    # GET
    clientes = read_csv(CLIENTES_CSV)
    
    # Suggest Folio
    existing = read_csv(TARIFICADOR_CSV)
    max_num = 0
    if existing:
        for r in existing:
            try:
                # Expecting TAR-XXX
                txt = r.get('folio_tar', '')
                import re
                nums = re.findall(r'\d+', txt)
                if nums:
                    val = int(nums[-1])
                    if val > max_num: max_num = val
            except: pass
    suggested_folio = f"TAR-{max_num + 1:03d}"
    
    return render_template('crear_tarificador.html', clientes=clientes, suggested_folio=suggested_folio, todays_date=datetime.date.today().strftime('%d/%m/%Y'), rangos=load_rangos(), default_lmps=get_default_lmps())

@app.route('/tarificador/<folio>')
def detalle_tarificador(folio):
    print(f"Buscando detalle para folio: {folio}")
    rows = read_csv(TARIFICADOR_CSV)
    target = next((r for r in rows if r.get('folio_tar') == folio), None)
    
    if not target:
        flash('Registro no encontrado.', 'error')
        return redirect(url_for('tarificador'))
        
    clientes = read_csv(CLIENTES_CSV)
    # We pass 'tarificador' object to template to trigger Edit Mode
    return render_template('crear_tarificador.html', tarificador=target, clientes=clientes, rangos=load_rangos(), default_lmps=get_default_lmps())

TARIFICADORES_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'tarificadores'))

@app.route('/ver_tarificador/<folio>')
def ver_tarificador(folio):
    safe_folio = folio.replace('/', '-')
    filename = f"TARIFICADOR_{safe_folio}.html"
    try:
        if not os.path.exists(TARIFICADORES_GEN_DIR):
             return "Directorio de documentos no encontrado", 404
             
        return send_from_directory(TARIFICADORES_GEN_DIR, filename)
    except FileNotFoundError:
        return "Archivo no encontrado", 404
    except Exception as e:
        return f"Error leyendo el archivo: {e}", 500

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

def get_orden_data(tipo, folio):
    filepath = ''
    id_key = ''
    
    if tipo == 'desazolve':
        filepath = ORDENES_CSV
        id_key = 'folio_cot' # confusing naming in csv
    elif tipo == 'trampa':
        filepath = TRAMPAS_CSV
        id_key = 'folio_ot'
    elif tipo == 'visita':
        filepath = VISITAS_CSV
        id_key = 'folio_vt'
    else:
        return None, None
        
    rows = read_csv(filepath)
    target = next((r for r in rows if r.get(id_key) == folio), None)
    return target, filepath

@app.route('/nueva_orden/<tipo>', methods=['GET', 'POST'])
def nueva_orden(tipo):
    if request.method == 'POST':
        # Create logic
        folio = request.form.get(
            'folio_cot' if tipo == 'desazolve' else 'folio_ot' if tipo == 'trampa' else 'folio_vt'
        )
        
        filepath = ''
        if tipo == 'desazolve': filepath = ORDENES_CSV
        elif tipo == 'trampa': filepath = TRAMPAS_CSV
        elif tipo == 'visita': filepath = VISITAS_CSV
        
        # Check if already exists? (Optional but good practice)
        existing_rows = read_csv(filepath)
        id_key = 'folio_cot' if tipo == 'desazolve' else 'folio_ot' if tipo == 'trampa' else 'folio_vt'
        
        if any(r.get(id_key) == folio for r in existing_rows):
            flash(f'El Folio {folio} ya existe.', 'error')
            return redirect(url_for('nueva_orden', tipo=tipo))

        # Basic structure based on type
        new_row = {}
        # We need headers to know what keys to expect, or rely on form
        # Better: get headers from existing CSV
        headers = []
        if existing_rows:
            headers = list(existing_rows[0].keys())
        
        # Ensure we have the full expected schema for desazolve regardless of existing CSV
        if tipo == 'desazolve':
            expected_fields = ['folio_cot','fecha_cot','nombre_cliente','direccion_cliente','no_cliente','nombre_contacto','telefono_contacto','ubicacion_area','tipo_tuberia','diametro_tuberia','longitud_sondeada','flujo_nulo','flujo_lento','flujo_normal','equipo_guia','equipo_hidro','equipo_vactor','tipo_obstruccion','volumen_azolve','estado_bueno','estado_danado','estado_obstruido','observaciones','obs_evidencia_01','obs_evidencia_02','obs_evidencia_03','comentarios_cliente']
            for f in expected_fields:
                if f not in headers:
                    headers.append(f)
        
        elif tipo == 'trampa':
            expected_fields = ['folio_ot','fecha_ot','nombre_cliente','direccion_cliente','no_cliente','ubicacion_equipo','tipo_trampa','capacidad_trampa','estado_tapa','nivel_saturacion','accion_retiro_solidos','accion_succion_liquidos','accion_raspado_paredes','accion_lavado_presion','accion_aplicacion_bacterias','accion_prueba_flujo','accion_limpieza_perimetral','volumen_extraido','caracteristicas_residuo','estado_bueno','estado_reparacion','estado_faltantes','observaciones_tecnico','obs_evidencia_01','obs_evidencia_02']
            for f in expected_fields:
                if f not in headers:
                    headers.append(f)
                    
        elif tipo == 'visita':
            matrix_items = ['cisterna','tinacos','tomas','registro','trampas','valvulas','bombas','tuberias','griferia','medidores','fregadero','cespol','coladeras','pluviales','wc']
            matrix_fields = []
            for m in matrix_items:
                matrix_fields.append(f"st_{m}")
                matrix_fields.append(f"obs_{m}")
            
            expected_fields = ['folio_vt','fecha_vt','nombre_cliente','direccion_cliente','no_cliente',
                               'inv_cisterna_no','inv_cisterna_cap','inv_tinacos_no','inv_tinacos_cap','inv_medidor_serie',
                               'inv_medidor_lectura','inv_pipas_sn','inv_pipas_m3','inv_bombas','inv_tanque_hidro',
                               'inv_tomas_no','inv_registro_no','inv_trampas_no','inv_trampas_cap','inv_wc_no',
                               'inv_lavamanos_no','inv_fregaderos_no','inv_ahorro_sn','inv_ahorro_lista',
                               'obs_evidencia_01','obs_evidencia_02','obs_evidencia_03','obs_evidencia_04','hallazgos_comentarios'] + matrix_fields
                               
            for f in expected_fields:
                if f not in headers:
                    headers.append(f)

        elif not headers:
            # Fallback headers if file is empty (Logic above handles schema enforcement, this is just legacy fallback for completely empty files if logic above missed something)
            pass

        # Fill with form data
        for h in headers:
            new_row[h] = request.form.get(h, '')
            
        # Ensure mandatory ID and DATE if not in form (visita usually auto, but let's trust form mostly)
        new_row[id_key] = folio
        new_row['fecha_cot' if tipo == 'desazolve' else 'fecha_ot' if tipo == 'trampa' else 'fecha_vt'] = request.form.get(
             'fecha_cot' if tipo == 'desazolve' else 'fecha_ot' if tipo == 'trampa' else 'fecha_vt') or datetime.date.today().strftime('%d/%m/%Y')
        
        try:
             # Check if we need to update the file structure (if we added headers)
             # But append_to_csv usually just appends. If headers changed, we might need to rewriting or DictWriter will handle if we pass the larger header list?
             # DictWriter writes only what is in fieldnames. If we pass a larger fieldnames list to DictWriter than what is in the file... 
             # If append mode is used, DictWriter keys order must match file columns if we want to be safe? 
             # Actually, if we pass new fieldnames, DictWriter doesn't care about the file content, it just writes that row.
             # BUT new columns won't have headers in the file unless we rewrite it.
             # Ideally we should rewrite the whole file if headers expanded.
             
             if existing_rows and len(headers) > len(existing_rows[0].keys()):
                 # Headers expanded, rewrite file
                 existing_rows.append(new_row)
                 overwrite_csv(filepath, headers, existing_rows)
             else:
                 append_to_csv(filepath, headers, [new_row])
                 
             flash('Orden creada exitosamente.', 'success')
             
             if generate_order_html(tipo, new_row):
                 flash('Documento visual (HTML) generado correctamente.', 'success')
             else:
                 flash('Se guardó el CSV pero falló la generación visual.', 'warning')
                 
             return redirect(url_for('ordenes'))
        except PermissionError:
             flash('PERMISO DENEGADO: Archivo abierto en otro programa.', 'error')
             data = new_row # Keep data to retry
             
    # GET: Prepare empty form
    else:
        # Determine next folio
        prefix = ''
        if tipo == 'desazolve': 
            filepath = ORDENES_CSV
            prefix = 'OT-DES-'
            id_key = 'folio_cot'
        elif tipo == 'trampa': 
            filepath = TRAMPAS_CSV
            prefix = 'OT-TRA-'
            id_key = 'folio_ot'
        else: 
            filepath = VISITAS_CSV
            prefix = 'VT-'
            id_key = 'folio_vt'
            
        rows = read_csv(filepath)
        max_num = 0
        for r in rows:
            try:
                # Extract number from format like PREFIX-001
                # Robust extraction: find last digits
                txt = r.get(id_key, '')
                import re
                nums = re.findall(r'\d+', txt)
                if nums:
                    val = int(nums[-1])
                    if val > max_num: max_num = val
            except: pass
            
        suggested_folio = f"{prefix}{max_num + 1:03d}"
        
        # Empty data structure with just today's date
        data = {
            id_key: suggested_folio,
            'fecha_cot' if tipo == 'desazolve' else 'fecha_ot' if tipo == 'trampa' else 'fecha_vt': datetime.date.today().strftime('%d/%m/%Y')
        }

    clientes = read_csv(CLIENTES_CSV)
    return render_template('crear_orden.html', orden=data, tipo=tipo, folio=data.get(id_key), clientes=clientes, is_new=True)

@app.route('/orden/<tipo>/<folio>', methods=['GET', 'POST'])
def detalle_orden(tipo, folio):
    data, filepath = get_orden_data(tipo, folio)
    
    if not data and request.method == 'GET':
        flash('Orden no encontrada.', 'error')
        return redirect(url_for('ordenes'))

    if request.method == 'POST':
        # Save logic
        # Read all rows again to ensure freshness
        all_rows = read_csv(filepath)
        
        # Determine ID key again
        id_key = 'folio_cot' if tipo == 'desazolve' else 'folio_ot' if tipo == 'trampa' else 'folio_vt'
        
        # Filter out the old row
        updated_rows = [r for r in all_rows if r.get(id_key) != folio]
        
        # Determine Headers
        headers = []
        if all_rows:
            headers = list(all_rows[0].keys())
            
        # Ensure we have the full expected schema for desazolve checks
        if tipo == 'desazolve':
            expected_fields = ['folio_cot','fecha_cot','nombre_cliente','direccion_cliente','no_cliente','nombre_contacto','telefono_contacto','ubicacion_area','tipo_tuberia','diametro_tuberia','longitud_sondeada','flujo_nulo','flujo_lento','flujo_normal','equipo_guia','equipo_hidro','equipo_vactor','tipo_obstruccion','volumen_azolve','estado_bueno','estado_danado','estado_obstruido','observaciones','obs_evidencia_01','obs_evidencia_02','obs_evidencia_03','comentarios_cliente']
            for f in expected_fields:
                if f not in headers:
                    headers.append(f)

        new_row = data.copy() # Start with existing data
        
        # Update from form
        for key in request.form:
             new_row[key] = request.form[key]
             if key not in headers:
                 headers.append(key)
            
        updated_rows.append(new_row)
        
        try:
            overwrite_csv(filepath, headers, updated_rows)
            flash('Orden actualizada exitosamente.', 'success')
            
            # Regenerate HTML
            if generate_order_html(tipo, new_row):
                 flash('Documento visual (HTML) regenerado correctamente.', 'success')
            else:
                 flash('Advertencia: Se guardaron datos pero falló la generación del documento visual.', 'warning')
                 
        except PermissionError:
            flash(f'PERMISO DENEGADO: El archivo "{os.path.basename(filepath)}" está abierto en otro programa (probablemente Excel). Ciérrelo y vuelva a intentar guardar.', 'error')
        except Exception as e:
            flash(f'Ocurrió un error al guardar: {e}', 'error')
        
        # Refresh data (keep user inputs even if save failed/succeeded to reflect state)
        data = new_row

        
    clientes = read_csv(CLIENTES_CSV)
    return render_template('crear_orden.html', orden=data, tipo=tipo, folio=folio, clientes=clientes, is_new=False)


def generate_permiso_html(data):
    """Genera los archivos HTML para permiso de descarga (Cuestionario, Acuse, Carta Poder)."""
    try:
        from jinja2 import Environment, FileSystemLoader
        import re
        
        env = Environment(loader=FileSystemLoader(TEMPLATE_PERMISOS_DIR))
        
        # Plantillas configuradas
        templates_to_gen = [
            {'file': 'v2_cuestionario.html', 'prefix': 'Cuestionario'},
            {'file': 'acuse.html',           'prefix': 'Acuse'},
            {'file': 'carta-poder.html',     'prefix': 'Carta_Poder'}
        ]
        
        # Sanitizar nombre para carpeta
        nombre_entidad = data.get('arr_nombre', '').strip() or data.get('prop_nombre', '').strip() or "SinNombre"
        safe_name = re.sub(r'[<>:"/\\|?*]', '', nombre_entidad).strip()
        current_year = datetime.datetime.now().year
        
        client_folder = f"{safe_name}_Permiso_descargas_{current_year}"
        output_client_path = os.path.join(PERMISOS_GEN_DIR, client_folder)
        
        if not os.path.exists(output_client_path):
            os.makedirs(output_client_path)
            
        # Asegurar imagen header
        header_src = os.path.join(TEMPLATE_PERMISOS_DIR, 'header.JPG')
        header_dst = os.path.join(output_client_path, 'header.JPG')
        if os.path.exists(header_src) and not os.path.exists(header_dst):
            import shutil
            shutil.copy2(header_src, header_dst)
            
        for t_cfg in templates_to_gen:
            template = env.get_template(t_cfg['file'])
            html_content = template.render(**data)
            
            # Ajustar rutas de estilos/scripts si es necesario (asumiendo que v2_cuestionario lo necesita)
            # El script original no lo hacía porque usaba file:// con Playwright.
            # Aquí lo dejamos igual o añadimos ajustes si el usuario lo pide.
            
            filename = f"{t_cfg['prefix']}_{safe_name}_{current_year}.html"
            with open(os.path.join(output_client_path, filename), 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        return True
    except Exception as e:
        print(f"Error generando HTML para permiso: {e}")
        return False



def generate_order_html(tipo, data):
    """Generates the HTML file for a specific order based on its type and data."""
    try:
        # Determine paths
        plantillas_root = os.path.abspath(os.path.join(BASE_DIR, '..'))
        docs_gen_root = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados'))
        
        template_path = ''
        output_dir = ''
        filename = ''
        
        # Prepare context data (copy to avoid mutating original)
        ctx = data.copy()
        
        if tipo == 'desazolve':
            template_path = os.path.join(plantillas_root, 'Orden de trabajo', 'desazolve.html')
            output_dir = os.path.join(docs_gen_root, 'dezasolves')
            
            # Mapper specific to desazolve template
            ctx['folio_ot'] = ctx.get('folio_cot', 'N/A')
            ctx['fecha_ot'] = ctx.get('fecha_cot', 'N/A')
            if 'no_cliente' not in ctx: ctx['no_cliente'] = '---'
            
            # Checkboxes x -> bool
            checkbox_fields = [
                'flujo_nulo', 'flujo_lento', 'flujo_normal',
                'equipo_guia', 'equipo_hidro', 'equipo_vactor',
                'estado_bueno', 'estado_danado', 'estado_obstruido'
            ]
            for field in checkbox_fields:
                val = ctx.get(field, '')
                # Handle inconsistent values ('x', 'on', 'true')
                ctx[field] = val.lower().strip() in ['x', 'on', 'true', '1']
                
            # Default evidences if empty
            if not ctx.get('obs_evidencia_01'): ctx['obs_evidencia_01'] = 'Evidencia inicial del área.'
            if not ctx.get('obs_evidencia_02'): ctx['obs_evidencia_02'] = 'Evidencia final del servicio.'
            if not ctx.get('obs_evidencia_03'): ctx['obs_evidencia_03'] = 'Equipo utilizado durante el proceso.'
            
            filename = f"OT_DESAZOLVE_{ctx['folio_ot']}.html"

        elif tipo == 'trampa':
            template_path = os.path.join(plantillas_root, 'Orden de trabajo', 'limpieza_trampa_grasa.html')
            output_dir = os.path.join(docs_gen_root, 'limpiezas_trampa_grasa')
            
            if 'no_cliente' not in ctx: ctx['no_cliente'] = '---'
            
            checkbox_fields = [
                'accion_retiro_solidos', 'accion_succion_liquidos', 'accion_raspado_paredes',
                'accion_lavado_presion', 'accion_aplicacion_bacterias', 'accion_prueba_flujo',
                'accion_limpieza_perimetral', 'estado_bueno', 'estado_reparacion', 'estado_faltantes'
            ]
            for field in checkbox_fields:
                val = ctx.get(field, '')
                ctx[field] = val.lower().strip() in ['x', 'on', 'true', '1']
                
            if not ctx.get('obs_evidencia_01'): ctx['obs_evidencia_01'] = 'Trampa saturada antes del servicio.'
            if not ctx.get('obs_evidencia_02'): ctx['obs_evidencia_02'] = 'Trampa limpia después del servicio.'
            
            filename = f"OT_TRAMPA_{ctx['folio_ot']}.html"

        elif tipo == 'visita':
            template_path = os.path.join(plantillas_root, 'Visita_tecnica', 'visita_tecnica.html')
            output_dir = os.path.join(docs_gen_root, 'visitas_tecnicas')
            
            folio_vt = ctx.get('folio_vt', 'SINFOLIO').replace('/', '-')
            filename = f"VISITA_TECNICA_{folio_vt}.html"
            
        else:
            return False

        # Read template
        if not os.path.exists(template_path):
             print(f"Template missing: {template_path}")
             return False
             
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        template = Template(template_content)
        output_html = template.render(**ctx)

        # Fix paths
        output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
        output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
        output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')

        # Ensure output dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as out:
            out.write(output_html)
            
        return True
        
    except Exception as e:
        print(f"Error generating order HTML: {e}")
        return False

@app.route('/ver_orden_pdf/<tipo>/<folio>')
def ver_orden_pdf(tipo, folio):
    # Define correct subdirectories based on user input
    # Paths are relative to: C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Documentos_generados
    base_gen = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados'))
    
    folder = ''
    if tipo == 'desazolve':
        # User specified "dezasolves" (sic)
        folder = 'dezasolves' 
    elif tipo == 'trampa':
        folder = 'limpiezas_trampa_grasa'
    elif tipo == 'visita':
        folder = 'visitas_tecnicas'
    else:
        return "Tipo de orden no válido", 400
        
    target_dir = os.path.join(base_gen, folder)
    
    # Robustness: Check for 'desazolves' if 'dezasolves' doesn't exist, just in case
    if tipo == 'desazolve' and not os.path.exists(target_dir):
        alt_dir = os.path.join(base_gen, 'desazolves')
        if os.path.exists(alt_dir):
            target_dir = alt_dir
    
    if os.path.exists(target_dir):
        try:
            files = os.listdir(target_dir)
            # Find file containing folio
            for f in files:
                if folio in f and f.endswith('.html'):
                    return send_from_directory(target_dir, f)
        except Exception as e:
            print(f"Error searching directory {target_dir}: {e}")
            
    return f"Archivo no encontrado para el folio {folio} en {folder}. Asegúrese de haber generado el documento.", 404



@app.route('/permiso_descarga/<nis>')
def detalle_permiso_descarga(nis):
    raw_data = read_csv(PERMISOS_CSV)
    target = next((r for r in raw_data if r.get('nis') == nis), None)
    
    if not target:
        flash('Permiso de descarga no encontrado.', 'error')
        return redirect(url_for('permisos_descarga'))
        
    clientes = read_csv(CLIENTES_CSV)
    return render_template('crear_permiso_descarga.html', permiso=target, clientes=clientes)


@app.route('/permisos_descarga')
def permisos_descarga():
    raw_data = read_csv(PERMISOS_CSV)
    
    # Invertir para mostrar los nuevos primero
    all_permisos = raw_data[::-1]
    
    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 15
    total_items = len(all_permisos)
    total_pages = math.ceil(total_items / per_page)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_permisos = all_permisos[start:end]
    
    return render_template('permiso_descarga.html', 
                         permisos=paginated_permisos,
                         page=page,
                         total_pages=total_pages)


@app.route('/nuevo_permiso_descarga', methods=['GET', 'POST'])
def nuevo_permiso_descarga():
    if request.method == 'POST':
        nis = request.form.get('nis')
        
        existing = read_csv(PERMISOS_CSV)
        headers = []
        if existing:
            headers = list(existing[0].keys())
        else:
            headers = ['nis','nombre_negocio','prop_nombre','prop_direccion','prop_colonia','prop_municipio','prop_telefono','prop_localidad','prop_cp','prop_rfc','arr_nombre','arr_ine','arr_direccion','arr_colonia','arr_municipio','arr_telefono','arr_localidad','arr_cp','arr_rfc','giro_licencia','giro_descripcion','num_empleados','turnos','horario_atencion','pozo','num_concesion','pipas','datos_pipas','red','num_tomas','fuente_otro','total_wc','total_mingitorios','total_lavamanos','total_regaderas','total_cisternas','cap_cisternas','total_tinacos','cap_tinacos','tiene_comedor','mecanismos_ahorro','descarga_muni','promedio_descarga','tiene_registro','localización_registro','profundidad_registro','diametro_registro','material_registro','tiene_medidor_descargas','tiene_pretrat','operación_pretratamiento','disposicion_residuos','desc_pretratamiento','tiene_analisis','fecha_acuse','testigo1_nombre','testigo2_nombre']
            
        new_row = {}
        for h in headers:
            new_row[h] = request.form.get(h, '')
            
        # Normalización básica de Si/No como en el script original
        for k, v in new_row.items():
            if v:
                v_lower = v.strip().lower()
                if v_lower in ['si', 'sí', 'on', 'true']:
                    new_row[k] = 'Si'
                elif v_lower in ['no', 'off', 'false']:
                    new_row[k] = 'No'

        # Actualizar o Añadir
        updated_rows = [r for r in existing if r.get('nis') != nis]
        updated_rows.append(new_row)
        
        try:
            overwrite_csv(PERMISOS_CSV, headers, updated_rows)
            flash('Permiso de descarga guardado exitosamente.', 'success')
            
            if generate_permiso_html(new_row):
                flash('Documentos HTML generados correctamente.', 'success')
            else:
                flash('Se guardó el CSV pero hubo un error al generar los documentos.', 'warning')
                
            return redirect(url_for('permisos_descarga'))
        except Exception as e:
            flash(f'Error al guardar: {e}', 'error')
            return redirect(url_for('permisos_descarga'))

    # GET
    clientes = read_csv(CLIENTES_CSV)
    
    # Sugerir NIS (numericamente si es posible)
    existing = read_csv(PERMISOS_CSV)
    max_num = 0
    if existing:
        for r in existing:
            try:
                import re
                nums = re.findall(r'\d+', str(r.get('nis', '')))
                if nums:
                    val = int(nums[-1])
                    if val > max_num: max_num = val
            except: pass
    suggested_nis = max_num + 1

    return render_template('crear_permiso_descarga.html', clientes=clientes, suggested_nis=suggested_nis)


@app.route('/ver_permiso_pdf/<nis>/<tipo>')
def ver_permiso_pdf(nis, tipo):
    """
    Muestra el HTML generado para un permiso. 
    tipo puede ser: 'Cuestionario', 'Acuse', 'Carta_Poder'
    """
    raw_data = read_csv(PERMISOS_CSV)
    target = next((r for r in raw_data if r.get('nis') == nis), None)
    
    if not target:
        return "Permiso no encontrado", 404
        
    import re
    nombre_entidad = target.get('arr_nombre', '').strip() or target.get('prop_nombre', '').strip() or "SinNombre"
    safe_name = re.sub(r'[<>:"/\\|?*]', '', nombre_entidad).strip()
    current_year = datetime.datetime.now().year
    
    client_folder = f"{safe_name}_Permiso_descargas_{current_year}"
    target_dir = os.path.join(PERMISOS_GEN_DIR, client_folder)
    
    filename = f"{tipo}_{safe_name}_{current_year}.html"
    
    if os.path.exists(os.path.join(target_dir, filename)):
        return send_from_directory(target_dir, filename)
    else:
        return f"Documento {filename} no encontrado en {client_folder}. Intente guardarlo de nuevo para regenerarlo.", 404


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

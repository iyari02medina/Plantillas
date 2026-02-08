from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, make_response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import csv
import os
import datetime
import math
from jinja2 import Template

app = Flask(__name__)
app.secret_key = 'cophi-secret-key-2026' # Cambiar por algo más seguro

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor inicia sesión para acceder."
login_manager.login_message_category = "info"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    users = read_users()
    if user_id in users:
        return User(user_id, users[user_id]['username'])
    return None

def read_users():
    users = {}
    users_file = os.path.join(BASE_DIR, 'usuarios.csv')
    if os.path.exists(users_file):
        with open(users_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                uid = row['username'] # Usamos el username como ID para simplicidad
                users[uid] = row
    return users

# --- Flexible Field Mapping ---
FIELD_MAPPING = {
    'folio_cot': ['folio_cot', 'folio', 'Folio'],
    'nombre_cliente': ['nombre_cliente', 'cliente', 'Cliente', 'Nombre Cliente', 'nombre_empresa'],
    'nombre_cot': ['nombre_cot', 'nombre', 'Nombre', 'nombre_cotizacion', 'nombre_cotización'],
    'fecha_cot': ['fecha_cot', 'fecha', 'Fecha', 'fecha_cotización'],
    'id_cliente': ['id_cliente', 'id', 'ID', 'ID Cliente', 'folio'],
    'razon_social_cliente': ['razon_social_cliente', 'razon_social', 'Razon Social', 'Razón Social'],
    'direccion_cliente': ['direccion_cliente', 'direccion', 'Direccion', 'Dirección'],
    'telefono_contacto': ['telefono_contacto', 'telefono', 'Teléfono', 'Telefono'],
    'nombre_item': ['nombre_item', 'item', 'Nombre', 'Nombre del Concepto'],
    'descripcion_item': ['descripcion_item', 'descripcion', 'Descripción', 'Concepto'],
    'unidad_item': ['unidad_item', 'unidad', 'Unidad'],
    'cantidad_item': ['cantidad_item', 'cantidad', 'Cant', 'Cantidad'],
    'precio_unitario_item': ['precio_unitario_item', 'precio', 'Precio U', 'Precio Unitario', 'Precio'],
    'importe_item': ['importe_item', 'importe', 'Importe', 'Subtotal Item'],
    'subtotal': ['subtotal', 'Subtotal'],
    'iva': ['iva', 'IVA'],
    'total': ['total', 'Total', 'Total Final'],
    'terminos': ['terminos', 'Terminos', 'Términos', 'Condiciones']
}

def safe_get_field(row, field_name):
    """Obtiene un valor del diccionario intentando exact match, case-insensitive y alias."""
    if not row: return ''
    
    # 1. Exact match
    if field_name in row: return str(row[field_name] or '')
    
    # 2. Case insensitive exact match
    for k in row:
        if str(k).lower().strip() == field_name.lower():
            return str(row[k] or '')
            
    # 3. Aliases mapping
    aliases = FIELD_MAPPING.get(field_name, [])
    for alias in aliases:
        if alias in row: return str(row[alias] or '')
        for k in row:
            if str(k).lower().strip() == alias.lower():
                return str(row[k] or '')
                
    return ''
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COTIZACIONES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion', 'cotizaciones.csv'))
ORDENES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Orden de trabajo', 'ordenes_desazolve.csv'))
TRAMPAS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Orden de trabajo', 'ordenes_trampas.csv'))
VISITAS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Visita_tecnica', 'datos_visita_tecnica.csv'))
PRODUCTOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'productos.csv'))
SERVICIOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'servicios.csv'))
CLIENTES_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'empresas.csv'))
TARIFICADOR_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'tarificador', 'datos_tarificador.csv'))
PERMISOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cuestionario_permiso_descargas', 'cuestionario_variables.csv'))
COTIZACIONES_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'cotizaciones'))
PERMISOS_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'Cuestionarios_permiso_descarga'))
TEMPLATE_COT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cotizacion'))
TEMPLATE_PERMISOS_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'Cuestionario_permiso_descargas'))
CONSUMOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Consumos_agua', 'consumos.csv'))
RANGOS_AGUA_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'Consumos_agua', 'rangos.csv'))

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
                for row in reader:
                    # Limpiar llaves y valores (quitar espacios y Nones)
                    clean_row = {str(k).strip(): (str(v) if v is not None else '') 
                                for k, v in row.items() if k is not None}
                    items.append(clean_row)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            try:
                # Fallback
                with open(filepath, mode='r', encoding='latin-1') as f:
                    reader = csv.DictReader(f)
                    items = []
                    for row in reader:
                        clean_row = {str(k).strip(): (str(v) if v is not None else '') 
                                    for k, v in row.items() if k is not None}
                        items.append(clean_row)
            except Exception as e2:
                print(f"Error reading fallback {filepath}: {e2}")

    print(f"Loaded {len(items)} items from {filepath}")
    # Filter out empty rows
    items = [row for row in items if any(val and str(val).strip() for val in row.values())]
    if items:
        print(f"First item keys: {list(items[0].keys())}")
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = read_users()
        if username in users and check_password_hash(users[username]['password'], password):
            user = User(username, username)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    cotizaciones = read_csv(COTIZACIONES_CSV)
    ordenes = read_csv(ORDENES_CSV)
    
    # Simple metrics
    total_cotizaciones = len(set(c['folio_cot'] for c in cotizaciones if c.get('folio_cot')))
    total_ordenes = len(set(o['folio_des'] for o in ordenes if o.get('folio_des')))
    
    return render_template('index.html', total_cotizaciones=total_cotizaciones, total_ordenes=total_ordenes)

@app.route('/cotizaciones')
@login_required
def cotizaciones():
    raw_data = read_csv(COTIZACIONES_CSV)
    
    # Extract search parameters
    q_cliente = request.args.get('cliente', '').lower()
    q_nombre = request.args.get('nombre_cot', '').lower()
    q_mes = request.args.get('mes', '')
    q_anio = request.args.get('anio', '')
    
    # Get available clients for datalist
    clientes_disponibles = sorted(list(set(str(row.get('nombre_cliente')) for row in raw_data if row.get('nombre_cliente'))))

    # Group by folio and filter
    grouped_cotizaciones = {}
    for row in raw_data:
        folio = row.get('folio_cot')
        if not folio: continue
        
        # Apply filters during grouping (optimistic approach: filter out rows that don't match)
        # Note: since multiple rows can have the same folio, we only need to check matches once per folio
        # or check if ANY row for this folio matches. Standard practice here is that folio details are consistent.
        
        if folio not in grouped_cotizaciones:
            # Check filters
            cliente_val = row.get('nombre_cliente', '')
            nombre_val = row.get('nombre_cot', '')
            fecha_val = row.get('fecha_cot', '')
            
            match = True
            if q_cliente and q_cliente not in cliente_val.lower(): match = False
            if q_nombre and q_nombre not in nombre_val.lower(): match = False
            
            if (q_mes or q_anio) and fecha_val:
                parts = fecha_val.split('/')
                if len(parts) == 3:
                    if q_mes and parts[1] != q_mes: match = False
                    if q_anio and parts[2] != q_anio: match = False
                else:
                    match = False
            
            if not match: continue

            grouped_cotizaciones[folio] = {
                'folio': folio,
                'nombre_cot': nombre_val,
                'cliente': cliente_val,
                'fecha': fecha_val,
                'total': row.get('total'),
                'items_count': 0
            }
        
        if folio in grouped_cotizaciones:
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
    # Prepare data for autocompletes
    # 1. All available companies from empresas.csv
    empresas = read_csv(CLIENTES_CSV)
    clientes_all = sorted(list(set((str(row.get('nombre_empresa')) or str(row.get('nombre_cliente')) or '').strip() for row in empresas if row.get('nombre_empresa') or row.get('nombre_cliente'))))
    
    # 2. All quotation names from cotizaciones.csv
    nombres_all = sorted(list(set((str(row.get('nombre_cot')) or '').strip() for row in raw_data if row.get('nombre_cot'))))
    
    return render_template('cotizaciones.html', 
                         cotizaciones=paginated_cots,
                         clientes_disponibles=clientes_disponibles, # Existing (only filtered)
                         clientes_all=clientes_all,
                         nombres_all=nombres_all,
                         page=page,
                         total_pages=total_pages)

@app.route('/nueva_cotizacion', methods=['GET', 'POST'])
@login_required
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
            'id_cliente': request.form.get('id_cliente') or 'CLI-GENERICO',
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
    # Load inventory from both files
    productos = read_csv(PRODUCTOS_CSV)
    servicios = read_csv(SERVICIOS_CSV)
    
    # Add 'categoria' or type if missing and harmonize keys
    inventario = []
    
    # Normalize keys function
    def normalize_item(item, tipo):
        # Utilizar safe_get_field para ser flexible con los nombres de las columnas
        return {
            'nombre': safe_get_field(item, 'nombre_item'),
            'descripcion': safe_get_field(item, 'descripcion_item') or safe_get_field(item, 'nombre_item'),
            'precio': safe_get_field(item, 'precio_unitario_item') or '0',
            'unidad': safe_get_field(item, 'unidad_item') or 'pza',
            'categoria': safe_get_field(item, 'Categoría') or safe_get_field(item, 'categoria') or tipo
        }

    for p in productos:
        inventario.append(normalize_item(p, 'Producto'))
        
    for s in servicios:
        inventario.append(normalize_item(s, 'Servicio'))

    clientes = read_csv(CLIENTES_CSV)
    
    # Get next folio suggestion: Format COT-MMYY-###
    now = datetime.date.today()
    month_str = now.strftime('%m')
    year_str = now.strftime('%y')
    prefix = f"COT-{month_str}{year_str}-"

    cotizaciones_existentes = read_csv(COTIZACIONES_CSV)
    max_num = 0
    if cotizaciones_existentes:
        for row in cotizaciones_existentes:
            f = row.get('folio_cot') or ''
            if f and f.startswith(prefix):
                try:
                    num = int(f.split('-')[-1])
                    if num > max_num: max_num = num
                except: pass
    
    suggested_folio = f"{prefix}{max_num + 1:03d}"

    return render_template('crear_cotizacion.html', 
                         inventario=inventario, 
                         clientes=clientes, 
                         suggested_folio=suggested_folio,
                         todays_date=now.strftime('%d/%m/%Y'))

@app.route('/eliminar_cotizacion/<folio>', methods=['POST'])
@login_required
def eliminar_cotizacion(folio):
    try:
        existing = read_csv(COTIZACIONES_CSV)
        headers = []
        if existing:
            headers = list(existing[0].keys())
        
        # Filter out all rows with the matching folio (Quotations have multiple rows for items)
        updated_rows = [r for r in existing if str(r.get('folio_cot', '')).strip() != str(folio).strip()]
        
        if len(updated_rows) < len(existing):
            # Something was deleted
            overwrite_csv(COTIZACIONES_CSV, headers, updated_rows)
            flash(f'Cotización {folio} eliminada correctamente.', 'success')
        else:
            flash(f'No se encontró la cotización {folio}.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar la cotización: {e}', 'error')
        
    return redirect(url_for('cotizaciones'))

@app.route('/ordenes')
@login_required
def ordenes():
    desazolves = read_csv(ORDENES_CSV)
    trampas = read_csv(TRAMPAS_CSV)
    visitas = read_csv(VISITAS_CSV)
    
    # Filter Desazolves
    q_folio = request.args.get('folio', '').lower()
    q_cliente = request.args.get('cliente', '').lower()
    q_servicio = request.args.get('servicio', '').lower()
    q_mes = request.args.get('mes', '')
    q_anio = request.args.get('anio', '')
    
    if q_folio or q_cliente or q_servicio or q_mes or q_anio:
        filtered = []
        for o in desazolves:
            match = True
            if q_folio and q_folio not in o.get('folio_des', '').lower(): match = False
            if q_cliente and q_cliente not in o.get('nombre_cliente', '').lower(): match = False
            
            # Servicio filter (checks columns: equipo_vactor, equipo_hidro, equipo_guia)
            if q_servicio:
                col = f"equipo_{q_servicio}"
                if o.get(col) != 'x': match = False
                
            # Date filter (expected format DD/MM/YYYY)
            fecha = o.get('fecha_des', '')
            if fecha and (q_mes or q_anio):
                parts = fecha.split('/')
                if len(parts) == 3:
                    if q_mes and parts[1] != q_mes: match = False
                    if q_anio and parts[2] != q_anio: match = False
                else:
                    match = False
            
            if match: filtered.append(o)
        desazolves = filtered

    # Filter Trampas
    t_folio = request.args.get('t_folio', '').lower()
    t_cliente = request.args.get('t_cliente', '').lower()
    t_tipo = request.args.get('t_tipo', '').lower()
    t_capacidad = request.args.get('t_capacidad', '').lower()
    t_mes = request.args.get('t_mes', '')
    t_anio = request.args.get('t_anio', '')
    
    if t_folio or t_cliente or t_tipo or t_capacidad or t_mes or t_anio:
        filtered_t = []
        for o in trampas:
            match = True
            if t_folio and t_folio not in o.get('folio_lt', '').lower(): match = False
            if t_cliente and t_cliente not in o.get('nombre_cliente', '').lower(): match = False
            if t_tipo and t_tipo not in o.get('tipo_trampa', '').lower(): match = False
            if t_capacidad and t_capacidad not in o.get('capacidad_trampa', '').lower(): match = False
            
            # Date filter (expected format DD/MM/YYYY)
            fecha = o.get('fecha_lt', '')
            if fecha and (t_mes or t_anio):
                parts = fecha.split('/')
                if len(parts) == 3:
                    if t_mes and parts[1] != t_mes: match = False
                    if t_anio and parts[2] != t_anio: match = False
                else:
                    match = False
            
            if match: filtered_t.append(o)
        trampas = filtered_t

    # Filter Visitas
    v_folio = request.args.get('v_folio', '').lower()
    v_cliente = request.args.get('v_cliente', '').lower()
    v_direccion = request.args.get('v_direccion', '').lower()
    v_no_cliente = request.args.get('v_no_cliente', '').lower()
    v_mes = request.args.get('v_mes', '')
    v_anio = request.args.get('v_anio', '')
    
    if v_folio or v_cliente or v_direccion or v_no_cliente or v_mes or v_anio:
        filtered_v = []
        for o in visitas:
            match = True
            if v_folio and v_folio not in o.get('folio_vt', '').lower(): match = False
            if v_cliente and v_cliente not in o.get('nombre_cliente', '').lower(): match = False
            if v_direccion and v_direccion not in o.get('direccion_cliente', '').lower(): match = False
            if v_no_cliente and v_no_cliente not in o.get('no_cliente', '').lower(): match = False
            
            # Date filter (expected format DD/MM/YYYY)
            fecha = o.get('fecha_vt', '')
            if fecha and (v_mes or v_anio):
                parts = fecha.split('/')
                if len(parts) == 3:
                    if v_mes and parts[1] != v_mes: match = False
                    if v_anio and parts[2] != v_anio: match = False
                else:
                    match = False
            
            if match: filtered_v.append(o)
        visitas = filtered_v

    # Prepare data for client autocomplete
    empresas = read_csv(CLIENTES_CSV)
    clientes_all = sorted(list(set((str(row.get('nombre_empresa')) or str(row.get('nombre_cliente')) or '').strip() for row in empresas if row.get('nombre_empresa') or row.get('nombre_cliente'))))

    return render_template('ordenes.html', 
                         desazolves=desazolves, 
                         trampas=trampas, 
                         visitas=visitas,
                         clientes_all=clientes_all)

@app.route('/tarificador')
@login_required
def tarificador():
    raw_data = read_csv(TARIFICADOR_CSV)
    
    # Extract search parameters
    q_folio = request.args.get('t_folio', '').lower()
    q_cliente = request.args.get('t_cliente', '').lower()
    q_mes = request.args.get('t_mes', '')
    q_anio = request.args.get('t_anio', '')
    
    if q_folio or q_cliente or q_mes or q_anio:
        filtered = []
        for t in raw_data:
            match = True
            if q_folio and q_folio not in str(t.get('folio_tar', '')).lower(): match = False
            if q_cliente and q_cliente not in str(t.get('nombre_cliente', '')).lower(): match = False
            
            # Date filter (expected format DD/MM/YYYY)
            fecha = t.get('fecha_tar', '')
            if fecha and (q_mes or q_anio):
                parts = fecha.split('/')
                if len(parts) == 3:
                    if q_mes and parts[1] != q_mes: match = False
                    if q_anio and parts[2] != q_anio: match = False
                else:
                    match = False
            elif (q_mes or q_anio) and not fecha:
                match = False
                
            if match: filtered.append(t)
        all_tars = filtered[::-1]
    else:
        # Reverse to show newest first
        all_tars = raw_data[::-1]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = len(all_tars) if all_tars else 0
    total_pages = math.ceil(total_items / per_page)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_tars = all_tars[start:end]
    
    # Get all client names for autocomplete search
    clientes_data = read_csv(CLIENTES_CSV)
    clientes_names = sorted(list(set([(str(r.get('nombre_empresa')) or '').strip() for r in clientes_data if r.get('nombre_empresa')])))
    
    return render_template('tarificador.html', 
                         tarificadores=paginated_tars,
                         page=page,
                         total_pages=total_pages,
                         clientes_all={'clientes': clientes_names})

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
                max_str = (row.get('Maximo') or '').strip()
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
@login_required
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
    
    # Suggest Folio: Format TAR-MMYY-### (e.g., TAR-0226-001)
    now = datetime.date.today()
    month_str = now.strftime('%m')
    year_str = now.strftime('%y')
    prefix = f"TAR-{month_str}{year_str}-"
    
    existing = read_csv(TARIFICADOR_CSV)
    max_num = 0
    if existing:
        for r in existing:
            f = r.get('folio_tar') or ''
            if f and f.startswith(prefix):
                try:
                    # Extract numeric part after prefix
                    parts = f.split('-')
                    if len(parts) >= 3:
                        num = int(parts[2])
                        if num > max_num: max_num = num
                except: pass
    
    suggested_folio = f"{prefix}{max_num + 1:03d}"
    
    return render_template('crear_tarificador.html', clientes=clientes, suggested_folio=suggested_folio, todays_date=now.strftime('%d/%m/%Y'), rangos=load_rangos(), default_lmps=get_default_lmps())

@app.route('/tarificador/<folio>')
@login_required
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

@app.route('/eliminar_tarificador/<folio>', methods=['POST'])
@login_required
def eliminar_tarificador(folio):
    try:
        all_rows = read_csv(TARIFICADOR_CSV)
        headers = []
        if all_rows:
            headers = list(all_rows[0].keys())
        
        # Filter out the matching folio
        updated_rows = [r for r in all_rows if str(r.get('folio_tar', '')).strip() != str(folio).strip()]
        
        if len(updated_rows) < len(all_rows):
            overwrite_csv(TARIFICADOR_CSV, headers, updated_rows)
            flash(f'Registro de tarificación {folio} eliminado correctamente.', 'success')
        else:
            flash(f'No se encontró el registro {folio}.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
        
    return redirect(url_for('tarificador'))

TARIFICADORES_GEN_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..', 'Documentos_generados', 'tarificadores'))

@app.route('/ver_tarificador/<folio>')
@login_required
def ver_tarificador(folio):
    safe_folio = folio.replace('/', '-')
    filename = f"TARIFICADOR_{safe_folio}.html"
    filepath = os.path.join(TARIFICADORES_GEN_DIR, filename)
    
    # Asegurar que el directorio exista
    if not os.path.exists(TARIFICADORES_GEN_DIR):
        os.makedirs(TARIFICADORES_GEN_DIR, exist_ok=True)
        
    # Si el archivo no existe, intentar generarlo al vuelo desde el CSV
    if not os.path.exists(filepath):
        print(f"Archivo {filename} no encontrado en {TARIFICADORES_GEN_DIR}. Intentando generar desde CSV...")
        rows = read_csv(TARIFICADOR_CSV)
        target = next((r for r in rows if r.get('folio_tar') == folio), None)
        if target:
            # Re-calcular para asegurar que los precios estén actualizados
            target = calculate_tarificador_row(target)
            if generate_single_tarificador_html(target):
                print(f"Archivo {filename} generado correctamente.")
            else:
                return "Error al intentar generar el documento visual automáticamente.", 500
        else:
             return f"Archivo no encontrado y el folio '{folio}' no existe en el registro del tarificador.", 404

    try:
        response = make_response(send_from_directory(TARIFICADORES_GEN_DIR, filename))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except FileNotFoundError:
        return "Archivo no encontrado", 404
    except Exception as e:
        return f"Error leyendo el archivo: {e}", 500

@app.route('/ver_cotizacion/<folio>')
@login_required
def ver_cotizacion(folio):
    filename = f"cotizacion_{folio}.html"
    filepath = os.path.join(COTIZACIONES_GEN_DIR, filename)
    
    # Si el archivo no existe, intentar generarlo al vuelo
    if not os.path.exists(filepath):
        print(f"Archivo {filename} no encontrado. Intentando generar desde CSV...")
        success = generate_quotation_html(folio)
        if not success:
            # Fallback: buscar si existe con otro nombre (código existente)
            print(f"Generación fallida o folio no encontrado. Buscando archivos coincidentes...")
            try:
                if os.path.exists(COTIZACIONES_GEN_DIR):
                    files = os.listdir(COTIZACIONES_GEN_DIR)
                    for f in files:
                        if folio in f and f.endswith('.html'):
                            return make_response(send_from_directory(COTIZACIONES_GEN_DIR, f))
            except:
                pass
            return "Archivo no encontrado y no se pudo generar (verifique que el folio exista en el CSV)", 404
            
    try:
        response = make_response(send_from_directory(COTIZACIONES_GEN_DIR, filename))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except FileNotFoundError:
        return "Archivo no encontrado", 404

def get_orden_data(tipo, folio):
    filepath = ''
    id_key = ''
    
    if tipo == 'desazolve':
        filepath = ORDENES_CSV
        id_key = 'folio_des' # confusing naming in csv
    elif tipo == 'trampa':
        filepath = TRAMPAS_CSV
        id_key = 'folio_lt'
    elif tipo == 'visita':
        filepath = VISITAS_CSV
        id_key = 'folio_vt'
    else:
        return None, None
        
    rows = read_csv(filepath)
    target = next((r for r in rows if r.get(id_key) == folio), None)
    return target, filepath

@app.route('/nueva_orden/<tipo>', methods=['GET', 'POST'])
@login_required
def nueva_orden(tipo):
    if request.method == 'POST':
        # Create logic
        folio = request.form.get(
            'folio_des' if tipo == 'desazolve' else 'folio_lt' if tipo == 'trampa' else 'folio_vt'
        )
        
        filepath = ''
        if tipo == 'desazolve': filepath = ORDENES_CSV
        elif tipo == 'trampa': filepath = TRAMPAS_CSV
        elif tipo == 'visita': filepath = VISITAS_CSV
        
        # Check if already exists? (Optional but good practice)
        existing_rows = read_csv(filepath)
        id_key = 'folio_des' if tipo == 'desazolve' else 'folio_lt' if tipo == 'trampa' else 'folio_vt'
        
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
            expected_fields = ['folio_des','fecha_des','nombre_cliente','direccion_cliente','no_cliente','nombre_contacto','telefono_contacto','ubicacion_area','tipo_tuberia','diametro_tuberia','longitud_sondeada','flujo_nulo','flujo_lento','flujo_normal','equipo_guia','equipo_hidro','equipo_vactor','tipo_obstruccion','volumen_azolve','estado_bueno','estado_danado','estado_obstruido','observaciones','obs_evidencia_01','obs_evidencia_02','obs_evidencia_03','comentarios_cliente']
            for f in expected_fields:
                if f not in headers:
                    headers.append(f)
        
        elif tipo == 'trampa':
            expected_fields = ['folio_lt','fecha_lt','nombre_cliente','direccion_cliente','no_cliente','ubicacion_equipo','tipo_trampa','capacidad_trampa','estado_tapa','nivel_saturacion','accion_retiro_solidos','accion_succion_liquidos','accion_raspado_paredes','accion_lavado_presion','accion_aplicacion_bacterias','accion_prueba_flujo','accion_limpieza_perimetral','volumen_extraido','caracteristicas_residuo','estado_bueno','estado_reparacion','estado_faltantes','observaciones_tecnico','obs_evidencia_01','obs_evidencia_02']
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
        new_row['fecha_des' if tipo == 'desazolve' else 'fecha_lt' if tipo == 'trampa' else 'fecha_vt'] = request.form.get(
             'fecha_des' if tipo == 'desazolve' else 'fecha_lt' if tipo == 'trampa' else 'fecha_vt') or datetime.date.today().strftime('%d/%m/%Y')
        
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
        now = datetime.datetime.now()
        mm_yy = now.strftime('%m%y')

        if tipo == 'desazolve': 
            filepath = ORDENES_CSV
            id_key = 'folio_des'
            prefix = f"DZ-{mm_yy}-"
        elif tipo == 'trampa': 
            filepath = TRAMPAS_CSV
            id_key = 'folio_lt'
            prefix = f"TG-{mm_yy}-"
        else: 
            filepath = VISITAS_CSV
            id_key = 'folio_vt'
            prefix = f"VT-{mm_yy}-"
            
        rows = read_csv(filepath)
        max_num = 0
        for r in rows:
            f = r.get(id_key, '')
            if f and f.startswith(prefix):
                try:
                    parts = f.split('-')
                    if len(parts) >= 3:
                        num = int(parts[-1])
                        if num > max_num: max_num = num
                except: pass
        
        suggested_folio = f"{prefix}{max_num + 1:03d}"
        
        # Empty data structure with just today's date
        data = {
            id_key: suggested_folio,
            'fecha_des' if tipo == 'desazolve' else 'fecha_lt' if tipo == 'trampa' else 'fecha_vt': datetime.date.today().strftime('%d/%m/%Y')
        }

    clientes = read_csv(CLIENTES_CSV)
    return render_template('crear_orden.html', orden=data, tipo=tipo, folio=data.get(id_key), clientes=clientes, is_new=True)

@app.route('/eliminar_orden/<tipo>/<folio>', methods=['POST'])
@login_required
def eliminar_orden(tipo, folio):
    try:
        data, filepath = get_orden_data(tipo, folio)
        if not filepath:
            flash('Tipo de orden no válido.', 'error')
            return redirect(url_for('ordenes'))
            
        all_rows = read_csv(filepath)
        id_key = 'folio_des' if tipo == 'desazolve' else 'folio_lt' if tipo == 'trampa' else 'folio_vt'
        
        headers = []
        if all_rows:
            headers = list(all_rows[0].keys())
            
        # Filter out the matching folio
        updated_rows = [r for r in all_rows if str(r.get(id_key, '')).strip() != str(folio).strip()]
        
        if len(updated_rows) < len(all_rows):
            overwrite_csv(filepath, headers, updated_rows)
            flash(f'Orden {folio} eliminada correctamente.', 'success')
        else:
            flash(f'No se encontró la orden {folio}.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar la orden: {e}', 'error')
        
    return redirect(url_for('ordenes', tab=tipo if tipo != 'desazolve' else 'desazolve'))

@app.route('/orden/<tipo>/<folio>', methods=['GET', 'POST'])
@login_required
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
        id_key = 'folio_des' if tipo == 'desazolve' else 'folio_lt' if tipo == 'trampa' else 'folio_vt'
        
        # Filter out the old row
        updated_rows = [r for r in all_rows if r.get(id_key) != folio]
        
        # Determine Headers
        headers = []
        if all_rows:
            headers = list(all_rows[0].keys())
            
        # Ensure we have the full expected schema for desazolve checks
        if tipo == 'desazolve':
            expected_fields = ['folio_des','fecha_des','nombre_cliente','direccion_cliente','no_cliente','nombre_contacto','telefono_contacto','ubicacion_area','tipo_tuberia','diametro_tuberia','longitud_sondeada','flujo_nulo','flujo_lento','flujo_normal','equipo_guia','equipo_hidro','equipo_vactor','tipo_obstruccion','volumen_azolve','estado_bueno','estado_danado','estado_obstruido','observaciones','obs_evidencia_01','obs_evidencia_02','obs_evidencia_03','comentarios_cliente']
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
        
        # Determinar año de la fecha de acuse si existe, si no, año actual
        # Corregido: sincronizado con ver_permiso_pdf
        current_year = datetime.datetime.now().year
        fecha_acuse = str(data.get('fecha_acuse', '')).strip()
        if fecha_acuse and '/' in fecha_acuse:
            try:
                parts = fecha_acuse.split('/')
                if len(parts) == 3:
                     # Tomar el año de la fecha (puede ser dd/mm/aaaa o aaaa/mm/dd dependiendo del input)
                     # Intentamos detectar si el año está al final o al principio
                     if len(parts[2]) == 4: current_year = int(parts[2])
                     elif len(parts[0]) == 4: current_year = int(parts[0])
            except:
                pass

        client_folder = f"{safe_name}_Permiso_descargas_{current_year}"
        output_client_path = os.path.join(PERMISOS_GEN_DIR, client_folder)
        
        if not os.path.exists(output_client_path):
            os.makedirs(output_client_path)
            
        # Asegurar imagen header (el usuario movió la imagen a ../img/header.JPG en la plantilla)
        header_src = os.path.abspath(os.path.join(TEMPLATE_PERMISOS_DIR, '..', 'img', 'header.JPG'))
        header_dst = os.path.join(output_client_path, 'header.JPG')
        
        if os.path.exists(header_src):
            import shutil
            shutil.copy2(header_src, header_dst)
            
        # Mapeo de claves con acentos para compatibilidad con plantillas
        # Algunas plantillas usan keys con acento, pero el CSV no.
        render_data = data.copy()
        mappings = {
            'disposicion_residuos': 'disposición_residuos',
            'localización_registro': 'localizacion_registro', # Por si acaso
            'operación_pretratamiento': 'operacion_pretratamiento'
        }
        for k_csv, k_tpl in mappings.items():
            if k_csv in render_data:
                render_data[k_tpl] = render_data[k_csv]
            if k_tpl in render_data:
                render_data[k_csv] = render_data[k_tpl]

        for t_cfg in templates_to_gen:
            template = env.get_template(t_cfg['file'])
            html_content = template.render(**render_data)
            
            filename = f"{t_cfg['prefix']}_{safe_name}_{current_year}.html"
            
            # Ajustar rutas de estilos/scripts/imágenes para que funcionen tanto en servidor como localmente
            # El patrón ../../../Plantillas/ funciona en el servidor (va a raíz /Plantillas) 
            # y localmente (sube 3 niveles desde Cliente/Permiso/ para llegar a Plantillas)
            html_content = html_content.replace('href="../estilos.css"', 'href="../../../Plantillas/estilos.css"')
            html_content = html_content.replace('src="../paginacion.js"', 'src="../../../Plantillas/paginacion.js"')
            
            # Ajustar la ruta del header para que sea universal
            # Buscamos todas las formas posibles en que pueda estar en la plantilla
            header_url = "../../../Plantillas/img/header.JPG"
            html_content = html_content.replace('src="../img/header.JPG"', f'src="{header_url}"')
            html_content = html_content.replace('src="../img/header.jpg"', f'src="{header_url}"')
            html_content = html_content.replace('src="header.JPG"', f'src="{header_url}"')
            html_content = html_content.replace('src="header.jpg"', f'src="{header_url}"')
            
            with open(os.path.join(output_client_path, filename), 'w', encoding='utf-8') as f:
                f.write(html_content)
                
        print(f"DEBUG: Archivos generados correctamente en {output_client_path}")
        return True
    except Exception as e:
        print(f"ERROR: Fallo en generate_permiso_html: {e}")
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
            ctx['folio_ot'] = ctx.get('folio_des', 'N/A')
            ctx['fecha_ot'] = ctx.get('fecha_des', 'N/A')
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
            
            ctx['folio_ot'] = ctx.get('folio_lt', 'N/A')
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
@login_required
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
                    response = make_response(send_from_directory(target_dir, f))
                    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response.headers['Pragma'] = 'no-cache'
                    response.headers['Expires'] = '0'
                    return response
        except Exception as e:
            print(f"Error searching directory {target_dir}: {e}")
            
    return f"Archivo no encontrado para el folio {folio} en {folder}. Asegúrese de haber generado el documento.", 404



@app.route('/permiso_descarga/<nis>')
@login_required
def detalle_permiso_descarga(nis):
    raw_data = read_csv(PERMISOS_CSV)
    target = next((r for r in raw_data if str(r.get('nis', '')).strip() == str(nis).strip()), None)
    
    if not target:
        flash('Permiso de descarga no encontrado.', 'error')
        return redirect(url_for('permisos_descarga'))
        
    clientes = read_csv(CLIENTES_CSV)
    return render_template('crear_permiso_descarga.html', permiso=target, clientes=clientes)


@app.route('/permisos_descarga')
@login_required
def permisos_descarga():
    raw_data = read_csv(PERMISOS_CSV)
    
    # Extract search parameters
    q_nis = request.args.get('p_nis', '').lower()
    q_cliente = request.args.get('p_cliente', '').lower()
    q_mes = request.args.get('p_mes', '')
    q_anio = request.args.get('p_anio', '')
    
    if q_nis or q_cliente or q_mes or q_anio:
        filtered = []
        for p in raw_data:
            match = True
            if q_nis and q_nis not in str(p.get('nis', '')).lower(): match = False
            
            # Check business name or person name
            cliente_match = False
            if q_cliente:
                if q_cliente in str(p.get('nombre_empresa', '')).lower(): cliente_match = True
                if q_cliente in str(p.get('arr_nombre', '')).lower(): cliente_match = True
                if q_cliente in str(p.get('prop_nombre', '')).lower(): cliente_match = True
                # Added support for p.nombre_negocio if used in templates
                if q_cliente in str(p.get('nombre_negocio', '')).lower(): cliente_match = True
                if not cliente_match: match = False
            
            # Date filter (expected format DD/MM/YYYY)
            fecha = p.get('fecha_acuse', '')
            if fecha and (q_mes or q_anio):
                parts = fecha.split('/')
                if len(parts) == 3:
                    if q_mes and parts[1] != q_mes: match = False
                    if q_anio and parts[2] != q_anio: match = False
                else:
                    match = False
            
            if match: filtered.append(p)
        all_permisos = filtered[::-1]
    else:
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
    
    # Get all client names for autocomplete search
    clientes_data = read_csv(CLIENTES_CSV)
    clientes_names = sorted(list(set([(str(r.get('nombre_empresa')) or '').strip() for r in clientes_data if r.get('nombre_empresa')])))

    return render_template('permiso_descarga.html', 
                         permisos=paginated_permisos,
                         page=page,
                         total_pages=total_pages,
                         clientes_all={'clientes': clientes_names})


@app.route('/nuevo_permiso_descarga', methods=['GET', 'POST'])
@login_required
def nuevo_permiso_descarga():
    if request.method == 'POST':
        nis = request.form.get('nis')
        
        existing = read_csv(PERMISOS_CSV)
        headers = []
        if existing:
            headers = list(existing[0].keys())
        else:
            headers = ['folio', 'fecha_creacion', 'nis','nombre_empresa','prop_nombre','prop_direccion','prop_colonia','prop_municipio','prop_telefono','prop_localidad','prop_cp','prop_rfc','arr_nombre','arr_ine','arr_direccion','arr_colonia','arr_municipio','arr_telefono','arr_localidad','arr_cp','arr_rfc','giro_licencia','giro_descripcion','num_empleados','turnos','horario_atencion','pozo','num_concesion_pozo','pipas','prom_pipas_mes','capacidad_pipas','red','num_tomas','fuente_otro','total_wc','total_mingitorios','total_lavamanos','total_regaderas','total_cisternas','cap_cisternas','total_tinacos','cap_tinacos','tiene_comedor','mecanismos_ahorro','prom_descarga_muni','tiene_registro','localización_registro','profundidad_registro','diametro_registro','material_registro','tiene_medidor_descargas','tiene_pretrat','operación_pretratamiento','disposicion_residuos','desc_pretratamiento','tiene_analisis','fecha_acuse','testigo1_nombre','testigo2_nombre']
            
        # Buscar si ya existe para preservar campos no presentes en el form
        target_existing = next((r for r in existing if str(r.get('nis', '')).strip() == str(nis).strip()), None)
        new_row = target_existing.copy() if target_existing else {}

        # Asegurar que los nuevos campos estén en los encabezados
        expected_fields = ['folio', 'fecha_creacion', 'nombre_empresa', 'num_concesion_pozo', 'prom_pipas_mes', 'capacidad_pipas', 'prom_descarga_muni', 'croquis_imagen']
        for f in expected_fields:
            if f not in headers:
                headers.append(f)
        
        # Definir campos que son checkboxes (si no están en el form, son 'No')
        checkbox_fields = ['pozo','pipas','red','tiene_comedor','descarga_muni','tiene_registro','tiene_medidor_descargas','tiene_pretrat','tiene_analisis']
        
        # Actualizar con datos del formulario
        for h in headers:
            val = request.form.get(h)
            if val is not None:
                new_row[h] = val
            elif h in checkbox_fields:
                new_row[h] = 'No'
            elif h not in new_row:
                 new_row[h] = ''

        # Auto-fill folio and fecha_creacion if new
        if not new_row.get('folio'):
            now = datetime.date.today()
            prefix = f"PER-{now.strftime('%m%y')}-"
            max_num = 0
            for r in existing:
                f = r.get('folio', '')
                if f.startswith(prefix):
                    try:
                        num = int(f.split('-')[-1])
                        if num > max_num: max_num = num
                    except: pass
            new_row['folio'] = f"{prefix}{max_num + 1:03d}"
            
        if not new_row.get('fecha_creacion'):
            new_row['fecha_creacion'] = datetime.date.today().strftime('%d/%m/%Y')

        # Manejo de Archivo Croquis
        croquis_file = request.files.get('croquis_file')
        if croquis_file and croquis_file.filename:
            try:
                # Definir carpeta de destino
                upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img', 'croquis')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                # 1. Borrar imagen anterior si existe para no llenar la memoria
                old_img = new_row.get('croquis_imagen')
                if old_img:
                    old_path = os.path.join(upload_folder, old_img)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except:
                            pass # Ignorar si no se puede borrar en ese momento
                
                # 2. Procesar y guardar la nueva imagen (PNG optimizado)
                from werkzeug.utils import secure_filename
                from PIL import Image
                
                fname = secure_filename(croquis_file.filename)
                safe_nis = str(nis).strip().replace('/', '').replace('\\', '').replace(' ', '_')
                
                # Forzamos formato .png
                final_name = f"croquis_{safe_nis}.png"
                save_path = os.path.join(upload_folder, final_name)
                
                # Abrir imagen con Pillow
                img = Image.open(croquis_file)
                
                # Redimensionar si supera los 800px (manteniendo proporción)
                max_dim = 800
                if img.width > max_dim or img.height > max_dim:
                    img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                
                # Guardar como PNG optimizado
                # 'optimize=True' intenta reducir el tamaño sin perder calidad (compresión sin pérdida)
                img.save(save_path, "PNG", optimize=True)
                
                new_row['croquis_imagen'] = final_name
            except Exception as e:
                print(f"Error saving croquis: {e}")
            
        # Normalización de Si/No y NIS
        new_row['nis'] = str(nis).strip()
        for k, v in new_row.items():
            if v and isinstance(v, str):
                v_str = v.strip().lower()
                if v_str in ['si', 'sí', 'on', 'true']:
                    new_row[k] = 'Si'
                elif v_str in ['no', 'off', 'false']:
                    new_row[k] = 'No'

        # Actualizar o Añadir
        updated_rows = [r for r in existing if str(r.get('nis', '')).strip() != str(nis).strip()]
        updated_rows.append(new_row)
        
        # Asegurar consistencia de columnas en todas las filas para DictWriter
        for r in updated_rows:
            for h in headers:
                if h not in r:
                    r[h] = ''
        
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

    # Suggest Folio: PER-MMYY-###
    now = datetime.date.today()
    prefix = f"PER-{now.strftime('%m%y')}-"
    max_f = 0
    for r in existing:
        f = r.get('folio', '')
        if f.startswith(prefix):
            try:
                num = int(f.split('-')[-1])
                if num > max_f: max_f = num
            except: pass
    suggested_folio = f"{prefix}{max_f + 1:03d}"

    return render_template('crear_permiso_descarga.html', 
                         clientes=clientes, 
                         suggested_nis=suggested_nis, 
                         suggested_folio=suggested_folio,
                         todays_date=now.strftime('%d/%m/%Y'),
                         permiso=None)



@app.route('/eliminar_permiso_descarga/<nis>', methods=['POST'])
@login_required
def eliminar_permiso_descarga(nis):
    try:
        existing = read_csv(PERMISOS_CSV)
        headers = []
        if existing:
            headers = list(existing[0].keys())
        
        # Filter out the permission with the matching NIS
        updated_rows = [r for r in existing if str(r.get('nis', '')).strip() != str(nis).strip()]
        
        if len(updated_rows) < len(existing):
            # Something was deleted
            overwrite_csv(PERMISOS_CSV, headers, updated_rows)
            flash(f'Permiso de descarga con NIS {nis} eliminado correctamente.', 'success')
        else:
            flash(f'No se encontró el permiso con NIS {nis}.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar el permiso: {e}', 'error')
        
    return redirect(url_for('permisos_descarga'))

@app.route('/ver_permiso_pdf/<nis>/<tipo>')
@login_required
def ver_permiso_pdf(nis, tipo):
    """
    Muestra el HTML generado para un permiso. 
    tipo puede ser: 'Cuestionario', 'Acuse', 'Carta_Poder'
    """
    raw_data = read_csv(PERMISOS_CSV)
    target = next((r for r in raw_data if str(r.get('nis', '')).strip() == str(nis).strip()), None)
    
    if not target:
        return "Permiso no encontrado", 404
        
    import re
    nombre_entidad = target.get('arr_nombre', '').strip() or target.get('prop_nombre', '').strip() or "SinNombre"
    safe_name = re.sub(r'[<>:"/\\|?*]', '', nombre_entidad).strip()
    
    # Determinar año de la fecha de acuse (misma lógica que en generate)
    current_year = datetime.datetime.now().year
    fecha_acuse = str(target.get('fecha_acuse', '')).strip()
    if fecha_acuse and '/' in fecha_acuse:
        try:
            parts = fecha_acuse.split('/')
            if len(parts) == 3:
                 if len(parts[2]) == 4: current_year = int(parts[2])
                 elif len(parts[0]) == 4: current_year = int(parts[0])
        except:
            pass
            
    target_folder = f"{safe_name}_Permiso_descargas_{current_year}"
    target_dir = os.path.join(PERMISOS_GEN_DIR, target_folder)
    
    # Si la carpeta exacta no existe, intentar búsqueda robusta como fallback
    if not os.path.exists(target_dir):
        import glob
        search_pattern = os.path.join(PERMISOS_GEN_DIR, f"{safe_name}_Permiso_descargas_*")
        folders = glob.glob(search_pattern)
        if folders:
            folders.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            target_dir = folders[0]
        else:
            return f"No se encontró la carpeta para '{safe_name}'. Asegúrese de haber generado los documentos.", 404
    
    # Buscar el archivo que empiece con el tipo (Cuestionario, Acuse, etc)
    try:
        files = os.listdir(target_dir)
        filename = next((f for f in files if f.startswith(tipo) and f.endswith('.html')), None)
        
        if filename:
            response = make_response(send_from_directory(target_dir, filename))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        else:
            return f"No se encontró el archivo de tipo '{tipo}' en la carpeta.", 404
    except Exception as e:
        return f"Error al acceder a los documentos: {e}", 500


@app.route('/cotizacion/<folio>')
@login_required
def detalle_cotizacion(folio):
    data = get_cotizacion_data(folio)
    if not data:
        flash('Cotización no encontrada.', 'error')
        return redirect(url_for('cotizaciones'))
        
    # Combine products and services for inventory
    productos = read_csv(PRODUCTOS_CSV)
    servicios = read_csv(SERVICIOS_CSV)
    
    inventario = []
    def normalize_item_local(item, tipo):
        return {
            'nombre': item.get('Nombre') or item.get('nombre') or '',
            'descripcion': item.get('Nombre') or item.get('nombre') or '',
            'precio': item.get('Precio') or item.get('precio') or '0',
            'unidad': item.get('Unidad') or item.get('unidad') or 'pza',
            'categoria': item.get('Categoría') or item.get('categoria') or tipo
        }
        
    for p in productos:
        inventario.append(normalize_item_local(p, 'Producto'))
    for s in servicios:
        inventario.append(normalize_item_local(s, 'Servicio'))
        
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

@app.route('/directorio')
@login_required
def directorio():
    return render_template('directorio.html')

@app.route('/catalogo')
@login_required
def catalogo():
    return render_template('Catalogo.html')

PRODUCTOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'productos.csv'))
SERVICIOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'servicios.csv'))

@app.route('/ver_catalogo/<tipo>')
@login_required
def ver_catalogo(tipo):
    if tipo not in ['productos', 'servicios']:
        return redirect(url_for('catalogo'))
    
    csv_file = PRODUCTOS_CSV if tipo == 'productos' else SERVICIOS_CSV
    data = read_csv(csv_file)
    
    # Extract search parameters
    q_search = request.args.get('c_search', '').lower()
    q_cat = request.args.get('c_categoria', '').lower()
    
    # Get available categories for filter
    categorias = sorted(list(set(str(row.get('Categoría')) for row in data if row.get('Categoría'))))

    # Filter data
    filtered_data = []
    for item in data:
        match = True
        
        # General search (ID, Nombre, Categoría)
        if q_search:
            search_fields = ['ID', 'Nombre', 'Categoría', 'Unidad']
            row_match = False
            for field in search_fields:
                if q_search in str(item.get(field, '')).lower():
                    row_match = True
                    break
            if not row_match: match = False
            
        # Category filter
        if q_cat and q_cat != str(item.get('Categoría', '')).lower():
            match = False
            
        if match:
            filtered_data.append(item)
            
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / per_page)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = filtered_data[start:end]
    
    # Headers
    headers = ['ID', 'Nombre', 'Categoría', 'Unidad', 'Precio']
    
    # Names for autocomplete
    autocomplete_names = sorted(list(set((str(row.get('Nombre')) or '').strip() for row in data if row.get('Nombre'))))
    
    return render_template('tabla_catalogo.html',
                         tipo=tipo,
                         data=paginated_data,
                         headers=headers,
                         page=page,
                         total_pages=total_pages,
                         categorias=categorias,
                         autocomplete_names={'items': autocomplete_names})

@app.route('/catalogo/nuevo/<tipo>', methods=['GET'])
@login_required
def nuevo_catalogo_item(tipo):
    is_prod = (tipo == 'productos')
    csv_file = PRODUCTOS_CSV if is_prod else SERVICIOS_CSV
    existing = read_csv(csv_file)
    
    # Suggest ID
    prefix = 'P-' if is_prod else 'S-'
    max_num = 0
    for r in existing:
        try:
            txt = r.get('ID', '')
            import re
            nums = re.findall(r'\d+', txt)
            if nums:
                 val = int(nums[-1])
                 if val > max_num: max_num = val
        except: pass
    suggested_id = f"{prefix}{max_num+1:03d}"
    
    return render_template('crear_catalogo.html', tipo=tipo, is_new=True, item={}, suggested_id=suggested_id)

@app.route('/catalogo/detalle/<tipo>/<id_val>')
@login_required
def detalle_catalogo(tipo, id_val):
    if tipo not in ['productos', 'servicios']: return redirect(url_for('catalogo'))
    
    csv_file = PRODUCTOS_CSV if tipo == 'productos' else SERVICIOS_CSV
    data = read_csv(csv_file)
    
    item = next((r for r in data if str(r.get('ID', '')).strip() == str(id_val).strip()), None)
    
    if not item:
        flash('Item no encontrado.', 'error')
        return redirect(url_for('ver_catalogo', tipo=tipo))
        
    return render_template('crear_catalogo.html', tipo=tipo, is_new=False, item=item)

@app.route('/catalogo/guardar/<tipo>', methods=['POST'])
@login_required
def guardar_catalogo_item(tipo):
    csv_file = PRODUCTOS_CSV if tipo == 'productos' else SERVICIOS_CSV
    existing = read_csv(csv_file)
    headers = ['ID', 'Nombre', 'Categoría', 'Unidad', 'Precio']
    
    item_id = request.form.get('ID')
    original_id = request.form.get('original_ID')
    
    new_row = {
        'ID': item_id,
        'Nombre': request.form.get('Nombre'),
        'Categoría': request.form.get('Categoría'),
        'Unidad': request.form.get('Unidad'),
        'Precio': request.form.get('Precio')
    }
    
    if original_id:
        # Update
        updated_rows = [r for r in existing if str(r.get('ID', '')).strip() != str(original_id).strip()]
        updated_rows.append(new_row)
        # Sort? Maybe by ID
        try:
            updated_rows.sort(key=lambda x: str(x.get('ID') or ''))
        except: pass
        
        overwrite_csv(csv_file, headers, updated_rows)
        flash('Item actualizado correctamente.', 'success')
        
    else:
        # New
        # DUPLICATE CHECK
        if any(r.get('ID') == item_id for r in existing):
             flash(f'El ID {item_id} ya existe. Se sugiere usar otro o editar el existente.', 'error')
             return redirect(url_for('nuevo_catalogo_item', tipo=tipo))
             
        existing.append(new_row)
        overwrite_csv(csv_file, headers, existing)
        flash('Item creado exitosamente.', 'success')
        
    return redirect(url_for('ver_catalogo', tipo=tipo))

@app.route('/catalogo/eliminar/<tipo>/<id_val>', methods=['POST'])
@login_required
def eliminar_catalogo_item(tipo, id_val):
    csv_file = PRODUCTOS_CSV if tipo == 'productos' else SERVICIOS_CSV
    existing = read_csv(csv_file)
    headers = ['ID', 'Nombre', 'Categoría', 'Unidad', 'Precio']
    
    updated_rows = [r for r in existing if str(r.get('ID', '')).strip() != str(id_val).strip()]
    
    if len(updated_rows) < len(existing):
        overwrite_csv(csv_file, headers, updated_rows)
        flash('Item eliminado correctamente.', 'success')
    else:
         flash('No se encontró el ítem para eliminar.', 'error')
         
    return redirect(url_for('ver_catalogo', tipo=tipo))

PROSPECTOS_CSV = os.path.abspath(os.path.join(BASE_DIR, '..', 'inventario', 'prospectos.csv'))

@app.route('/directorio/<tipo>')
@login_required
def ver_directorio(tipo):
    if tipo not in ['clientes', 'prospectos']:
        return redirect(url_for('directorio'))
    
    csv_file = CLIENTES_CSV if tipo == 'clientes' else PROSPECTOS_CSV
    data = read_csv(csv_file)
    
    # Extract search parameters
    q_search = request.args.get('d_search', '').lower()
    q_tipo_emp = request.args.get('d_tipo_emp', '').lower()
    
    # Filter data
    filtered_data = []
    for item in data:
        match = True
        
        # General search (ID, Folio, Name, Address)
        if q_search:
            search_fields = ['folio', 'nombre_empresa', 'propietario_empresa', 'rfc_propietario', 'rfc_empresa', 'calle_num_empresa', 'colonia_empresa', 'municipio_empresa', 'localidad_empresa', 'cp_empresa', 'nombre_usuario', 'titular_pago', 'regimen', 'giro', 'uso', 'contrato_con']
            row_match = False
            for field in search_fields:
                if q_search in str(item.get(field, '')).lower():
                    row_match = True
                    break
            if not row_match: match = False
            
        # Type filter
        if q_tipo_emp and q_tipo_emp != str(item.get('tipo_empresa', '')).lower():
            match = False
            
        if match:
            filtered_data.append(item)
            
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / per_page)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = filtered_data[start:end]
    
    # Headers to show
    headers = []
    if data:
        # Prioritize important headers
        all_keys = list(data[0].keys())
        priority = ['folio', 'nombre_empresa', 'propietario_empresa', 'rfc_propietario', 'rfc_empresa', 'telefono_empresa', 'calle_num_empresa', 'colonia_empresa', 'municipio_empresa', 'localidad_empresa', 'cp_empresa', 'tipo_empresa'] 
        headers = [k for k in priority if k in all_keys]
        # Add others up to 5 cols
        for k in all_keys:
            if k not in headers and len(headers) < 5 and k and not k.startswith('unnamed'):
                headers.append(k)
    else:
         headers = ['nombre_empresa', 'telefono_empresa', 'direccion_empresa', 'tipo_empresa']

    # Get all names for autocomplete (from current CSV)
    names = sorted(list(set((str(r.get('nombre_empresa')) or '').strip() for r in data if r.get('nombre_empresa'))))

    return render_template('tabla_directorio.html', 
                         tipo=tipo, 
                         data=paginated_data, 
                         headers=headers, 
                         page=page, 
                         total_pages=total_pages,
                         clientes_all={'clientes': names})

@app.route('/directorio/eliminar/<tipo>/<id_val>', methods=['POST'])
@login_required
def eliminar_directorio_item(tipo, id_val):
    if tipo not in ['clientes', 'prospectos']:
        return redirect(url_for('directorio'))
        
    csv_file = CLIENTES_CSV if tipo == 'clientes' else PROSPECTOS_CSV
    try:
        existing = read_csv(csv_file)
        headers = []
        if existing:
            headers = list(existing[0].keys())
        
        key = 'folio'
        
        # Deletion logic: try primary key (folio), then ID (for clients), then name
        updated_rows = [r for r in existing if str(r.get(key, '')).strip() != str(id_val).strip()]
        
        if len(updated_rows) == len(existing) and tipo == 'clientes':
            updated_rows = [r for r in existing if str(r.get('ID', '')).strip() != str(id_val).strip()]

        if len(updated_rows) == len(existing):
            normalized_id_val = str(id_val).strip().lower()
            updated_rows = [r for r in existing if str(r.get('nombre_empresa', '')).strip().lower() != normalized_id_val]

        if len(updated_rows) < len(existing):
            overwrite_csv(csv_file, headers, updated_rows)
            flash(f'Registro eliminado correctamente del directorio de {tipo}.', 'success')
        else:
            flash(f'No se encontró el registro para eliminar.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
        
    return redirect(url_for('ver_directorio', tipo=tipo))

@app.route('/directorio/nuevo/<tipo>')
@login_required
def nuevo_directorio_item(tipo):
    csv_file = CLIENTES_CSV if tipo == 'clientes' else PROSPECTOS_CSV
    existing = read_csv(csv_file)
    now = datetime.date.today()
    todays_date = now.strftime('%d/%m/%Y')
    
    # Suggest Folio: CLI-MMYY-### or PRO-MMYY-###
    prefix = ("CLI-" if tipo == 'clientes' else "PRO-") + now.strftime('%m%y') + "-"
    max_num = 0
    for r in existing:
        f = r.get('folio', '')
        if f.startswith(prefix):
            try:
                num = int(f.split('-')[-1])
                if num > max_num: max_num = num
            except: pass
    suggested_folio = f"{prefix}{max_num + 1:03d}"
    
    return render_template('crear_directorio.html', 
                         tipo=tipo, 
                         is_new=True, 
                         item={}, 
                         suggested_folio=suggested_folio,
                         todays_date=todays_date)

@app.route('/directorio/detalle/<tipo>/<id_val>')
@login_required
def detalle_directorio(tipo, id_val):
    if tipo not in ['clientes', 'prospectos']:
        return redirect(url_for('directorio'))
        
    csv_file = CLIENTES_CSV if tipo == 'clientes' else PROSPECTOS_CSV
    data = read_csv(csv_file)
    
    # Find item
    key = 'folio' # Both clients and prospects use 'folio' as primary identifier
    item = next((r for r in data if str(r.get(key, '')).strip() == str(id_val).strip()), None)
    
    # Fallback to 'id_cliente' if legacy key exists in some rows
    if not item:
        item = next((r for r in data if str(r.get('id_cliente', '')).strip() == str(id_val).strip()), None)
    
    # Fallback to 'ID' for clients if numeric ID exists
    if not item and tipo == 'clientes':
        item = next((r for r in data if str(r.get('ID', '')).strip() == str(id_val).strip()), None)

    # Fallback to name if not found by ID
    if not item:
        normalized_id_val = str(id_val).strip().lower()
        item = next((r for r in data if str(r.get('nombre_empresa', '')).strip().lower() == normalized_id_val), None)
    
    if not item:
        flash('Registro no encontrado.', 'error')
        return redirect(url_for('ver_directorio', tipo=tipo))

    # Load Related Data for Clients
    related_data = {}
    if tipo == 'clientes' and item:
        client_id = item.get('folio', '').strip() or item.get('id_cliente', '').strip()
        client_name = item.get('nombre_empresa', '').strip().lower()
        
        def filter_rows(rows, id_keys, name_key='nombre_cliente'):
            res = []
            seen_ids = set() # For avoiding duplicates if multiple lines per entity (like quot items)
            # But duplicate check depends on entity type. 
            # For simplicity, filtering all rows here, dedupe later if needed.
            for r in rows:
                # Check IDs
                match = False
                if client_id:
                    for k in id_keys:
                        if r.get(k, '').strip() == client_id:
                            match = True
                            break
                if not match and client_name:
                    if client_name == r.get(name_key, '').strip().lower():
                        match = True
                
                if match:
                    res.append(r)
            return res

        # Cotizaciones (Deduplicate by folio_cot)
        raw_cots = filter_rows(read_csv(COTIZACIONES_CSV), ['id_cliente'], 'nombre_cliente')
        unique_cots = {}
        for c in raw_cots:
            f = c.get('folio_cot')
            if f and f not in unique_cots:
                unique_cots[f] = c
        related_data['cotizaciones'] = list(unique_cots.values())

        # Ordenes
        related_data['ordenes_des'] = filter_rows(read_csv(ORDENES_CSV), ['no_cliente'], 'nombre_cliente')
        related_data['ordenes_trampa'] = filter_rows(read_csv(TRAMPAS_CSV), ['no_cliente'], 'nombre_cliente')
        # Visitas (maybe not requested explicitly but good to have)
        related_data['ordenes_visita'] = filter_rows(read_csv(VISITAS_CSV), ['no_cliente'], 'nombre_cliente')

        # Tarificador
        related_data['tarificadores'] = filter_rows(read_csv(TARIFICADOR_CSV), ['no_cliente'], 'nombre_cliente')

        # Permisos (Name key might be nombre_empresa)
        related_data['permisos'] = filter_rows(read_csv(PERMISOS_CSV), ['nis'], 'nombre_empresa')

        # Consumos
        consumos_data = filter_rows(read_csv(CONSUMOS_CSV), ['ID_cliente'], 'nombre_cliente')
        # Sort consumos by date (assuming folio/date correlation or just take last in list)
        # Better to sort by folio descending or date if possible. For now, list order (usually chron).
        related_data['consumos'] = consumos_data
        
        # Calculate Current Tariff based on latest consumption (Accumulated for the period)
        latest_consumo = 0.0
        
        try:
            # Determine billing period start date
            corte_day = int(item.get('corte_servicio', 1)) 
            # If invalid day, default to 1
            if corte_day < 1 or corte_day > 31: corte_day = 1
        except:
            corte_day = 1
            
        today = datetime.date.today()
        q_anio = request.args.get('q_anio', '')
        q_mes = request.args.get('q_mes', '')
        
        # Determine Period Start Date
        start_date = None
        end_date = None
        
        try:
             # If filters provided, use them to set start_date
             if q_anio and q_mes:
                 target_year = int(q_anio)
                 target_month = int(q_mes)
                 
                 # Logic change: Selecting 'February' shows the period ENDING in February's cutoff.
                 # This means it shows from Jan corte_day to Feb corte_day.
                 prev_month = target_month - 1
                 prev_year = target_year
                 if prev_month == 0:
                     prev_month = 12
                     prev_year -= 1
                     
                 try:
                     start_date = datetime.date(prev_year, prev_month, corte_day)
                 except ValueError:
                     import calendar
                     last_day = calendar.monthrange(prev_year, prev_month)[1]
                     start_date = datetime.date(prev_year, prev_month, last_day)
                         
             # If no filters (default), use current cycle logic
             if not start_date:
                 if today.day < corte_day:
                     # We are in the period that started last month
                     prev_month = today.month - 1
                     prev_year = today.year
                     if prev_month == 0:
                         prev_month = 12
                         prev_year -= 1
                     try:
                         start_date = datetime.date(prev_year, prev_month, corte_day)
                     except ValueError:
                         import calendar
                         last_day = calendar.monthrange(prev_year, prev_month)[1]
                         start_date = datetime.date(prev_year, prev_month, last_day)
                 else:
                     # We are in the period that started this month
                     try:
                         start_date = datetime.date(today.year, today.month, corte_day)
                     except ValueError:
                         import calendar
                         last_day = calendar.monthrange(today.year, today.month)[1]
                         start_date = datetime.date(today.year, today.month, last_day)
        except Exception as e:
             # Ultimate fallback
             start_date = datetime.date(today.year, today.month, 1)

        # Calculate End Date (Start Date + 1 Month roughly, until next cutoff)
        # Actually we just want consumos >= start_date AND < next_start_date
        # Getting next cutoff date
        try:
            if start_date.month == 12:
                 next_start_date = datetime.date(start_date.year + 1, 1, start_date.day)
            else:
                 try:
                    next_start_date = datetime.date(start_date.year, start_date.month + 1, start_date.day)
                 except ValueError:
                    import calendar
                    last_day = calendar.monthrange(start_date.year, start_date.month + 1)[1]
                    next_start_date = datetime.date(start_date.year, start_date.month + 1, last_day)
        except:
             next_start_date = datetime.date(2100, 1, 1) # Future

        filtered_consumos = []
        if consumos_data and start_date:
            accumulated = 0.0
            for c in consumos_data:
                try:
                    fecha_str = c.get('fecha_lectura', '').strip()
                    lectura_date = None
                    if '-' in fecha_str:
                        # Try YYYY-MM-DD
                        parts = fecha_str.split('-')
                        if len(parts) == 3:
                            if len(parts[0]) == 4: # YYYY-MM-DD
                                lectura_date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                            else: # DD-MM-YYYY
                                lectura_date = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                    elif '/' in fecha_str:
                        # Try DD/MM/YYYY
                        parts = fecha_str.split('/')
                        if len(parts) == 3:
                            if len(parts[2]) == 4: # DD/MM/YYYY
                                lectura_date = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
                            else: # YYYY/MM/DD
                                lectura_date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                    
                    if lectura_date:
                        # Monitor Accumulator: Always for the selected period
                        # Period logic: (start_date, next_start_date]
                        # A reading on the cutoff day belongs to the period ending that day.
                        if lectura_date > start_date and lectura_date <= next_start_date:
                            accumulated += float(c.get('consumo', 0))
                            filtered_consumos.append(c)
                except: pass
            latest_consumo = accumulated
            # Update consumos list to only show filtered? 
            # If user selected a filter, yes. If default, maybe show all (history)?
            # Let's show all in history table but highlight current in monitor?
            # User request: "filtro para filtrar por año y mes".
            # Usually filters affect the list.
            if q_anio and q_mes:
                related_data['consumos'] = filtered_consumos
            else:
                # Default view: Show all history in table, but monitor is current period
                pass 
            
        related_data['latest_consumo'] = latest_consumo
        
        # Pass filter context to template
        related_data['q_anio'] = q_anio or str(start_date.year)
        related_data['q_mes'] = q_mes or str(start_date.month)
            
        related_data['latest_consumo'] = latest_consumo
        related_data['period_start_date'] = start_date.strftime('%d/%m/%Y') if start_date else ''
        
        # Ranges Logic
        raw_rangos = read_csv(RANGOS_AGUA_CSV)
        rangos = []
        for r in raw_rangos:
             # Sanitize keys (remove spaces)
             rangos.append({k.strip(): v for k, v in r.items()})
             
        current_tariff = None
        
        for r in rangos:
            try:
                min_val = float(r.get('minimo', 0))
                max_val = float(r.get('maximo', 999999))
                if min_val <= latest_consumo <= max_val:
                    current_tariff = r
                    break
            except: pass
            
        if not current_tariff and rangos:
             # Fallback logic
             try:
                 first_min = float(rangos[0].get('minimo', 0))
                 if latest_consumo < first_min:
                     current_tariff = rangos[0]
                 else:
                     current_tariff = rangos[-1]
             except:
                 current_tariff = rangos[-1]
             
        related_data['current_tariff'] = current_tariff
        
    return render_template('crear_directorio.html', tipo=tipo, is_new=False, item=item, **related_data)

@app.route('/directorio/guardar/<tipo>', methods=['POST'])
@login_required
def guardar_directorio(tipo):
    csv_file = CLIENTES_CSV if tipo == 'clientes' else PROSPECTOS_CSV
    
    existing = read_csv(csv_file)
    headers = []
    if existing:
        headers = list(existing[0].keys())
    else:
        if tipo == 'clientes':
            headers = ['folio', 'fecha_creacion', 'nombre_empresa', 'propietario_empresa', 'rfc_propietario', 'telefono_empresa', 'calle_num_empresa', 'colonia_empresa', 'municipio_empresa', 'localidad_empresa', 'cp_empresa', 'tipo_empresa', 'razon_social', 'rfc_empresa', 'nombre_usuario', 'corte_servicio', 'titular_pago', 'tarifa', 'regimen', 'giro', 'uso', 'contrato_con', 'no_wc', 'no_mingitorios', 'no_lavamanos', 'no_regaderas']
        else:
            headers = ['folio', 'fecha_creacion', 'nombre_empresa', 'propietario_empresa', 'rfc_propietario', 'telefono_empresa', 'calle_num_empresa', 'colonia_empresa', 'municipio_empresa', 'localidad_empresa', 'cp_empresa', 'tipo_empresa', 'rfc_empresa', 'nombre_usuario', 'corte_servicio', 'titular_pago', 'tarifa', 'regimen', 'giro', 'uso', 'contrato_con', 'no_wc', 'no_mingitorios', 'no_lavamanos', 'no_regaderas']
            
    # Key is always folio now
    key = 'folio'
    id_val = request.form.get('ID') if tipo == 'clientes' else request.form.get('folio')
    
    # Fallback to folio in form if ID not present for clients
    if tipo == 'clientes' and not id_val:
        id_val = request.form.get('folio')
    
    # Handle new fields from form not in headers
    # Always ensure basic fields + others from form serve as headers if missing
    for k in request.form.keys():
        if k not in headers and k != key: 
             headers.append(k)
    
    if id_val:
        # Update
        target = None
        
        # Try finding by numeric ID first (most robust for created items)
        if tipo == 'clientes':
            target = next((r for r in existing if str(r.get('ID', '')).strip() == str(id_val).strip()), None)
            
        # Try finding by primary key (id_cliente/folio)
        if not target:
             target = next((r for r in existing if str(r.get(key, '')).strip() == str(id_val).strip()), None)

        # Fallback to name if ID search fails
        if not target:
            target = next((r for r in existing if str(r.get('nombre_empresa', '')).strip().lower() == str(id_val).strip().lower()), None)
            
        if target:
            # Update target in place
            for k in request.form:
                 target[k] = request.form[k]
             # Ensure headers covers everything
            updated_rows = existing
            flash('Registro actualizado correctamente.', 'success')
        else:
             # If ID passed but not found, create new
             flash('Registro no encontrado para edición, se creó uno nuevo.', 'warning')
             return guardar_nuevo_directorio_logic(tipo, existing, headers, csv_file)
    else:
        # New
        return guardar_nuevo_directorio_logic(tipo, existing, headers, csv_file)

    # Normalize rows
    for r in existing:
        for h in headers:
            if h not in r:
                r[h] = ''
                
    try:
        overwrite_csv(csv_file, headers, existing)
    except Exception as e:
        flash(f'Error al guardar: {e}', 'error')
        
    return redirect(url_for('ver_directorio', tipo=tipo))

def guardar_nuevo_directorio_logic(tipo, existing, headers, csv_file):
    new_row = {}
    
    # Generate ID for clients (numeric internal ID)
    if tipo == 'clientes':
        try:
            max_id = max([int(r.get('ID', 0)) for r in existing if str(r.get('ID','')).isdigit()], default=0)
            new_row['ID'] = max_id + 1
        except:
            new_row['ID'] = 1
            
    # Generate Folio: CLI-MMYY-### or PRO-MMYY-###
    now = datetime.date.today()
    prefix = ("CLI-" if tipo == 'clientes' else "PRO-") + now.strftime('%m%y') + "-"
    max_num = 0
    for r in existing:
        f = r.get('folio', '')
        if f.startswith(prefix):
            try:
                num = int(f.split('-')[-1])
                if num > max_num: max_num = num
            except: pass
    new_row['folio'] = f"{prefix}{max_num + 1:03d}"
    
    # Set Creation Date
    new_row['fecha_creacion'] = now.strftime('%d/%m/%Y')
             
    # Fill Data
    for k in request.form:
        new_row[k] = request.form[k]
        
    # Append
    existing.append(new_row)
    
    # Fix headers
    for k in new_row.keys():
        if k not in headers:
            headers.append(k)
            
    # Normalize
    for r in existing:
        for h in headers:
            if h not in r:
                r[h] = ''
    
    try:
        overwrite_csv(csv_file, headers, existing)
        flash(f'{tipo.capitalize()[:-1]} creado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al guardar: {e}', 'error')
        
    return redirect(url_for('ver_directorio', tipo=tipo))


@app.route('/consumos')
@login_required
def consumos():
    raw_data = read_csv(CONSUMOS_CSV)
    
    # Extract search parameters
    q_folio = request.args.get('c_folio', '').lower()
    q_cliente = request.args.get('c_cliente', '').lower()
    q_mes = request.args.get('c_mes', '')
    q_anio = request.args.get('c_anio', '')
    
    if q_folio or q_cliente or q_mes or q_anio:
        filtered = []
        for c in raw_data:
            match = True
            if q_folio and q_folio not in str(c.get('folio', '')).lower(): match = False
            if q_cliente and q_cliente not in str(c.get('nombre_cliente', '')).lower(): match = False
            
            # Date filter (expected format YYYY-MM-DD in this CSV)
            fecha = c.get('fecha_lectura', '')
            if fecha and (q_mes or q_anio):
                parts = fecha.split('-')
                if len(parts) == 3:
                    # YYYY-MM-DD
                    if q_mes and parts[1] != q_mes: match = False
                    if q_anio and parts[0] != q_anio: match = False
                else:
                    # Fallback if format is different
                    match = False
            elif (q_mes or q_anio) and not fecha:
                match = False
                
            if match: filtered.append(c)
        all_consumos = filtered[::-1]
    else:
        # Reverse to show newest first
        all_consumos = raw_data[::-1]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_items = len(all_consumos)
    total_pages = math.ceil(total_items / per_page)
    
    if page < 1: page = 1
    if page > total_pages and total_pages > 0: page = total_pages
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated_consumos = all_consumos[start:end]
    
    # Get all client names for autocomplete search
    clientes_data = read_csv(CLIENTES_CSV)
    clientes_names = sorted(list(set([(str(r.get('nombre_empresa')) or '').strip() for r in clientes_data if r.get('nombre_empresa')])))

    return render_template('consumos_agua.html', 
                         consumos=paginated_consumos,
                         page=page,
                         total_pages=total_pages,
                         clientes_all={'clientes': clientes_names})

@app.route('/crear_consumo', methods=['GET'])
@login_required
def crear_consumo():
    # Load clients for the search
    clientes = read_csv(CLIENTES_CSV)
    
    # Suggest Folio: CON-MMYY-###
    now = datetime.date.today()
    prefix = f"CON-{now.strftime('%m%y')}-"
    
    existing = read_csv(CONSUMOS_CSV)
    max_num = 0
    if existing:
        for r in existing:
            try:
                # Expecting CON-MMYY-###
                txt = r.get('folio', '')
                if txt.startswith(prefix):
                    nums = txt.split('-')
                    if len(nums) == 3:
                        val = int(nums[2])
                        if val > max_num: max_num = val
            except: pass
    suggested_folio = f"{prefix}{max_num + 1:03d}"
    
    return render_template('crea_consumo.html', clientes=clientes, suggested_folio=suggested_folio)

@app.route('/guardar_consumo', methods=['POST'])
@login_required
def guardar_consumo():
    folio = request.form.get('folio')
    original_folio = request.form.get('original_folio')
    
    existing = read_csv(CONSUMOS_CSV)
    
    # Headers
    headers = []
    if existing:
        headers = list(existing[0].keys())
    if not headers:
        headers = ['folio', 'fecha_registro', 'fecha_lectura', 'ID_cliente', 'nombre_cliente', 'lectura', 'consumo']
        
    # If new, we must not allow the user to override the suggested folio with something invalid
    # though for consistency with other modules we take it from form but check collisions.
    # The user said "user cannot modify the folio" - we already have 'readonly' in HTML.
    
    # If strictly new, let's re-generate prefix to ensure it's correct for CURRENT month
    if not original_folio:
        now = datetime.date.today()
        prefix = f"CON-{now.strftime('%m%y')}-"
        # Only override if the provided folio doesn't match the monthly pattern (failsafe)
        if not folio.startswith(prefix):
            flash('Error en el formato del folio generado.', 'error')
            return redirect(url_for('crear_consumo'))

    # Check duplicates if new
    if not original_folio and any(r.get('folio') == folio for r in existing):
        flash(f'El Folio {folio} ya existe.', 'error')
        return redirect(url_for('crear_consumo'))

    # Prepare row
    row = {}
    for h in headers:
        row[h] = request.form.get(h, '')
        
    # Ensure ID if missing in form for some reason
    row['folio'] = folio

    # Calculate Consumo (Current Reading - Previous Reading)
    try:
        lectura_actual = float(request.form.get('lectura', 0))
        id_cliente = request.form.get('ID_cliente')
        
        # Determine Previous Reading
        # 1. Get all consumes for this client
        client_rows = [r for r in existing if r.get('ID_cliente') == id_cliente]
        
        # 2. Exclude current folio if editing to avoid self-reference (though we want the previous relative to this one)
        # If editing, we need to find the record immediately preceding this one in DATE.
        # If new, we find the record with max date.
        
        # Let's sort client_rows by date
        current_date_str = request.form.get('fecha_lectura', '9999-12-31')
        
        # Filter for records strictly before this date (or same date but created earlier? Date granularity might be insufficient for same-day)
        # Assuming one reading per month/date.
        previous_records = [r for r in client_rows if r.get('folio') != folio and r.get('fecha_lectura', '') < current_date_str]
        
        if previous_records:
             # Sort by date descending
             previous_records.sort(key=lambda x: str(x.get('fecha_lectura') or ''), reverse=True)
             last_record = previous_records[0]
             lectura_anterior = float(last_record.get('lectura', 0))
        else:
             lectura_anterior = 0.0
             
        consumo_val = lectura_actual - lectura_anterior
        # If negative, implies reset or error. Ensure non-negative? User said "calcula desde 0" monthly.
        # If meter reset, maybe just take current reading?
        # For safety/simplicity per request: "diferencia entre la actual y la pasada"
        if consumo_val < 0:
             consumo_val = lectura_actual # Assume baseline reset if previous > current
        
        row['consumo'] = f"{consumo_val:.2f}"
        
    except Exception as e:
        print(f"Error calculating consumption: {e}")
        # Fallback to form value if calculation fails
        row['consumo'] = request.form.get('consumo', '0')

    if original_folio:
        # Edit
        updated_rows = [r for r in existing if r.get('folio') != original_folio]
        updated_rows.append(row)
        # Re-sort entire CSV by folio or date? Keeping original order mostly, but appended.
        # Maybe better to sort list by folio to keep it clean.
        updated_rows.sort(key=lambda x: str(x.get('folio') or '')) # Simple sort
        
        overwrite_csv(CONSUMOS_CSV, headers, updated_rows)
        flash('Consumo actualizado exitosamente.', 'success')
    else:
        # New
        append_to_csv(CONSUMOS_CSV, headers, [row])
        flash('Consumo registrado exitosamente.', 'success')
        
    return redirect(url_for('consumos'))

@app.route('/eliminar_consumo/<folio>', methods=['POST'])
@login_required
def eliminar_consumo(folio):
    try:
        all_rows = read_csv(CONSUMOS_CSV)
        headers = []
        if all_rows:
            headers = list(all_rows[0].keys())
        
        # Filter out the matching folio
        updated_rows = [r for r in all_rows if str(r.get('folio', '')).strip() != str(folio).strip()]
        
        if len(updated_rows) < len(all_rows):
            overwrite_csv(CONSUMOS_CSV, headers, updated_rows)
            flash(f'Registro de consumo {folio} eliminado correctamente.', 'success')
        else:
            flash(f'No se encontró el registro {folio}.', 'error')
            
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
        
    return redirect(url_for('consumos'))

@app.route('/consumo/<folio>')
def detalle_consumo(folio):
    print(f"Buscando detalle para consumo folio: {folio}")
    rows = read_csv(CONSUMOS_CSV)
    target = next((r for r in rows if r.get('folio') == folio), None)
    
    if not target:
        flash('Consumo no encontrado.', 'error')
        return redirect(url_for('consumos'))
        
    clientes = read_csv(CLIENTES_CSV)
    return render_template('crea_consumo.html', consumo=target, clientes=clientes)

@app.route('/calendario')
@login_required
def calendario():
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    # Función helper para convertir fechas a formato ISO
    def parse_fecha(fecha_str):
        """Convierte fecha de DD/MM/YYYY o YYYY-MM-DD a YYYY-MM-DD"""
        if not fecha_str:
            return None
        
        fecha_str = str(fecha_str).strip()
        
        try:
            # Intentar formato YYYY-MM-DD primero (ya está en formato ISO)
            if '-' in fecha_str and len(fecha_str.split('-')[0]) == 4:
                return fecha_str
            
            # Intentar formato DD/MM/YYYY
            if '/' in fecha_str:
                partes = fecha_str.split('/')
                if len(partes) == 3:
                    dia, mes, anio = partes
                    return f"{anio}-{mes.zfill(2)}-{dia.zfill(2)}"
        except:
            pass
        
        return None
    
    # Leer todos los eventos de los CSVs
    eventos = []
    
    # Órdenes de Desazolve
    desazolves = read_csv(ORDENES_CSV)
    for d in desazolves:
        fecha_iso = parse_fecha(d.get('fecha_des', ''))
        if fecha_iso:
            eventos.append({
                'title': f"Desazolve - {d.get('nombre_cliente', 'Sin cliente')}",
                'start': fecha_iso,
                'color': '#0099cf',  # Primary
                'url': f"/orden/desazolve/{d.get('folio_des', '')}"
            })
    
    # Órdenes de Trampa
    trampas = read_csv(TRAMPAS_CSV)
    for t in trampas:
        fecha_iso = parse_fecha(t.get('fecha_lt', ''))
        if fecha_iso:
            eventos.append({
                'title': f"Trampa - {t.get('nombre_cliente', 'Sin cliente')}",
                'start': fecha_iso,
                'color': '#6ebe43',  # Secondary
                'url': f"/orden/trampa/{t.get('folio_lt', '')}"
            })
    
    # Visitas Técnicas
    visitas = read_csv(VISITAS_CSV)
    for v in visitas:
        fecha_iso = parse_fecha(v.get('fecha_vt', ''))
        if fecha_iso:
            eventos.append({
                'title': f"Visita - {v.get('nombre_cliente', 'Sin cliente')}",
                'start': fecha_iso,
                'color': '#ff9800',  # Orange
                'url': f"/orden/visita/{v.get('folio_vt', '')}"
            })
    
    # Análisis de Laboratorio
    tarificador = read_csv(TARIFICADOR_CSV)
    for tar in tarificador:
        fecha_iso = parse_fecha(tar.get('fecha_tar', ''))
        if fecha_iso:
            eventos.append({
                'title': f"Análisis - {tar.get('nombre_cliente', 'Sin cliente')}",
                'start': fecha_iso,
                'color': '#9c27b0',  # Purple
                'url': f"/tarificador/{tar.get('folio_tar', '')}"
            })
    
    return render_template('calendario.html', 
                          now_formatted=today.isoformat(),
                          tomorrow_formatted=tomorrow.isoformat(),
                          eventos=eventos)

@app.route('/api/actualizar_fecha_evento', methods=['POST'])
@login_required
def actualizar_fecha_evento():
    """API para actualizar la fecha de un evento (drag and drop del calendario)"""
    from flask import jsonify
    
    try:
        data = request.get_json()
        tipo = data.get('tipo', '')
        folio = data.get('folio', '')
        nueva_fecha = data.get('nueva_fecha', '')  # Formato YYYY-MM-DD
        
        if not tipo or not folio or not nueva_fecha:
            return jsonify({'success': False, 'error': 'Datos incompletos'})
        
        # Determinar qué CSV modificar y qué campo de fecha usar
        csv_info = {
            'desazolve': {'csv': ORDENES_CSV, 'campo_folio': 'folio_des', 'campo_fecha': 'fecha_des'},
            'trampa': {'csv': TRAMPAS_CSV, 'campo_folio': 'folio_lt', 'campo_fecha': 'fecha_lt'},
            'visita': {'csv': VISITAS_CSV, 'campo_folio': 'folio_vt', 'campo_fecha': 'fecha_vt'},
            'tarificador': {'csv': TARIFICADOR_CSV, 'campo_folio': 'folio_tar', 'campo_fecha': 'fecha_tar'}
        }
        
        if tipo not in csv_info:
            return jsonify({'success': False, 'error': f'Tipo de evento no válido: {tipo}'})
        
        info = csv_info[tipo]
        csv_path = info['csv']
        campo_folio = info['campo_folio']
        campo_fecha = info['campo_fecha']
        
        # Leer el CSV
        rows = read_csv(csv_path)
        
        # Buscar y actualizar el registro
        encontrado = False
        for row in rows:
            if row.get(campo_folio) == folio:
                row[campo_fecha] = nueva_fecha
                encontrado = True
                break
        
        if not encontrado:
            return jsonify({'success': False, 'error': f'No se encontró el evento con folio {folio}'})
        
        # Guardar el CSV actualizado
        if rows:
            fieldnames = list(rows[0].keys())
            overwrite_csv(csv_path, fieldnames, rows)
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

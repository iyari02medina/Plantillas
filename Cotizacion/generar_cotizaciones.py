import csv
import os
import shutil
import re
from jinja2 import Environment, FileSystemLoader

def clean_float(value):
    """Limpia y convierte un valor a float. Maneja símbolos de moneda, comas y texto adicional."""
    if not value: return 0.0
    try:
        # Extraer solo el primer número encontrado (útil para "1 mensual")
        match = re.search(r'[\d\.,]+', str(value))
        if match:
            clean_value = match.group().replace(',', '')
            return float(clean_value)
        return 0.0
    except:
        return 0.0

def format_currency(value):
    """Formatea un número como moneda sin el símbolo $ (para ser añadido en el template si se desea)"""
    return f"{value:,.2f}"

# Configuración
base_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(base_dir, 'cotizaciones.csv')
template_file = 'plantilla_cotizacion.html'
output_dir = os.path.join(base_dir, '..', '..', 'Documentos_generados', 'cotizaciones')

# Crear directorio de salida si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Configuración de Jinja2
env = Environment(loader=FileSystemLoader(base_dir))
template = env.get_template(template_file)

# Leer CSV y Agrupar Datos
rows_to_update = []
quotations_totals = {}

with open(csv_file, mode='r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    header = [h.strip() for h in header]
    
    for row_values in reader:
        if not row_values: continue
        row = dict(zip(header, row_values))
        
        folio = row.get('folio_cot')
        if not folio:
            continue
            
        # Cálculos numéricos para agrupación
        cantidad = clean_float(row.get('cantidad_item', '0'))
        precio = clean_float(row.get('precio_unitario_item', '0'))
        importe = cantidad * precio
        
        if folio not in quotations_totals:
            quotations_totals[folio] = {
                'subtotal': 0.0,
                'items_calculated': []
            }
        
        quotations_totals[folio]['subtotal'] += importe
        
        # Guardar datos calculados del item en la fila para el CSV
        row['importe_item'] = f"{importe:.2f}"
        rows_to_update.append(row)

# Calcular IVA y Total por Folio
for folio, data in quotations_totals.items():
    data['iva'] = data['subtotal'] * 0.16
    data['total'] = data['subtotal'] + data['iva']

# Actualizar filas finales (subtotal, iva, total) y preparar para HTML
quotations = {}
for row in rows_to_update:
    folio = row['folio_cot']
    totals = quotations_totals[folio]
    
    # Actualizar fila para el CSV (valores sin formato para evitar errores futuros en python)
    row['subtotal'] = f"{totals['subtotal']:.2f}"
    row['iva'] = f"{totals['iva']:.2f}"
    row['total'] = f"{totals['total']:.2f}"
    
    # Estructura para Jinja2
    if folio not in quotations:
        quotations[folio] = {
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
            'subtotal': format_currency(totals['subtotal']),
            'iva': format_currency(totals['iva']),
            'total': format_currency(totals['total']),
            'items': [],
            'unique_images': [],
            'seen_images': set()
        }
    
    # Agregar item al HTML (con formato)
    quotations[folio]['items'].append({
        'nombre_item': row.get('nombre_item', ''),
        'descripcion_item': row.get('descripcion_item', ''),
        'unidad_item': row.get('unidad_item', ''),
        'cantidad_item': row.get('cantidad_item', ''),
        'precio_unitario_item': format_currency(clean_float(row.get('precio_unitario_item'))),
        'importe_item': format_currency(clean_float(row.get('importe_item'))),
        'imagen_item': row.get('imagen_item', '')
    })

    # Imágenes y Alcance
    img = row.get('imagen_item', '')
    if img and img not in quotations[folio]['seen_images']:
        quotations[folio]['seen_images'].add(img)
        quotations[folio]['unique_images'].append({'filename': img, 'caption': row.get('nombre_item', '')})
    
    if 'alcance_lines' not in quotations[folio]:
        quotations[folio]['alcance_lines'] = row.get('alcance_cot', '').split('\n')

# 1. ACTUALIZAR EL ARCHIVO CSV
try:
    with open(csv_file, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows_to_update)
    print(f"CSV actualizado correctamente: {csv_file}")
except Exception as e:
    print(f"Error actualizando CSV: {e}")

# 2. GENERAR ARCHIVOS HTML
for folio, data in quotations.items():
    try:
        output = template.render(data)
        
        # Ajustar rutas para el archivo final generado
        output = output.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
        output = output.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
        output = output.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')
        
        output_filename = os.path.join(output_dir, f'cotizacion_{folio}.html')
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Generado: {output_filename}')
    except Exception as e:
        print(f"Error generando folio {folio}: {e}")



import csv
import os
import shutil
from jinja2 import Environment, FileSystemLoader

# Configuración
csv_file = 'cotizaciones.csv'
template_file = 'diseno-sin-imagen.html'
output_dir = 'output'
css_source = 'estilos.css'

# Crear directorio de salida si no existe
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Copiar archivo CSS a la carpeta de salida
if os.path.exists(css_source):
    shutil.copy(css_source, output_dir)
    print(f"Copiado {css_source} a {output_dir}")
else:
    print(f"Advertencia: No se encontró {css_source}")



# Configuración de Jinja2
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template(template_file)

# Leer CSV y Agrupar Datos
quotations = {}

with open(csv_file, mode='r', encoding='utf-8-sig') as f:
    # Leer encabezado manualmente para limpiar espacios
    reader = csv.reader(f)
    header = next(reader)
    header = [h.strip() for h in header]
    
    # Volver a leer con DictReader usando el encabezado limpio
    # No podemos reiniciar el generador f facilmente sin seek, asi que creamos un DictReader manual
    
    for row_values in reader:
        if not row_values: continue
        # Crear diccionario combinando header y valores
        row = dict(zip(header, row_values))
        
        folio = row.get('folio_cot')
        if not folio:
            continue
            
        if folio not in quotations:
            # Inicializar con los datos comunes de la primera fila encontrada para este folio
            quotations[folio] = {
                'folio_cot': folio,
                'nombre_cot': row.get('nombre_cot', ''),
                'fecha_cot': row.get('fecha_cot', ''),
                'nombre_cliente': row.get('nombre_cliente', ''),
                'direccion_cliente': row.get('direccion_cliente', ''),
                'nombre_contacto': row.get('nombre_contacto', ''),
                'telefono_contacto': row.get('telefono_contacto', ''),
                'alcance_cot': row.get('alcance_cot', ''),
                'subtotal': row.get('subtotal', '0.00'),
                'iva': row.get('iva', '0.00'),
                'total': row.get('total', '0.00'),
                'terminos': row.get('terminos', ''),
                # Valores por defecto o placeholders si no están en el CSV
                'gestor': 'ING. EJEMPLO GESTOR', 
                'puesto_gestor': 'GERENTE DE PROYECTOS',
                'items': []
            }
        else:
            # Si ya existe, actualizar subtotal, iva, total y terminos si vienen en esta fila
            if row.get('subtotal'): quotations[folio]['subtotal'] = row.get('subtotal')
            if row.get('iva'): quotations[folio]['iva'] = row.get('iva')
            if row.get('total'): quotations[folio]['total'] = row.get('total')
            if row.get('terminos'): quotations[folio]['terminos'] = row.get('terminos')
        
        # Agregar detalles del item
        quotations[folio]['items'].append({
            'nombre_item': row.get('nombre_item', ''),
            'descripcion_item': row.get('descripcion_item', ''),
            'unidad_item': row.get('unidad_item', ''),
            'cantidad_item': row.get('cantidad_item', ''),
            'precio_unitario_item': row.get('precio_unitario_item', ''),
            'importe_item': row.get('importe_item', ''),
            'imagen_item': row.get('imagen_item', '')
        })

        # Actualizar lista de imágenes únicas para este folio
        if 'unique_images' not in quotations[folio]:
            quotations[folio]['unique_images'] = []
            quotations[folio]['seen_images'] = set()

        img = row.get('imagen_item', '')
        nombre_item = row.get('nombre_item', '')
        
        if img and img not in quotations[folio]['seen_images']:
            quotations[folio]['seen_images'].add(img)
            quotations[folio]['unique_images'].append({
                'filename': img,
                'caption': nombre_item
            })
            
        # Actualizar alcance_lines si no existe (solo necesitamos hacerlo una vez por folio, pero es barato)
        if 'alcance_lines' not in quotations[folio]:
            quotations[folio]['alcance_lines'] = row.get('alcance_cot', '').split('\n')
        elif not quotations[folio]['alcance_cot'] and row.get('alcance_cot'):
            quotations[folio]['alcance_cot'] = row.get('alcance_cot')
            quotations[folio]['alcance_lines'] = row.get('alcance_cot').split('\n')


# Generar Archivos
for folio, data in quotations.items():
    try:
        output = template.render(data)
        output_filename = os.path.join(output_dir, f'cotizacion_{folio}.html')
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f'Generado: {output_filename}')
    except Exception as e:
        print(f"Error generando folio {folio}: {e}")

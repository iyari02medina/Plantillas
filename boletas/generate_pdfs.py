
import os
import csv
import shutil
from playwright.sync_api import sync_playwright

# Obtener el directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Nombre del archivo CSV y de la plantilla HTML (rutas absolutas)
csv_filename = os.path.join(current_dir, 'V2_Consumos_agua_Excedentes_Contaminantes.csv')
template_filename = os.path.join(current_dir, 'boleta_kentro.html')

# Leer el contenido de la plantilla HTML
with open(template_filename, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Lista para almacenar los archivos HTML generados
html_files = []

# Definir la ruta base de salida: .../Documentos_generados/boletas
# Definir la ruta base de salida: .../Documentos_generados/boletas
# current_dir ya fue definido arriba
output_base_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'Documentos_generados', 'boletas'))

# Crear la carpeta base si no existe
if not os.path.exists(output_base_dir):
    os.makedirs(output_base_dir)

# Leer el archivo CSV y procesar cada fila
with open(csv_filename, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Verificar si la columna 'excedentes_contaminantes' es 'si'
        if row.get('excedentes_contaminantes', '').strip().lower() == 'si':
            # Obtener el mes de consumo para nombrar la carpeta
            mes_consumo = row.get('mes_consumo', 'sin_mes').strip()
            
            # Definir la carpeta destino dentro de Documentos_generados/boletas/mes_consumo
            target_folder = os.path.join(output_base_dir, mes_consumo)

            # Crear la carpeta si no existe
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            # Crear una copia del contenido de la plantilla para modificar
            new_html_content = template_content
            
            # Preparar el contexto para Jinja2
            context = {}
            numeric_columns = ['consumo', 'precio_m3', 'IVA', 'precio_total', 'precio']
            
            for key, value in row.items():
                # Formatear a dos decimales si la columna es numérica
                if key in numeric_columns:
                    try:
                        # Limpiar el valor de posibles caracteres no numéricos excepto punto y menos
                        clean_value = str(value).replace(',', '').strip()
                        if clean_value:
                           context[key] = f"{float(clean_value):,.2f}"
                        else:
                           context[key] = value
                    except (ValueError, TypeError):
                        context[key] = value # Dejar el valor original si no se puede convertir
                else:
                    context[key] = value

            # Renderizar la plantilla usando Jinja2
            from jinja2 import Template
            template = Template(template_content)
            new_html_content = template.render(context)
            
            # Generar el nombre del nuevo archivo HTML
            local_name = row.get('Local', 'desconocido').strip().replace(' ', '_')
            output_filename = os.path.join(target_folder, f'Boleta_local_{local_name}_{mes_consumo}.html')
            
            # Guardar el nuevo archivo HTML
            with open(output_filename, 'w', encoding='utf-8') as new_f:
                new_f.write(new_html_content)
            
            # Agregar a la lista para convertir a PDF
            html_files.append(output_filename)

print(f"Se han generado {len(html_files)} archivos HTML.")
print("Generando archivos PDF...")

# Convertir HTML a PDF usando Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    for html_file in html_files:
        # Generar nombre del archivo PDF
        pdf_file = html_file.replace('.html', '.pdf')
        
        # Convertir ruta a URL absoluta
        html_path = os.path.abspath(html_file)
        file_url = f'file:///{html_path.replace(os.sep, "/")}'
        
        # Navegar al HTML y guardar como PDF
        page.goto(file_url)
        page.pdf(path=pdf_file, format='A4', print_background=True)
        
        print(f"✓ PDF generado: {pdf_file}")
    
    browser.close()

print(f"\n✅ Proceso completado. Se han generado {len(html_files)} archivos HTML y PDF en sus respectivas carpetas.")

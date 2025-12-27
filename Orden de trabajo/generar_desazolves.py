import csv
import os
from jinja2 import Template

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "desazolve.html")
CSV_FILE = os.path.join(BASE_DIR, "ordenes_desazolve.csv")
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Documentos_generados\dezasolves"

def generar_html():
    # Crear directorio de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio creado: {OUTPUT_DIR}")

    # Cargar plantilla
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    template = Template(template_content)

    # Leer CSV y generar archivos
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Mapeo de campos si los nombres en el CSV difieren de la plantilla
            # En el CSV es folio_cot, en plantilla es folio_ot
            data = row.copy()
            data['folio_ot'] = row.get('folio_cot', 'N/A')
            data['fecha_ot'] = row.get('fecha_cot', 'N/A')
            data['no_cliente'] = row.get('no_cliente', '---')
            
            # Asegurar que los campos de checkbox sean booleanos para Jinja2
            # El CSV parece usar 'x' para marcado
            checkbox_fields = [
                'flujo_nulo', 'flujo_lento', 'flujo_normal',
                'equipo_guia', 'equipo_hidro', 'equipo_vactor',
                'estado_bueno', 'estado_danado', 'estado_obstruido'
            ]
            for field in checkbox_fields:
                data[field] = row.get(field, '').lower().strip() == 'x'

            # Campos opcionales de evidencia
            data['obs_evidencia_01'] = row.get('obs_evidencia_01', 'Evidencia inicial del área.')
            data['obs_evidencia_02'] = row.get('obs_evidencia_02', 'Evidencia final del servicio.')
            data['obs_evidencia_03'] = row.get('obs_evidencia_03', 'Equipo utilizado durante el proceso.')

            # Ajustar la ruta del CSS para los archivos generados
            output_html = template.render(**data)
            output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
            output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
            output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')

            # Guardar archivo
            filename = f"OT_DESAZOLVE_{data['folio_ot']}.html"
            filename = f"OT_DESAZOLVE_{data['folio_ot']}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(output_html)
            
            print(f"Generado: {filename}")

if __name__ == "__main__":
    generar_html()

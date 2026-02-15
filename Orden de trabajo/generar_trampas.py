import csv
import os
from jinja2 import Template

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "limpieza_trampa_grasa.html")
CSV_FILE = os.path.join(BASE_DIR, "ordenes_trampas.csv")
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Documentos_generados\limpiezas_trampa_grasa"

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
            data = row.copy()
            data['folio_ot'] = row.get('folio_lt', 'N/A')
            data['fecha_ot'] = row.get('fecha_lt', 'N/A')
            data['no_cliente'] = row.get('no_cliente', '---')
            
            # Asegurar que los campos de checkbox sean booleanos para Jinja2
            checkbox_fields = [
                'accion_retiro_solidos', 'accion_succion_liquidos', 'accion_raspado_paredes',
                'accion_lavado_presion', 'accion_aplicacion_bacterias', 'accion_prueba_flujo',
                'accion_limpieza_perimetral', 'estado_bueno', 'estado_reparacion', 'estado_faltantes'
            ]
            for field in checkbox_fields:
                data[field] = row.get(field, '').lower().strip() == 'x'

            # Campos opcionales de evidencia
            data['obs_evidencia_01'] = row.get('obs_evidencia_01', 'Trampa saturada antes del servicio.')
            data['obs_evidencia_02'] = row.get('obs_evidencia_02', 'Trampa limpia después del servicio.')

            # Ajustar la ruta del CSS para los archivos generados
            output_html = template.render(**data)
            output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
            output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
            output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')

            # Guardar archivo
            filename = f"OT_TRAMPA_{data['folio_ot']}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(output_html)
            
            print(f"Generado: {filename}")

if __name__ == "__main__":
    generar_html()

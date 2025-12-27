import csv
import os
from jinja2 import Template

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "tarificador.html")
CSV_FILE = os.path.join(BASE_DIR, "datos_tarificador.csv")
# Siguiendo el patrón de carpetas del usuario
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Documentos_generados\tarificadores"

def generar_html():
    # Crear directorio de salida si no existe
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio creado: {OUTPUT_DIR}")

    # Cargar plantilla
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: No se encontró la plantilla en {TEMPLATE_FILE}")
        return

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    template = Template(template_content)

    # Leer CSV y generar archivos
    if not os.path.exists(CSV_FILE):
        print(f"Error: No se encontró el archivo CSV en {CSV_FILE}")
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data = row.copy()
            
            # Ajustar la ruta del CSS para los archivos generados
            output_html = template.render(**data)
            output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
            output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
            output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')

            # Guardar archivo
            folio = data.get('folio_tar', 'SINFOLIO').replace('/', '-')
            filename = f"TARIFICADOR_{folio}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(output_html)
            
            print(f"Generado: {filename}")

if __name__ == "__main__":
    generar_html()

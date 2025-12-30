import csv
import os
import re
from jinja2 import Template

def clean_float(value):
    """Limpia y convierte un valor a float. Maneja símbolos de moneda, comas y texto."""
    if not value: return 0.0
    try:
        # Extraer solo el número (incluyendo decimales y comas)
        match = re.search(r'[\d\.,]+', str(value))
        if match:
            clean_value = match.group().replace(',', '')
            return float(clean_value)
        return 0.0
    except:
        return 0.0

def format_currency(value):
    """Formatea un número como moneda con comas y 2 decimales."""
    return f"{value:,.2f}"

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "tarificador.html")
CSV_FILE = os.path.join(BASE_DIR, "datos_tarificador.csv")
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

    # Lista de contaminantes para sumar sus precios
    contaminantes = [
        'sst', 'dbo', 'gya', 'ss', 'mf', 'temp', 
        'saam', 'dqo', 'nt', 'fen', 'color'
    ]

    # Leer CSV
    if not os.path.exists(CSV_FILE):
        print(f"Error: No se encontró el archivo CSV en {CSV_FILE}")
        return

    rows_to_update = []
    
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        for row in reader:
            data = row.copy()
            
            # 1. Calcular precio_m3_total (suma de todos los precios de contaminantes)
            precio_total_m3 = 0.0
            for c in contaminantes:
                precio_val = clean_float(row.get(f'{c}_precio', '0'))
                precio_total_m3 += precio_val
            
            # 2. Calcular total_pagar
            volumen = clean_float(row.get('volumen_promedio_descargado', '0'))
            total_final = precio_total_m3 * volumen
            
            # Guardar valores calculados en el diccionario para el CSV y la plantilla
            # Para el CSV usamos números limpios (sin comas ni $) para evitar problemas en futuras lecturas
            data['precio_m3_total'] = f"{precio_total_m3:.2f}"
            data['total_pagar'] = f"{total_final:.2f}"
            
            # Crear copia para la plantilla con valores formateados
            data_template = data.copy()
            data_template['precio_m3_total'] = format_currency(precio_total_m3)
            data_template['total_pagar'] = format_currency(total_final)
            
            # Formatear también los precios individuales para la plantilla
            for c in contaminantes:
                p_key = f'{c}_precio'
                data_template[p_key] = format_currency(clean_float(row.get(p_key, '0')))

            # Renderizar y ajustar rutas
            output_html = template.render(**data_template)
            output_html = output_html.replace('href="../estilos.css"', 'href="../../Plantillas/estilos.css"')
            output_html = output_html.replace('src="../img/logo-cophi-negro.jpg"', 'src="../../Plantillas/img/logo-cophi-negro.jpg"')
            output_html = output_html.replace('src="../paginacion.js"', 'src="../../Plantillas/paginacion.js"')

            # Guardar archivo HTML
            folio = data.get('folio_tar', 'SINFOLIO').replace('/', '-')
            filename = f"TARIFICADOR_{folio}.html"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, "w", encoding="utf-8") as out:
                out.write(output_html)
            
            print(f"Generado: {filename}")
            rows_to_update.append(data)

    # Actualizar CSV con los nuevos cálculos
    try:
        with open(CSV_FILE, "w", encoding="utf-8-sig", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(rows_to_update)
        print(f"CSV actualizado correctamente: {CSV_FILE}")
    except Exception as e:
        print(f"Error actualizando CSV: {e}. Asegúrese de cerrar el archivo si está abierto en Excel.")

if __name__ == "__main__":
    generar_html()


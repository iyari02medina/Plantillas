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
RANGOS_FILE = os.path.join(BASE_DIR, "rango_incumplimiento.csv")
OUTPUT_DIR = r"C:\Users\DELL\Desktop\Cophi\Recursos\Programa_cophi\Documentos_generados\tarificadores"

def cargar_rangos():
    """Carga la tabla de rangos de incumplimiento."""
    rangos = []
    if not os.path.exists(RANGOS_FILE):
        print(f"Error: No se encontró el archivo de rangos en {RANGOS_FILE}")
        return rangos
        
    with open(RANGOS_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                min_val = clean_float(row['Minimo'])
                # Manejar Maximo vacío (última fila)
                max_str = row.get('Maximo', '').strip()
                max_val = clean_float(max_str) if max_str else float('inf')
                
                # Intentar leer columnas comunes para el precio
                precio = clean_float(row.get('Contaminantes Básicos', 0))
                
                rangos.append({
                    'min': min_val,
                    'max': max_val,
                    'precio': precio
                })
            except Exception as e:
                print(f"Error leyendo fila de rangos: {row} - {e}")
    return rangos

def obtener_precio_por_rango(ratio, rangos):
    """Obtiene el precio basado en el ratio de incumplimiento."""
    # Si el ratio es <= 0, significa que cumple o está por debajo del límite.
    if ratio <= 0:
        return 0.0
        
    for r in rangos:
        # Lógica: mayor que el mínimo y hasta el máximo
        # min < ratio <= max
        if r['min'] < ratio <= r['max']:
            return r['precio']
            
    # Si supera todos los rangos (y el último no era inf), retorna 0 o el último?
    # Como definimos el último con inf, debería caer allí si es > min del último.
    return 0.0

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

    # Cargar rangos de precios
    rangos_incumplimiento = cargar_rangos()
    if not rangos_incumplimiento:
        print("Advertencia: No se cargaron rangos de incumplimiento. Los precios calculados serán 0.")

    # Lista de contaminantes para calcular y sumar sus precios
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
            
            # 1. Calcular precios individuales y suma total
            precio_total_m3 = 0.0
            
            for c in contaminantes:
                # Obtener Resultado y LMP
                resultado = clean_float(row.get(f'{c}_resultado', '0'))
                lmp = clean_float(row.get(f'{c}_lmp', '0'))
                
                precio_calculado = 0.0
                
                # Fórmula: ((resultado - lmp) / lmp)
                # Solo calculamos si lmp > 0 para evitar división por cero
                if lmp > 0:
                    ratio = (resultado - lmp) / lmp
                    # Buscar precio en la tabla según el ratio
                    precio_calculado = obtener_precio_por_rango(ratio, rangos_incumplimiento)
                
                # Actualizar el precio en los datos
                row_key_precio = f'{c}_precio'
                
                # Guardamos formateado con signo de pesos para consistencia visual en CSV
                data[row_key_precio] = f"${precio_calculado:.2f}"
                
                precio_total_m3 += precio_calculado
            
            # 2. Calcular total_pagar
            volumen = clean_float(row.get('volumen_promedio_descargado', '0'))
            total_final = precio_total_m3 * volumen
            
            # Guardar valores calculados en el diccionario para el CSV y la plantilla
            data['precio_m3_total'] = f"{precio_total_m3:.2f}"
            data['total_pagar'] = f"{total_final:.2f}"
            
            # Crear copia para la plantilla con valores formateados para HTML
            data_template = data.copy()
            data_template['precio_m3_total'] = format_currency(precio_total_m3)
            data_template['total_pagar'] = format_currency(total_final)
            
            # Asegurar que los precios individuales estén formateados para la vista HTML
            # (El CSV ya tiene '$', pero clean_float lo maneja si lo re-leemos, aquí usamos la variable en memoria)
            for c in contaminantes:
                p_key = f'{c}_precio'
                # data[p_key] es string '$X.XX'
                val_limpio = clean_float(data.get(p_key, '0'))
                data_template[p_key] = format_currency(val_limpio)

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

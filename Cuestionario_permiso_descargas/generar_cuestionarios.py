import csv
import os
import re
import shutil
import pathlib
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

# Configuración
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Lista de plantillas a procesar con su prefijo para el nombre de archivo
TEMPLATES_CONFIG = [
    {'filename': 'v2_cuestionario.html', 'prefix': 'Cuestionario'},
    {'filename': 'acuse.html',           'prefix': 'Acuse'},
    {'filename': 'carta-poder.html',     'prefix': 'Carta_Poder'}
]
CSV_FILE = 'cuestionario_variables.csv'
OUTPUT_DIR = os.path.join('..', '..', 'Documentos_generados', 'Cuestionarios_permiso_descarga')
HEADER_IMAGE = '../img/header.JPG'

def sanitize_filename(name):
    """
    Limpia el nombre de archivo eliminando caracteres prohibidos en Windows
    y espacios innecesarios.
    """
    if not name:
        return "Desconocido"
    # Caracteres no permitidos en nombres de archivo: < > : " / \ | ? *
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name.strip()

def main():
    # 1. Configurar entorno Jinja2
    env = Environment(loader=FileSystemLoader(BASE_DIR))
    
    # Cargar todas las plantillas
    loaded_templates = {}
    print("Cargando plantillas...")
    for config in TEMPLATES_CONFIG:
        fname = config['filename']
        prefix = config['prefix']
        try:
            loaded_templates[prefix] = env.get_template(fname)
            print(f"  - Plantilla cargada: {fname} (Prefijo: {prefix})")
        except Exception as e:
            print(f"ERROR: No se pudo cargar la plantilla '{fname}'. NO se generarán documentos de tipo '{prefix}'.\nDetalle: {e}")

    if not loaded_templates:
        print("ERROR CRÍTICO: No se pudo cargar ninguna plantilla. Abortando.")
        return

    # 2. Verificar archivo CSV
    csv_path = os.path.join(BASE_DIR, CSV_FILE)
    if not os.path.exists(csv_path):
        print(f"ERROR CRÍTICO: No se encuentra el archivo de datos '{CSV_FILE}'.")
        return

    # 3. Preparar directorio de salida
    output_path_dir = os.path.normpath(os.path.join(BASE_DIR, OUTPUT_DIR))
    if not os.path.exists(output_path_dir):
        try:
            os.makedirs(output_path_dir)
            print(f"Directorio creado: {OUTPUT_DIR}")
        except OSError as e:
            print(f"ERROR: No se pudo crear el directorio '{OUTPUT_DIR}'.\nDetalle: {e}")
            return

    # 4. Asegurar que la imagen del header esté en la carpeta de salida
    src_img = os.path.join(BASE_DIR, HEADER_IMAGE)
    dst_img = os.path.join(output_path_dir, HEADER_IMAGE)
    
    if os.path.exists(src_img):
        if not os.path.exists(dst_img):
            try:
                shutil.copy2(src_img, dst_img)
                print(f"Imagen '{HEADER_IMAGE}' copiada a '{OUTPUT_DIR}' para asegurar visualización correcta.")
            except Exception as e:
                print(f"ADVERTENCIA: No se pudo copiar la imagen de encabezado.\nDetalle: {e}")
    else:
        print(f"ADVERTENCIA: La imagen '{HEADER_IMAGE}' no se encuentra en el directorio raíz.")

    # 5. Procesar CSV y generar archivos
    files_created = 0
    pdf_files_created = 0
    files_skipped = 0
    current_year = datetime.now().year

    # Iniciar Playwright para generar PDFs
    playwright_manager = None
    playwright = None
    browser = None
    
    try:
        playwright_manager = sync_playwright()
        playwright = playwright_manager.start()
        # Intentamos lanzar chromium
        browser = playwright.chromium.launch()
        print("Motor de generación PDF (Playwright) activado.")
    except Exception as e:
        print(f"ADVERTENCIA: No se pudo iniciar el generador de PDF (Playwright). solo se crearán HTMLs.")
        print(f"Detalle del error: {e}")
        # Intentar limpieza si falló a medias
        if playwright_manager:
            try:
                playwright_manager.stop()
            except:
                pass
            playwright_manager = None

    # Intentar leer con diferentes codificaciones
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            print(f"Leyendo CSV con codificación: {encoding}...")
            with open(csv_path, mode='r', encoding=encoding) as f:
                # Leer todo el contenido primero para asegurar que no falle a mitad
                reader = csv.DictReader(f)
                rows = list(reader) # Esto disparará el error si la codificación está mal
            
            # Si llegamos aquí, la lectura fue exitosa
            print(f"CSV leído exitosamente con '{encoding}'. Procesando {len(rows)} registros.")
            
            # Procesar filas
            for row in rows:
                # Normalizar valores Si/No para que coincidan con la plantilla
                for k, v in row.items():
                    if v is not None:
                        v_lower = v.strip().lower()
                        if v_lower == 'si' or v_lower == 'sí':
                            row[k] = 'Si' # Normalizar a 'Si'
                        elif v_lower == 'no':
                            row[k] = 'No' # Normalizar a 'No'

                # Lógica para el nombre del archivo
                nombre_entidad = row.get('arr_nombre', '').strip()
                if not nombre_entidad:
                    nombre_entidad = row.get('prop_nombre', '').strip()
                
                safe_name = sanitize_filename(nombre_entidad)

                # Definir y crear carpeta del cliente
                # [nombre_negocio]_Permiso_descargas_[año de creacion del documento]
                client_folder_name = f"{safe_name}_Permiso_descargas_{current_year}"
                client_folder_path = os.path.join(output_path_dir, client_folder_name)
                
                if not os.path.exists(client_folder_path):
                    try:
                        os.makedirs(client_folder_path)
                        print(f"Carpeta creada: {client_folder_name}")
                    except OSError as e:
                        print(f"ERROR: No se pudo crear la carpeta '{client_folder_name}'. Detalle: {e}")
                        continue

                # Copiar header image a la carpeta del cliente para asegurar visualización correcta
                # src_img ya fue definido anteriormente en main()
                client_img_path = os.path.join(client_folder_path, HEADER_IMAGE)
                if os.path.exists(src_img) and not os.path.exists(client_img_path):
                    try:
                        shutil.copy2(src_img, client_img_path)
                    except Exception as e:
                        print(f"ADVERTENCIA: No se pudo copiar imagen a carpeta cliente: {e}")

                # Iterar sobre cada tipo de documento configurado
                for config in TEMPLATES_CONFIG:
                    prefix = config['prefix']
                    template = loaded_templates.get(prefix)
                    
                    if not template:
                        continue # Saltamos si la plantilla no cargó

                    # Nombre de archivo
                    base_name = f"{prefix}_{safe_name}_{current_year}"
                    html_filename = f"{base_name}.html"
                    pdf_filename = f"{base_name}.pdf"
                    
                    html_file_path = os.path.join(client_folder_path, html_filename)
                    pdf_file_path = os.path.join(client_folder_path, pdf_filename)

                    # Validar existencia HTML
                    html_exists = os.path.exists(html_file_path)
                    
                    if html_exists:
                        # Si HTML existe, verificamos si falta el PDF
                        if browser and not os.path.exists(pdf_file_path):
                             print(f"[REINTENTO PDF] El HTML existe pero el PDF no: {pdf_filename}")
                             # Continuamos para generar PDF
                        else:
                            print(f"[OMITIDO] Ya existen los archivos para: {html_filename}")
                            files_skipped += 1
                            continue
                    
                    if not html_exists:
                        # Renderizar contenido HTML
                        try:
                            html_content = template.render(**row)
                            with open(html_file_path, 'w', encoding='utf-8') as out:
                                out.write(html_content)
                            print(f"[CREADO HTML] {html_filename}")
                            files_created += 1
                        except Exception as render_err:
                            print(f"ERROR al generar HTML '{html_filename}': {render_err}")
                            continue

                    # Generar PDF
                    if browser:
                        try:
                            # Usar pathlib as_uri() asegura que el path sea correcto para el navegador (file://...)
                            uri = pathlib.Path(html_file_path).as_uri()
                            
                            page = browser.new_page()
                            page.goto(uri)
                            
                            # Opciones de PDF: Formato carta, márgenes estándar, imprimir fondo
                            page.pdf(
                                path=pdf_file_path,
                                format="Letter",
                                print_background=True,
                                margin={'top': '1cm', 'right': '1cm', 'bottom': '1cm', 'left': '1cm'}
                            )
                            page.close()
                            print(f"[CREADO PDF]  {pdf_filename}")
                            pdf_files_created += 1
                        except Exception as pdf_err:
                            print(f"ERROR al generar PDF '{pdf_filename}': {pdf_err}")
            
            # Si tuvimos éxito, salimos del bucle de encodings
            break

        except UnicodeDecodeError:
            print(f"Falló la lectura con {encoding}, intentando siguiente...")
            continue
        except Exception as csv_err:
            print(f"ERROR al leer el archivo CSV: {csv_err}")
            break

    # Limpieza
    if browser:
        browser.close()
    if playwright: 
        playwright.stop()

    print("-" * 40)
    print(f"Proceso finalizado.")
    print(f"HTMLs creados: {files_created}")
    print(f"PDFs creados:  {pdf_files_created}")
    print(f"Omitidos:      {files_skipped}")

if __name__ == "__main__":
    main()

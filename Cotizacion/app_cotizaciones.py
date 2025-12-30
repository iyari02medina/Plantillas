import streamlit as st
import pandas as pd
import os
from datetime import datetime
import subprocess

# Configuración de la página
st.set_page_config(page_title="Generador de Cotizaciones", layout="wide")

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_COTIZACIONES = os.path.join(BASE_DIR, "cotizaciones.csv")
CSV_PRODUCTOS = os.path.join(os.path.dirname(BASE_DIR), "inventario", "productos_servicios.csv")
CSV_EMPRESAS = os.path.join(os.path.dirname(BASE_DIR), "inventario", "empresas.csv")
SCRIPT_GENERADOR = os.path.join(BASE_DIR, "generar_cotizaciones.py")

# Función para cargar productos/servicios
def cargar_productos():
    if os.path.exists(CSV_PRODUCTOS):
        return pd.read_csv(CSV_PRODUCTOS)
    return pd.DataFrame(columns=["Nombre", "Unidad", "Precio"])

# Función para cargar empresas
def cargar_empresas():
    if os.path.exists(CSV_EMPRESAS):
        return pd.read_csv(CSV_EMPRESAS)
    return pd.DataFrame(columns=["ID", "nombre_empresa", "telefono_empresa", "direccion_empresa", "tipo_empresa"])

# Función para cargar cotizaciones existentes
def cargar_cotizaciones():
    if os.path.exists(CSV_COTIZACIONES):
        # Leer todas las columnas como string para evitar problemas de formato
        return pd.read_csv(CSV_COTIZACIONES, dtype=str) 
    return pd.DataFrame(columns=[
        "folio_cot", "nombre_cot", "fecha_cot", "id_cliente", "nombre_cliente", 
        "razon_social_cliente", "direccion_cliente", "nombre_contacto", 
        "telefono_contacto", "alcance_cot", "nombre_item", "descripcion_item", 
        "imagen_item", "unidad_item", "cantidad_item", "precio_unitario_item", 
        "importe_item", "subtotal", "iva", "total", "terminos"
    ])

# Título
st.title("📄 Sistema de Cotizaciones COPHI")

# Tabs para Separar "Nueva Cotización" de "Historial"
tab1, tab2 = st.tabs(["➕ Nueva Cotización", "📜 Historial Completo"])

with tab1:
    st.header("Datos del Cliente y Cotización")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Generar folio sugerido basado en fecha
        folio_sugerido = f"COT-{datetime.now().strftime('%d%m%y-%H%M')}"
        folio_cot = st.text_input("Folio Cotización", value=folio_sugerido)
        fecha_cot = st.date_input("Fecha", datetime.now()).strftime("%d/%m/%Y")
        terminos = st.text_area("Términos y Condiciones", value="50% anticipo, 50% contra entrega.\nVigencia de 15 días.")
        alcance_cot = st.text_area("Alcance General / Observaciones")

    with col2:
        # Cargar catálogo de clientes
        df_empresas = cargar_empresas()
        lista_empresas = df_empresas["nombre_empresa"].tolist() if not df_empresas.empty else []
        
        cliente_seleccionado = st.selectbox("Seleccionar Cliente (Opcional)", [""] + lista_empresas)

        # Variables para pre-llenar
        id_cli_val = ""
        nom_cli_val = ""
        raz_soc_val = ""
        dir_cli_val = ""
        tel_cli_val = ""

        if cliente_seleccionado and not df_empresas.empty:
            datos_cliente = df_empresas[df_empresas["nombre_empresa"] == cliente_seleccionado].iloc[0]
            id_cli_val = str(datos_cliente.get("ID", ""))
            nom_cli_val = str(datos_cliente.get("nombre_empresa", ""))
            raz_soc_val = str(datos_cliente.get("nombre_empresa", "")) # Por defecto la misma, si no hay columna especifica
            dir_cli_val = str(datos_cliente.get("direccion_empresa", ""))
            tel_cli_val = str(datos_cliente.get("telefono_empresa", ""))

        id_cliente = st.text_input("ID Cliente", value=id_cli_val)
        nombre_cliente = st.text_input("Nombre Comercial Cliente", value=nom_cli_val)
        razon_social = st.text_input("Razón Social", value=raz_soc_val)
        direccion = st.text_area("Dirección Fiscal/Entrega", value=dir_cli_val)
        contacto = st.text_input("Nombre Contacto")
        telefono = st.text_input("Teléfono Contacto", value=tel_cli_val)

    st.markdown("---")
    st.header("Partidas (Items)")

    # Cargar catálogo para facilitar llenado
    df_productos = cargar_productos()
    nombres_productos = df_productos["Nombre"].tolist() if not df_productos.empty else []

    # Estado de sesión para items
    if "items" not in st.session_state:
        st.session_state.items = []

    # Formulario para agregar item
    with st.expander("Agregar Nueva Partida", expanded=True):
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            prod_seleccionado = st.selectbox("Buscar en Catálogo (Opcional)", [""] + nombres_productos)
        
        # Pre-llenar datos si selecciona del catálogo
        precio_sugerido = 0.0
        unidad_sugerida = "Servicio"
        desc_sugerida = ""
        
        if prod_seleccionado and not df_productos.empty:
            item_data = df_productos[df_productos["Nombre"] == prod_seleccionado].iloc[0]
            precio_sugerido = float(item_data.get("Precio", 0))
            unidad_sugerida = item_data.get("Unidad", "Pieza")
            # desc_sugerida = f"Categoría: {item_data.get('Categoría', '')}"

        with st.form("add_item_form"):
            col_a, col_b = st.columns([2, 1])
            nombre_item = col_a.text_input("Nombre del Ítem", value=prod_seleccionado if prod_seleccionado else "")
            descripcion_item = col_a.text_area("Descripción Detallada", value=desc_sugerida)
            imagen_item = col_a.text_input("Nombre Imagen (ej. foto.jpg)", value="")
            
            unidad_item = col_b.text_input("Unidad", value=unidad_sugerida)
            cantidad_item = col_b.number_input("Cantidad", min_value=0.0, value=1.0, step=0.5)
            precio_unitario = col_b.number_input("Precio Unitario ($)", min_value=0.0, value=precio_sugerido, step=10.0)
            
            submitted = st.form_submit_button("Añadir Partida")
            if submitted:
                importe = cantidad_item * precio_unitario
                st.session_state.items.append({
                    "nombre_item": nombre_item,
                    "descripcion_item": descripcion_item,
                    "imagen_item": imagen_item,
                    "unidad_item": unidad_item,
                    "cantidad_item": cantidad_item,
                    "precio_unitario_item": precio_unitario,
                    "importe_item": importe
                })
                # st.experimental_rerun()  # Forzar recarga para ver tabla actualizada

    # Mostrar tabla de items
    if st.session_state.items:
        df_items = pd.DataFrame(st.session_state.items)
        st.dataframe(df_items)
        
        # Botón para limpiar items
        if st.button("Limpiar Partidas"):
            st.session_state.items = []
            # st.experimental_rerun()

    # Cálculos Totales
    subtotal = sum(item["importe_item"] for item in st.session_state.items)
    iva = subtotal * 0.16
    total = subtotal + iva

    st.markdown(f"### 💰 Subtotal: ${subtotal:,.2f}")
    st.markdown(f"### 🏛️ IVA (16%): ${iva:,.2f}")
    st.markdown(f"### 💵 Total: ${total:,.2f}")

    # Guardar en CSV
    if st.button("💾 Guardar en cotizaciones.csv", type="primary"):
        if not st.session_state.items:
            st.error("⚠️ No hay partidas para guardar.")
        elif not folio_cot:
            st.error("⚠️ Falta el Folio.")
        else:
            # Preparar Dataframe final
            rows = []
            for item in st.session_state.items:
                row = {
                    "folio_cot": folio_cot,
                    "nombre_cot": "", # Opcional si quieres un titulo general
                    "fecha_cot": fecha_cot,
                    "id_cliente": id_cliente,
                    "nombre_cliente": nombre_cliente,
                    "razon_social_cliente": razon_social,
                    "direccion_cliente": direccion,
                    "nombre_contacto": contacto,
                    "telefono_contacto": telefono,
                    "alcance_cot": alcance_cot,
                    "nombre_item": item["nombre_item"],
                    "descripcion_item": item["descripcion_item"],
                    "imagen_item": item["imagen_item"],
                    "unidad_item": item["unidad_item"],
                    "cantidad_item": item["cantidad_item"],
                    "precio_unitario_item": item["precio_unitario_item"],
                    "importe_item": f"{item['importe_item']:.2f}",
                    "subtotal": f"{subtotal:.2f}",
                    "iva": f"{iva:.2f}",
                    "total": f"{total:.2f}",
                    "terminos": terminos
                }
                rows.append(row)
            
            df_new = pd.DataFrame(rows)
            
            # Cargar existente y concatenar (append)
            # Nota: Usamos mode='a' de pandas to_csv o cargamos todo y reescribimos.
            # Mejor cargar todo, concat y guardar para asegurar integridad.
            try:
                # Si existe, cargar headers, si no, crear
                if os.path.exists(CSV_COTIZACIONES):
                    df_new.to_csv(CSV_COTIZACIONES, mode='a', header=False, index=False, encoding='utf-8-sig')
                else:
                    df_new.to_csv(CSV_COTIZACIONES, mode='w', header=True, index=False, encoding='utf-8-sig')
                    
                st.success(f"✅ Cotización {folio_cot} guardada exitosamente!")
                st.session_state.items = [] # Limpiar después de guardar
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    # Botón para generar HTML
    if st.button("⚙️ Generar Documentos (Ejecutar Script)"):
        with st.spinner("Ejecutando script de generación..."):
            try:
                result = subprocess.run(["python", SCRIPT_GENERADOR], capture_output=True, text=True, cwd=BASE_DIR)
                if result.returncode == 0:
                    st.success("✅ Documentos generados correctamente.")
                    st.code(result.stdout)
                else:
                    st.error("❌ Error en la generación.")
                    st.code(result.stderr)
            except Exception as e:
                st.error(f"Error ejecutando subproceso: {e}")

with tab2:
    st.header("Historial de Cotizaciones")
    df_history = cargar_cotizaciones()
    st.dataframe(df_history)
    
    st.info("Para editar, es recomendable usar un editor de CSV externo por seguridad, o implementar lógica de edición avanzada.")

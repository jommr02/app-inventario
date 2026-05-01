import streamlit as st
import pandas as pd
import requests
from datetime import datetime
# --- ESTILO PROFESIONAL AZUL (#0014DC) ---
st.markdown(f"""
    <style>
    /* Color de fondo de la barra lateral */
    [data-testid="stSidebar"] {{
        background-color: #0014DC;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    /* Botones Principales */
    .stButton>button {{
        background-color: #0014DC;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #000eb3;
        color: white;
    }}
    /* Títulos y Subtítulos */
    h1, h2, h3 {{
        color: #0014DC !important;
    }}
    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab"] {{
        color: #64748b;
    }}
    .stTabs [aria-selected="true"] {{
        color: #0014DC !important;
        border-bottom-color: #0014DC !important;
    }}
    </style>
    """, unsafe_allow_html=True)




# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LIMS - WCF Fluids Lab", page_icon="🔬", layout="wide")

# ENLACES 
URL_HOJA_EQUIPOS = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"
URL_HOJA_MUESTRAS = "https://docs.google.com/spreadsheets/d/1fZBvKgt2-S5CRKRBuzIZ8hMS_M9pLYQiz_KcSYDX31o/export?format=csv"
URL_DB_EQUIPOS = "https://sheetdb.io/api/v1/9pogtini9kr0k"
URL_DB_MUESTRAS = "https://sheetdb.io/api/v1/cn4v870fg7c8z"

# --- MENÚ LATERAL ---
st.sidebar.title("🧪 LIMS WCF")
st.sidebar.markdown("Sistema de Gestión de Laboratorio")
menu = st.sidebar.radio("Módulos:", [
    "📦 Inventario de Equipos",
    "📥 Recepción de Muestras",
    "🚚 Despachos a Taladros",
    "📊 Panel de Control"
])

# --- FUNCIÓN PARA CARGAR DATOS ---
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        return df
    except:
        return pd.DataFrame()

# ==========================================
# MODULO 1: INVENTARIO DE EQUIPOS
# ==========================================
if menu == "📦 Inventario de Equipos":
    st.title("Gestión de Equipos")
    
    df = cargar_datos(URL_HOJA_EQUIPOS)
    pestaña_ver, pestaña_agregar = st.tabs(["📋 Ver Inventario", "➕ Registrar Equipo"])

    # --- PESTAÑA 1: VER INVENTARIO ---
    with pestaña_ver:
        st.subheader("Inventario Actual en la Nube")
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar equipo por Nombre, Clave o Serial:")
            if busqueda:
                df_filtrado = df[df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False, na=False)).any(axis=1)]
                st.dataframe(df_filtrado, use_container_width=True)
            else:
                st.dataframe(df, use_container_width=True)
        else:
            st.info("No se encontraron equipos o hay un error de conexión.")

    # --- PESTAÑA 2: AGREGAR NUEVO EQUIPO ---
    with pestaña_agregar:
        st.subheader("Registrar un nuevo equipo")
        col1, col2 = st.columns(2)
        
        with col1:
            clave = st.text_input("Clave * (Única)")
            clave_valida = False
            if clave:
                clave_limpia = clave.strip().upper()
                if not df.empty and 'Clave' in df.columns and df['Clave'].astype(str).str.strip().str.upper().isin([clave_limpia]).any():
                    st.error(f"❌ La Clave '{clave_limpia}' YA EXISTE.")
                else:
                    st.success("✅ Clave disponible")
                    clave_valida = True

            nombre = st.text_input("Nombre *")
            ubicacion = st.selectbox("Ubicación", ["ALMACEN", "LAB. MATURIN", "TALLER"])
            estatus = st.selectbox("Estatus", ["OPERATIVO", "PENDIENTE CALIBRACION", "PENDIENTE VERIFICACION", "DAÑADA"])
            
        with col2:
            serie = st.text_input("Serie * (Escribe 'S/S' si no tiene serial)")
            serie_valida = False
            if serie:
                serie_limpia = serie.strip().upper()
                if serie_limpia in ["S/S", "SS"]:
                    st.warning("⚠️ Equipo sin serial. Se dependerá únicamente de la Clave.")
                    serie_valida = True
                elif not df.empty and 'Serie' in df.columns and df['Serie'].astype(str).str.strip().str.upper().isin([serie_limpia]).any():
                    st.error(f"❌ El Serial '{serie_limpia}' YA EXISTE.")
                else:
                    st.success("✅ Serial disponible")
                    serie_valida = True

            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            
        st.markdown("*Obligatorio")
        campos_llenos = bool(clave and nombre and serie)
        todo_valido = clave_valida and serie_valida and campos_llenos
        
        if st.button("Guardar Equipo", type="primary", disabled=not todo_valido):
            datos_nuevos = {"data": [{"Clave": clave_limpia, "Nombre": nombre.upper(), "Ubicacion": ubicacion, "Marca": marca.upper(), "Modelo": modelo.upper(), "Serie": serie_limpia, "Estatus": estatus}]}
            respuesta = requests.post(URL_DB_EQUIPOS, json=datos_nuevos)
            if respuesta.status_code == 201:
                st.success(f"✅ ¡Éxito! Equipo guardado correctamente. (Presiona F5 para limpiar el formulario)")
            else:
                st.error("⚠️ Error al guardar en la nube.")

# ==========================================
# MODULO 2: RECEPCIÓN DE MUESTRAS
# ==========================================
elif menu == "📥 Recepción de Muestras":
    st.title("Bitácora de Recepción de Muestras")
    
    df_muestras = cargar_datos(URL_HOJA_MUESTRAS)
    tab_v, tab_a = st.tabs(["📋 Ver Muestras", "🆕 Ingresar Muestra"])
    
    # --- PESTAÑA 1: VER MUESTRAS ---
    with tab_v:
        st.subheader("Listado de Productos Recibidos")
        if not df_muestras.empty:
            busqueda_m = st.text_input("🔍 Buscar muestra (ID, Producto o Lote):")
            if busqueda_m:
                df_filtro_m = df_muestras[df_muestras.astype(str).apply(lambda x: x.str.contains(busqueda_m, case=False, na=False)).any(axis=1)]
                st.dataframe(df_filtro_m, use_container_width=True)
            else:
                st.dataframe(df_muestras, use_container_width=True)
        else:
            st.info("Aún no hay muestras registradas.")
            
    # --- PESTAÑA 2: INGRESAR MUESTRA ---
    with tab_a:
        st.subheader("Formulario de Ingreso")
        
        siguiente_id = "DS-01"
        if not df_muestras.empty and 'ID_MUESTRA' in df_muestras.columns:
            ids_actuales = df_muestras['ID_MUESTRA'].dropna().astype(str)
            numeros = []
            for val in ids_actuales:
                val = val.strip().upper()
                if val.startswith("DS-"):
                    try:
                        num = int(val.replace("DS-", ""))
                        numeros.append(num)
                    except:
                        pass
            if numeros:
                siguiente_id = f"DS-{max(numeros) + 1:02d}"

        col1, col2 = st.columns(2)
        with col1:
            id_muestra = st.text_input("ID Number (Sugerido automático) *", value=siguiente_id)
            id_valido = False
            if id_muestra:
                id_limpio = id_muestra.strip().upper()
                if not df_muestras.empty and 'ID_MUESTRA' in df_muestras.columns and df_muestras['ID_MUESTRA'].astype(str).str.strip().str.upper().isin([id_limpio]).any():
                    st.error(f"❌ El ID '{id_limpio}' YA EXISTE.")
                else:
                    st.success("✅ ID disponible")
                    id_valido = True
                    
            producto = st.text_input("Nombre del Producto *")
            cant = st.number_input("Cantidad", min_value=0.0, step=0.1)
            unidad = st.selectbox("Unidad", ["gr", "ml", "Kg", "L", "Gal"])
            proveedor = st.text_input("Proveedor")
            
        with col2:
            lote = st.text_input("Lote #")
            recibido = st.text_input("Recibido por (Iniciales)")
            f_muestreo = st.date_input("Fecha de Muestreo", datetime.now())
            f_recepcion = st.date_input("Fecha de Recepción", datetime.now())
            estatus = st.selectbox("Estatus Inicial", ["PENDIENTE", "EN ANALISIS", "URGENTE"])

        st.markdown("*Obligatorio")
        campos_m_llenos = bool(id_muestra and producto)
        todo_m_valido = id_valido and campos_m_llenos

        if st.button("Registrar Muestra", type="primary", disabled=not todo_m_valido):
            nueva_muestra = {"data": [{"ID_MUESTRA": id_limpio, "PRODUCTO": producto.upper(), "CANTIDAD": cant, "UNIDAD": unidad, "PROVEEDOR": proveedor.upper(), "LOTE": lote.upper(), "RECIBIDO_POR": recibido.upper(), "FECHA_MUESTREO": str(f_muestreo), "FECHA_RECEPCION": str(f_recepcion), "ESTATUS": estatus, "CERTIFICADO": "PENDIENTE"}]}
            res = requests.post(URL_DB_MUESTRAS, json=nueva_muestra)
            if res.status_code == 201:
                st.success(f"✅ Muestra {id_limpio} registrada correctamente. (Presiona F5 para registrar otra)")
            else:
                st.error("⚠️ Error al guardar.")

# ==========================================
# OTROS MÓDULOS
# ==========================================
elif menu == "🚚 Despachos a Taladros":
    st.title("Despachos a Taladros")
    st.info("Módulo en construcción. Próximamente.")

# ==========================================
# MODULO 4: PANEL DE CONTROL
# ==========================================
elif menu == "📊 Panel de Control":
    st.title("📊 Panel de Control y Analíticas")
    st.markdown("Visión general en tiempo real del estatus del laboratorio y operaciones en campo.")
    
    # Cargamos ambas bases de datos
    df_eq = cargar_datos(URL_HOJA_EQUIPOS)
    df_muestras = cargar_datos(URL_HOJA_MUESTRAS)
    
    if not df_eq.empty and not df_muestras.empty:
        
        # --- FILA 1: KPIs (Métricas Rápidas) ---
        col1, col2, col3 = st.columns(3)
        
        total_equipos = len(df_eq)
        # Contamos cuántos equipos están en un taladro (Ubicación distinta a almacén/taller)
        if 'Ubicacion' in df_eq.columns:
            equipos_base = df_eq[df_eq['Ubicacion'].isin(['ALMACEN', 'LAB. MATURIN', 'TALLER'])]
            equipos_campo = total_equipos - len(equipos_base)
        else:
            equipos_campo = 0
            
        total_muestras = len(df_muestras)
        
        col1.metric("📦 Total Equipos en Inventario", total_equipos)
        col2.metric("🚚 Equipos Despachados a Campo", equipos_campo)
        col3.metric("🧪 Total Muestras Recibidas", total_muestras)
        
        st.markdown("---")
        
        # --- FILA 2: GRÁFICOS ---
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("📍 Distribución de Equipos")
            if 'Ubicacion' in df_eq.columns:
                # Contamos cuántos equipos hay en cada ubicación y graficamos
                ubicacion_counts = df_eq['Ubicacion'].value_counts()
                st.bar_chart(ubicacion_counts, color="#0014DC")
                
        with col_chart2:
            st.subheader("⏱️ Estatus de Muestras")
            if 'ESTATUS' in df_muestras.columns:
                # Contamos el estatus de las muestras
                estatus_counts = df_muestras['ESTATUS'].value_counts()
                st.bar_chart(estatus_counts, color="#0014DC")
                
        st.markdown("---")
        
        # --- FILA 3: ALERTAS OPERATIVAS ---
        st.subheader("⚠️ Alertas de Atención Requerida")
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            st.error("Equipos Dañados o Pendientes de Calibración")
            if 'Estatus' in df_eq.columns:
                # Filtramos equipos con problemas
                equipos_alert = df_eq[df_eq['Estatus'].isin(['DAÑADA', 'PENDIENTE CALIBRACION', 'PENDIENTE VERIFICACION'])]
                if not equipos_alert.empty:
                    st.dataframe(equipos_alert[['Clave', 'Nombre', 'Estatus']], hide_index=True, use_container_width=True)
                else:
                    st.success("¡Todo en orden! No hay equipos dañados.")
                    
        with alert_col2:
            st.warning("Muestras Urgentes o Pendientes")
            if 'ESTATUS' in df_muestras.columns:
                # Filtramos muestras urgentes
                muestras_alert = df_muestras[df_muestras['ESTATUS'].isin(['URGENTE', 'PENDIENTE'])]
                if not muestras_alert.empty:
                    st.dataframe(muestras_alert[['ID_MUESTRA', 'PRODUCTO', 'ESTATUS']], hide_index=True, use_container_width=True)
                else:
                    st.success("¡Excelente! No hay muestras pendientes.")
                    
    else:
        st.info("Esperando conexión con la base de datos para generar analíticas...")

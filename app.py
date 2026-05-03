import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LIMS - WCF Fluids Lab", page_icon="🔬", layout="wide")

# --- ESTILO PROFESIONAL AZUL (#0014DC) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ background-color: #0014DC; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .stButton>button {{
        background-color: #0014DC;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }}
    .stButton>button:hover {{ background-color: #000eb3; color: white; }}
    h1, h2, h3 {{ color: #0014DC !important; }}
    .stTabs [data-baseweb="tab"] {{ color: #64748b; }}
    .stTabs [aria-selected="true"] {{ color: #0014DC !important; border-bottom-color: #0014DC !important; }}
    </style>
    """, unsafe_allow_html=True)

# ENLACES 
URL_HOJA_EQUIPOS = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"
URL_HOJA_MUESTRAS = "https://docs.google.com/spreadsheets/d/1fZBvKgt2-S5CRKRBuzIZ8hMS_M9pLYQiz_KcSYDX31o/export?format=csv"
URL_DB_EQUIPOS = "https://sheetdb.io/api/v1/9pogtini9kr0k"
URL_DB_MUESTRAS = "https://sheetdb.io/api/v1/cn4v870fg7c8z"

# --- MENÚ LATERAL ---
st.sidebar.title("🧪 LIMS WCF")
st.sidebar.markdown("Sistema de Gestión de Laboratorio")
menu = st.sidebar.radio("Módulos:", [
    "📊 Panel de Control",
    "📦 Inventario de Equipos",
    "📥 Recepción de Muestras",
    "🚚 Despachos a Taladros"
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
# MODULO 4: PANEL DE CONTROL (Ahora de primero en el menú)
# ==========================================
if menu == "📊 Panel de Control":
    st.title("📊 Panel de Control y Analíticas")
    st.markdown("Visión general en tiempo real del estatus del laboratorio y operaciones en campo.")
    
    df_eq = cargar_datos(URL_HOJA_EQUIPOS)
    df_muestras = cargar_datos(URL_HOJA_MUESTRAS)
    
    if not df_eq.empty and not df_muestras.empty:
        col1, col2, col3 = st.columns(3)
        total_equipos = len(df_eq)
        equipos_campo = total_equipos - len(df_eq[df_eq['Ubicacion'].isin(['ALMACEN', 'LAB. MATURIN', 'TALLER'])]) if 'Ubicacion' in df_eq.columns else 0
        total_muestras = len(df_muestras)
        
        col1.metric("📦 Total Equipos en Inventario", total_equipos)
        col2.metric("🚚 Equipos Despachados a Campo", equipos_campo)
        col3.metric("🧪 Total Muestras Recibidas", total_muestras)
        st.markdown("---")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.subheader("📍 Distribución de Equipos")
            if 'Ubicacion' in df_eq.columns: st.bar_chart(df_eq['Ubicacion'].value_counts(), color="#0014DC")
        with col_chart2:
            st.subheader("⏱️ Estatus de Muestras")
            if 'ESTATUS' in df_muestras.columns: st.bar_chart(df_muestras['ESTATUS'].value_counts(), color="#0014DC")
                
        st.markdown("---")
        st.subheader("⚠️ Alertas de Atención Requerida")
        alert_col1, alert_col2 = st.columns(2)
        with alert_col1:
            st.error("Equipos con problemas")
            if 'Estatus' in df_eq.columns:
                equipos_alert = df_eq[df_eq['Estatus'].isin(['DAÑADA', 'PENDIENTE CALIBRACION', 'PENDIENTE VERIFICACION'])]
                if not equipos_alert.empty: st.dataframe(equipos_alert[['Clave', 'Nombre', 'Estatus']], hide_index=True, use_container_width=True)
                else: st.success("No hay equipos dañados.")
        with alert_col2:
            st.warning("Muestras Urgentes o en Cuarentena")
            if 'ESTATUS' in df_muestras.columns:
                muestras_alert = df_muestras[df_muestras['ESTATUS'].isin(['URGENTE', 'CUARENTENA'])]
                if not muestras_alert.empty: st.dataframe(muestras_alert[['ID_MUESTRA', 'PRODUCTO', 'ESTATUS']], hide_index=True, use_container_width=True)
                else: st.success("No hay muestras pendientes.")
    else:
        st.info("Cargando base de datos...")

# ==========================================
# MODULO 1: INVENTARIO DE EQUIPOS
# ==========================================
elif menu == "📦 Inventario de Equipos":
    st.title("Gestión de Equipos")
    df = cargar_datos(URL_HOJA_EQUIPOS)
    pestaña_ver, pestaña_agregar = st.tabs(["📋 Ver Inventario", "➕ Registrar Equipo"])

    with pestaña_ver:
        if not df.empty:
            busqueda = st.text_input("🔍 Buscar equipo:")
            if busqueda: st.dataframe(df[df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False, na=False)).any(axis=1)], use_container_width=True)
            else: st.dataframe(df, use_container_width=True)

    with pestaña_agregar:
        col1, col2 = st.columns(2)
        with col1:
            clave = st.text_input("Clave * (Única)")
            clave_valida = False
            if clave:
                clave_limpia = clave.strip().upper()
                if not df.empty and 'Clave' in df.columns and df['Clave'].astype(str).str.strip().str.upper().isin([clave_limpia]).any(): st.error("❌ Clave YA EXISTE.")
                else: st.success("✅ Clave disponible"); clave_valida = True
            nombre = st.text_input("Nombre *")
            ubicacion = st.selectbox("Ubicación", ["ALMACEN", "LAB. MATURIN", "TALLER"])
            estatus = st.selectbox("Estatus", ["OPERATIVO", "PENDIENTE CALIBRACION", "PENDIENTE VERIFICACION", "DAÑADA"])
        with col2:
            serie = st.text_input("Serie * (Escribe 'S/S' si no tiene serial)")
            serie_valida = False
            if serie:
                serie_limpia = serie.strip().upper()
                if serie_limpia in ["S/S", "SS"]: st.warning("⚠️ Sin serial. Se validará por Clave."); serie_valida = True
                elif not df.empty and 'Serie' in df.columns and df['Serie'].astype(str).str.strip().str.upper().isin([serie_limpia]).any(): st.error("❌ Serial YA EXISTE.")
                else: st.success("✅ Serial disponible"); serie_valida = True
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
        
        campos_llenos = bool(clave and nombre and serie)
        if st.button("Guardar Equipo", type="primary", disabled=not (clave_valida and serie_valida and campos_llenos)):
            datos_nuevos = {"data": [{"Clave": clave_limpia, "Nombre": nombre.upper(), "Ubicacion": ubicacion, "Marca": marca.upper(), "Modelo": modelo.upper(), "Serie": serie_limpia, "Estatus": estatus}]}
            res = requests.post(URL_DB_EQUIPOS, json=datos_nuevos)
            if res.status_code == 201: st.success("✅ Guardado. Presiona F5.")

# ==========================================
# MODULO 2: RECEPCIÓN DE MUESTRAS (CON MODO CUARENTENA)
# ==========================================
elif menu == "📥 Recepción de Muestras":
    st.title("Bitácora de Recepción de Muestras")
    df_muestras = cargar_datos(URL_HOJA_MUESTRAS)
    tab_v, tab_a = st.tabs(["📋 Ver Muestras", "🆕 Ingresar Muestra"])
    
    with tab_v:
        if not df_muestras.empty:
            busqueda_m = st.text_input("🔍 Buscar muestra:")
            if busqueda_m: st.dataframe(df_muestras[df_muestras.astype(str).apply(lambda x: x.str.contains(busqueda_m, case=False, na=False)).any(axis=1)], use_container_width=True)
            else: st.dataframe(df_muestras, use_container_width=True)

    with tab_a:
        siguiente_id = "DS-01"
        if not df_muestras.empty and 'ID_MUESTRA' in df_muestras.columns:
            numeros = [int(v.replace("DS-", "")) for v in df_muestras['ID_MUESTRA'].astype(str) if v.startswith("DS-") and v.replace("DS-", "").isdigit()]
            if numeros: siguiente_id = f"DS-{max(numeros) + 1:02d}"

        col1, col2 = st.columns(2)
        with col1:
            id_muestra = st.text_input("ID Number *", value=siguiente_id)
            id_valido = False
            if id_muestra:
                id_limpio = id_muestra.strip().upper()
                if not df_muestras.empty and 'ID_MUESTRA' in df_muestras.columns and df_muestras['ID_MUESTRA'].astype(str).str.strip().str.upper().isin([id_limpio]).any(): st.error("❌ ID YA EXISTE.")
                else: st.success("✅ ID disponible"); id_valido = True
            
            producto = st.text_input("Nombre del Producto *")
            cant = st.number_input("Cantidad", min_value=0.0)
            unidad = st.selectbox("Unidad", ["gr", "ml", "Kg", "L", "Gal"])
            
            # --- SECCIÓN DE DOCUMENTACIÓN ---
            st.markdown("---")
            st.markdown("**Documentación Técnica (Requerida)**")
            coa_recibido = st.checkbox("Certificado de Análisis (COA) recibido")
            sds_recibida = st.checkbox("Hoja de Seguridad (SDS) recibida")
            
        with col2:
            proveedor = st.text_input("Proveedor")
            lote = st.text_input("Lote #")
            recibido = st.text_input("Recibido por")
            f_recepcion = st.date_input("Fecha de Recepción", datetime.now())
            
            # --- LÓGICA DE CUARENTENA ---
            st.markdown("---")
            st.markdown("**Estatus Operativo**")
            if coa_recibido and sds_recibida:
                estatus = st.selectbox("Estatus Inicial", ["PENDIENTE", "EN ANALISIS", "URGENTE"])
            else:
                st.warning("⚠️ Falta documentación obligatoria (COA/SDS). La muestra ingresará en CUARENTENA automática.")
                estatus = "CUARENTENA"
                st.text_input("Estatus Inicial", value="CUARENTENA", disabled=True)

        if st.button("Registrar Muestra", type="primary", disabled=not (id_valido and producto)):
            # Se añaden COA y SDS al payload (Asegúrate de que existan en el Excel)
            nueva_muestra = {"data": [{"ID_MUESTRA": id_limpio, "PRODUCTO": producto.upper(), "CANTIDAD": cant, "UNIDAD": unidad, "PROVEEDOR": proveedor.upper(), "LOTE": lote.upper(), "RECIBIDO_POR": recibido.upper(), "FECHA_RECEPCION": str(f_recepcion), "ESTATUS": estatus, "COA": "SI" if coa_recibido else "NO", "SDS": "SI" if sds_recibida else "NO"}]}
            res = requests.post(URL_DB_MUESTRAS, json=nueva_muestra)
            if res.status_code == 201: st.success("✅ Muestra guardada con éxito.")

# ==========================================
# MODULO 3: DESPACHOS A TALADROS
# ==========================================
elif menu == "🚚 Despachos a Taladros":
    st.title("🚚 Movimiento de Activos a Campo")
    df_eq = cargar_datos(URL_HOJA_EQUIPOS)
    if not df_eq.empty:
        lista_equipos = (df_eq['Clave'].astype(str) + " - " + df_eq['Nombre'].astype(str)).tolist()
        seleccion = st.selectbox("Seleccione el Equipo a despachar:", ["Seleccione..."] + lista_equipos)
        if seleccion != "Seleccione...":
            clave_sel = seleccion.split(" - ")[0]
            info_actual = df_eq[df_eq['Clave'] == clave_sel].iloc[0]
            st.info(f"📍 Ubicación Actual: **{info_actual['Ubicacion']}** | 📊 Estatus Actual: **{info_actual['Estatus']}**")
            
            col1, col2 = st.columns(2)
            with col1: nuevo_destino = st.text_input("Nuevo Destino (Pozo) *")
            with col2: nuevo_estatus = st.selectbox("Cambiar Estatus a:", ["EN CAMPO", "OPERATIVO", "EN TRANSITO", "MANTENIMIENTO"])
            
            if st.button("Confirmar Despacho a Campo", type="primary"):
                if nuevo_destino:
                    res_upd = requests.patch(f"{URL_DB_EQUIPOS}/Clave/{clave_sel}", json={"data": {"Ubicacion": nuevo_destino.upper(), "Estatus": nuevo_estatus}})
                    if res_upd.status_code == 200: st.success(f"✅ Equipo movido a {nuevo_destino.upper()}.")
                    else: st.error("⚠️ Error al actualizar.")
                else: st.warning("Indique el destino.")

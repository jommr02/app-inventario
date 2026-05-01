import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Inventario de Laboratorio", page_icon="🔬", layout="wide")

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"

# Put the link you got from Google Apps Script here!
APPS_SCRIPT_URL = https://sheetdb.io/api/v1/9pogtini9kr0k

st.title("🔬 Sistema de Gestión de Inventario WCF")

try:
    df = pd.read_csv(URL_GOOGLE_SHEET)
    df.columns = df.columns.str.strip() # Ninja trick to clean spaces
except Exception as e:
    st.error("⚠️ No se pudieron cargar los datos de la nube.")
    df = pd.DataFrame()

pestaña_ver, pestaña_agregar = st.tabs(["📋 Ver Equipos", "➕ Agregar Nuevo Equipo"])

# --- TAB 1: VIEW INVENTORY ---
with pestaña_ver:
    st.subheader("Inventario Actual en la Nube")
    if not df.empty:
        busqueda = st.text_input("🔍 Buscar equipo por Nombre, Clave o Serial:")
        if busqueda:
            df_filtrado = df[df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False, na=False)).any(axis=1)]
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# --- TAB 2: ADD NEW EQUIPMENT (THE ULTIMATE GUARDIAN) ---
with pestaña_agregar:
    st.subheader("Registrar un nuevo equipo")
    
    # We build the form completely inside the app now!
    with st.form("registro_equipo", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            clave = st.text_input("Clave * (Única)")
            nombre = st.text_input("Nombre *")
            ubicacion = st.selectbox("Ubicación", ["ALMACEN", "LAB. MATURIN", "TALLER"])
            estatus = st.selectbox("Estatus", ["OPERATIVO", "PENDIENTE CALIBRACION", "PENDIENTE VERIFICACION", "DAÑADA"])
            
        with col2:
            marca = st.text_input("Marca")
            modelo = st.text_input("Modelo")
            serie = st.text_input("Serie * (Única)")
            
        st.markdown("*Obligatorio")
        boton_guardar = st.form_submit_button("Validar y Guardar")

        if boton_guardar:
            if not clave or not nombre or not serie:
                st.error("Por favor, llena los campos obligatorios: Clave, Nombre y Serie.")
            else:
                # 1. Validation Phase (The Guardian)
                clave_limpia = clave.strip().upper()
                serie_limpia = serie.strip().upper()
                
                existe_clave = df['Clave'].astype(str).str.strip().str.upper().isin([clave_limpia]).any()
                existe_serie = df['Serie'].astype(str).str.strip().str.upper().isin([serie_limpia]).any()
                
                if existe_clave:
                    st.error(f"❌ ¡Alto! La Clave '{clave_limpia}' YA EXISTE en el inventario.")
                elif existe_serie:
                    st.error(f"❌ ¡Alto! El Serial '{serie_limpia}' YA EXISTE en el inventario.")
                else:
                    # 2. Sending Phase (The Tunnel)
                    datos_nuevos = {
                        "Clave": clave_limpia,
                        "Nombre": nombre.upper(),
                        "Ubicacion": ubicacion,
                        "Marca": marca.upper(),
                        "Modelo": modelo.upper(),
                        "Serie": serie_limpia,
                        "Estatus": estatus
                    }
                    
                    # We send the data through the secret tunnel
                    respuesta = requests.post(APPS_SCRIPT_URL, json=datos_nuevos)
                    
                    if respuesta.text == "Success":
                        st.success(f"✅ ¡Éxito! El equipo '{nombre}' se guardó en la base de datos.")
                        st.balloons()
                    else:
                        st.error("⚠️ Hubo un problema al guardar en la nube.")

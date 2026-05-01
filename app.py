import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Inventario de Laboratorio", page_icon="🔬", layout="wide")

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"
URL_SHEETDB = "https://sheetdb.io/api/v1/9pogtini9kr0k"

st.title("🔬 Sistema de Gestión de Inventario WCF")

try:
    df = pd.read_csv(URL_GOOGLE_SHEET)
    df.columns = df.columns.str.strip() 
except Exception as e:
    st.error("⚠️ No se pudieron cargar los datos de la nube.")
    df = pd.DataFrame()

pestaña_ver, pestaña_agregar = st.tabs(["📋 Ver Equipos", "➕ Agregar Nuevo Equipo"])

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

# --- PESTAÑA 2: AGREGAR NUEVO EQUIPO (DINÁMICO) ---
with pestaña_agregar:
    st.subheader("Registrar un nuevo equipo")
    st.markdown("Escribe la Clave y el Serial para verificar su disponibilidad al instante.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        clave = st.text_input("Clave * (Única)")
        
        # --- Validación Dinámica de Clave (Siempre estricta) ---
        clave_valida = False
        if clave:
            clave_limpia = clave.strip().upper()
            if df['Clave'].astype(str).str.strip().str.upper().isin([clave_limpia]).any():
                st.error(f"❌ La Clave '{clave_limpia}' YA EXISTE.")
            else:
                st.success("✅ Clave disponible")
                clave_valida = True

        nombre = st.text_input("Nombre *")
        ubicacion = st.selectbox("Ubicación", ["ALMACEN", "LAB. MATURIN", "TALLER"])
        estatus = st.selectbox("Estatus", ["OPERATIVO", "PENDIENTE CALIBRACION", "PENDIENTE VERIFICACION", "DAÑADA"])
        
    with col2:
        serie = st.text_input("Serie * (Escribe 'S/S' si no tiene serial)")
        
        # --- Validación Dinámica de Serie (Con excepción 'S/S') ---
        serie_valida = False
        if serie:
            serie_limpia = serie.strip().upper()
            
            # EXCEPCIÓN: Si es S/S, le damos un pase libre
            if serie_limpia == "S/S" or serie_limpia == "SS":
                st.warning("⚠️ Equipo sin serial. Se dependerá únicamente de la Clave.")
                serie_valida = True
            # Si no es S/S, buscamos duplicados normalmente
            elif df['Serie'].astype(str).str.strip().str.upper().isin([serie_limpia]).any():
                st.error(f"❌ El Serial '{serie_limpia}' YA EXISTE.")
            else:
                st.success("✅ Serial disponible")
                serie_valida = True

        marca = st.text_input("Marca")
        modelo = st.text_input("Modelo")
        
    st.markdown("*Obligatorio")
    
    # --- Lógica del Botón Inteligente ---
    campos_llenos = bool(clave and nombre and serie)
    todo_valido = clave_valida and serie_valida and campos_llenos
    
    if st.button("Guardar en Base de Datos", type="primary", disabled=not todo_valido):
        datos_nuevos = {
            "data": [
                {
                    "Clave": clave_limpia,
                    "Nombre": nombre.upper(),
                    "Ubicacion": ubicacion,
                    "Marca": marca.upper(),
                    "Modelo": modelo.upper(),
                    "Serie": serie_limpia,
                    "Estatus": estatus
                }
            ]
        }
        
        respuesta = requests.post(URL_SHEETDB, json=datos_nuevos)
        
        if respuesta.status_code == 201:
            st.success(f"✅ ¡Éxito! El equipo '{nombre}' se guardó en la base de datos. (Presiona F5 para limpiar el formulario y registrar otro)")
            st.balloons()
        else:
            st.error("⚠️ Hubo un problema al guardar en la nube.")

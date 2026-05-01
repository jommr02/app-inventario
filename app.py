import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inventario de Laboratorio", page_icon="🔬", layout="wide")

URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"
ENLACE_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSfffv_cw6Ns0q077yeyW1Z-R1MZF-3-yQ4eirjZsmoahp-i6Q/viewform?usp=publish-editor"

st.title("🔬 Sistema de Gestión de Inventario WCF")

# Intentamos cargar los datos al inicio para usarlos en ambas pestañas
try:
    df = pd.read_csv(URL_GOOGLE_SHEET)
except Exception as e:
    st.error("⚠️ No se pudieron cargar los datos de la nube.")
    df = pd.DataFrame() # Creamos una tabla vacía para que la app no se rompa

pestaña_ver, pestaña_agregar = st.tabs(["📋 Ver Equipos", "➕ Agregar Nuevo Equipo"])

# --- PESTAÑA PARA VER EL INVENTARIO ---
with pestaña_ver:
    st.subheader("Inventario Actual en la Nube")
    
    if not df.empty:
        busqueda = st.text_input("🔍 Buscar equipo por Nombre, Clave o Serial:")
        
        if busqueda:
            df_filtrado = df[df.astype(str).apply(lambda x: x.str.contains(busqueda, case=False, na=False)).any(axis=1)]
            st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# --- PESTAÑA PARA AGREGAR (EL GUARDIÁN) ---
with pestaña_agregar:
    st.subheader("Paso 1: Verificación de Duplicados")
    st.info("Para evitar errores, el sistema debe verificar que la Clave y el Serial sean únicos antes de permitir el registro.")
    
    # Cajitas para que el usuario escriba lo que quiere verificar
    clave_nueva = st.text_input("Ingresa la CLAVE del equipo nuevo:")
    serial_nuevo = st.text_input("Ingresa el SERIAL del equipo nuevo:")
    
    # Solo procedemos a evaluar si el usuario escribió en ambas cajitas
    if clave_nueva and serial_nuevo:
        
        # Limpiamos los textos (quitamos espacios extra y ponemos mayúsculas para comparar bien)
        clave_limpia = clave_nueva.strip().upper()
        serial_limpio = serial_nuevo.strip().upper()
        
        # Revisamos si existen en la base de datos (ignorando mayúsculas/minúsculas)
        # Asumimos que las columnas se llaman 'Clave' y 'Serie' según tu archivo original
        existe_clave = df['Clave'].astype(str).str.strip().str.upper().isin([clave_limpia]).any()
        existe_serial = df['Serie'].astype(str).str.strip().str.upper().isin([serial_limpio]).any()
        
        # Lógica de validación
        if existe_clave:
            st.error(f"❌ ¡Alto! La Clave '{clave_nueva}' YA EXISTE en el inventario.")
        elif existe_serial:
            st.error(f"❌ ¡Alto! El Serial '{serial_nuevo}' YA EXISTE en el inventario.")
        else:
            # Si pasa la prueba, mostramos el éxito y el botón
            st.success(f"✅ ¡Perfecto! La Clave y el Serial están disponibles.")
            
            st.subheader("Paso 2: Registrar en la Base de Datos")
            st.markdown("Haz clic en el botón para abrir el formulario y completar los demás datos del equipo:")
            st.link_button("📝 Abrir Formulario de Registro", ENLACE_FORMULARIO)
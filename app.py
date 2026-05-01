import streamlit as st

st.set_page_config(page_title="LIMS - Laboratorio WCF", layout="wide")

# --- MENÚ LATERAL ---
st.sidebar.title("⚙️ Menú Principal")
menu = st.sidebar.radio("Selecciona un módulo:", [
    "🏠 Panel de Control",
    "📦 Inventario (Equipos y Reactivos)",
    "🚚 Movimientos a Taladros",
    "🔬 Control de Calidad",
    "📄 Certificados"
])

st.sidebar.markdown("---")
st.sidebar.info("Usuario: Administrador")

# --- LÓGICA DE NAVEGACIÓN ---

if menu == "🏠 Panel de Control":
    st.title("Panel de Control")
    st.write("Aquí pondremos gráficos y alertas de bajo stock.")

elif menu == "📦 Inventario (Equipos y Reactivos)":
    st.title("Gestión de Inventario")
    # Aquí irían las pestañas que ya creamos de "Ver" y "Agregar"

elif menu == "🚚 Movimientos a Taladros":
    st.title("Despacho a Campo")
    st.write("Formulario para cambiar la ubicación de Equipos a Pozo X.")

elif menu == "🔬 Control de Calidad":
    st.title("Análisis de Muestras")
    st.write("Registro de pruebas de fluidos y cementación.")

elif menu == "📄 Certificados":
    st.title("Emisión de Certificados")
    st.write("Generador de reportes finales.")

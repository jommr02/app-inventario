import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LIMS - WCF Fluids Lab", page_icon="🔬", layout="wide")

# ENLACES (Sustituye con tus enlaces reales)
URL_HOJA_EQUIPOS = "https://docs.google.com/spreadsheets/d/12luDlLrUIiPtxX7iqGuU3QuG_E6psGWtfYrQmSTzJCU/export?format=csv"
URL_HOJA_MUESTRAS = "https://docs.google.com/spreadsheets/d/1fZBvKgt2-S5CRKRBuzIZ8hMS_M9pLYQiz_KcSYDX31o/export?format=csv"
URL_DB_EQUIPOS = "https://sheetdb.io/api/v1/9pogtini9kr0k"

# Pega aquí el NUEVO enlace de SheetDB para la pestaña de Muestras
URL_DB_MUESTRAS = "https://sheetdb.io/api/v1/cn4v870fg7c8z"

# --- MENÚ LATERAL ---
st.sidebar.title("🧪 LIMS WCF")
st.sidebar.markdown("Sistema de Gestión de Laboratorio")
menu = st.sidebar.radio("Módulos:", [
    "📦 Inventario de Equipos",
    "📥 Recepción de Muestras",
    "🚚 Despachos a Pozos",
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
# MODULO: INVENTARIO DE EQUIPOS
# ==========================================
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

# ==========================================
# MODULO: RECEPCIÓN DE MUESTRAS
# ==========================================
elif menu == "📥 Recepción de Muestras":
    st.title("Bitácora de Recepción de Muestras")
    
    # ⚠️ ESTA ES LA LÍNEA QUE TE FALTABA ⚠️
    # Aquí le decimos a Python que descargue los datos y los guarde en "df_muestras"
    df_muestras = cargar_datos(URL_HOJA_MUESTRAS)
    
    tab_v, tab_a = st.tabs(["📋 Ver Muestras", "🆕 Ingresar Muestra"])
    
    with tab_v:
        st.subheader("Listado de Productos Recibidos")
        
        # Ahora Python ya sabe qué es df_muestras y no dará error
        if not df_muestras.empty:
            # Añadimos un buscador rápido para las muestras
            busqueda_m = st.text_input("🔍 Buscar muestra (ID, Producto o Lote):")
            
            if busqueda_m:
                # Filtramos la tabla de muestras
                df_filtro_m = df_muestras[df_muestras.astype(str).apply(lambda x: x.str.contains(busqueda_m, case=False, na=False)).any(axis=1)]
                st.dataframe(df_filtro_m, use_container_width=True)
            else:
                # Mostramos todo si no hay búsqueda
                st.dataframe(df_muestras, use_container_width=True)
        else:
            st.info("Aún no hay muestras registradas en la bitácora o hay un error en el enlace.")
            
    with tab_a:
        st.subheader("Formulario de Ingreso de Producto/Muestra")
        
        col1, col2 = st.columns(2)
        with col1:
            id_muestra = st.text_input("ID Number (DS-XX) *")
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

        if st.button("Registrar Muestra en Bitácora", type="primary"):
            if id_muestra and producto:
                nueva_muestra = {
                    "data": [
                        {
                            "ID_MUESTRA": id_muestra.upper(),
                            "PRODUCTO": producto.upper(),
                            "CANTIDAD": cant,
                            "UNIDAD": unidad,
                            "PROVEEDOR": proveedor.upper(),
                            "LOTE": lote.upper(),
                            "RECIBIDO_POR": recibido.upper(),
                            "FECHA_MUESTREO": str(f_muestreo),
                            "FECHA_RECEPCION": str(f_recepcion),
                            "ESTATUS": estatus,
                            "CERTIFICADO": "PENDIENTE"
                        }
                    ]
                }
                
                res = requests.post(URL_DB_MUESTRAS, json=nueva_muestra)
                if res.status_code == 201:
                    st.success(f"✅ Muestra {id_muestra} registrada correctamente.")
                    st.balloons()
                else:
                    st.error("⚠️ Error al conectar con la base de datos de muestras.")
            else:
                st.warning("El ID y el Nombre del Producto son obligatorios.")
# ==========================================
# OTROS MÓDULOS (PRÓXIMAMENTE)
# ==========================================
else:
    st.title(menu)
    st.warning("Este módulo está en fase de diseño. Pronto estará disponible.")


import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import hashlib

# 1. CONFIGURACIÓN E INICIALIZACIÓN
st.set_page_config(page_title="Gestión Flota Pro", layout="wide")

# Inicializar estados para evitar errores de ejecución
if 'auth_admin' not in st.session_state: st.session_state['auth_admin'] = False

# 2. MOTOR DE COMUNICACIÓN (Seguro y a prueba de errores)
def sup_query(tabla, metodo="GET", datos=None, filtros=None):
    try:
        url = f"{st.secrets['SUPABASE_URL'].strip()}/rest/v1/{tabla}"
        if filtros: url += f"?{filtros}"
        headers = {
            "apikey": st.secrets['SUPABASE_KEY'],
            "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        res = requests.request(metodo, url, headers=headers, json=datos)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# 3. INTERFAZ PRINCIPAL
st.title("🚛 Gestión Flota Profesional")
menu = st.sidebar.selectbox("Módulo", ["Administrador", "Transportista", "Conductor"])

# --- MÓDULO ADMINISTRADOR (Protegido con clave privada) ---
if menu == "Administrador":
    if not st.session_state['auth_admin']:
        pwd = st.text_input("Ingrese Clave Privada", type="password")
        if st.button("Acceder"):
            if pwd == "Admin1234": # Cambia esta clave por la que tú definas
                st.session_state['auth_admin'] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    else:
        st.subheader("⚙️ Panel de Administración Global")
        if st.button("Cargar Directorio de Empresas"):
            empresas = sup_query("empresas")
            if empresas:
                df = pd.DataFrame(empresas)
                st.dataframe(df, use_container_width=True)
        if st.button("Cerrar Sesión"):
            st.session_state['auth_admin'] = False
            st.rerun()

# --- MÓDULO TRANSPORTISTA (Gestión, Excel y GPS) ---
elif menu == "Transportista":
    st.header("🏢 Portal del Transportista")
    tabs = st.tabs(["📊 Reportes y Excel", "📍 Monitoreo GPS"])
    
    with tabs[0]:
        st.write("Descarga de guías para facturación:")
        if st.button("Generar Excel de Guías"):
            datos = sup_query("reportes")
            if datos:
                df = pd.DataFrame(datos)
                st.download_button("📥 Descargar Excel", df.to_csv(index=False), "guias.csv", "text/csv")
    
    with tabs[1]:
        st.write("Seguridad y Posición en tiempo real:")
        # Aquí insertaremos la lógica del mapa cuando los datos GPS estén fluyendo
        st.info("El sistema está esperando coordenadas desde la base de datos.")

# --- MÓDULO CONDUCTOR ---
elif menu == "Conductor":
    st.header("🚚 Reporte de Viaje")
    st.write("Formulario de carga de datos...")

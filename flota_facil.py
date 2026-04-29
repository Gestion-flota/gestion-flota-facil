import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Plataforma Logística", layout="centered")

# Simulación de base de datos de usuarios (PIN: Nombre)
USUARIOS = {
    "1234": "Conductor 1",
    "5678": "Conductor 2",
    "9999": "Administrador (Transportista)"
}

# --- LÓGICA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🚚 Acceso al Sistema")
    pin = st.text_input("Ingrese su PIN de seguridad", type="password")
    
    if st.button("Entrar"):
        if pin in USUARIOS:
            st.session_state.autenticado = True
            st.session_state.usuario = USUARIOS[pin]
            st.session_state.es_admin = (pin == "9999")
            st.rerun()
        else:
            st.error("PIN incorrecto. Intente de nuevo.")

# --- SISTEMA PARA CONDUCTORES ---
else:
    st.sidebar.write(f"Usuario: **{st.session_state.usuario}**")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

    if not st.session_state.es_admin:
        st.header("📝 Registro de Jornada")
        patente = st.text_input("Patente del Camión (Ej: ABCD-12)").upper()
        ruta = st.text_input("ID de Ruta o Destino")
        novedades = st.text_area("Novedades del trayecto")

        if st.button("Iniciar / Reportar Trabajo"):
            if patente and ruta:
                # Aquí se guardaría en una base de datos real
                st.success(f"✅ ¡Buen viaje! Patente {patente} registrada a las {datetime.now().strftime('%H:%M')}")
            else:
                st.warning("Por favor complete Patente y Ruta.")

    # --- PANEL PARA EL TRANSPORTISTA (ADMIN) ---
    else:
        st.header("📊 Panel de Control (Transportista)")
        st.write("Estado actual de los 20 equipos en trabajo:")
        
        # Simulación de los datos que vería el dueño
        datos_ejemplo = {
            "Conductor": ["Juan Pérez", "Pedro Soto", "Luis Jara"],
            "Patente": ["CCRS-20", "ABCD-12", "XY-9988"],
            "Estado": ["En Ruta", "Descarga", "Iniciando"],
            "Último Reporte": ["13:45", "14:10", "14:25"]
        }
        st.table(pd.DataFrame(datos_ejemplo))

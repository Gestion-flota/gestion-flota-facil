import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Control de Transportes", page_icon="🚚")

# --- TU BASE DE DATOS (Agrega aquí tus clientes reales) ---
EMPRESAS = {
    "Transportes Maule": {
        "pin_dueño": "9090",
        "choferes": {
            "1111": {"nombre": "Juan Pérez", "patente": "CCRS-20"},
            "2222": {"nombre": "Pedro Soto", "patente": "ABCD-12"}
        }
    }
}

if "sesion" not in st.session_state:
    st.session_state.sesion = None

# --- ACCESO ---
if st.session_state.sesion is None:
    st.title("🚚 Acceso al Sistema")
    pin = st.text_input("Ingrese su PIN", type="password")
    if st.button("Entrar"):
        for nombre, datos in EMPRESAS.items():
            if pin == datos["pin_dueño"]:
                st.session_state.sesion = {"tipo": "dueño", "empresa": nombre}
                st.rerun()
            elif pin in datos["choferes"]:
                info = datos["choferes"][pin]
                st.session_state.sesion = {"tipo": "chofer", "nombre": info["nombre"], "patente": info["patente"]}
                st.rerun()

# --- VISTA DEL CONDUCTOR (Cámara y Reporte) ---
elif st.session_state.sesion["tipo"] == "chofer":
    s = st.session_state.sesion
    st.header(f"Hola {s['nombre']}")
    st.info(f"Patente: {s['patente']}")
    
    # Captura de guía (el navegador del celular permitirá elegir la cámara trasera)
    foto = st.camera_input("Fotografiar Guía de Flete")
    
    if foto:
        st.success("✅ Guía capturada.")
        if st.button("Finalizar y Enviar Ubicación"):
            st.info("📍 Ubicación GPS enviada al transportista.")
            st.balloons()
    
    if st.button("Salir"):
        st.session_state.sesion = None
        st.rerun()

# --- VISTA DEL TRANSPORTISTA (Mapa y Control) ---
elif st.session_state.sesion["tipo"] == "dueño":
    st.title(f"Panel: {st.session_state.sesion['empresa']}")
    st.subheader("Ubicación de los 20 camiones")
    
    # Mapa con ubicaciones de ejemplo en la zona central
    mapa = pd.DataFrame({'lat': [-35.59, -33.44], 'lon': [-71.67, -70.66]})
    st.map(mapa)
    
    if st.button("Cerrar Sesión"):
        st.session_state.sesion = None
        st.rerun()

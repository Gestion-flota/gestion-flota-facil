import streamlit as st
import pandas as pd
from datetime import datetime

# --- BASE DE DATOS ACTUALIZADA ---
EMPRESAS = {
    "Transportes Linares": {
        "pin_admin": "9090",
        "conductores": {
            "1111": {"nombre": "Juan Pérez", "patente": "CCRS-20", "ruta": "Talca - Santiago"},
            "2222": {"nombre": "Pedro Soto", "patente": "ABCD-12", "ruta": "Linares - Concepción"}
        }
    }
}

if "sesion" not in st.session_state:
    st.session_state.sesion = None

# --- ACCESO ---
if st.session_state.sesion is None:
    st.title("🚚 Plataforma Logística Central")
    pin = st.text_input("Ingrese su PIN", type="password")
    if st.button("Entrar"):
        for nombre, datos in EMPRESAS.items():
            if pin == datos["pin_admin"]:
                st.session_state.sesion = {"tipo": "dueño", "empresa": nombre}
                st.rerun()
            elif pin in datos["conductores"]:
                info = datos["conductores"][pin]
                st.session_state.sesion = {"tipo": "conductor", "nombre": info["nombre"], "patente": info["patente"]}
                st.rerun()

# --- PANTALLA DEL CONDUCTOR (Subir Guía y GPS) ---
elif st.session_state.sesion["tipo"] == "conductor":
    s = st.session_state.sesion
    st.header(f"Hola {s['nombre']} | Patente: {s['patente']}")
    
    st.subheader("📷 Reportar Entrega")
    # Función para subir foto de la guía
    foto_guia = st.camera_input("Tome una foto a la guía de flete")
    
    if foto_guia:
        st.success("Foto capturada con éxito.")
    
    if st.button("Enviar Ubicación GPS y Finalizar"):
        # Aquí simulamos la captura de coordenadas
        st.info("📍 Ubicación enviada: -35.59, -71.51 (Linares)")
        st.success("✅ Jornada reportada correctamente.")
    
    if st.button("Salir"):
        st.session_state.sesion = None
        st.rerun()

# --- PANTALLA DEL DUEÑO (Mapa y Documentos) ---
elif st.session_state.sesion["tipo"] == "dueño":
    st.title(f"Panel: {st.session_state.sesion['empresa']}")
    
    # Simulador de Mapa GPS
    st.subheader("🗺️ Ubicación de Equipos en Tiempo Real")
    mapa_data = pd.DataFrame({'lat': [-33.44, -35.42], 'lon': [-70.66, -71.67]})
    st.map(mapa_data) # Esto dibuja un mapa real en la pantalla
    
    st.subheader("📂 Guías de Flete Recibidas")
    st.write("1. Guía_Juan_CCRS20.jpg - [Ver Imagen]")
    st.write("2. Guía_Pedro_ABCD12.jpg - [Ver Imagen]")

    if st.button("Cerrar Sesión"):
        st.session_state.sesion = None
        st.rerun()

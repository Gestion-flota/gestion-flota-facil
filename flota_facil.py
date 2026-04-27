import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Base de datos con nuevos campos
def crear_db():
    conn = sqlite3.connect('datos_logistica.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                  foto_url TEXT, latitud REAL, longitud REAL, fecha TEXT)''')
    conn.commit()
    conn.close()

st.set_page_config(page_title="Logística Profesional", layout="wide")
crear_db()

# Pestañas nuevas
tab1, tab2 = st.tabs(["🚛 Registro Conductor", "🏢 Panel Transportista"])

with tab1:
    st.header("Envío de Guía - Sección Conductor")
    cod_empresa = st.text_input("Código de Empresa")
    nombre_conductor = st.text_input("Nombre del Conductor")
    patente = st.text_input("Patente del Camión")
    n_guia = st.text_input("Número de Guía")
    archivo_foto = st.file_uploader("Subir foto de la guía", type=['png', 'jpg', 'jpeg'])
    
    # Ubicación Linares por defecto
    lat = st.number_input("Latitud", value=-35.8400, format="%.4f")
    lon = st.number_input("Longitud", value=-71.5900, format="%.4f")

    if st.button("Finalizar y Enviar Reporte"):
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect('datos_logistica.db')
        c = conn.cursor()
        c.execute("INSERT INTO reportes VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (cod_empresa, nombre_conductor, patente, n_guia, "Imagen", lat, lon, ahora))
        conn.commit()
        conn.close()
        st.success("¡Enviado!")

with tab2:
    st.header("Control de Flota - Sección Transportista")
    consulta_cod = st.text_input("Ingrese Código", type="password")
    if consulta_cod:
        conn = sqlite3.connect('datos_logistica.db')
        df = pd.read_sql_query(f"SELECT * FROM reportes WHERE empresa='{consulta_cod}'", conn)
        conn.close()
        if not df.empty:
            st.dataframe(df)
            st.subheader("Mapa de Entregas")
            df_mapa = df.rename(columns={'latitud': 'lat', 'longitud': 'lon'})
            st.map(df_mapa)

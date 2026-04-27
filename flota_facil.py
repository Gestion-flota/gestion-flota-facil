import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Configuración de Base de Datos
def crear_db():
    conn = sqlite3.connect('base_nueva_linares.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                  foto BLOB, latitud REAL, longitud REAL, fecha TEXT)''')
    conn.commit()
    conn.close()

st.set_page_config(page_title="Control de Flota Profesional", layout="wide")
crear_db()

tab1, tab2 = st.tabs(["🚛 Registro Conductor", "📊 Panel Transportista"])

with tab1:
    st.header("Envío de Guía - Sección Conductor")
    cod_empresa = st.text_input("Código de Empresa")
    nombre_conductor = st.text_input("Nombre del Conductor")
    patente = st.text_input("Patente del Camión")
    n_guia = st.text_input("Número de Guía")
    
    foto_camara = st.camera_input("Toma una foto de la guía")
    
    st.write("Ubicación actual (GPS)")
    lat = st.number_input("Latitud", value=-35.8406, format="%.4f")
    lon = st.number_input("Longitud", value=-71.5941, format="%.4f")
    
    if st.button("Finalizar y Enviar Reporte") and foto_camara:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        img_bytes = foto_camara.getvalue()
        
        conn = sqlite3.connect('base_nueva_linares.db')
        c = conn.cursor()
        c.execute("INSERT INTO reportes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (cod_empresa, nombre_conductor, patente, n_guia, img_bytes, lat, lon, ahora))
        conn.commit()
        conn.close()
        st.success("✅ Reporte enviado con éxito")

with tab2:
    st.header("Acceso Privado - Panel Transportista")
    clave = st.text_input("Ingrese Clave de Administrador", type="password")
    
    if clave == "linares2026":
        st.success("Acceso concedido")
        conn = sqlite3.connect('base_nueva_linares.db')
        df = pd.read_sql_query("SELECT empresa, conductor, patente, guia, fecha, latitud, longitud FROM reportes", conn)
        conn.close()

        if not df.empty:
            st.write("### Listado de Reportes Recibidos")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Reportes (CSV)", csv, "reportes_flota.csv", "text/csv")
        else:
            st.info("Aún no hay reportes registrados.")

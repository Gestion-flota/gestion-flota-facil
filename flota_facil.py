import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Base de datos
def crear_db():
    conn = sqlite3.connect('datos_vFinal.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                 foto BLOB, latitud REAL, longitud REAL, fecha TEXT)''')
    conn.commit()
    conn.close()

st.set_page_config(page_title="Control de Flota Profesional", layout="wide")
crear_db()

tab1, tab2 = st.tabs(["🚛 Registro Conductor", "🏢 Panel Transportista"])

with tab1:
    st.header("Envío de Guía - Sección Conductor")
    cod_empresa = st.text_input("Código de Empresa")
    nombre_conductor = st.text_input("Nombre del Conductor")
    patente = st.text_input("Patente del Camión")
    n_guia = st.text_input("Número de Guía")
    
    # CÁMARA DIRECTA
    foto_camara = st.camera_input("Toma una foto de la guía")
    
    # GPS (Linares por defecto, ajustable)
    st.write("Ubicación actual (GPS)")
    lat = st.number_input("Latitud", value=-35.8406, format="%.4f")
    lon = st.number_input("Longitud", value=-71.5941, format="%.4f")

    if st.button("Finalizar y Enviar Reporte") and foto_camara:
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        img_bytes = foto_camara.getvalue()
        conn = sqlite3.connect('datos_logistica.db')
        c = conn.cursor()
        c.execute("INSERT INTO reportes (empresa, conductor, patente, guia, foto, latitud, longitud, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (cod_empresa, nombre_conductor, patente, n_guia, img_bytes, lat, lon, ahora))
        conn.commit()
        conn.close()
        st.success("✅ Guía enviada con éxito")

with tab2:
    st.header("Control de Flota - Sección Transportista")
    consulta_cod = st.text_input("Ingrese su Clave de Empresa", type="password")
    if consulta_cod:
        conn = sqlite3.connect('datos_logistica.db')
        df = pd.read_sql_query(f"SELECT conductor, patente, guia, fecha, latitud, longitud, foto FROM reportes WHERE empresa='{consulta_cod}'", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df.drop(columns=['foto'])) # Mostramos tabla sin los datos crudos de la foto
            
            st.subheader("📍 Ubicación en Mapa")
            df_mapa = df.rename(columns={'latitud': 'lat', 'longitud': 'lon'})
            st.map(df_mapa)

            st.subheader("📸 Visualizador de Guías")
            # Esto permite ver la última foto subida
            ultima_foto = df['foto'].iloc[-1]
            st.image(ultima_foto, caption=f"Última guía subida por {df['conductor'].iloc[-1]}", width=400)

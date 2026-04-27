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

st.set_page_config(page_title="Gestión de Flota - Linares", layout="wide")
crear_db()

tab1, tab2 = st.tabs(["🚛 Registro Conductor", "🔐 Panel Transportista (Privado)"])

with tab1:
    st.header("Envío de Guía")
    # El conductor solo pone el nombre de la empresa, NO necesita clave
    cod_empresa = st.text_input("Nombre de la Empresa Destino")
    nombre_conductor = st.text_input("Nombre del Conductor")
    patente = st.text_input("Patente del Camión")
    n_guia = st.text_input("Número de Guía")
    
    foto_camara = st.camera_input("Toma una foto de la guía")
    
    if st.button("Finalizar y Enviar Reporte"):
        if foto_camara:
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img_bytes = foto_camara.getvalue()
            conn = sqlite3.connect('base_nueva_linares.db')
            c = conn.cursor()
            c.execute("INSERT INTO reportes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (cod_empresa, nombre_conductor, patente, n_guia, img_bytes, -35.8406, -71.5941, ahora))
            conn.commit()
            conn.close()
            st.success("✅ Reporte enviado con éxito")
        else:
            st.error("⚠️ Debes tomar la foto para enviar")

with tab2:
    st.header("Panel de Control del Dueño")
    # ESTA ES TU CLAVE ÚNICA Y ESPECIAL
    clave_maestra = "linares2026" 
    
    acceso = st.text_input("Ingrese Clave de Administrador", type="password")
    
    if acceso == clave_maestra:
        st.success("Acceso autorizado")
        conn = sqlite3.connect('base_nueva_linares.db')
        df = pd.read_sql_query("SELECT empresa, conductor, patente, guia, fecha FROM reportes", conn)
        conn.close()

        if not df.empty:
            st.write("### Reportes de Camiones")
            st.dataframe(df) # Aquí verás lo que el chofer envió
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Excel (CSV)", csv, "reportes.csv", "text/csv")
        else:
            st.info("No hay reportes nuevos aún.")
    elif acceso != "":
        st.error("❌ Clave incorrecta. Solo el transportista puede ver esto.")

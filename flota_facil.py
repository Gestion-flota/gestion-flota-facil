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
    st.info("Conductor: Complete los datos y tome la foto de la guía para enviar.")
    
    cod_empresa = st.text_input("Nombre de la Empresa Destino (Cliente)")
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
            st.error("⚠️ Error: Debe tomar la foto de la guía para poder enviar el reporte.")

with tab2:
    st.header("Panel de Control del Dueño")
    clave_maestra = "linares2026" 
    
    acceso = st.text_input("Ingrese Clave de Administrador", type="password")
    
    if acceso == clave_maestra:
        st.success("Acceso autorizado")
        
        conn = sqlite3.connect('base_nueva_linares.db')
        # Traemos todos los datos para el transportista
        query = "SELECT empresa, conductor, patente, guia, foto, fecha FROM reportes ORDER BY fecha DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if not df.empty:
            st.write("### 1. Resumen de Operaciones (Excel)")
            # Mostramos la tabla sin la columna de foto para que sea limpia
            st.dataframe(df.drop(columns=['foto']), use_container_width=True)
            
            # Botón de descarga para el registro mensual
            csv = df.drop(columns=['foto']).to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Descargar Reporte Mensual (Excel/CSV)",
                data=csv,
                file_name=f"reporte_flota_{datetime.now().strftime('%m_%Y')}.csv",
                mime="text/csv",
            )
            
            st.write("---")
            st.write("### 2. Galería de Guías Digitales")
            st.caption("Haga clic en cada fila para ver la foto de la guía enviada.")
            
            # Aquí el transportista ve las fotos una por una
            for index, row in df.iterrows():
                with st.expander(f"📄 Guía: {row['guia']} | Camión: {row['patente']} | Fecha: {row['fecha']}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.write(f"**Conductor:** {row['conductor']}")
                        st.write(f"**Cliente:** {row['empresa']}")
                    with col2:
                        st.image(row['foto'], caption=f"Copia digital de Guía {row['guia']}", use_container_width=True)
        else:
            st.info("Aún no hay reportes registrados por los conductores.")
    elif acceso != "":
        st.error("❌ Clave incorrecta. Acceso restringido al dueño del transporte.")

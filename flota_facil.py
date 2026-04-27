
import sqlite3
import pandas as pd
import streamlit as st

# 1. Crear/Conectar a la base de datos (se crea un archivo llamado datos_flota.db)
def crear_db():
    conn = sqlite3.connect('datos_flota.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, patente TEXT, guia TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# 2. Función para guardar datos
def guardar_datos(empresa, patente, guia):
    conn = sqlite3.connect('datos_flota.db')
    c = conn.cursor()
    c.execute("INSERT INTO reportes (empresa, patente, guia) VALUES (?, ?, ?)", (empresa, patente, guia))
    conn.commit()
    conn.close()

# --- EN TU INTERFAZ DE STREAMLIT ---
st.title("Control de Flota Profesional")

# Pestañas para separar el trabajo
tab1, tab2 = st.tabs(["🚛 Registro Chofer", "📊 Panel Dueño"])

with tab1:
    st.header("Envío de Guía")
    cod_empresa = st.text_input("Código de Empresa (Entregado por soporte)")
    patente = st.text_input("Patente del Camión")
    n_guia = st.text_input("Número de Guía")
    
    if st.button("Enviar Reporte"):
        crear_db()
        guardar_datos(cod_empresa, patente, n_guia)
        st.success("Reporte enviado con éxito")

with tab2:
    st.header("Visualización de Guías")
    consulta_cod = st.text_input("Ingrese su Código para ver sus datos", type="password")
    
    if consulta_cod:
        conn = sqlite3.connect('datos_flota.db')
        # Aquí ocurre la magia: solo filtramos por el código de esa empresa
        df = pd.read_sql_query(f"SELECT patente, guia, fecha FROM reportes WHERE empresa='{consulta_cod}'", conn)
        conn.close()
        
        if not df.empty:
            st.write(f"Mostrando reportes para: {consulta_cod}")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No hay datos para este código o el código es incorrecto.")

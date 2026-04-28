import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Flota Linares", layout="wide")

# --- 2. BASE DE DATOS ---
def conectar():
    return sqlite3.connect('base_nueva_linares.db', check_same_thread=False)

def crear_db():
    conn = conectar()
    c = conn.cursor()
    # Tabla de reportes con GPS y Foto
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                  fecha TEXT, ubicacion TEXT)''')
    # Tabla de Transportistas
    c.execute('''CREATE TABLE IF NOT EXISTS transportistas
                 (nombre_dueño TEXT, nombre_empresa TEXT PRIMARY KEY)''')
    # Tabla de Camiones
    c.execute('''CREATE TABLE IF NOT EXISTS camiones
                 (patente TEXT PRIMARY KEY, empresa_pertenece TEXT)''')
    conn.commit()
    conn.close()

crear_db()

# --- 3. NAVEGACIÓN ---
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a:", ["Registro de Conductor", "Panel Administrativo", "Historial de Viajes"])

# --- 4. PANEL ADMINISTRATIVO (CORREGIDO) ---
if seccion == "Panel Administrativo":
    st.header("⚙️ Panel Administrativo de Transportistas")
    st.write("Gestione sus empresas y visualice las patentes asociadas.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Registrar Nuevo Dueño/Empresa")
        n_dueño = st.text_input("Nombre del Dueño")
        n_empresa = st.text_input("Nombre de la Empresa")
        if st.button("Guardar Transportista"):
            if n_dueño and n_empresa:
                conn = conectar()
                try:
                    conn.execute("INSERT INTO transportistas VALUES (?,?)", (n_dueño, n_empresa))
                    conn.commit()
                    st.success("Transportista guardado.")
                    st.rerun()
                except: st.error("La empresa ya existe.")
                finally: conn.close()

    with col2:
        st.subheader("Asociar Patente")
        conn = conectar()
        empresas = [f[0] for f in conn.execute("SELECT nombre_empresa FROM transportistas").fetchall()]
        conn.close()

        if empresas:
            emp_sel = st.selectbox("Seleccione Empresa:", empresas)
            nueva_p = st.text_input("Patente (Ej: ABCD-12)")
            if st.button("Asociar Camión"):
                conn = conectar()
                try:
                    conn.execute("INSERT INTO camiones VALUES (?,?)", (nueva_p, emp_sel))
                    conn.commit()
                    st.success(f"Patente {nueva_p} asociada.")
                    st.rerun()
                except: st.error("Patente ya registrada.")
                finally: conn.close()

    st.divider()
    st.subheader("📋 Patentes Registradas en el Sistema")
    conn = conectar()
    df_patentes = pd.read_sql_query("SELECT patente, empresa_pertenece FROM camiones", conn)
    conn.close()
    if not df_patentes.empty:
        st.table(df_patentes) # Aquí visualizas todas las patentes asociadas
    else:
        st.info("No hay patentes registradas aún.")

# --- 5. REGISTRO DE CONDUCTOR (CON CÁMARA Y GPS) ---
if seccion == "Registro de Conductor":
    st.header("🚛 Registro de Ruta")
    
    conn = conectar()
    empresas = [f[0] for f in conn.execute("SELECT nombre_empresa FROM transportistas").fetchall()]
    conn.close()

    if not empresas:
        st.warning("Primero cargue empresas en el Panel Administrativo.")
    else:
        emp_final = st.selectbox("Seleccione su Empresa", empresas)
        
        conn = conectar()
        patentes = [f[0] for f in conn.execute("SELECT patente FROM camiones WHERE empresa_pertenece=?", (emp_final,)).fetchall()]
        conn.close()

        cond = st.text_input("Nombre del Conductor")
        pat_sel = st.selectbox("Seleccione Patente", patentes)
        n_guia = st.text_input("N° Guía de Despacho")

        # --- CÁMARA ---
        foto_guia = st.camera_input("Tome una foto a la Guía de Despacho")

        # --- SIMULACIÓN GPS ---
        st.write("📍 Ubicación: Linares, Región del Maule (GPS Activado)")
        geo = "-35.84, -71.59" # Coordenadas de Linares para la prueba

        if st.button("Finalizar Registro"):
            if foto_guia and cond and n_guia:
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn = conectar()
                conn.execute("INSERT INTO reportes (empresa, conductor, patente, guia, fecha, ubicacion) VALUES (?,?,?,?,?,?)", 
                             (emp_final, cond, pat_sel, n_guia, ahora, geo))
                conn.commit()
                conn.close()
                st.balloons()
                st.success("Registro completado y guardado.")
            else:
                st.error("Por favor, complete todos los datos y tome la foto.")

# --- 6. HISTORIAL ---
if seccion == "Historial de Viajes":
    st.header("📊 Historial de Viajes")
    conn = conectar()
    df_h = pd.read_sql_query("SELECT * FROM reportes", conn)
    conn.close()
    st.dataframe(df_h, use_container_width=True)

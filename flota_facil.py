import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Flota Linares", layout="wide")

# --- 2. CONFIGURACIÓN DE BASE DE DATOS ---
def crear_db():
    conn = sqlite3.connect('base_nueva_linares.db')
    c = conn.cursor()
    # Tabla de reportes (fotos y datos de ruta)
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                  foto BLOB, latitud REAL, longitud REAL, fecha TEXT)''')
    
    # Tabla de Transportistas (Dueños)
    c.execute('''CREATE TABLE IF NOT EXISTS transportistas
                 (nombre_dueño TEXT, nombre_empresa TEXT PRIMARY KEY)''')
    
    # Tabla de Camiones vinculados
    c.execute('''CREATE TABLE IF NOT EXISTS camiones
                 (patente TEXT PRIMARY KEY, empresa_pertenece TEXT,
                  FOREIGN KEY(empresa_pertenece) REFERENCES transportistas(nombre_empresa))''')
    conn.commit()
    conn.close()

# Ejecutamos la creación al inicio
crear_db()

def conectar():
    return sqlite3.connect('base_nueva_linares.db')

# --- 3. MENÚ LATERAL ---
st.sidebar.title("Navegación")
seccion = st.sidebar.radio("Ir a:", ["Registro de Conductor", "Panel Administrativo"])

# --- 4. SECCIÓN: PANEL ADMINISTRATIVO (Carga de Datos Inventados) ---
if seccion == "Panel Administrativo":
    st.header("⚙️ Panel de Administración")
    st.info("Desde aquí puedes cargar los transportistas y camiones para tu simulación.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Registrar Empresa/Dueño")
        nombre_d = st.text_input("Nombre del Dueño")
        nombre_e = st.text_input("Nombre de la Empresa")
        if st.button("Guardar Transportista"):
            if nombre_d and nombre_e:
                conn = conectar()
                c = conn.cursor()
                try:
                    c.execute("INSERT INTO transportistas VALUES (?,?)", (nombre_d, nombre_e))
                    conn.commit()
                    st.success(f"Empresa {nombre_e} registrada con éxito.")
                except:
                    st.error("Error: Esta empresa ya existe.")
                finally:
                    conn.close()
            else:
                st.warning("Completa ambos campos.")

    with col2:
        st.subheader("Registrar Camión")
        # Traer empresas existentes para el selector
        conn = conectar()
        c = conn.cursor()
        c.execute("SELECT nombre_empresa FROM transportistas")
        lista_e = [f[0] for f in c.fetchall()]
        conn.close()

        if lista_e:
            emp_selec = st.selectbox("Asignar a Empresa:", lista_e)
            patente_n = st.text_input("Patente (Ej: ABCD-12)")
            if st.button("Asociar Camión"):
                if patente_n:
                    conn = conectar()
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO camiones VALUES (?,?)", (patente_n, emp_selec))
                        conn.commit()
                        st.success(f"Patente {patente_n} asociada a {emp_selec}")
                    except:
                        st.error("Error: La patente ya está registrada.")
                    finally:
                        conn.close()
        else:
            st.write("Primero registra una empresa para asignar camiones.")

# --- 5. SECCIÓN: REGISTRO DE CONDUCTOR (Uso diario) ---
if seccion == "Registro de Conductor":
    st.header("🚛 Registro de Conductor - Control de Guías")
    
    # Obtener datos de la DB para los Selectores
    conn = conectar()
    c = conn.cursor()
    c.execute("SELECT nombre_empresa FROM transportistas")
    empresas = [f[0] for f in c.fetchall()]
    conn.close()

    if not empresas:
        st.warning("⚠️ No hay empresas en el sistema. Ve al Panel Administrativo para cargar datos de prueba.")
    else:
        with st.container():
            empresa_final = st.selectbox("Estimado Conductor: Seleccione la empresa", empresas)
            
            # Filtrar camiones solo de esa empresa
            conn = conectar()
            c = conn.cursor()
            c.execute("SELECT patente FROM camiones WHERE empresa_pertenece = ?", (empresa_final,))
            patentes = [f[0] for f in c.fetchall()]
            conn.close()

            if patentes:
                patente_final = st.selectbox("Seleccione Patente del Camión", patentes)
                conductor = st.text_input("Nombre del Conductor")
                n_guia = st.text_input("Número de Guía de Despacho")
                
                st.divider()
                st.write("Proceso de simulación listo para registro.")
                if st.button("Finalizar Registro de Prueba"):
                    st.balloons()
                    st.success(f"Registro exitoso para {conductor} en el camión {patente_final}")
            else:
                st.info(f"La empresa {empresa_final} no tiene camiones asociados todavía.")

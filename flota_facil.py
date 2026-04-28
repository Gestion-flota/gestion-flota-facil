4import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Flota Pro", layout="centered")

# Estilo CSS para botones grandes y diseño limpio
st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; border-radius: 10px; font-weight: bold; }
    .stCamera { border: 2px solid #007bff; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. BASE DE DATOS ---
def conectar():
    return sqlite3.connect('base_nueva_linares.db', check_same_thread=False)

def crear_db():
    conn = conectar()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, fecha TEXT, ubicacion TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS transportistas
                 (nombre_dueño TEXT, nombre_empresa TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS camiones
                 (patente TEXT PRIMARY KEY, empresa_pertenece TEXT)''')
    conn.commit()
    conn.close()

crear_db()

# --- 3. LÓGICA DE ACCESO ---
st.sidebar.title("🚛 Acceso al Sistema")
conn = conectar()
lista_e = [f[0] for f in conn.execute("SELECT nombre_empresa FROM transportistas ORDER BY nombre_empresa ASC").fetchall()]
conn.close()

# El usuario selecciona su empresa UNA SOLA VEZ
empresa_activa = st.sidebar.selectbox("Seleccione su Empresa:", ["---"] + lista_e)

if empresa_activa == "---":
    st.info("### Bienvenida/o\nPor favor, seleccione su empresa en el menú lateral para ingresar.")
    # Panel para crear empresas nuevas (Solo para ti)
    with st.expander("Registrar Nueva Empresa (Admin)"):
        n_e = st.text_input("Nombre de la Empresa")
        if st.button("Crear Empresa"):
            if n_e:
                conn = conectar()
                try:
                    conn.execute("INSERT INTO transportistas VALUES (?,?)", ("Dueño", n_e))
                    conn.commit()
                    st.success("Empresa creada. Selecciónela en el menú lateral.")
                    st.rerun()
                except: st.error("Ya existe.")
                finally: conn.close()
else:
    # Una vez seleccionada la empresa, se definen los roles
    rol = st.sidebar.radio("Entrar como:", ["Conductor (Ruta)", "Dueño (Panel Administrativo)"])
    
    # --- MÓDULO CONDUCTOR: MÁXIMA SIMPLICIDAD ---
    if rol == "Conductor (Ruta)":
        st.header(f"📋 Registro de Salida")
        st.subheader(empresa_activa)

        conn = conectar()
        patentes = [f[0] for f in conn.execute("SELECT patente FROM camiones WHERE empresa_pertenece=?", (empresa_activa,)).fetchall()]
        conn.close()

        if not patentes:
            st.error("⚠️ No tienes camiones asignados. Avisa a tu jefe.")
        else:
            cond = st.text_input("Nombre del Conductor", placeholder="Ej: Juan Pérez")
            n_guia = st.text_input("N° Guía de Despacho", placeholder="00123")
            pat_sel = st.selectbox("Seleccione Patente", patentes)
            
            st.write("---")
            st.write("📷 **Capturar Guía de Despacho**")
            # El parámetro 'facing_mode' intenta activar la cámara trasera en móviles
            foto = st.camera_input("Tome la foto", label_visibility="collapsed")

            if st.button("✅ FINALIZAR Y ENVIAR"):
                if foto and cond and n_guia:
                    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
                    conn = conectar()
                    conn.execute("INSERT INTO reportes VALUES (?,?,?,?,?,?)", 
                                 (empresa_activa, cond, pat_sel, n_guia, ahora, "Linares, Chile"))
                    conn.commit()
                    conn.close()
                    st.balloons()
                    st.success("¡Registro enviado con éxito!")
                else:
                    st.warning("Completa todos los datos y toma la foto.")

    # --- MÓDULO DUEÑO: GESTIÓN FÁCIL ---
    elif rol == "Dueño (Panel Administrativo)":
        st.header(f"📊 Panel de Control: {empresa_activa}")
        
        tab1, tab2 = st.tabs(["🚛 Mi Flota", "📜 Historial de Viajes"])
        
        with tab1:
            st.write("### Agregar Camión a mi Flota")
            nueva_p = st.text_input("Patente del nuevo camión").upper()
            if st.button("➕ Registrar Patente"):
                if nueva_p:
                    conn = conectar()
                    try:
                        conn.execute("INSERT INTO camiones VALUES (?,?)", (nueva_p, empresa_activa))
                        conn.commit()
                        st.success("Patente agregada")
                        st.rerun()
                    except: st.error("Esa patente ya está en el sistema.")
                    finally: conn.close()
            
            st.write("---")
            conn = conectar()
            mis_c = pd.read_sql_query("SELECT patente FROM camiones WHERE empresa_pertenece=?", conn, params=(empresa_activa,))
            conn.close()
            st.write(f"**Tienes {len(mis_c)} camiones registrados:**")
            st.dataframe(mis_c, use_container_width=True)

        with tab2:
            st.write("### Registros Recibidos")
            conn = conectar()
            mis_v = pd.read_sql_query("SELECT conductor, patente, guia, fecha FROM reportes WHERE empresa=?", 
                                      conn, params=(empresa_activa,))
            conn.close()
            if mis_v.empty:
                st.info("No hay viajes registrados todavía.")
            else:
                st.dataframe(mis_v, use_container_width=True)

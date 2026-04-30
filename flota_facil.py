import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Plataforma Central Logística", layout="wide")

# --- BASE DE DATOS INTERNA (El "Cerebro" de tu servicio) ---
def iniciar_sistema():
    conn = sqlite3.connect('logistica.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, empresa TEXT, 
                  chofer TEXT, patente TEXT, latitud REAL, longitud REAL)''')
    conn.commit()
    conn.close()

def guardar_movimiento(empresa, chofer, patente):
    conn = sqlite3.connect('logistica.db')
    c = conn.cursor()
    # Coordenadas de prueba (Linares) que luego serán reales por GPS
    c.execute("INSERT INTO reportes (fecha, empresa, chofer, patente, latitud, longitud) VALUES (?,?,?,?,?,?)",
              (datetime.now().strftime("%d/%m/%Y %H:%M"), empresa, chofer, patente, -35.84, -71.59))
    conn.commit()
    conn.close()

iniciar_sistema()

# --- TU GESTIÓN DE CLIENTES (Tú controlas esto desde el PC) ---
# Aquí es donde tú agregas empresas y les cobras por el PIN
CLIENTES = {
    "Transportes Linares": {"pin_dueño": "9090", "choferes": {"1111": "Juan Pérez", "2222": "Pedro Soto"}},
    "Logística Maule": {"pin_dueño": "8080", "choferes": {"3333": "Luis Jara"}}
}

# --- LÓGICA DE ACCESO ---
if "login" not in st.session_state: st.session_state.login = None

if st.session_state.login is None:
    st.title("🚚 Acceso al Sistema Central")
    pin = st.text_input("Ingrese su PIN de Seguridad", type="password")
    if st.button("Entrar"):
        for emp, datos in CLIENTES.items():
            if pin == datos["pin_dueño"]:
                st.session_state.login = {"tipo": "dueño", "empresa": emp}
                st.rerun()
            elif pin in datos["choferes"]:
                st.session_state.login = {"tipo": "chofer", "nombre": datos["choferes"][pin], "empresa": emp, "pin": pin}
                st.rerun()
        st.error("PIN no reconocido.")

# --- LO QUE VE EL CHOFER (En su teléfono) ---
elif st.session_state.login["tipo"] == "chofer":
    u = st.session_state.login
    st.header(f"Hola {u['nombre']} - {u['empresa']}")
    foto = st.camera_input("Capturar Guía (Cámara Trasera)")
    if foto and st.button("Finalizar y Enviar Reporte"):
        guardar_movimiento(u['empresa'], u['nombre'], u['pin'])
        st.success("✅ Reporte enviado al transportista.")
    if st.button("Salir"): 
        st.session_state.login = None
        st.rerun()

# --- LO QUE VE EL TRANSPORTISTA (Tu cliente en su PC o teléfono) ---
elif st.session_state.login["tipo"] == "dueño":
    emp = st.session_state.login["empresa"]
    st.title(f"Panel de Control: {emp}")
    
    conn = sqlite3.connect('logistica.db')
    df = pd.read_sql_query(f"SELECT * FROM reportes WHERE empresa='{emp}'", conn)
    conn.close()

    tab1, tab2 = st.tabs(["📍 Mapa de Flota", "📋 Historial"])
    with tab1:
        if not df.empty: st.map(df[['latitud', 'longitud']])
        else: st.info("Sin movimientos reportados.")
    with tab2:
        st.dataframe(df, use_container_width=True)
    
    if st.button("Cerrar Sesión"):
        st.session_state.login = None
        st.rerun()

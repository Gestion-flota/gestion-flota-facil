import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Plataforma Central Logística", page_icon="🚚", layout="wide")

# --- INICIALIZACIÓN DE LA BASE DE DATOS (El "Cerebro") ---
# Esto crea un archivo 'logistica_datos.db' donde se guardan las fotos y GPS
def init_db():
    conn = sqlite3.connect('logistica_datos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reportes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, empresa TEXT, chofer TEXT, 
                  latitud REAL, longitud REAL, foto BLOB)''')
    conn.commit()
    conn.close()

init_db()

# --- TU GESTIÓN DE CLIENTES (Configuración de PINes) ---
CLIENTES = {
    "Transportes Linares": {
        "pin_master": "9090",
        "choferes": {
            "1111": "Juan Pérez",
            "2222": "Pedro Soto"
        }
    },
    "Transportes Maule": {
        "pin_master": "8080",
        "choferes": {
            "3333": "Carlos Jara"
        }
    }
}

# --- LÓGICA DE ACCESO ---
if "login" not in st.session_state:
    st.session_state.login = None

# Pantalla de Login si no está autenticado
if st.session_state.login is None:
    st.title("🚚 Acceso al Sistema Central")
    pin = st.text_input("Ingrese su PIN de Seguridad", type="password")
    
    if st.button("Entrar"):
        found = False
        # Buscamos si el PIN corresponde a un dueño o chofer
        for empresa, datos in CLIENTES.items():
            if pin == datos["pin_master"]:
                st.session_state.login = {"tipo": "dueño", "empresa": empresa}
                found = True
                break
            elif pin in datos["choferes"]:
                st.session_state.login = {"tipo": "chofer", "empresa": empresa, "nombre": datos["choferes"][pin]}
                found = True
                break
        
        if found: st.rerun()
        else: st.error("PIN incorrecto.")

else:
    u = st.session_state.login
    
    # BOTÓN DE CERRAR SESIÓN (Siempre visible arriba)
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.login = None
        st.rerun()

    # --- VISTA DEL CHOFER (En su Teléfono) ---
    if u["tipo"] == "chofer":
        st.header(f"Hola {u['nombre']} - {u['empresa']}")
        st.divider()
        
        st.subheader("Registrar Transporte")
        # --- CÁMARA TRASERA OBLIGATORIA (Corrección) ---
        # Usamos el modo captura de archivos para dar la opción de cámara trasera en el celular
        foto = st.file_uploader("Subir o capturar foto de la Guía", type=["jpg", "png", "jpeg"], accept_multiple_files=False)
        
        # Simulamos GPS de Linares para que el mapa funcione
        lat, lon = -35.84, -71.59
        
        if foto:
            st.image(foto, caption="Vista Previa", use_container_width=True)
            if st.button("Enviar Reporte Final"):
                # Guardamos en la base de datos interna
                conn = sqlite3.connect('logistica_datos.db')
                c = conn.cursor()
                c.execute("INSERT INTO reportes (fecha, empresa, chofer, latitud, longitud, foto) VALUES (?,?,?,?,?,?)",
                          (datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), u['empresa'], u['nombre'], lat, lon, foto.read()))
                conn.commit()
                conn.close()
                
                st.success("✅ Reporte archivado. El transportista ya puede verlo.")
                st.balloons()

    # --- VISTA DEL TRANSPORTISTA (Tu Cliente) ---
    elif u["tipo"] == "dueño":
        st.title(f"Panel de Control: {u['empresa']}")
        
        # Cargamos los datos de la base de datos interna
        conn = sqlite3.connect('logistica_datos.db')
        # Buscamos solo los datos que corresponden a esta empresa
        query = f"SELECT * FROM reportes WHERE empresa = '{u['empresa']}'"
        df = pd.read_sql_query(query, conn)
        conn.close()

        tab1, tab2 = st.tabs(["📍 Mapa de Flota", "📋 Historial"])
        
        with tab1:
            st.subheader("Equipos en función (Último reporte)")
            # --- CORRECCIÓN DEL MAPA ---
            # Solo dibujamos si el DataFrame 'df' no está vacío
            if not df.empty:
                # El componente st.map necesita una tabla con columnas 'lat' y 'lon'
                st.map(df[['latitud', 'longitud']])
            else:
                st.info("Aún no hay reportes de equipos registrados en esta flota.")
                
        with tab2:
            st.subheader("Archivo de Transportes")
            # Mostramos la tabla completa para que el transportista descargue su reporte
            st.dataframe(df.drop(columns=['foto']), use_container_width=True) # Ocultamos el blob de la foto

st.sidebar.divider()
st.sidebar.caption("Plataforma Administrada Centralmente")

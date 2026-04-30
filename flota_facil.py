import streamlit as st
import pandas as pd
import sqlite3
import datetime

# --- CONFIGURACIÓN DE LA PLATAFORMA ---
st.set_page_config(page_title="Plataforma Logística Central", layout="wide")

# --- SISTEMA DE ARCHIVO INTERNO ---
def inicializar_base_datos():
    conn = sqlite3.connect('logistica_v3.db')
    c = conn.cursor()
    # Registramos: Fecha, Tu Cliente, Chofer, Patente, Empresa Destino, Ubicación y Foto
    c.execute('''CREATE TABLE IF NOT EXISTS reportes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, empresa_transportista TEXT, 
                  chofer TEXT, patente TEXT, cliente_destino TEXT, latitud REAL, longitud REAL, foto BLOB)''')
    conn.commit()
    conn.close()

inicializar_base_datos()

# --- GESTIÓN DE TUS CLIENTES (Transportistas) ---
# Aquí es donde tú controlas quién accede al servicio
CLIENTES = {
    "Transportes Linares": {
        "pin_dueño": "9090", 
        "choferes": {"1111": "Juan Pérez", "2222": "Pedro Soto"}
    }
}

if "sesion" not in st.session_state:
    st.session_state.sesion = None

# --- PANTALLA DE INGRESO ---
if st.session_state.sesion is None:
    st.title("🚚 Acceso al Sistema Central")
    pin_entrada = st.text_input("Ingrese su PIN de Seguridad", type="password")
    if st.button("Entrar"):
        for emp, datos in CLIENTES.items():
            if pin_entrada == datos["pin_dueño"]:
                st.session_state.sesion = {"tipo": "dueño", "empresa": emp}
                st.rerun()
            elif pin_entrada in datos["choferes"]:
                st.session_state.sesion = {"tipo": "chofer", "empresa": emp, "nombre": datos["choferes"][pin_entrada]}
                st.rerun()
        st.error("PIN no válido")

else:
    s = st.session_state.sesion
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.sesion = None
        st.rerun()

    # --- LO QUE VE EL CONDUCTOR (Simplicidad total) ---
    if s["tipo"] == "chofer":
        st.header(f"Hola {s['nombre']}")
        st.subheader("Registro de Servicio")
        
        # Campos obligatorios
        patente = st.text_input("Patente del Camión", placeholder="Ej: CCRS-20")
        cliente_destino = st.text_input("Empresa a la que presta servicio", placeholder="Ej: Frutícola El Monte")
        
        st.write("### Subir Guía de Despacho")
        # El componente de carga activa la cámara trasera automáticamente en móviles
        foto_archivo = st.file_uploader("Presione para activar cámara trasera y tomar foto", type=["jpg", "png", "jpeg"])
        
        if st.button("🚀 Enviar Reporte Ahora"):
            if patente and cliente_destino and foto_archivo:
                # Simulación de ubicación en Linares
                lat, lon = -35.84, -71.59
                
                conn = sqlite3.connect('logistica_v3.db')
                c = conn.cursor()
                c.execute("""INSERT INTO reportes (fecha, empresa_transportista, chofer, patente, cliente_destino, latitud, longitud, foto) 
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), s['empresa'], s['nombre'], 
                           patente.upper(), cliente_destino, lat, lon, foto_archivo.read()))
                conn.commit()
                conn.close()
                st.success("✅ Reporte enviado correctamente.")
                st.balloons()
            else:
                st.error("Por favor completa todos los datos y toma la foto.")

    # --- LO QUE VE EL TRANSPORTISTA (Fácil y directo) ---
    elif s["tipo"] == "dueño":
        st.title(f"Panel: {s['empresa']}")
        
        conn = sqlite3.connect('logistica_v3.db')
        df = pd.read_sql_query(f"SELECT fecha, chofer, patente, cliente_destino, latitud, longitud FROM reportes WHERE empresa_transportista = '{s['empresa']}'", conn)
        conn.close()

        menu = st.radio("Ver información:", ["Mapa de Flota", "Historial de Guías"], horizontal=True)
        
        if menu == "Mapa de Flota":
            if not df.empty:
                st.map(df)
            else:
                st.info("No hay camiones en función todavía.")
        else:
            st.write("### Lista de Transportes Realizados")
            st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)

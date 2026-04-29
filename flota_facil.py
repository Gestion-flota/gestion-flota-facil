import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. BASE DE DATOS DE TUS CLIENTES (Tú controlas esto) ---
# Aquí es donde registras a cada empresa que te contrata
EMPRESAS = {
    "Transportes Linares": {
        "pin_admin": "9090",
        "conductores": {
            "1111": {"nombre": "Juan Pérez", "patente": "CCRS-20", "ruta": "Talca - Santiago"},
            "2222": {"nombre": "Pedro Soto", "patente": "ABCD-12", "ruta": "Linares - Concepción"}
        }
    },
    "Logística Maule": {
        "pin_admin": "8080",
        "conductores": {
            "3333": {"nombre": "Luis Jara", "patente": "XY-9988", "ruta": "Curicó - Chillán"}
        }
    }
}

# --- LÓGICA DE NAVEGACIÓN ---
if "sesion" not in st.session_state:
    st.session_state.sesion = None

def cerrar_sesion():
    st.session_state.sesion = None
    st.rerun()

# --- PANTALLA DE ACCESO (LOGIN) ---
if st.session_state.sesion is None:
    st.title("🚚 Sistema Central de Transportes")
    st.subheader("Acceso Seguro")
    
    pin_ingresado = st.text_input("Ingrese su PIN", type="password")
    
    if st.button("Entrar"):
        encontrado = False
        # Buscamos en todas las empresas si el PIN coincide con un Dueño o un Conductor
        for nombre_empresa, datos in EMPRESAS.items():
            # Check si es Dueño
            if pin_ingresado == datos["pin_admin"]:
                st.session_state.sesion = {"tipo": "dueño", "empresa": nombre_empresa}
                encontrado = True
                break
            # Check si es Conductor
            elif pin_ingresado in datos["conductores"]:
                info = datos["conductores"][pin_ingresado]
                st.session_state.sesion = {
                    "tipo": "conductor", 
                    "empresa": nombre_empresa,
                    "nombre": info["nombre"],
                    "patente": info["patente"],
                    "ruta": info["ruta"]
                }
                encontrado = True
                break
        
        if encontrado:
            st.rerun()
        else:
            st.error("PIN no reconocido.")

# --- VISTA DEL CONDUCTOR (SIMPLE Y DIRECTA) ---
elif st.session_state.sesion["tipo"] == "conductor":
    s = st.session_state.sesion
    st.title(f"Hola, {s['nombre']}")
    st.info(f"📍 **Empresa:** {s['empresa']}")
    
    st.subheader("Asignación de hoy:")
    col1, col2 = st.columns(2)
    col1.metric("Patente", s["patente"])
    col2.metric("Ruta", s["ruta"])
    
    estado = st.radio("Estado de la jornada:", ["En Espera", "Iniciada", "En Ruta", "Finalizada"])
    notas = st.text_area("Observaciones (opcional):")
    
    if st.button("Confirmar Reporte"):
        # Aquí enviarías la información a una base de datos central
        st.success("✅ Reporte enviado al transportista.")
    
    if st.button("Cerrar Sesión"):
        cerrar_sesion()

# --- VISTA DEL DUEÑO / TRANSPORTISTA (MONITOREO) ---
elif st.session_state.sesion["tipo"] == "dueño":
    empresa = st.session_state.sesion["empresa"]
    st.title(f"Panel de Control: {empresa}")
    
    st.subheader("Estado de su Flota")
    # Mostramos a sus conductores específicos
    lista_conductores = EMPRESAS[empresa]["conductores"]
    df = pd.DataFrame.from_dict(lista_conductores, orient='index')
    st.table(df)
    
    if st.button("Cerrar Sesión"):
        cerrar_sesion()

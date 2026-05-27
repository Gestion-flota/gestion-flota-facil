
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="Gestión Flota Fácil", layout="wide")

# Seguridad: Las credenciales ahora viven protegidas en la nube
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def ejecutar_consulta(tabla, metodo="GET", datos=None, filtros=None):
    """Motor central de comunicación con la base de datos"""
    url = f"{SUPABASE_URL}/rest/v1/{tabla}"
    if filtros:
        url += f"?{filtros}"
        
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    try:
        if metodo == "POST":
            response = requests.post(url, headers=headers, json=datos)
        else:
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# ==========================================
# 2. INTERFAZ DE USUARIO
# ==========================================
st.title("🚛 Gestión Flota Fácil")
menu = st.sidebar.selectbox("Perfil de Usuario", ["Transportista", "Conductor"])

# --- MÓDULO TRANSPORTISTA ---
if menu == "Transportista":
    st.header("🏢 Portal de la Empresa")
    
    if "usuario" not in st.session_state: 
        st.session_state["usuario"] = None

    # Pantalla de Login / Registro
    if not st.session_state["usuario"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Iniciar Sesión")
            log_email = st.text_input("Correo electrónico").lower().strip()
            log_pass = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                seguro_email = urllib.parse.quote(log_email)
                res = ejecutar_consulta("empresas", filtros=f"correo=eq.{seguro_email}")
                if res and res[0]['password'] == log_pass:
                    st.session_state["usuario"] = log_email
                    st.session_state["nombre_empresa"] = res[0]['empresa']
                    st.rerun()
                else: 
                    st.error("Correo o contraseña incorrectos")
                    
        with col2:
            st.subheader("Registrar Empresa")
            reg_nom = st.text_input("Nombre Empresa")
            reg_email = st.text_input("Correo Registro").lower().strip()
            reg_pass = st.text_input("Crear Clave", type="password")
            if st.button("Crear Cuenta"):
                if reg_nom and reg_email and reg_pass:
                    datos = {"empresa": reg_nom, "correo": reg_email, "password": reg_pass}
                    if ejecutar_consulta("empresas", "POST", datos):
                        st.success("¡Registrado con éxito! Ya puede iniciar sesión.")
    
    # Pantalla de Gestión (Una vez logueado)
    else:
        st.info(f"Conectado como: **{st.session_state['nombre_empresa']}**")
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state["usuario"] = None
            st.rerun()

        tab1, tab2, tab3 = st.tabs(["📊 Mis Camiones", "🧾 Guías en Tiempo Real", "📥 Facturación"])

        with tab1:
            st.subheader("Añadir Equipos")
            nueva_patente = st.text_input("Ingresar nueva patente").upper().strip()
            if st.button("Registrar Camión"):
                if nueva_patente:
                    ejecutar_consulta("equipos", "POST", {"patente": nueva_patente, "correo_trans": st.session_state["usuario"]})
                    st.success(f"Patente {nueva_patente} añadida a su flota.")
            
            st.write("---")
            st.write("Flota actual:")
            equipos = ejecutar_consulta("equipos", filtros=f"correo_trans=eq.{st.session_state['usuario']}")
            if equipos:
                for eq in equipos: 
                    st.write(f"🚚 {eq['patente']}")

        with tab2:
            st.subheader("Reportes de Conductores")
            guias = ejecutar_consulta("reportes", filtros=f"correo_trans=eq.{st.session_state['usuario']}&order=id.desc")
            if guias:
                for g in guias:
                    st.markdown(f"**Camión:** {g['patente']} | **Conductor:** {g['conductor']}")
            else: 
                st.write("Aún no hay guías recibidas.")

        with tab3:
            st.subheader("Descargar Datos para Facturar")
            if st.button("Generar Excel (CSV)"):
                guias_csv = ejecutar_consulta("reportes", filtros=f"correo_trans=eq.{st.session_state['usuario']}")
                if guias_csv:
                    df = pd.DataFrame(guias_csv)
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar Fletes",
                        data=csv,
                        file_name=f"fletes_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

# --- MÓDULO CONDUCTOR ---
elif menu == "Conductor":
    st.header("🚚 Reporte Rápido de Guía")
    patente_input = st.text_input("Patente del Camión").upper().strip()
    
    if patente_input:
        seguro_pat = urllib.parse.quote(patente_input)
        verificacion = ejecutar_consulta("equipos", filtros=f"patente=eq.{seguro_pat}")
        
        if verificacion:
            st.success("✅ Camión encontrado.")
            nombre_conductor = st.text_input("Nombre del Conductor")
            if st.button("Enviar Guía Digital") and nombre_conductor:
                datos_guia = {
                    "patente": patente_input, 
                    "conductor": nombre_conductor, 
                    "correo_trans": verificacion[0]['correo_trans']
                }
                if ejecutar_consulta("reportes", "POST", datos_guia):
                    st.balloons()
                    st.success("Reporte enviado al transportista exitosamente.")
        else:
            st.error("❌ Patente no registrada.")

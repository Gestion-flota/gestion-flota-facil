
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y DISEÑO PROFESIONAL
# ==========================================
st.set_page_config(page_title="Gestión Flota Fácil", layout="wide")

# Inyección de CSS para diseño moderno
st.markdown("""
    <style>
    /* Fondo general y tipografía */
    .stApp { background-color: #f4f7f6; }
    h1 { color: #1e3a8a; font-family: 'Segoe UI', Helvetica, sans-serif; text-align: center; font-weight: 700; margin-bottom: 30px; }
    h2, h3, p, span { color: #2c3e50; font-family: 'Segoe UI', Helvetica, sans-serif; }
    
    /* Estilo de botones profesionales */
    div.stButton > button {
        background-color: #2563eb; color: white; border-radius: 8px;
        padding: 10px 24px; font-weight: bold; border: none; width: 100%;
        transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { background-color: #1d4ed8; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    
    /* Estilo de los campos de texto */
    .stTextInput > div > div > input { border-radius: 8px; border: 1px solid #cbd5e1; padding: 10px; }
    
    /* Panel lateral (Sidebar) */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SEGURIDAD A PRUEBA DE ERRORES
# ==========================================
# Usamos .strip() para destruir automáticamente cualquier espacio o salto de línea invisible
SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().replace("\n", "").replace("\r", "")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip().replace("\n", "").replace("\r", "")

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
# 3. INTERFAZ DE USUARIO PRINCIPAL
# ==========================================
st.title("🚛 Gestión Flota Fácil")

# SOLUCIÓN: El perfil de Administrador ahora sí existe en las opciones
menu = st.sidebar.selectbox("Perfil de Usuario", ["Transportista", "Conductor", "Administrador"])

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

# --- MÓDULO ADMINISTRADOR ---
elif menu == "Administrador":
    st.header("⚙️ Panel de Administración Global")
    st.warning("Área restringida para supervisión general del sistema.")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric(label="Proyección de Escalamiento", value="Hasta 50 Camiones")
    with col_m2:
        st.metric(label="Estado de Conexión", value="Operativa")
        
    st.subheader("Directorio de Empresas Registradas")
    if st.button("Cargar Base de Datos"):
        empresas = ejecutar_consulta("empresas")
        if empresas:
            df_empresas = pd.DataFrame(empresas)
            # Ocultamos la columna de contraseñas para que no se vea en pantalla
            if 'password' in df_empresas.columns:
                df_empresas = df_empresas.drop(columns=['password'])
            st.dataframe(df_empresas, use_container_width=True)
        else:
            st.info("Aún no hay empresas registradas en el sistema.")

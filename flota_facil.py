
import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURACIÓN Y TEMA
st.set_page_config(page_title="Gestión Flota Profesional", layout="wide")

# 2. MOTOR DE CONEXIÓN ROBUSTO
def sup_query(tabla, filtros=None):
    try:
        # Aseguramos limpieza de espacios en las credenciales
        url_base = st.secrets["SUPABASE_URL"].strip()
        key = st.secrets["SUPABASE_KEY"].strip()
        url = f"{url_base}/rest/v1/{tabla}"
        if filtros: url += f"?{filtros}"
        
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return None

# 3. INTERFAZ PRINCIPAL
st.title("🚛 Gestión Flota Profesional")
menu = st.sidebar.selectbox("Acceso al Sistema", ["Transportista", "Administrador"])

# --- MÓDULO TRANSPORTISTA ---
if menu == "Transportista":
    st.subheader("🏢 Acceso Transportista")
    email = st.text_input("Correo electrónico")
    pwd = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar"):
        usuario = sup_query("empresas", filtros=f"correo=eq.{email}")
        if usuario and len(usuario) > 0 and usuario[0].get('password') == pwd:
            st.session_state['usuario'] = usuario[0]['nombre_empresa']
            st.success(f"Bienvenido, {st.session_state['usuario']}")
        else:
            st.error("Correo o contraseña incorrectos")

# --- MÓDULO ADMINISTRADOR ---
elif menu == "Administrador":
    st.subheader("⚙️ Panel de Control Global")
    admin_key = st.text_input("Clave Maestra", type="password")
    
    if st.button("Acceder al Panel"):
        if admin_key == "Admin1234": # Define tu clave aquí
            st.success("Acceso Admin concedido")
            empresas = sup_query("empresas")
            if empresas:
                st.table(pd.DataFrame(empresas))
            else:
                st.warning("No se encontraron empresas registradas.")
        else:
            st.error("Clave de administrador incorrecta.")

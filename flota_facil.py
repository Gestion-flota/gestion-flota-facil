
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Gestión de Flota", layout="wide")

# Configuración de conexión (usando secrets)
def get_headers():
    return {
        "apikey": st.secrets["SUPABASE_KEY"],
        "Authorization": f"Bearer {st.secrets['SUPABASE_KEY']}",
        "Content-Type": "application/json"
    }

st.title("🚛 Gestión de Flota - Andrés")

# Definición de roles
perfil = st.sidebar.selectbox("Seleccione su Perfil", ["Transportista", "Conductor"])

if perfil == "Transportista":
    st.header("🏢 Panel del Transportista")
    if st.button("Ver Guías y Reportes"):
        try:
            url = f"{st.secrets['SUPABASE_URL']}/rest/v1/reportes"
            res = requests.get(url, headers=get_headers())
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(df)
            else:
                st.error("Error al conectar con la base de datos")
        except Exception as e:
            st.error(f"Error de red: {e}")

elif perfil == "Conductor":
    st.header("🚚 Registro de Viaje")
    with st.form("registro_viaje"):
        nombre = st.text_input("Nombre del Conductor")
        patente = st.text_input("Patente del Camión")
        if st.form_submit_button("Registrar Viaje"):
            try:
                url = f"{st.secrets['SUPABASE_URL']}/rest/v1/reportes"
                data = {"conductor": nombre, "patente": patente}
                res = requests.post(url, headers=get_headers(), json=data)
                if res.status_code == 201:
                    st.success("Viaje registrado exitosamente")
                else:
                    st.error("Error al guardar el registro")
            except Exception as e:
                st.error(f"Error técnico: {e}")

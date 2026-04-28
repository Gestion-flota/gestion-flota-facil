import streamlit as st
import pandas as pd # Para manejar datos fácilmente

# --- FUNCIONES DE CONTROL (El motor de la app) ---

def validar_usuario(usuario, password):
    # Aquí simulamos la lectura de una base de datos segura
    # En el futuro, aquí conectaremos con tu base de datos real
    db_usuarios = {
        "user01": {"pin": "1111", "rol": "conductor", "empresa": "Transportes Linares"},
        "admin01": {"pin": "admin123", "rol": "transportista", "empresa": "Transportes Linares"},
        "user02": {"pin": "2222", "rol": "conductor", "empresa": "Carga Sur"},
    }
    
    if usuario in db_usuarios and db_usuarios[usuario]["pin"] == password:
        return db_usuarios[usuario]
    return None

# --- ESTRUCTURA DE LA APP ---

def main():
    st.set_page_config(page_title="Sistema Logístico Profesional", layout="centered")

    if "sesion" not in st.session_state:
        st.session_state.sesion = None

    # PANTALLA DE LOGIN
    if st.session_state.sesion is None:
        st.title("🚚 Acceso Transportistas")
        with st.container():
            user = st.text_input("Usuario / ID de Chofer")
            clave = st.text_input("PIN / Contraseña", type="password")
            if st.button("Ingresar al Sistema"):
                datos = validar_usuario(user, clave)
                if datos:
                    st.session_state.sesion = datos
                    st.rerun()
                else:
                    st.error("Credenciales no válidas. Intente de nuevo.")
    
    # PANTALLA SEGÚN ROL
    else:
        datos = st.session_state.sesion
        st.sidebar.title(f"🏢 {datos['empresa']}")
        st.sidebar.info(f"Conectado como: {datos['rol'].upper()}")
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.sesion = None
            st.rerun()

        # --- VISTA PARA EL CONDUCTOR (Simple y Rápida) ---
        if datos['rol'] == 'conductor':
            st.header("📲 Reporte Rápido")
            patente = st.text_input("Patente del Camión")
            empresa_carga = st.text_input("Empresa donde está cargando")
            
            # Cámara bajo demanda
            if st.button("📸 Activar Cámara para Foto"):
                foto = st.camera_input("Capturar carga")
            
            if st.button("🚀 Enviar Reporte"):
                # Aquí guardaríamos el GPS y la foto
                st.success("¡Datos enviados! Ya puede continuar su ruta.")

        # --- VISTA PARA EL TRANSPORTISTA (Gestión Eficiente) ---
        elif datos['rol'] == 'transportista':
            st.header("📊 Panel de Control de Flota")
            st.write(f"Bienvenido al panel de administración de **{datos['empresa']}**.")
            
            opcion = st.radio("Ir a:", ["Seguimiento GPS", "Historial de Fotos", "Mis Conductores"])
            
            if opcion == "Seguimiento GPS":
                st.subheader("Ubicación de camiones")
                st.info("Aquí se mostrará el mapa con los puntos de carga de hoy.")
            elif opcion == "Historial de Fotos":
                st.subheader("Registro Fotográfico")
                # Aquí solo se filtrarán las fotos de SU empresa

import streamlit as st

# 1. Configuración básica (SIEMPRE debe ir primero)
st.set_page_config(page_title="Transportes Linares", layout="centered")

# 2. Inicializar la sesión
if 'sesion' not in st.session_state:
    st.session_state.sesion = None

# 3. Función Principal
def mostrar_login():
    st.title("🚛 Acceso Transportistas")
    st.subheader("Ingrese sus credenciales")
    
    usuario = st.text_input("Usuario")
    pin = st.text_input("PIN", type="password")
    
    if st.button("Ingresar"):
        # Datos de prueba rápidos
        if usuario == "admin01" and pin == "admin123":
            st.session_state.sesion = usuario
            st.rerun()
        else:
            st.error("Usuario o PIN incorrecto")

def mostrar_panel():
    st.title(f"Bienvenido, {st.session_state.sesion}")
    st.write("Panel de gestión de flota y rutas.")
    if st.button("Cerrar Sesión"):
        st.session_state.sesion = None
        st.rerun()

# 4. Lógica de arranque (Esto es lo que faltaba para que no saliera blanco)
if st.session_state.sesion is None:
    mostrar_login()
else:
    mostrar_panel()

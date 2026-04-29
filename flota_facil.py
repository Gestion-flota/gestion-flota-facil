import streamlit as st

# 1. Configuración principal
st.set_page_config(page_title="Transportes Linares", layout="centered")

# 2. Base de datos temporal (El único usuario que existe al inicio es el Administrador)
if "db_usuarios" not in st.session_state:
    st.session_state.db_usuarios = {
        "admin01": {"pin": "admin123", "rol": "transportista"}
    }

if "sesion" not in st.session_state:
    st.session_state.sesion = None

# ==========================================
# PANTALLA 1: INICIO DE SESIÓN
# ==========================================
def mostrar_login():
    st.title("🚛 Acceso al Sistema")
    st.write("Por favor, ingrese sus datos para continuar.")
    
    usuario = st.text_input("Usuario")
    clave = st.text_input("PIN / Clave", type="password") # Palabra corregida
    
    if st.button("Ingresar"):
        db = st.session_state.db_usuarios
        if usuario in db and db[usuario]["pin"] == clave:
            st.session_state.sesion = usuario
            st.rerun()
        else:
            st.error("Error: Usuario o Clave incorrectos. Intente nuevamente.")

# ==========================================
# PANTALLA 2: PANEL DE TRABAJO
# ==========================================
def mostrar_panel():
    usuario_actual = st.session_state.sesion
    datos_usuario = st.session_state.db_usuarios[usuario_actual]
    rol = datos_usuario["rol"]

    # --- Barra lateral para salir ---
    st.sidebar.title(f"👤 {usuario_actual}")
    st.sidebar.write(f"Rol: {rol.capitalize()}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.sesion = None
        st.rerun()

    # --- VISTA PARA EL DUEÑO (TRANSPORTISTA) ---
    if rol == "transportista":
        st.title("📊 Panel de Administración")
        st.write("Desde aquí puedes gestionar tu flota y crear nuevos accesos.")
        
        st.divider()
        st.subheader("➕ Crear Nuevo Usuario (Conductores)")
        with st.form("form_crear_usuario", clear_on_submit=True):
            nuevo_user = st.text_input("Nombre del nuevo usuario (Ej: ANDRES_R)")
            nuevo_pin = st.text_input("Clave para este usuario (Ej: 1234)")
            nuevo_rol = st.selectbox("Tipo de cuenta", ["conductor", "transportista"])
            
            submit = st.form_submit_button("REGISTRAR USUARIO")
            if submit:
                if nuevo_user and nuevo_pin:
                    st.session_state.db_usuarios[nuevo_user] = {"pin": nuevo_pin, "rol": nuevo_rol}
                    st.success(f"✅ ¡El usuario '{nuevo_user}' ha sido creado exitosamente!")
                else:
                    st.warning("⚠️ Debes ingresar un nombre y una clave.")
        
        st.divider()
        st.subheader("📋 Usuarios Registrados Actualmente")
        for u, datos in st.session_state.db_usuarios.items():
            st.write(f"- **{u}** (Rol: {datos['rol']})")

    # --- VISTA PARA EL CHOFER (CONDUCTOR) ---
    elif rol == "conductor":
        st.title("📲 Panel del Conductor")
        st.write("Registra tu actividad de ruta aquí.")
        
        patente = st.text_input("Patente del Camión")
        carga = st.text_input("Detalle del reparto")
        
        st.write("📸 Captura de documento/comprobante:")
        foto = st.camera_input("Tomar foto")
        
        if st.button("Enviar Reporte"):
            if patente and foto:
                st.success("✅ Reporte enviado correctamente a la central.")
            else:
                st.warning("⚠️ Faltan datos o la foto para enviar el reporte.")

# ==========================================
# MOTOR DE ARRANQUE
# ==========================================
if st.session_state.sesion is None:
    mostrar_login()
else:
    mostrar_panel()


import streamlit as st
from PIL import Image
from streamlit_js_eval import get_geolocation

# Configuración de la página
st.title("Gestión de Flota Fácil")
st.subheader("Registro de Guías y Ubicación GPS")

# 1. Campos de texto
col1, col2 = st.columns(2)
with col1:
    nombre_chofer = st.text_input("Nombre del Chofer")
    patente = st.text_input("Patente del Camión")
    id_clave = st.text_input("ID / Número de Guía")
with col2:
    servicio = st.text_input("Servicio / Empresa")
    destino = st.text_input("Ciudad de Destino")
    correo = st.text_input("Correo de contacto")

st.divider()

# 2. Captura de GPS
st.write("### Ubicación de Entrega")
loc = get_geolocation()

if loc:
    lat = loc['coords']['LATITUDE'.lower()]
    lon = loc['coords']['LONGITUDE'.lower()]
    
    st.success(f"📍 Ubicación capturada: Lat {lat}, Lon {lon}")
else:
    st.info("Esperando señal de GPS... (Asegúrese de dar permisos en su celular)")

st.divider()

# 3. Subida de Foto
archivo_guia = st.file_uploader("Tome una foto de la guía", type=["png", "jpg", "jpeg"])

if archivo_guia is not None:
    imagen = Image.open(archivo_guia)
    st.image(imagen, caption="Vista previa de la guía")

# 4. Botón Guardar
if st.button("Guardar Datos y Ubicación"):
    # Aquí irá la lógica para guardar más adelante
    st.balloons()
    st.success("¡Datos registrados con éxito!")

    if archivo_guia is not None and loc is not None:
        # Nombre del archivo con patente y guía
        nombre_foto = f"guia_{patente}_{id_clave}.png"
        
        # Guardar foto
        with open(nombre_foto, "wb") as f:
            f.write(archivo_guia.getbuffer())
            
        # Mensaje final
        st.balloons()
        st.success(f"✅ ¡Registro completo!")
        st.write(f"Chofer: {nombre_chofer} | Ubicación guardada con éxito.")
    else:
        st.error("Faltan datos: Asegúrese de subir la foto y permitir el acceso al GPS.")
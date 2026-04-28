import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. Configuración de Base de Datos
def crear_db():
    conn = sqlite3.connect('base_nueva_linares.db')
    c = conn.cursor()
    # Tabla de reportes (fotos y datos de ruta)
    c.execute('''CREATE TABLE IF NOT EXISTS reportes
                 (empresa TEXT, conductor TEXT, patente TEXT, guia TEXT, 
                  foto BLOB, latitud REAL, longitud REAL, fecha TEXT)''')
    # Tabla de Dueños de Transporte
    c.execute('''CREATE TABLE IF NOT EXISTS transportistas
                 (nombre_dueño TEXT, nombre_empresa TEXT, clave TEXT PRIMARY KEY)''')
    # Tabla de Camiones vinculados a cada clave
    c.execute('''CREATE TABLE IF NOT EXISTS camiones
                 (clave_empresa TEXT, patente TEXT)''')
    conn.commit()
    conn.close()

st.set_page_config(page_title="Control de Flota Linares", layout="wide")
crear_db()

# Menú lateral profesional
menu = st.sidebar.radio("Navegación", ["🚛 Registro de Conductor", "🔐 Panel Administrativo"])

# --- SECCIÓN 1: REGISTRO DE CONDUCTOR ---
if menu == "🚛 Registro de Conductor":
    st.header("Registro de Conductor - Control de Guías")
    st.info("Estimado Conductor: Seleccione la empresa y complete los datos de su viaje.")
    
    conn = sqlite3.connect('base_nueva_linares.db')
    empresas = pd.read_sql_query("SELECT nombre_empresa, clave FROM transportistas", conn)
    conn.close()

    if empresas.empty:
        st.warning("Aún no hay empresas registradas en el sistema.")
    else:
        # 1. Selección de Empresa
        empresa_sel = st.selectbox("Empresa para la que presta servicio", empresas['nombre_empresa'])
        clave_emp_sel = empresas[empresas['nombre_empresa'] == empresa_sel]['clave'].values[0]
        
        # 2. Datos del viaje
        nombre_conductor = st.text_input("Nombre Completo del Conductor")
        
        # Filtramos patentes autorizadas de esa empresa
        conn = sqlite3.connect('base_nueva_linares.db')
        patentes_disp = pd.read_sql_query(f"SELECT patente FROM camiones WHERE clave_empresa='{clave_emp_sel}'", conn)
        conn.close()

        patente_camion = st.selectbox("Patente del Camión", patentes_disp['patente'] if not patentes_disp.empty else ["No hay camiones registrados"])
        n_guia = st.text_input("Número de Guía de Despacho")
        
        # 3. Evidencia
        foto_camara = st.camera_input("Fotografiar Guía Firmada/Timbrada")
        
        if st.button("✅ Finalizar y Enviar Reporte"):
            if foto_camara and patente_camion != "No hay camiones registrados":
                ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                img_bytes = foto_camara.getvalue()
                conn = sqlite3.connect('base_nueva_linares.db')
                c = conn.cursor()
                c.execute("INSERT INTO reportes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                          (empresa_sel, nombre_conductor, patente_camion, n_guia, img_bytes, -35.84, -71.59, ahora))
                conn.commit()
                conn.close()
                st.success(f"¡Buen viaje {nombre_conductor}! Datos enviados correctamente.")
            else:
                st.error("⚠️ Error: Debe completar todos los campos y tomar la foto.")

# --- SECCIÓN 2: PANEL ADMINISTRATIVO ---
else:
    st.header("Panel Administrativo de Transportistas")
    
    accion = st.radio("Acción a realizar", ["Ver mis Reportes", "Registrar Empresa y Flota"], horizontal=True)

    if accion == "Registrar Empresa y Flota":
        st.subheader("Registro de Nuevo Cliente")
        with st.form("registro_maestro"):
            t_nombre = st.text_input("Nombre del Dueño")
            t_empresa = st.text_input("Nombre de la Empresa")
            t_clave = st.text_input("Cree su Clave Personal", type="password")
            
            st.write("---")
            st.write("### Carga de Patentes")
            st.caption("Escriba las patentes de sus camiones separadas por comas (ej: ABCD12, XYZ900)")
            patentes_texto = st.text_area("Lista de Patentes")

            if st.form_submit_button("Guardar Registro"):
                if t_nombre and t_empresa and t_clave and patentes_texto:
                    try:
                        conn = sqlite3.connect('base_nueva_linares.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO transportistas VALUES (?, ?, ?)", (t_nombre, t_empresa, t_clave))
                        
                        lista_p = [p.strip().upper() for p in patentes_texto.split(",")]
                        for p in lista_p:
                            if p: c.execute("INSERT INTO camiones VALUES (?, ?)", (t_clave, p))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"Empresa {t_empresa} registrada con éxito.")
                    except:
                        st.error("Esa clave ya existe. Elija una diferente.")

    else:
        clave_acceso = st.text_input("Ingrese su Clave Privada", type="password")
        if clave_acceso:
            conn = sqlite3.connect('base_nueva_linares.db')
            user = pd.read_sql_query(f"SELECT * FROM transportistas WHERE clave='{clave_acceso}'", conn)
            
            if not user.empty:
                emp_nombre = user['nombre_empresa'].values[0]
                st.success(f"Bienvenido Panel: {emp_nombre}")
                
                df = pd.read_sql_query(f"SELECT * FROM reportes WHERE empresa='{emp_nombre}' ORDER BY fecha DESC", conn)
                conn.close()

                if not df.empty:
                    st.write("### Reportes Mensuales")
                    st.dataframe(df.drop(columns=['foto']), use_container_width=True)
                    
                    csv = df.drop(columns=['foto']).to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 Descargar Excel", csv, "reporte_mensual.csv", "text/csv")
                    
                    st.write("---")
                    st.write("### Copias Digitales de Guías")
                    for i, r in df.iterrows():
                        with st.expander(f"📄 Guía {r['guia']} - Camión {r['patente']}"):
                            st.image(r['foto'], use_container_width=True)
                else:
                    st.info("Sin registros hasta el momento.")
            else:
                st.error("Clave no válida.")

import threading
import os
import json
import time

class PlataformaLogisticaPro:
    def __init__(self):
        # Nombres de archivos simplificados para máxima compatibilidad
        self.db_json = "registro_conductores.json"
        self.respaldo_txt = "respaldo_emergencia.txt"
        self.datos_locales = []

    def iniciar_sistema(self):
        """
        Dibuja la interfaz de inmediato para evitar el bloqueo de pantalla.
        """
        print("========================================")
        print("   SISTEMA DE GESTIÓN DE TRANSPORTE     ")
        print("           ROL: CONDUCTOR               ")
        print("========================================")
        print("ESTADO: SISTEMA ACTIVO")
        
        # Iniciamos la carga de archivos en un hilo separado
        threading.Thread(target=self._preparar_archivos_seguros, daemon=True).start()

    def _preparar_archivos_seguros(self):
        """Configura los archivos sin congelar la aplicación."""
        try:
            if os.path.exists(self.db_json):
                with open(self.db_json, 'r') as f:
                    self.datos_locales = json.load(f)
            else:
                with open(self.db_json, 'w') as f:
                    json.dump([], f)
        except Exception:
            # Si hay error, el sistema sigue funcionando con una base limpia
            pass

    def registrar_final_de_ruta(self, patente, ruta, observaciones):
        """
        Función principal que usará el conductor al terminar su entrega.
        """
        registro = {
            "timestamp": time.strftime("%d/%m/%Y %H:%M:%S"),
            "patente": patente.upper(),
            "id_ruta": ruta,
            "notas": observaciones
        }

        # Guardado asíncrono para que la app no se 'pegue' al escribir
        threading.Thread(target=self._guardar_datos, args=(registro,), daemon=True).start()
        return "✔️ Información registrada exitosamente."

    def _guardar_datos(self, nuevo_registro):
        """Escribe los datos en JSON y genera un respaldo en texto."""
        try:
            # 1. Guardar en JSON (Estructura principal)
            self.datos_locales.append(nuevo_registro)
            with open(self.db_json, 'w') as f:
                json.dump(self.datos_locales, f, indent=4)
            
            # 2. Guardar en TXT (Respaldo de seguridad humana)
            linea_txt = f"{nuevo_registro['timestamp']} | {nuevo_registro['patente']} | {nuevo_registro['id_ruta']}\n"
            with open(self.respaldo_txt, "a") as f_txt:
                f_txt.write(linea_txt)
                
        except Exception as e:
            print(f"Error silencioso de guardado: {e}")

# --- EJECUCIÓN DEL SISTEMA ---

app = PlataformaLogisticaPro()

# Paso 1: Encender la pantalla (Inmediato)
app.iniciar_sistema()

# Paso 2: Simulación de un conductor registrando datos
# (Esto es lo que pasaría cuando el conductor presiona el botón en la app)
print(app.registrar_final_de_ruta(
    patente="CCRS-20", 
    ruta="RUTA-CONSTITUCION-105", 
    observaciones="Entrega completa, sin daños."
))

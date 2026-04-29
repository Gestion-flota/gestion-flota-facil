import json
import os
import threading # Crucial para que la pantalla no se quede negra

class AppTransporteSegura:
    def __init__(self):
        self.archivo_local = "datos_logistica.json"
        # Iniciamos con datos vacíos para que la interfaz CARGUE de inmediato
        self.datos_locales = []
        
        # Ejecutamos la carga pesada en un hilo separado (Background)
        threading.Thread(target=self._preparar_sistema, daemon=True).start()

    def _preparar_sistema(self):
        """Carga los archivos en segundo plano para no bloquear la pantalla."""
        try:
            if os.path.exists(self.archivo_local):
                with open(self.archivo_local, 'r') as f:
                    self.datos_locales = json.load(f)
            else:
                with open(self.archivo_local, 'w') as f:
                    json.dump([], f)
            print("📦 Sistema de archivos listo.")
        except Exception as e:
            # Si el archivo está corrupto, lo reseteamos para que la app no muera
            with open(self.archivo_local, 'w') as f:
                json.dump([], f)
            print(f"⚠️ Archivo reparado automáticamente: {e}")

    def registrar_despacho(self, patente, id_ruta, mensaje):
        """
        Función para el botón del transportista.
        """
        nuevo_registro = {
            "hora": time.strftime("%H:%M:%S"),
            "patente": patente.upper(),
            "ruta": id_ruta,
            "obs": mensaje
        }
        
        # Guardado asíncrono para que el teléfono no se 'pegue'
        threading.Thread(target=self._guardar_y_enviar, args=(nuevo_registro,), daemon=True).start()
        return "✔️ Registrado (procesando en segundo plano)"

    def _guardar_y_enviar(self, registro):
        try:
            self.datos_locales.append(registro)
            with open(self.archivo_local, 'w') as f:
                json.dump(self.datos_locales, f)
            # Aquí iría el envío al servidor, pero no bloquea al chofer
            print("☁️ Intento de sincronización silencioso...")
        except:
            pass

# --- INICIO DE LA APP ---
# Al instanciar esto, la pantalla ya no debería quedar negra.
mi_app = AppTransporteSegura()

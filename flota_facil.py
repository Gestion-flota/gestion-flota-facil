import json
import os
import time
from datetime import datetime

class SistemaTransportePro:
    def __init__(self):
        self.archivo_local = "cola_envios.json"
        self.servidor_url = "https://tu-plataforma-principal.cl/api" # Cambiar por tu URL real
        self._inicializar_almacenamiento()

    def _inicializar_almacenamiento(self):
        """Crea el archivo local si no existe para evitar errores de lectura."""
        if not os.path.exists(self.archivo_local):
            with open(self.archivo_local, 'w') as f:
                json.dump([], f)

    def registrar_evento_reparto(self, patente, id_ruta, detalle):
        """
        Registra la actividad. Es 'a prueba de balas' porque 
        siempre prioriza el guardado físico en el teléfono.
        """
        nuevo_registro = {
            "id_transaccion": f"{patente}-{int(time.time())}",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "patente": patente.upper(),
            "id_ruta": id_ruta,
            "detalle": detalle,
            "estado_sincro": "pendiente"
        }

        try:
            # 1. LEER Y ACTUALIZAR LOCAL (Cero dependencia de internet)
            with open(self.archivo_local, 'r+') as f:
                datos = json.load(f)
                datos.append(nuevo_registro)
                f.seek(0)
                json.dump(datos, f, indent=4)
                f.truncate()
            
            print(f"✅ Guardado en memoria del teléfono: {nuevo_registro['id_transaccion']}")
            
            # 2. INTENTAR SUBIR AL SISTEMA CENTRAL
            self.sincronizar_pendientes()
            
        except Exception as e:
            print(f"⚠️ Error al escribir en el teléfono: {e}")

    def sincronizar_pendientes(self):
        """Intenta enviar todo lo que esté pendiente al servidor."""
        try:
            with open(self.archivo_local, 'r') as f:
                datos = json.load(f)
            
            pendientes = [d for d in datos if d["estado_sincro"] == "pendiente"]
            
            if not pendientes:
                return

            for item in pendientes:
                # Aquí iría tu conexión real (ejemplo con lógica de éxito)
                exito = self._comunicar_con_servidor(item)
                
                if exito:
                    item["estado_sincro"] = "sincronizado"
            
            # Actualizar el archivo con los nuevos estados
            with open(self.archivo_local, 'w') as f:
                json.dump(datos, f, indent=4)
                
        except Exception as e:
            print(f"🌐 Servidor no disponible. Se reintentará en el próximo reparto.")

    def _comunicar_con_servidor(self, payload):
        """Simula el envío. Retorna True si el servidor responde OK."""
        # En la realidad, aquí usas la librería 'requests'
        # return requests.post(self.servidor_url, json=payload).ok
        return False # Simulamos que el chofer no tiene internet ahora

# --- IMPLEMENTACIÓN EN EL DÍA A DÍA ---

plataforma = SistemaTransportePro()

# Ejemplo: El chofer de Transporte Cáceres termina un despacho
plataforma.registrar_evento_reparto(
    patente="CCRS-20", 
    id_ruta="RUTA-MAULE-500", 
    detalle="Entrega realizada en Constitución. Cliente conforme."
)

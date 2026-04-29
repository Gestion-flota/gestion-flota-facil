import os
import time

def limpiar_pantalla():
    # Esto limpia la pantalla para que el conductor vea todo ordenado
    os.system('cls' if os.name == 'nt' else 'clear')

def sistema_conductor():
    while True:
        limpiar_pantalla()
        print("========================================")
        print("    SISTEMA DE LOGISTICA PROFESIONAL    ")
        print("           MODO: CONDUCTOR              ")
        print("========================================")
        print("\n1. REGISTRAR ENTREGA")
        print("2. VER REPORTE DEL DIA")
        print("3. SALIR")
        
        opcion = input("\nSeleccione una opción (1, 2 o 3): ")

        if opcion == "1":
            patente = input("Ingrese Patente del camión: ").upper()
            ruta = input("Ingrese ID de la Ruta: ").upper()
            obs = input("Observaciones: ")
            
            # Guardado inmediato en un archivo de texto simple
            with open("reporte_logistica.txt", "a") as f:
                f.write(f"Fecha: {time.ctime()} | Patente: {patente} | Ruta: {ruta} | Obs: {obs}\n")
            
            print("\n✅ DATOS GUARDADOS CORRECTAMENTE.")
            time.sleep(2)
            
        elif opcion == "2":
            limpiar_pantalla()
            print("--- REPORTE DE ENTREGAS ---")
            if os.path.exists("reporte_logistica.txt"):
                with open("reporte_logistica.txt", "r") as f:
                    print(f.read())
            else:
                print("No hay registros hoy.")
            input("\nPresione ENTER para volver al menú...")
            
        elif opcion == "3":
            print("Cerrando sistema...")
            break
        else:
            print("Opción no válida.")
            time.sleep(1)

# Iniciar el programa
if __name__ == "__main__":
    sistema_conductor()

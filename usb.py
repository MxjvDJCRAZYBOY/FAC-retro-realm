import os
import signal
import time
import pyudev
import subprocess
import threading
def cerrar_snes9x():
    # Cambia la ruta del ejecutable de SNES9x según tu configuración
    ruta_snes9x = "~/snes9x-1.60/gtk/build/snes9x-gtk"

    # Intenta cerrar SNES9x enviando la señal SIGTERM
    try:
        subprocess.run(["killall","snes9x-gtk"], check=True)
    except subprocess.CalledProcessError:
        print("Error al intentar cerrar SNES9x")

def monitorear_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='disk')

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            print("USB conectada. Cerrando SNES9x.")
            cerrar_snes9x()

if __name__ == "__main__":
    hilo_usb = None

    try:
        # Inicia el hilo de monitoreo USB
        hilo_usb = threading.Thread(target=monitorear_usb)
        hilo_usb.daemon = True
        hilo_usb.start()

        # Puedes agregar aquí cualquier otra lógica o comandos necesarios

        # Mantén el script en ejecución
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Maneja la interrupción del teclado (Ctrl+C)
        pass

    finally:
        # Detén el hilo antes de salir
        if hilo_usb:
            hilo_usb.join()

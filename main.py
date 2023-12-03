# Importación de módulos y bibliotecas necesarios
import os
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import subprocess
import threading
import time
import pyudev
import shutil
import pygame

# Función para borrar el archivo seleccionado en la lista de ROMs
def borrar_archivo_seleccionado():
    # Obtiene la selección actual en la lista
    seleccion = listbox_archivos.curselection()
    if seleccion:
        index = seleccion[0]
        nombre_archivo = listbox_archivos.get(index)
        ruta_completa = os.path.join(os.path.dirname(__file__), "roms", nombre_archivo)
        ruta_imagen = os.path.join(os.path.dirname(__file__), "roms", f"{os.path.splitext(nombre_archivo)[0]}.png")

        try:
            # Intenta borrar el archivo y su imagen asociada
            os.remove(ruta_completa)
            os.remove(ruta_imagen)
            time.sleep(1)
            # Actualiza la lista y la imagen después de borrar
            listbox_archivos.delete(index)
            seleccionar_fila(None)
        except Exception as e:
            print(f"Error al borrar archivos: {e}")

# Función para cargar nombres de archivos desde la carpeta de ROMs
def cargar_nombres_archivos():
    carpeta_roms = os.path.join(os.path.dirname(__file__), "roms")

    if os.path.exists(carpeta_roms) and os.path.isdir(carpeta_roms):
        # Filtra los archivos con extensiones .smc y .zip
        nombres_archivos = [archivo for archivo in os.listdir(carpeta_roms) if archivo.lower().endswith((".smc", ".zip"))]
        return nombres_archivos
    else:
        return []

# Función para obtener la ruta de la imagen según la extensión del archivo
def obtener_ruta_imagen_extension(extension):
    if extension == ".smc":
        return os.path.join(os.path.dirname(__file__), "1.png")
    elif extension == ".zip":
        return os.path.join(os.path.dirname(__file__), "2.png")
    else:
        return os.path.join(os.path.dirname(__file__), "nofound.png")

# Función para mostrar la imagen en el centro de la interfaz
def mostrar_imagen_centro(extension):
    ruta_imagen = obtener_ruta_imagen_extension(extension)
    imagen = Image.open(ruta_imagen)
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen_sistema.config(image=imagen_tk)
    etiqueta_imagen_sistema.image = imagen_tk

# Función para actualizar la imagen según el archivo seleccionado
def actualizar_imagen(nombre_archivo):
    ruta_imagen = os.path.join(os.path.dirname(__file__), "roms", f"{os.path.splitext(nombre_archivo)[0]}.png")

    if not os.path.exists(ruta_imagen):
        ruta_imagen = os.path.join(os.path.dirname(__file__), "nofound.png")

    imagen = Image.open(ruta_imagen)
    imagen_tk = ImageTk.PhotoImage(imagen)
    etiqueta_imagen.config(image=imagen_tk)
    etiqueta_imagen.image = imagen_tk

# Función llamada al seleccionar una fila en la lista de ROMs
def seleccionar_fila(event):
    seleccion = listbox_archivos.curselection()
    if seleccion:
        index = seleccion[0]
        nombre_archivo = listbox_archivos.get(index)
        actualizar_imagen(nombre_archivo)
        _, extension = os.path.splitext(nombre_archivo)
        mostrar_imagen_centro(extension)

# Función que maneja la entrada del joystick para navegación y ejecución de comandos
def joystick_input():
    verifica = 0
    conta = 0
    pygame.init()
    pygame.joystick.init()
    # Verificar si hay al menos un controlador conectado
    if pygame.joystick.get_count() == 0:
        print("No se encontraron controladores de Xbox conectados.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    while True:
        if conta > 0:
            conta = conta - 1
        for event in pygame.event.get():
            if event.type == pygame.JOYAXISMOTION:

                # Mover hacia arriba o hacia abajo al mover el joystick izquierdo
                if event.axis == 1:  # Eje Y del joystick izquierdo
                    if event.value < -0.5 and conta == 0 and verifica == 0:
                        conta = 10000
                        mover_up()
                    elif event.value > 0.5 and conta == 0 and verifica == 0:
                        conta = 10000
                        mover_down()
            if event.type == pygame.JOYBUTTONDOWN:
                print(":{event.button}")
                # Presionar el botón A para ejecutar el comando
                if event.button == 0 and verifica == 0:  # Botón A
                    ejecutar_comando(None)
                    verifica = 1
                if event.button == 3 and verifica == 0:  # Botón y
                    borrar_archivo_seleccionado()
                    seleccionar_primer_archivo(None)
                if event.button == 4 and verifica == 1:  # Botón lb
                    verifica = 0

# Funciones para mover la selección hacia arriba y hacia abajo en la lista
def mover_up():
    index = listbox_archivos.curselection()
    if index and index[0] > 0:
        index = index[0] - 1
        listbox_archivos.selection_clear(0, tk.END)
        listbox_archivos.selection_set(index)
        listbox_archivos.activate(index)
        listbox_archivos.see(index)
        seleccionar_fila(None)

def mover_down():
    index = listbox_archivos.curselection()
    if index and index[0] < listbox_archivos.size() - 1:
        index = index[0] + 1
        listbox_archivos.selection_clear(0, tk.END)
        listbox_archivos.selection_set(index)
        listbox_archivos.activate(index)
        listbox_archivos.see(index)
        seleccionar_fila(None)

# Función para seleccionar automáticamente el primer archivo en la lista
def seleccionar_primer_archivo(event):
    listbox_archivos.select_set(0)
    listbox_archivos.event_generate("<<ListboxSelect>>")

    seleccionar_fila(None)

# Función para ejecutar el comando asociado al archivo seleccionado
def ejecutar_comando(event):
    seleccion = listbox_archivos.curselection()
    if seleccion:
        index = seleccion[0]
        nombre_archivo = listbox_archivos.get(index)
        ruta_completa = os.path.join(os.path.dirname(__file__), "roms", nombre_archivo)

        if nombre_archivo.lower().endswith(".smc"):
            comando = f'~/snes9x-1.60/gtk/build/snes9x-gtk "{ruta_completa}"'
        elif nombre_archivo.lower().endswith(".zip"):
            comando = f'/usr/games/mame "{ruta_completa}"'
        else:
            # Agrega un manejo para otros tipos de archivos si es necesario
            print(f"Error: Extensión de archivo no admitida para {nombre_archivo}")
            return

        os.system(comando)

# Función para mostrar un mensaje temporal de copia de ROMs nuevas
def mostrar_mensaje_copiando():
    mensaje_copiando = tk.Toplevel()
    mensaje_copiando.title("Copiando ROMs Nuevas")
    # Dimensiones de la pantalla
    ancho_pantalla = mensaje_copiando.winfo_screenwidth()
    altura_pantalla = mensaje_copiando.winfo_screenheight()

    # Calcular la posición centrada
    x_pos = 700
    y_pos = 500

    mensaje_copiando.geometry(f"300x100+{x_pos}+{y_pos}")
    mensaje_copiando.attributes("-topmost", True)

    etiqueta_mensaje = tk.Label(mensaje_copiando, text="Copiando ROMs Nuevas", font=("Arial", 14))
    etiqueta_mensaje.pack(pady=20)
    mensaje_copiando.after(5000, mensaje_copiando.destroy)  # Cerrar el mensaje después de 5 segundos

# Función para copiar archivos desde una unidad USB a la carpeta de ROMs
def copiar_archivos_usb(ruta_usb, ruta_destino):
    extensiones_permitidas = {".png", ".smc", ".zip"}
    archivos_copiados = []
    for archivo in os.listdir(ruta_usb):
        nombre_archivo, extension = os.path.splitext(archivo)

        if extension.lower() in extensiones_permitidas:
            ruta_origen = os.path.join(ruta_usb, archivo)
            ruta_destino_archivo = os.path.join(ruta_destino, archivo)

            if not os.path.exists(ruta_destino_archivo):
                shutil.copy(ruta_origen, ruta_destino)
                archivos_copiados.append(archivo)
                print(f"Archivo copiado: {archivo}")
            else:
                print(f"El archivo {archivo} ya existe en la carpeta de destino.")
    return archivos_copiados

# Funciones para cerrar los emuladores SNES9x y MAME
def cerrar_snes9x():
    # Intenta cerrar SNES9x enviando la señal SIGTERM
    try:
        subprocess.run(["killall", "-9", "snes9x-gtk"], check=True)
    except subprocess.CalledProcessError:
        print("Error al intentar cerrar SNES9x")

def cerrar_mame():
    # Intenta cerrar SNES9x enviando la señal SIGTERM
    try:
        subprocess.run(["killall", "-9", "mame"], check=True)
    except subprocess.CalledProcessError:
        print("Error al intentar cerrar SNES9x")

# Función para monitorear la conexión de unidades USB y copiar ROMs
def monitorear_usb():
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='block', device_type='disk')

    for device in iter(monitor.poll, None):
        if device.action == 'add':
            cerrar_snes9x()
            cerrar_mame()
            mostrar_mensaje_copiando()
            # Agregar la siguiente línea para obtener la ruta de la unidad USB
            time.sleep(3)
            ruta_usb = os.path.join('/media/fac/KINGSTON')

            archivos_copiados = copiar_archivos_usb(ruta_usb, '/home/fac/Desktop/Proyecto/roms')

            for archivo in archivos_copiados:
                if not archivo.lower().endswith(".png"):
                    listbox_archivos.insert(tk.END, archivo)

# Creación de la ventana principal de la aplicación
ventana = tk.Tk()
ventana.title("FAC Retro Realm")
ventana.attributes('-fullscreen', True)
# Creación de fuentes personalizadas y carga de imágenes de fondo y banner
fuente_personalizada = font.Font(family="Helvetica", size=24, weight="bold", slant="italic")

ruta_fondo = os.path.join(os.path.dirname(__file__), "fondo.png")
imagen_fondo = Image.open(ruta_fondo)
ancho_ventana = ventana.winfo_screenwidth()
altura_ventana = ventana.winfo_screenheight()
imagen_fondo = imagen_fondo.resize((ancho_ventana, altura_ventana), Image.LANCZOS)
imagen_fondo_tk = ImageTk.PhotoImage(imagen_fondo)
# Creación de widgets (etiquetas, listbox, botones) y configuración de la interfaz
etiqueta_fondo = tk.Label(ventana, image=imagen_fondo_tk, borderwidth=0)
etiqueta_fondo.place(relx=0, rely=0, relwidth=1, relheight=1)

ruta_banner = os.path.join(os.path.dirname(__file__), "banner.png")
imagen_banner = Image.open(ruta_banner)
imagen_banner = imagen_banner.resize((ancho_ventana, int(altura_ventana * 0.2)), Image.LANCZOS)
imagen_banner_tk = ImageTk.PhotoImage(imagen_banner)

etiqueta_banner = tk.Label(ventana, image=imagen_banner_tk, borderwidth=0)
etiqueta_banner.pack(side="top", fill="x")

canvas_lista = tk.Canvas(ventana, width=700, height=altura_ventana, bg="white")
canvas_lista.pack(side="left", fill="both", expand=False, padx=20, pady=20)

nombres_archivos = cargar_nombres_archivos()

listbox_archivos = tk.Listbox(canvas_lista, font=("Arial", 14), selectbackground="gray", selectmode=tk.SINGLE, bg="white", width=40)
for nombre_archivo in nombres_archivos:
    listbox_archivos.insert(tk.END, nombre_archivo)

listbox_archivos.pack(fill="both", expand=True)

listbox_archivos.bind("<ButtonRelease-1>", seleccionar_fila)

etiqueta_imagen = tk.Label(ventana, bg="white")
etiqueta_imagen.pack(side="left", padx=0)

etiqueta_imagen_sistema = tk.Label(ventana, bg="white")
etiqueta_imagen_sistema.pack(side="left", padx=0)

ancho_pantalla = ventana.winfo_screenwidth()
altura_pantalla = ventana.winfo_screenheight()
ancho_imagen = imagen_fondo.width
altura_imagen = imagen_fondo.height

posicion_vertical = (altura_pantalla - altura_imagen) // 2 + 540
etiqueta_imagen.place(relx=0.5, rely=posicion_vertical/altura_pantalla, anchor="center")
etiqueta_imagen_sistema.place(relx=0.8, rely=posicion_vertical/altura_pantalla, anchor="center")

ruta_boton = os.path.join(os.path.dirname(__file__), "boton.png")
imagen_boton = Image.open(ruta_boton)
imagen_boton_tk = ImageTk.PhotoImage(imagen_boton)

ancho_boton = imagen_boton.width
altura_boton = imagen_boton.height

posicion_vertical_boton = (altura_pantalla - altura_boton) // 2 - 100
etiqueta_boton = tk.Label(ventana, image=imagen_boton_tk, borderwidth=0)
etiqueta_boton.pack(side="bottom", pady=20)
etiqueta_boton.place(relx=0.5, rely=posicion_vertical_boton/altura_pantalla, anchor="center")
# Inicio de hilos para la entrada del joystick y el monitoreo de USB
hilo_joystick = threading.Thread(target=joystick_input)
hilo_joystick.daemon = True
hilo_joystick.start()


hilo_usb = threading.Thread(target=monitorear_usb)
hilo_usb.daemon = True
hilo_usb.start()
# Llamada a la función para seleccionar automáticamente el primer archivo
seleccionar_primer_archivo(None)
# Inicio del bucle principal de la interfaz gráfica
ventana.mainloop()
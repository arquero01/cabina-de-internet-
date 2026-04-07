import requests
import time
import threading
import tkinter as tk
import os
import socket

# ---------------- CONFIG ----------------
SERVIDOR = "http://127.0.0.1:5000"
NOMBRE_PC = socket.gethostname()

# ---------------- VARIABLES ----------------
tiempo_restante = 0
bloqueado = False
ventana_bloqueo = None
gracia_hasta = 0

# ---------------- UI ----------------
ventana = tk.Tk()
ventana.title("Cliente Cabina")
ventana.geometry("300x200")
ventana.configure(bg="#0f172a")

label_pc = tk.Label(ventana, text=NOMBRE_PC, font=("Arial", 16), bg="#0f172a", fg="white")
label_pc.pack(pady=10)

label_tiempo = tk.Label(ventana, text="00:00:00", font=("Arial", 28, "bold"), bg="#0f172a", fg="#22c55e")
label_tiempo.pack(pady=10)

label_estado = tk.Label(ventana, text="", font=("Arial", 12), bg="#0f172a", fg="red")
label_estado.pack(pady=10)

# ---------------- FUNCIONES ----------------

def ejecutar_ui(func):
    ventana.after(0, func)

def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

# ---------------- BLOQUEO ----------------

def mostrar_bloqueo():
    global ventana_bloqueo

    if ventana_bloqueo:
        return

    ventana_bloqueo = tk.Toplevel()
    ventana_bloqueo.attributes("-fullscreen", True)
    ventana_bloqueo.configure(bg="#020617")
    ventana_bloqueo.attributes("-topmost", True)

    label = tk.Label(
        ventana_bloqueo,
        text="⛔ TIEMPO TERMINADO",
        font=("Arial", 40, "bold"),
        fg="red",
        bg="#020617"
    )
    label.pack(expand=True)

    sub = tk.Label(
        ventana_bloqueo,
        text="Contacte al administrador",
        font=("Arial", 18),
        fg="white",
        bg="#020617"
    )
    sub.pack()

    #BOTÓN DE PRUEBA (ACTIVA GRACIA)
    btn = tk.Button(
        ventana_bloqueo,
        text="DESBLOQUEAR (TEST)",
        command=lambda: desbloqueo_manual(None),
        bg="red",
        fg="white"
    )
    btn.pack(pady=20)

    # ATAJO GARANTIZADO
    ventana_bloqueo.bind("<Control-Shift-U>", desbloqueo_manual)

    # bloquear cerrar
    ventana_bloqueo.protocol("WM_DELETE_WINDOW", lambda: None)

def quitar_bloqueo():
    global ventana_bloqueo

    if ventana_bloqueo:
        ventana_bloqueo.destroy()
        ventana_bloqueo = None

def desbloqueo_manual(event):
    global bloqueado, gracia_hasta

    quitar_bloqueo()
    bloqueado = False

    # activar minuto de gracia
    gracia_hasta = time.time() + 60

    ejecutar_ui(lambda: label_estado.config(text="⚠️ MODO PRUEBA: 1 MINUTO"))

# ---------------- SERVIDOR ----------------

def actualizar_servidor():
    global tiempo_restante, bloqueado, gracia_hasta

    while True:
        try:
            r = requests.get(f"{SERVIDOR}/datos")
            data = r.json()

            if NOMBRE_PC in data:
                tiempo_restante = data[NOMBRE_PC]["tiempo"]

                ahora = time.time()

                # TIENE TIEMPO
                if tiempo_restante > 0:
                    if bloqueado:
                        ejecutar_ui(quitar_bloqueo)
                        bloqueado = False

                    gracia_hasta = 0

                    ejecutar_ui(lambda: label_estado.config(text=""))

                # SIN TIEMPO
                else:
                    if ahora < gracia_hasta:
                        restante = int(gracia_hasta - ahora)

                        ejecutar_ui(lambda: label_estado.config(
                            text=f"⚠️ Agrega tiempo ({restante}s)"
                        ))

                    else:
                        if not bloqueado:
                            ejecutar_ui(mostrar_bloqueo)
                            bloqueado = True

        except:
            pass

        time.sleep(3)

# ---------------- CONTADOR ----------------

def contador():
    global tiempo_restante

    while True:
        if tiempo_restante > 0:
            tiempo_restante -= 1

            ejecutar_ui(lambda: label_tiempo.config(
                text=formatear(tiempo_restante)
            ))
        else:
            ejecutar_ui(lambda: label_tiempo.config(text="00:00:00"))

        time.sleep(1)

# ---------------- INICIO ----------------

# registrar cliente
try:
    requests.post(f"{SERVIDOR}/registrar", json={"nombre": NOMBRE_PC})
except:
    pass

threading.Thread(target=actualizar_servidor, daemon=True).start()
threading.Thread(target=contador, daemon=True).start()

ventana.mainloop()
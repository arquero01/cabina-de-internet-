import requests
import time
import threading
import tkinter as tk
import socket

PUERTO = 5000
ID_UNICO = socket.gethostname()  # ID real del equipo

servidor_url = None
nombre_asignado = None
tiempo_restante = 0

ventana = tk.Tk()
ventana.title("Cliente Cabina")
ventana.geometry("350x250")

label_pc = tk.Label(ventana, text="Conectando...", font=("Arial", 16))
label_pc.pack(pady=10)

label_tiempo = tk.Label(ventana, text="00:00:00", font=("Arial", 32))
label_tiempo.pack(pady=10)

# ---------------- DETECTAR SERVIDOR ----------------
def detectar_servidor():
    global servidor_url

    base_ip = "192.168.1"

    for i in range(1, 255):
        ip = f"{base_ip}.{i}"
        try:
            url = f"http://{ip}:{PUERTO}/datos"
            r = requests.get(url, timeout=0.3)
            if r.status_code == 200:
                servidor_url = f"http://{ip}:{PUERTO}"
                return
        except:
            pass

    servidor_url = "http://127.0.0.1:5000"

# ---------------- REGISTRAR ----------------
def registrar():
    global nombre_asignado

    while not nombre_asignado:
        try:
            if not servidor_url:
                detectar_servidor()

            r = requests.post(
                f"{servidor_url}/registrar",
                json={"nombre": ID_UNICO},
                timeout=2
            )

            data = r.json()
            nombre_asignado = data["nombre"]

            label_pc.config(text=f"💻 {nombre_asignado}")

        except:
            pass

        time.sleep(2)

# ---------------- ACTUALIZAR ----------------
def actualizar():
    global tiempo_restante

    while True:
        try:
            r = requests.get(f"{servidor_url}/datos", timeout=2)
            data = r.json()

            if nombre_asignado in data:
                tiempo_restante = data[nombre_asignado]["tiempo"]

        except:
            pass

        time.sleep(2)

# ---------------- CONTADOR ----------------
def contador():
    global tiempo_restante

    while True:
        if tiempo_restante > 0:
            tiempo_restante -= 1

        h = tiempo_restante // 3600
        m = (tiempo_restante % 3600) // 60
        s = tiempo_restante % 60

        label_tiempo.config(text=f"{h:02}:{m:02}:{s:02}")

        time.sleep(1)

threading.Thread(target=registrar, daemon=True).start()
threading.Thread(target=actualizar, daemon=True).start()
threading.Thread(target=contador, daemon=True).start()

ventana.mainloop()
import requests
import time
import threading
import tkinter as tk
import os 


NOMBRE_PC = "PC-1"
SERVIDOR = "http://127.0.0.1:5000"

# Registrar cliente
try:
    requests.post(f"{SERVIDOR}/registrar", json={"nombre": NOMBRE_PC})
except:
    pass

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

tiempo_restante = 0

# Convertir a formato HH:MM:SS
def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

# Obtener tiempo del servidor cada cierto tiempo
def actualizar_servidor():
    global tiempo_restante
    while True:
        try:
            r = requests.get(f"{SERVIDOR}/estado/{NOMBRE_PC}")
            data = r.json()

            minutos = data.get("tiempo", 0)
            tiempo_restante = minutos # convertir a segundos

        except:
            pass

        time.sleep(10)  # consulta cada 10 seg

# Cuenta regresiva en tiempo real
bloqueado = False

def contador():
    global tiempo_restante, bloqueado

    while True:
        if tiempo_restante > 0:
            tiempo_restante -= 1
            label_tiempo.config(text=formatear(tiempo_restante))
            label_estado.config(text="")
            bloqueado = False
        

        else:
            label_tiempo.config(text="00:00:00")
            label_estado.config(text="🔒 TIEMPO TERMINADO")

            if not bloqueado:
                if tiempo_restante == 60:
                    label_estado.config(text="⚠️ 1 MINUTO RESTANTE")
                try:
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                    bloqueado = True
                except:
                    pass

        time.sleep(1)
# Hilos
threading.Thread(target=actualizar_servidor, daemon=True).start()
threading.Thread(target=contador, daemon=True).start()

ventana.mainloop()
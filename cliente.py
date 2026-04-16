import requests
import time
import threading
import tkinter as tk
import socket
import os
import platform
import sys

# ---------------- CONFIG ----------------
PUERTO = 5000
PASSWORD_DESBLOQUEO = "1234"

NOMBRE_PC = socket.gethostname()
tiempo_restante = 0
bloqueado = False
servidor_url = None
ventana_bloqueo = None

# ---------------- AUTO REINICIO ----------------
def reiniciar():
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ---------------- DETECTAR SERVIDOR ----------------
def detectar_servidor():
    global servidor_url

    try:
        base_ip = socket.gethostbyname(socket.gethostname()).rsplit(".", 1)[0]
    except:
        base_ip = "192.168.1"

    for i in range(1, 255):
        ip = f"{base_ip}.{i}"
        try:
            url = f"http://{ip}:{PUERTO}/datos"
            r = requests.get(url, timeout=0.2)
            if r.status_code == 200:
                servidor_url = f"http://{ip}:{PUERTO}"
                print("✅ Servidor encontrado:", servidor_url)
                return
        except:
            pass

    servidor_url = "http://127.0.0.1:5000"
    print("⚠️ Usando localhost")

# ---------------- BLOQUEO REAL ----------------
def bloquear_sistema_real():
    sistema = platform.system()

    try:
        if sistema == "Windows":
            os.system("rundll32.exe user32.dll,LockWorkStation")
        elif sistema == "Linux":
            os.system("gnome-screensaver-command -l")
            os.system("xdg-screensaver lock")
            os.system("loginctl lock-session")
    except:
        pass

# ---------------- UI ----------------
ventana = tk.Tk()
ventana.title("CyberControl Cliente")
ventana.geometry("400x420")
ventana.configure(bg="#020617")
ventana.resizable(False, False)

tk.Label(
    ventana,
    text=f"💻 {NOMBRE_PC}",
    font=("Segoe UI", 14, "bold"),
    bg="#020617",
    fg="#38bdf8"
).pack(pady=10)

label_tiempo = tk.Label(
    ventana,
    text="00:00:00",
    font=("Consolas", 42, "bold"),
    bg="#020617",
    fg="#22c55e"
)
label_tiempo.pack()

canvas = tk.Canvas(ventana, width=320, height=20, bg="#020617", highlightthickness=0)
canvas.pack(pady=10)
barra = canvas.create_rectangle(0, 0, 0, 20, fill="#22c55e")

label_estado = tk.Label(
    ventana,
    text="🔄 Conectando...",
    font=("Segoe UI", 11),
    bg="#020617",
    fg="#94a3b8"
)
label_estado.pack(pady=5)

label_consumo = tk.Label(
    ventana,
    text="🧾 Consumo: $0",
    font=("Segoe UI", 12, "bold"),
    bg="#020617",
    fg="#facc15"
)
label_consumo.pack(pady=10)

# ---------------- FORMATO ----------------
def formatear(seg):
    h = seg // 3600
    m = (seg % 3600) // 60
    s = seg % 60
    return f"{h:02}:{m:02}:{s:02}"

# ---------------- ANIMACIÓN ----------------
def animar_barra(valor):
    actual = canvas.coords(barra)[2]
    objetivo = 320 * valor
    paso = (objetivo - actual) / 10

    for _ in range(10):
        actual += paso
        canvas.coords(barra, 0, 0, actual, 20)
        ventana.update()
        time.sleep(0.01)

# ---------------- AUTO REGISTRO ----------------
def registrar():
    global servidor_url

    while True:
        try:
            if servidor_url:
                requests.post(
                    f"{servidor_url}/registrar",
                    json={"nombre": NOMBRE_PC},
                    timeout=2
                )
                return
        except:
            pass

        time.sleep(2)

# ---------------- ACTUALIZAR SERVIDOR ----------------
def actualizar_servidor():
    global tiempo_restante, servidor_url

    while True:
        try:
            if not servidor_url:
                detectar_servidor()

            r = requests.get(f"{servidor_url}/datos", timeout=2)
            data = r.json()

            if NOMBRE_PC in data:
                tiempo_restante = data[NOMBRE_PC]["tiempo"]

                nota = data[NOMBRE_PC].get("nota", "")
                label_consumo.config(text=f"🧾 {nota}")

                label_estado.config(text="🟢 Conectado")

        except:
            label_estado.config(text="🔴 Sin conexión...")
            servidor_url = None

        time.sleep(2)

# ---------------- CONTADOR ----------------
def contador():
    global tiempo_restante, bloqueado

    tiempo_total = 1

    while True:
        if tiempo_restante > 0:
            tiempo_restante -= 1

            label_tiempo.config(text=formatear(tiempo_restante))

            if tiempo_restante > 1800:
                color = "#22c55e"
                estado = "🟢 Activo"
            elif tiempo_restante > 300:
                color = "#f59e0b"
                estado = "⚠️ Por terminar"
            else:
                color = "#ef4444"
                estado = "🔴 Últimos minutos"

            label_tiempo.config(fg=color)
            label_estado.config(text=estado)

            tiempo_total = max(tiempo_total, tiempo_restante)
            animar_barra(tiempo_restante / tiempo_total)

            bloqueado = False

        else:
            label_tiempo.config(text="00:00:00", fg="#ef4444")
            label_estado.config(text="⛔ TIEMPO TERMINADO")

            if not bloqueado:
                mostrar_bloqueo()
                bloquear_sistema_real()
                bloqueado = True

        time.sleep(1)

# ================== MODO KIOSCO TOTAL ==================

def salida_admin(event=None):
    global ventana_bloqueo, bloqueado

    print("🔓 Salida admin activada")

    if ventana_bloqueo:
        ventana_bloqueo.destroy()
        ventana_bloqueo = None

    bloqueado = False

def mostrar_bloqueo():
    global ventana_bloqueo

    ventana_bloqueo = tk.Toplevel()
    ventana_bloqueo.attributes("-fullscreen", True)
    ventana_bloqueo.configure(bg="#000000")
    ventana_bloqueo.attributes("-topmost", True)

    ventana_bloqueo.protocol("WM_DELETE_WINDOW", lambda: None)

    ventana_bloqueo.bind("<Alt-F4>", lambda e: "break")
    ventana_bloqueo.bind("<Escape>", lambda e: "break")

    # 🔓 salida secreta
    ventana_bloqueo.bind("<Control-Shift-Q>", salida_admin)

    frame = tk.Frame(ventana_bloqueo, bg="black")
    frame.pack(expand=True)

    tk.Label(
        frame,
        text="⛔ TIEMPO TERMINADO",
        font=("Segoe UI", 42, "bold"),
        fg="red",
        bg="black"
    ).pack(pady=40)

    tk.Label(
        frame,
        text="Contacte al administrador",
        font=("Segoe UI", 16),
        fg="white",
        bg="black"
    ).pack(pady=10)

    entrada = tk.Entry(frame, show="*", font=("Arial", 20), justify="center")
    entrada.pack(pady=20)

    def verificar():
        if entrada.get() == PASSWORD_DESBLOQUEO:
            salida_admin()

    tk.Button(
        frame,
        text="Desbloquear",
        command=verificar,
        font=("Arial", 14),
        bg="red",
        fg="white",
        width=20
    ).pack(pady=10)

# 🔒 BLOQUEO GLOBAL (requiere keyboard)
def bloquear_teclas_global():
    try:
        import keyboard
        keyboard.block_key("alt")
        keyboard.block_key("tab")
        keyboard.block_key("windows")
        keyboard.block_key("esc")
    except:
        print("⚠️ instala: pip install keyboard")

threading.Thread(target=bloquear_teclas_global, daemon=True).start()

# ================== FIN KIOSCO ==================

# ---------------- HILOS ----------------
threading.Thread(target=actualizar_servidor, daemon=True).start()
threading.Thread(target=contador, daemon=True).start()
threading.Thread(target=registrar, daemon=True).start()

# ---------------- PROTECCIÓN ----------------
def loop_seguridad():
    while True:
        try:
            ventana.update()
        except:
            reiniciar()
        time.sleep(1)

threading.Thread(target=loop_seguridad, daemon=True).start()

ventana.mainloop()
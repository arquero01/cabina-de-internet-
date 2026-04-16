from flask import Flask, request, render_template, redirect
import time
import sys
import os
import threading
import webview  # 🔥 clave para app sin navegador

# ---------------- CONFIG ----------------
PRECIO_POR_MINUTO = 26

# ---------------- FIX PYINSTALLER ----------------
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.abspath(".")

app = Flask(__name__, template_folder=os.path.join(base_dir, "templates"))

# ---------------- MEMORIA ----------------
pcs = {}
contador_pcs = 1

# ---------------- GENERAR NOMBRE ----------------
def generar_nombre():
    global contador_pcs
    while True:
        nombre = f"PC-{contador_pcs:02}"
        contador_pcs += 1
        if nombre not in pcs:
            return nombre

# ---------------- PANEL ----------------
@app.route("/")
def panel():
    pcs_formateado = {}
    ahora = time.time()

    for pc, data in pcs.items():
        restante = int(data.get("fin", 0) - ahora)
        if restante < 0:
            restante = 0

        usado = int(data.get("usado", 0) + max(0, (ahora - data.get("inicio", ahora))))
        costo = int((usado / 60) * PRECIO_POR_MINUTO)

        pcs_formateado[pc] = {
            "tiempo": restante,
            "tiempo_str": formatear(restante),
            "nota": data.get("nota", ""),
            "costo": costo
        }

    return render_template("servidor_panel.html", pcs=pcs_formateado)

# ---------------- REGISTRAR AUTO ----------------
@app.route("/registrar", methods=["POST"])
def registrar():
    nombre_cliente = request.json.get("nombre")

    for pc, data in pcs.items():
        if data.get("id_cliente") == nombre_cliente:
            data["last_seen"] = time.time()
            return {"nombre": pc}

    nombre = generar_nombre()

    pcs[nombre] = {
        "fin": time.time(),
        "inicio": time.time(),
        "usado": 0,
        "nota": "",
        "id_cliente": nombre_cliente,
        "last_seen": time.time()
    }

    print(f"🖥️ Nueva PC registrada: {nombre}")
    return {"nombre": nombre}

# ---------------- NOTA ----------------
@app.route("/nota", methods=["POST"])
def nota():
    nombre = request.form.get("nombre")
    texto = request.form.get("nota", "")

    if nombre in pcs:
        pcs[nombre]["nota"] = texto
        pcs[nombre]["last_seen"] = time.time()

    return ("", 204)

# ---------------- ASIGNAR ----------------
@app.route("/asignar", methods=["POST"])
def asignar():
    nombre = request.form.get("nombre")
    minutos = request.form.get("tiempo")

    try:
        minutos = int(minutos)
    except:
        minutos = 0

    if nombre in pcs:
        ahora = time.time()
        pcs[nombre]["usado"] += max(0, ahora - pcs[nombre]["inicio"])
        pcs[nombre]["inicio"] = ahora
        pcs[nombre]["fin"] = ahora + (minutos * 60)
        pcs[nombre]["last_seen"] = ahora

    return redirect("/")

# ---------------- RESET ----------------
@app.route("/reset", methods=["POST"])
def reset():
    nombre = request.form.get("nombre")

    if nombre in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "inicio": time.time(),
            "usado": 0,
            "nota": "",
            "id_cliente": pcs[nombre].get("id_cliente"),
            "last_seen": time.time()
        }

    return redirect("/")

# ---------------- DATOS ----------------
@app.route("/datos")
def datos():
    ahora = time.time()
    respuesta = {}

    for pc, data in pcs.items():
        restante = int(data.get("fin", 0) - ahora)
        if restante < 0:
            restante = 0

        respuesta[pc] = {
            "tiempo": restante,
            "nota": data.get("nota", ""),
            "last_seen": data.get("last_seen", 0)
        }

    return respuesta

# ---------------- FORMATO ----------------
def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

# ---------------- INICIAR SERVIDOR ----------------
def iniciar_flask():
    app.run(host="127.0.0.1", port=5000, debug=False)

# ---------------- APP DESKTOP ----------------
if __name__ == "__main__":
    # 🔥 correr flask en segundo plano
    threading.Thread(target=iniciar_flask, daemon=True).start()

    # 🔥 abrir app tipo software
    webview.create_window(
        "CyberControl PRO",
        "http://127.0.0.1:5000",
        width=1200,
        height=800,
        resizable=True
    )

    webview.start()
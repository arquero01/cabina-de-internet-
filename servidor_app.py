from flask import Flask, request, render_template, redirect
import time
import sys
import os



#Detectar entorno (EXE o normal)
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'))

pcs = {}

# ---------------- PANEL ----------------
@app.route("/")
def panel():
    pcs_formateado = {}
    ahora = time.time()

    for pc, data in pcs.items():
        restante = int(data.get("fin", 0) - ahora)
        if restante < 0:
            restante = 0

        pcs_formateado[pc] = {
            "tiempo": restante,
            "tiempo_str": formatear(restante),
            "nota": data.get("nota", "")
        }

    return render_template("servidor_panel.html", pcs=pcs_formateado)

# ---------------- REGISTRAR ----------------
@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.json.get("nombre")

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "nota": ""
        }

    return "ok"

# ---------------- NOTAS ----------------
@app.route("/nota", methods=["POST"])
def nota():
    nombre = request.form.get("nombre")
    texto = request.form.get("nota", "")

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "nota": ""
        }

    pcs[nombre]["nota"] = texto
    return ("", 204)

# ---------------- ASIGNAR TIEMPO ----------------
@app.route("/asignar", methods=["POST"])
def asignar():
    nombre = request.form.get("nombre")
    minutos = request.form.get("tiempo")

    try:
        minutos = int(minutos)
    except:
        minutos = 0

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "nota": ""
        }

    #tiempo absoluto
    pcs[nombre]["fin"] = time.time() + (minutos * 60)

    return redirect("/")

# ---------------- DATOS EN TIEMPO REAL ----------------
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
            "nota": data.get("nota", "")
        }

    return respuesta

# ---------------- FORMATEO ----------------
def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)  
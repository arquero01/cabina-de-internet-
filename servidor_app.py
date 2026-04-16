from flask import Flask, request, render_template, redirect
import time

app = Flask(__name__)

pcs = {}
PRECIO_MINUTO = 26  # 💰 precio por minuto

# ---------------- PANEL ----------------
@app.route("/")
def panel():
    pcs_formateado = {}
    ahora = time.time()

    for pc, data in pcs.items():
        restante = int(data.get("fin", 0) - ahora)
        if restante < 0:
            restante = 0

        usado = int(data.get("fin", 0) - data.get("inicio", ahora))
        usado = max(0, usado - restante)

        costo = int((usado / 60) * PRECIO_MINUTO)

        pcs_formateado[pc] = {
            "tiempo": restante,
            "tiempo_str": formatear(restante),
            "nota": data.get("nota", ""),
            "costo": costo
        }

    return render_template("servidor_panel.html", pcs=pcs_formateado)

# ---------------- REGISTRAR ----------------
@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json

    nombre = data.get("nombre")
    ip = request.remote_addr

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "nota": "",
            "ip": ip,
            "activo": True
        }
    else:
        # actualizar info si ya existe
        pcs[nombre]["ip"] = ip
        pcs[nombre]["activo"] = True

    return "ok"
# ---------------- NOTAS ----------------
@app.route("/nota", methods=["POST"])
def nota():
    nombre = request.form.get("nombre")
    texto = request.form.get("nota", "")

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": time.time(),
            "inicio": time.time(),
            "nota": ""
        }

    pcs[nombre]["nota"] = texto
    return ("", 204)

# ---------------- ASIGNAR TIEMPO ----------------
@app.route("/asignar", methods=["POST"])
def asignar():
    nombre = request.form.get("nombre")

    try:
        minutos = int(request.form.get("tiempo", 0))
    except:
        minutos = 0

    ahora = time.time()

    if nombre not in pcs:
        pcs[nombre] = {
            "fin": ahora,
            "inicio": ahora,
            "nota": ""
        }

    # 🔥 sumar tiempo correctamente
    if pcs[nombre]["fin"] > ahora:
        pcs[nombre]["fin"] += minutos * 60
    else:
        pcs[nombre]["inicio"] = ahora
        pcs[nombre]["fin"] = ahora + (minutos * 60)

    return redirect("/")

# ---------------- COBRAR Y RESET ----------------
@app.route("/cobrar", methods=["POST"])
def cobrar():
    nombre = request.form.get("nombre")
    ahora = time.time()

    if nombre in pcs:
        data = pcs[nombre]

        restante = int(data["fin"] - ahora)
        if restante < 0:
            restante = 0

        usado = int(data["fin"] - data["inicio"])
        usado = max(0, usado - restante)

        costo = int((usado / 60) * PRECIO_MINUTO)

        print(f"💰 COBRO {nombre}: ${costo}")

        # 🔥 RESET PC
        pcs[nombre] = {
            "fin": ahora,
            "inicio": ahora,
            "nota": ""
        }

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
            "nota": data.get("nota", ""),
            "activo": data.get("activo", False)
        }

    return respuesta
# ---------------- FORMATO ----------------
def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
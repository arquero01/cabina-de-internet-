from flask import Flask, request, render_template, redirect
import threading
import time

app = Flask(__name__)

pcs = {}

@app.route("/")
def panel():
    pcs_formateado = {}

    for pc in pcs:
        pcs_formateado[pc] = {
            "tiempo": pcs[pc]["tiempo"],
            "tiempo_str": formatear(pcs[pc]["tiempo"])
        }

    return render_template("servidor_panel.html", pcs=pcs_formateado)
@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.json.get("nombre")
    if nombre not in pcs:
        pcs[nombre]={
            "tiempo":0,
            "nota":""
        }
    if nombre and nombre not in pcs:
        pcs[nombre] = {"tiempo": 0}
    return "ok"
@app.route("/nota", methods=["post"])
def nota():
    nombre=request.form.get("nombre")
    texto =request.form.get("nota","")
    if nombre not in pcs:
        pcs[nombre]={
            "tiempo":0, 
            "nota":""}
    pcs[nombre]["nota"]=texto
    return redirect("/")

@app.route("/asignar", methods=["post"])
def asignar():
    nombre = request.form.get("nombre")
    minutos = request.form.get("tiempo")

    print("DEBUG nombre:", nombre)
    print("DEBUG minutos raw:", minutos)

    # 🔥 limpiar input
    if not minutos or not minutos.isdigit():
        minutos = 0
    else:
        minutos = int(minutos)

    # 🔥 evitar PCs inexistentes
    if nombre not in pcs:
        pcs[nombre] = {"tiempo": 0}

    # 🔥 asignar correctamente
    pcs[nombre]["tiempo"] = minutos * 60

    print("DEBUG segundos:", pcs[nombre]["tiempo"])

    return redirect("/")

def consola():
    while True:
        try:
            comando = input(">> ")

            partes = comando.split()

            if len(partes) != 2:
                print("Formato: PC-1 +30 o PC-1 -10")
                continue

            nombre = partes[0]
            cambio = partes[1]

            if nombre not in pcs:
                print("PC no existe")
                continue

            valor = int(cambio)

            pcs[nombre]["tiempo"] += valor

            # Evitar negativos
            if pcs[nombre]["tiempo"] < 0:
                pcs[nombre]["tiempo"] = 0

            print(f"{nombre} ahora tiene {pcs[nombre]['tiempo']} min")
            if cambio =="reset":
                pcs[nombre]["tiempo"]=0
            if "=" in cambio:
                pcs[nombre]["tiempo"]=int(cambio.replace("=",""))

        except Exception as e:
            print("Error:", e)
def formatear_tiempo(minutos):
    total_segundos = minutos *60
    h = total_segundos // 3600
    m = (total_segundos % 3600) // 60
    s = total_segundos % 60
    return f"{h:02}:{m:02}:{s:02}"
@app.route("/estado/<nombre>")
def estado(nombre):
    return pcs.get(nombre, {})

# contador
def contador():
    while True:
        for pc in pcs:
            if pcs[pc]["tiempo"] > 0:
                pcs[pc]["tiempo"] -= 1
        time.sleep(1)  # 🔥 baja cada segundo
def formatear(segundos):
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02}:{m:02}:{s:02}"
        
@app.route("/datos")
def datos():
    return pcs
# hilo
threading.Thread(target=consola, daemon=True).start()
threading.Thread(target=contador, daemon=True).start()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
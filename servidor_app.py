import sys
import os
import time
import threading
import socket
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import webview

# ---------------- CONFIGURACION ----------------
PRECIO_POR_MINUTO = 26
TIMEOUT_OFFLINE = 60

# ---------------- INICIALIZACION ----------------
app = Flask(__name__)

# ---------------- MEMORIA PRINCIPAL ----------------
pcs = {}
contador_pcs = 1
lock = threading.Lock()

# ---------------- HTML TEMPLATE ----------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberControl PRO</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        .header {
            background: white;
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }

        .header h1 {
            color: #667eea;
            font-size: 28px;
        }

        .stats {
            display: flex;
            gap: 20px;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-number {
            font-size: 24px;
            font-weight: bold;
        }

        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 20px;
        }

        .pc-card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        .pc-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }

        .pc-name {
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }

        .pc-id {
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }

        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }

        .status-online {
            background: #4caf50;
            box-shadow: 0 0 5px #4caf50;
            animation: pulse 2s infinite;
        }

        .status-offline {
            background: #f44336;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .tiempo {
            text-align: center;
            padding: 20px;
            margin: 15px 0;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .tiempo-value {
            font-size: 48px;
            font-weight: bold;
            font-family: monospace;
        }

        .tiempo-verde { color: #4caf50; }
        .tiempo-naranja { color: #ff9800; }
        .tiempo-rojo { color: #f44336; }

        .costo {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            color: #ff9800;
            margin: 10px 0;
        }

        .form-group {
            margin-bottom: 10px;
        }

        input, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }

        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        button {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        button:hover {
            transform: translateY(-2px);
            filter: brightness(1.05);
        }

        .btn-asignar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-reset {
            background: #f44336;
            color: white;
        }

        .consumo-label {
            font-size: 13px;
            font-weight: bold;
            color: #ff9800;
            margin-bottom: 5px;
        }

        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 13px;
            font-family: 'Segoe UI', monospace;
            resize: vertical;
        }

        textarea:focus {
            outline: none;
            border-color: #ff9800;
        }

        .shortcut-hint {
            font-size: 10px;
            color: #999;
            text-align: right;
            margin-top: 4px;
        }

        .empty-state {
            text-align: center;
            padding: 60px;
            background: white;
            border-radius: 15px;
            color: #999;
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 12px 20px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            border-left: 4px solid #4caf50;
            font-size: 14px;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
            animation: fadeIn 0.3s ease-out;
        }

        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 0;
            width: 500px;
            max-width: 90%;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            animation: slideDown 0.3s ease-out;
        }

        .modal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 20px;
            border-radius: 15px 15px 0 0;
            color: white;
        }

        .modal-header h2 {
            margin: 0;
            font-size: 20px;
        }

        .modal-body {
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
        }

        .modal-footer {
            padding: 15px 20px;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }

        .modal-footer button {
            width: auto;
            padding: 8px 20px;
            margin: 0;
        }

        .btn-cancelar {
            background: #999;
            color: white;
        }

        .btn-confirmar {
            background: #f44336;
            color: white;
        }

        .resumen-linea {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }

        .resumen-linea strong {
            color: #667eea;
            width: 120px;
            display: inline-block;
        }

        .resumen-consumo {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-size: 13px;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideDown {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CyberControl PRO</h1>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="total-pcs">0</div>
                    <div class="stat-label">PCs Conectadas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="online-pcs">0</div>
                    <div class="stat-label">Online</div>
                </div>
            </div>
        </div>

        <div id="pcs-container" class="grid"></div>
    </div>

    <div id="resumen-modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>RESUMEN DE COBRO</h2>
            </div>
            <div class="modal-body" id="resumen-body"></div>
            <div class="modal-footer">
                <button class="btn-cancelar" onclick="cerrarModal()">Cancelar</button>
                <button class="btn-confirmar" onclick="confirmarReset()">Confirmar Cobro</button>
            </div>
        </div>
    </div>

    <script>
        let pcsData = {};
        let tiempoInterval = null;
        let datosInterval = null;
        let pendingReset = null;
        const PRECIO_POR_MINUTO = 26;

        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = seconds % 60;
            return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
        }

        function formatTiempoParaResumen(segundos) {
            const horas = Math.floor(segundos / 3600);
            const minutos = Math.floor((segundos % 3600) / 60);
            const segundosRest = segundos % 60;
            let resultado = '';
            if (horas > 0) resultado += horas + ' hora(s) ';
            if (minutos > 0) resultado += minutos + ' minuto(s) ';
            if (segundosRest > 0 || (horas === 0 && minutos === 0)) resultado += segundosRest + ' segundo(s)';
            return resultado.trim();
        }

        function getTimeClass(seconds) {
            if (seconds > 1800) return 'tiempo-verde';
            if (seconds > 300) return 'tiempo-naranja';
            return 'tiempo-rojo';
        }

        function showNotification(message, isError) {
            const notification = document.createElement('div');
            notification.className = 'notification';
            notification.style.borderLeftColor = isError ? '#f44336' : '#4caf50';
            notification.innerHTML = message;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        }

        function calcularCosto(tiempoSegundos) {
            const minutos = Math.floor(tiempoSegundos / 60);
            return minutos * PRECIO_POR_MINUTO;
        }

        async function guardarConsumo(pc, pcId) {
            const textarea = document.getElementById('consumo-' + pcId);
            const consumo = textarea.value;
            try {
                const formData = new FormData();
                formData.append('nombre', pc);
                formData.append('consumo', consumo);
                const response = await fetch('/consumo', { method: 'POST', body: formData });
                if (response.ok) {
                    showNotification('Consumo guardado para ' + pc, false);
                    if (pcsData[pc]) pcsData[pc].consumo = consumo;
                } else {
                    showNotification('Error al guardar consumo', true);
                }
            } catch (error) {
                showNotification('Error de conexion', true);
            }
        }

        async function asignarTiempoEnter(pc, pcId) {
            const input = document.getElementById('minutos-' + pcId);
            const minutos = parseInt(input.value);
            if (!minutos || minutos <= 0) {
                showNotification('Ingrese un tiempo valido', true);
                input.focus();
                return;
            }
            try {
                const formData = new FormData();
                formData.append('nombre', pc);
                formData.append('tiempo', minutos);
                const response = await fetch('/asignar', { method: 'POST', body: formData });
                if (response.ok) {
                    const costoAsignado = minutos * PRECIO_POR_MINUTO;
                    showNotification(minutos + ' minutos asignados a ' + pc + ' - Costo: $' + costoAsignado, false);
                    input.value = '';
                    input.focus();
                    await actualizarDatos();
                } else {
                    showNotification('Error al asignar tiempo', true);
                }
            } catch (error) {
                showNotification('Error de conexion', true);
            }
        }

        function mostrarResumen(pc) {
            const info = pcsData[pc];
            if (!info) return;
            const tiempoUsado = info.tiempoOriginal ? info.tiempoOriginal - info.tiempo : 0;
            const tiempoUsadoFormateado = formatTiempoParaResumen(tiempoUsado);
            const costoFijo = info.costoFijo || 0;
            const consumo = info.consumo || "Sin consumo registrado";
            const modalBody = document.getElementById('resumen-body');
            modalBody.innerHTML = `
                <div class="resumen-linea"><strong>PC:</strong> ${pc}</div>
                <div class="resumen-linea"><strong>Tiempo usado:</strong> ${tiempoUsadoFormateado}</div>
                <div class="resumen-linea"><strong>Costo total:</strong> <span style="color:#f44336;font-size:18px;">$${costoFijo}</span></div>
                <div class="resumen-linea"><strong>Consumo:</strong></div>
                <div class="resumen-consumo">${consumo.replace(/\\n/g, '<br>')}</div>
            `;
            pendingReset = pc;
            document.getElementById('resumen-modal').style.display = 'block';
        }

        function cerrarModal() {
            document.getElementById('resumen-modal').style.display = 'none';
            pendingReset = null;
        }

        function confirmarReset() {
            if (pendingReset) {
                resetearPC(pendingReset);
                cerrarModal();
            }
        }

        async function resetearPC(pc) {
            const formData = new FormData();
            formData.append('nombre', pc);
            await fetch('/reset', { method: 'POST', body: formData });
            showNotification(pc + ' reiniciado correctamente', false);
            await actualizarDatos();
        }

        function crearTarjetaPC(pc, info) {
            const tiempoClass = getTimeClass(info.tiempo);
            const tiempoFormatted = formatTime(info.tiempo);
            const costoFijoMostrar = info.costoFijo || 0;
            const pcId = pc.replace(/[^a-zA-Z0-9]/g, '');
            if (!info.tiempoOriginal) info.tiempoOriginal = info.tiempo;
            const consumoEscapado = (info.consumo || '').replace(/[&<>]/g, function(m) {
                if (m === '&') return '&amp;';
                if (m === '<') return '&lt;';
                if (m === '>') return '&gt;';
                return m;
            });
            const card = document.createElement('div');
            card.className = 'pc-card';
            card.setAttribute('data-pc', pc);
            card.setAttribute('data-pc-id', pcId);
            card.innerHTML = `
                <div class="pc-header">
                    <div><div class="pc-name">${pc}</div><div class="pc-id">${info.id_cliente || 'Cliente'}</div></div>
                    <div class="status-indicator ${info.online ? 'status-online' : 'status-offline'}"></div>
                </div>
                <div class="tiempo"><div class="tiempo-value ${tiempoClass}" id="tiempo-${pcId}">${tiempoFormatted}</div></div>
                <div class="costo" id="costo-${pcId}">Costo Total: $${costoFijoMostrar}</div>
                <div class="form-group"><input type="number" id="minutos-${pcId}" placeholder="Minutos" min="1"><div class="shortcut-hint">Escribe y presiona ENTER para asignar</div></div>
                <button class="btn-asignar" onclick="asignarTiempoEnter('${pc}', '${pcId}')">Asignar Tiempo</button>
                <div style="margin-top:15px;"><div class="consumo-label">CONSUMO</div>
                <textarea id="consumo-${pcId}" rows="3" placeholder="Escribe aqui los consumos...">${consumoEscapado}</textarea>
                <div class="shortcut-hint">Escribe y presiona ENTER para guardar</div></div>
                <button class="btn-reset" onclick="mostrarResumen('${pc}')">Cobrar y Resetear</button>
            `;
            setTimeout(() => {
                const minutosInput = document.getElementById('minutos-' + pcId);
                if (minutosInput) {
                    minutosInput.addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') { e.preventDefault(); asignarTiempoEnter(pc, pcId); }
                    });
                }
                const consumoTextarea = document.getElementById('consumo-' + pcId);
                if (consumoTextarea) {
                    consumoTextarea.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); guardarConsumo(pc, pcId); }
                    });
                }
            }, 0);
            return card;
        }

        function actualizarGrid(data) {
            const container = document.getElementById('pcs-container');
            const currentPCs = new Set(Object.keys(pcsData));
            const newPCs = new Set(Object.keys(data));
            for (const pc of newPCs) {
                if (!currentPCs.has(pc)) {
                    const card = crearTarjetaPC(pc, data[pc]);
                    container.appendChild(card);
                    showNotification('Nueva PC conectada: ' + pc, false);
                }
            }
            for (const pc of currentPCs) {
                if (!newPCs.has(pc)) {
                    const card = document.querySelector('.pc-card[data-pc="' + pc + '"]');
                    if (card) card.remove();
                }
            }
            for (const [pc, info] of Object.entries(data)) {
                const pcId = pc.replace(/[^a-zA-Z0-9]/g, '');
                const card = document.querySelector('.pc-card[data-pc="' + pc + '"]');
                if (card) {
                    const statusIndicator = card.querySelector('.status-indicator');
                    if (statusIndicator) {
                        const wasOnline = statusIndicator.classList.contains('status-online');
                        const isOnline = info.online;
                        if (wasOnline !== isOnline) {
                            statusIndicator.className = 'status-indicator ' + (isOnline ? 'status-online' : 'status-offline');
                        }
                    }
                    const tiempoElement = document.getElementById('tiempo-' + pcId);
                    if (tiempoElement) {
                        const tiempoClass = getTimeClass(info.tiempo);
                        const tiempoFormatted = formatTime(info.tiempo);
                        tiempoElement.textContent = tiempoFormatted;
                        tiempoElement.className = 'tiempo-value ' + tiempoClass;
                    }
                    const costoElement = document.getElementById('costo-' + pcId);
                    if (costoElement && info.costoFijo !== undefined) {
                        costoElement.innerHTML = 'Costo Total: $' + info.costoFijo;
                    }
                    const consumoTextarea = document.getElementById('consumo-' + pcId);
                    if (consumoTextarea && document.activeElement !== consumoTextarea) {
                        if (consumoTextarea.value !== info.consumo) consumoTextarea.value = info.consumo || '';
                    }
                    if (pcsData[pc]) {
                        if (info.tiempo > pcsData[pc].tiempo) info.tiempoOriginal = info.tiempo;
                        else if (!info.tiempoOriginal) info.tiempoOriginal = info.tiempo;
                        else info.tiempoOriginal = pcsData[pc].tiempoOriginal;
                        info.costoFijo = pcsData[pc].costoFijo || info.costoFijo;
                    } else {
                        info.tiempoOriginal = info.tiempo;
                    }
                }
            }
            const total = Object.keys(data).length;
            const online = Object.values(data).filter(pc => pc.online).length;
            document.getElementById('total-pcs').textContent = total;
            document.getElementById('online-pcs').textContent = online;
            pcsData = data;
        }

        function actualizarTiempos() {
            for (const [pc, info] of Object.entries(pcsData)) {
                const pcId = pc.replace(/[^a-zA-Z0-9]/g, '');
                const tiempoElement = document.getElementById('tiempo-' + pcId);
                if (tiempoElement && info.tiempo !== undefined && info.tiempo > 0) {
                    info.tiempo = Math.max(0, info.tiempo - 1);
                    tiempoElement.textContent = formatTime(info.tiempo);
                    tiempoElement.className = 'tiempo-value ' + getTimeClass(info.tiempo);
                }
            }
        }

        async function actualizarDatos() {
            try {
                const response = await fetch('/datos');
                const data = await response.json();
                actualizarGrid(data);
            } catch (error) {
                console.error('Error:', error);
            }
        }

        async function init() {
            await actualizarDatos();
            tiempoInterval = setInterval(actualizarTiempos, 1000);
            datosInterval = setInterval(actualizarDatos, 3000);
        }

        init();
        window.addEventListener('beforeunload', () => {
            if (tiempoInterval) clearInterval(tiempoInterval);
            if (datosInterval) clearInterval(datosInterval);
        });
        window.onclick = function(event) {
            const modal = document.getElementById('resumen-modal');
            if (event.target === modal) cerrarModal();
        }
    </script>
</body>
</html>
"""

# ---------------- FUNCIONES DE UTILIDAD ----------------
def ahora():
    return time.time()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# ---------------- RUTAS FLASK ----------------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/datos')
def datos():
    with lock:
        datos = {}
        for pc, data in pcs.items():
            restante = max(0, int(data["fin"] - ahora()))
            datos[pc] = {
                "tiempo": restante,
                "consumo": data.get("consumo", ""),
                "online": (ahora() - data.get("last_seen", 0)) < TIMEOUT_OFFLINE,
                "id_cliente": data.get("id_cliente", ""),
                "costoFijo": data.get("costoFijo", 0)
            }
        return jsonify(datos)

@app.route('/registrar', methods=['POST'])
def registrar():
    global contador_pcs
    try:
        data = request.get_json()
        id_cliente = data.get("nombre")
        print(f"Registro: {id_cliente}")
        with lock:
            for pc, d in pcs.items():
                if d.get("id_cliente") == id_cliente:
                    d["last_seen"] = ahora()
                    print(f"Reconectado: {pc}")
                    return jsonify({"nombre": pc})
            nuevo_nombre = f"PC-{contador_pcs:02d}"
            contador_pcs += 1
            pcs[nuevo_nombre] = {
                "fin": ahora(),
                "inicio": ahora(),
                "usado": 0,
                "consumo": "",
                "id_cliente": id_cliente,
                "last_seen": ahora(),
                "costoFijo": 0
            }
            print(f"Nuevo: {nuevo_nombre} (Total: {len(pcs)})")
            return jsonify({"nombre": nuevo_nombre})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/asignar', methods=['POST'])
def asignar():
    try:
        nombre = request.form.get("nombre")
        minutos = int(request.form.get("tiempo", 0))
        print(f"Asignando: {nombre} - {minutos} minutos")
        with lock:
            if nombre in pcs and minutos > 0:
                t = ahora()
                pcs[nombre]["usado"] += max(0, t - pcs[nombre]["inicio"])
                pcs[nombre]["inicio"] = t
                pcs[nombre]["fin"] = t + (minutos * 60)
                pcs[nombre]["last_seen"] = t
                pcs[nombre]["costoFijo"] = minutos * PRECIO_POR_MINUTO
                print(f"Asignado {minutos} min a {nombre} - Costo fijo: ${pcs[nombre]['costoFijo']}")
                return jsonify({"success": True}), 200
            else:
                return jsonify({"error": "PC no encontrada"}), 404
    except Exception as e:
        print(f"Error en asignar: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    nombre = request.form.get("nombre")
    with lock:
        if nombre in pcs:
            tiempo_usado = pcs[nombre]["usado"] + max(0, ahora() - pcs[nombre]["inicio"])
            costo_tiempo = int((tiempo_usado / 60) * PRECIO_POR_MINUTO)
            print(f"COBRADO - {nombre}:")
            print(f"   Tiempo usado: {tiempo_usado // 60} minutos")
            print(f"   Costo tiempo: ${costo_tiempo}")
            print(f"   Consumo: {pcs[nombre].get('consumo', 'Ninguno')}")
            id_cliente = pcs[nombre]["id_cliente"]
            pcs[nombre] = {
                "fin": ahora(),
                "inicio": ahora(),
                "usado": 0,
                "consumo": "",
                "id_cliente": id_cliente,
                "last_seen": ahora(),
                "costoFijo": 0
            }
            print(f"Reset: {nombre}")
            return jsonify({"success": True}), 200
    return jsonify({"error": "PC no encontrada"}), 404

@app.route('/consumo', methods=['POST'])
def consumo():
    nombre = request.form.get("nombre")
    texto = request.form.get("consumo", "")
    print(f"Consumo para {nombre}: {texto[:50]}...")
    with lock:
        if nombre in pcs:
            pcs[nombre]["consumo"] = texto
            pcs[nombre]["last_seen"] = ahora()
            print(f"Consumo guardado para {nombre}")
            return jsonify({"success": True}), 200
    return jsonify({"error": "PC no encontrada"}), 404

@app.route('/tiempo_gracia', methods=['POST'])
def tiempo_gracia():
    try:
        data = request.get_json()
        nombre = data.get("nombre")
        gracia = data.get("gracia", 60)
        print(f"Tiempo de gracia para {nombre}: {gracia} segundos")
        with lock:
            if nombre in pcs:
                t = ahora()
                tiempo_actual = max(0, pcs[nombre]["fin"] - t)
                pcs[nombre]["fin"] = t + tiempo_actual + gracia
                pcs[nombre]["last_seen"] = t
                print(f"Tiempo de gracia otorgado a {nombre}")
                return jsonify({"success": True}), 200
        return jsonify({"error": "PC no encontrada"}), 404
    except Exception as e:
        print(f"Error en tiempo de gracia: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------- INICIO ----------------
if __name__ == "__main__":
    print("="*60)
    print("CyberControl PRO - Servidor Estable")
    print("="*60)
    print(f"IP Local: {get_local_ip()}:5000")
    print(f"Local: http://127.0.0.1:5000")
    print("="*60)
    print("Caracteristicas:")
    print("   • Costo FIJO al asignar tiempo")
    print("   • El costo NO baja con el tiempo")
    print("   • Modal muestra costo fijo asignado")
    print("   • Guardar consumo con ENTER")
    print("   • Asignar tiempo con ENTER")
    print("="*60)
    
    def iniciar_flask():
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
    
    threading.Thread(target=iniciar_flask, daemon=True).start()
    time.sleep(2)
    
    webview.create_window(
        "CyberControl PRO - Sistema de Gestion",
        "http://127.0.0.1:5000",
        width=1280,
        height=800,
        resizable=True
    )
    webview.start()
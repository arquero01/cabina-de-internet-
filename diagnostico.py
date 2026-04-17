import socket
import requests

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

print("=== DIAGNÓSTICO DE RED ===")
print(f"Nombre del equipo: {socket.gethostname()}")
print(f"IP local: {get_local_ip()}")
print(f"IPs disponibles: {socket.gethostbyname_ex(socket.gethostname())}")

# Probar puerto 5000
print("\n=== PROBANDO SERVIDOR ===")
try:
    r = requests.get("http://127.0.0.1:5000/datos", timeout=2)
    print(f"✅ Servidor local responde: {r.status_code}")
except:
    print("❌ Servidor local NO responde")

try:
    r = requests.get(f"http://{get_local_ip()}:5000/datos", timeout=2)
    print(f"✅ Servidor IP local responde: {r.status_code}")
except:
    print(f"❌ Servidor IP local NO responde")

print("\n=== INSTRUCCIONES ===")
print("1. Asegúrate que el servidor esté ejecutándose")
print("2. En el cliente, ingresa la IP del servidor manualmente")
print("3. Si están en diferentes PCs, desactiva el firewall")
import requests
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import socket
from datetime import datetime
import sys
import os

# ---------------- CONFIGURACIÓN ----------------
PUERTO = 5000
SERVIDOR_URL = "http://127.0.0.1:5000"  # Cambiar según sea necesario
ID_EQUIPO = socket.gethostname()
CONTRASENA_ADMIN = "admin123"  # Contraseña para salir del bloqueo
TIEMPO_GRACIA = 60  # 60 segundos de tiempo de gracia

class CyberControlCliente:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("CyberControl - Control de Tiempo")
        self.ventana.geometry("400x500")
        self.ventana.configure(bg='#1a1a2e')
        self.ventana.resizable(False, False)
        
        # Permitir minimizar
        self.ventana.attributes('-topmost', False)
        
        # Variables de estado
        self.nombre_pc = None
        self.tiempo_restante = 0
        self.tiempo_inicial = 0  # Nuevo: guarda el tiempo inicial asignado
        self.conectado = False
        self.bloqueado = False
        self.tiempo_gracia = 0
        self.ejecutando = True
        self.nota_actual = ""
        self.ultimo_tiempo = 0
        
        # Configurar cierre con contraseña
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar_con_password)
        
        self.setup_ui()
        self.iniciar_hilos()
        
    def setup_ui(self):
        # Frame principal
        self.main = tk.Frame(self.ventana, bg='#1a1a2e')
        self.main.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Título
        titulo = tk.Label(self.main, text="CyberControl", 
                         font=("Segoe UI", 20, "bold"), 
                         fg="#667eea", bg='#1a1a2e')
        titulo.pack(pady=10)
        
        # Frame información
        info_frame = tk.Frame(self.main, bg='#16213e', relief='flat', bd=0)
        info_frame.pack(fill='x', pady=10, padx=10)
        
        self.label_pc = tk.Label(info_frame, text="🔄 Conectando...", 
                                 font=("Segoe UI", 14, "bold"), 
                                 fg="#38bdf8", bg='#16213e')
        self.label_pc.pack(pady=10)
        
        # Frame tiempo (centro)
        tiempo_frame = tk.Frame(self.main, bg='#16213e', relief='flat', bd=0)
        tiempo_frame.pack(fill='x', pady=20, padx=10)
        
        self.label_tiempo = tk.Label(tiempo_frame, text="00:00:00", 
                                     font=("Consolas", 48, "bold"), 
                                     fg="#4caf50", bg='#16213e')
        self.label_tiempo.pack(pady=20)
        
        # Barra progreso
        self.progress = ttk.Progressbar(tiempo_frame, length=350, mode='determinate')
        self.progress.pack(pady=10)
        
        # Frame notas/observaciones
        notas_frame = tk.Frame(self.main, bg='#16213e')
        notas_frame.pack(fill='both', expand=True, pady=10, padx=10)
        
        tk.Label(notas_frame, text="📝 OBSERVACIONES", 
                font=("Segoe UI", 12, "bold"), 
                fg="#ff9800", bg='#16213e').pack(pady=5)
        
        # Área de texto para observaciones (solo lectura)
        self.texto_notas = tk.Text(notas_frame, height=6, 
                                   font=("Segoe UI", 10), 
                                   bg='#0f0f23', fg='white',
                                   wrap=tk.WORD,
                                   state='disabled')
        self.texto_notas.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame estado
        estado_frame = tk.Frame(self.main, bg='#1a1a2e')
        estado_frame.pack(fill='x', pady=10)
        
        self.label_estado = tk.Label(estado_frame, text="🟡 Inicializando...", 
                                     font=("Segoe UI", 10), 
                                     fg="#ff9800", bg='#1a1a2e')
        self.label_estado.pack()
        
        # Frame info
        info_label = tk.Label(self.main, text=f"ID: {ID_EQUIPO}", 
                              font=("Segoe UI", 8), 
                              fg="#666", bg='#1a1a2e')
        info_label.pack(pady=5)
        
        # Instrucciones
        instrucciones = tk.Label(self.main, 
                                 text="💡 Puedes minimizar esta ventana\nEl tiempo sigue corriendo en segundo plano", 
                                 font=("Segoe UI", 8), 
                                 fg="#888", bg='#1a1a2e')
        instrucciones.pack(pady=5)
        
        # Ventana de bloqueo (inicialmente oculta)
        self.crear_ventana_bloqueo()
        
    def crear_ventana_bloqueo(self):
        """Crea la ventana de bloqueo que aparece cuando el tiempo termina"""
        self.bloqueo_ventana = tk.Toplevel(self.ventana)
        self.bloqueo_ventana.title("SISTEMA BLOQUEADO")
        self.bloqueo_ventana.attributes('-fullscreen', True)
        self.bloqueo_ventana.attributes('-topmost', True)
        self.bloqueo_ventana.configure(bg='#000000')
        self.bloqueo_ventana.protocol("WM_DELETE_WINDOW", lambda: None)  # Evitar cerrar
        
        # Frame principal
        bloqueo_frame = tk.Frame(self.bloqueo_ventana, bg='#000000')
        bloqueo_frame.pack(expand=True, fill='both')
        
        # Icono
        icono = tk.Label(bloqueo_frame, text="🔒", 
                        font=("Segoe UI", 120), 
                        fg="#f44336", bg='#000000')
        icono.pack(pady=50)
        
        # Mensaje
        tk.Label(bloqueo_frame, text="TIEMPO AGOTADO", 
                font=("Segoe UI", 48, "bold"), 
                fg="#f44336", bg='#000000').pack(pady=20)
        
        tk.Label(bloqueo_frame, text="Sistema bloqueado. Contacte al administrador.", 
                font=("Segoe UI", 18), 
                fg="#999", bg='#000000').pack(pady=10)
        
        # Campo para contraseña
        tk.Label(bloqueo_frame, text="Contraseña de Administrador:", 
                font=("Segoe UI", 14), 
                fg="white", bg='#000000').pack(pady=20)
        
        self.password_entry = tk.Entry(bloqueo_frame, show="*", 
                                       font=("Segoe UI", 14), 
                                       width=20)
        self.password_entry.pack(pady=10)
        self.password_entry.bind('<Return>', self.verificar_password)
        
        # Botón
        btn_desbloquear = tk.Button(bloqueo_frame, text="Desbloquear", 
                                    command=self.verificar_password,
                                    font=("Segoe UI", 14, "bold"),
                                    bg="#667eea", fg="white",
                                    cursor="hand2",
                                    width=20)
        btn_desbloquear.pack(pady=20)
        
        # Ocultar inicialmente
        self.bloqueo_ventana.withdraw()
        
    def verificar_password(self, event=None):
        """Verifica la contraseña y otorga tiempo de gracia"""
        password = self.password_entry.get()
        
        if password == CONTRASENA_ADMIN:
            self.tiempo_gracia = TIEMPO_GRACIA
            self.bloqueado = False
            self.bloqueo_ventana.withdraw()
            self.ventana.deiconify()  # Mostrar ventana principal
            self.label_estado.config(text=f"⚠️ Tiempo de gracia: {TIEMPO_GRACIA} segundos", fg="#ff9800")
            self.password_entry.delete(0, tk.END)
            
            # Notificar al servidor que hay tiempo de gracia
            self.notificar_gracia()
        else:
            messagebox.showerror("Error", "Contraseña incorrecta")
            self.password_entry.delete(0, tk.END)
    
    def notificar_gracia(self):
        """Notifica al servidor que se ha activado el tiempo de gracia"""
        try:
            requests.post(
                f"{SERVIDOR_URL}/tiempo_gracia",
                json={"nombre": self.nombre_pc, "gracia": TIEMPO_GRACIA},
                timeout=2
            )
            print("✅ Tiempo de gracia notificado al servidor")
        except Exception as e:
            print(f"❌ Error notificando gracia: {e}")
    
    def bloquear_sistema(self):
        """Bloquea el sistema completamente"""
        if not self.bloqueado:
            self.bloqueado = True
            self.ventana.iconify()  # Minimizar ventana principal
            self.bloqueo_ventana.deiconify()
            self.bloqueo_ventana.lift()
            self.label_estado.config(text="🔒 SISTEMA BLOQUEADO", fg="#f44336")
            print("🔒 Sistema bloqueado por tiempo agotado")
    
    def cerrar_con_password(self):
        """Cierra la aplicación con contraseña"""
        password = tk.simpledialog.askstring("Cerrar", "Contraseña de administrador:", show='*')
        if password == CONTRASENA_ADMIN:
            self.ejecutando = False
            self.ventana.destroy()
            sys.exit(0)
    
    def actualizar_notas(self, nota):
        """Actualiza el texto de observaciones"""
        if self.nota_actual != nota:
            self.nota_actual = nota
            self.texto_notas.config(state='normal')
            self.texto_notas.delete(1.0, tk.END)
            # Mostrar la nota o mensaje por defecto
            if nota and nota.strip():
                self.texto_notas.insert(1.0, nota)
            else:
                self.texto_notas.insert(1.0, "Sin observaciones")
            self.texto_notas.config(state='disabled')
            print(f"📝 Nota actualizada: {nota[:50] if nota else 'Sin observaciones'}")
    
    def log(self, mensaje):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}")
    
    def registrar(self):
        while self.ejecutando:
            try:
                self.log(f"Registrando {ID_EQUIPO}...")
                respuesta = requests.post(
                    f"{SERVIDOR_URL}/registrar",
                    json={"nombre": ID_EQUIPO},
                    timeout=3
                )
                
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    self.nombre_pc = datos.get("nombre")
                    self.conectado = True
                    
                    self.label_pc.config(text=f"💻 {self.nombre_pc}")
                    self.label_estado.config(text="✅ Conectado", fg="#4caf50")
                    self.log(f"✅ Registrado: {self.nombre_pc}")
                    return
                else:
                    self.log(f"❌ Error: {respuesta.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log("❌ Servidor no disponible")
                self.label_estado.config(text="⚠️ Servidor no disponible", fg="#ff9800")
            except Exception as e:
                self.log(f"❌ Error: {e}")
                
            time.sleep(3)
    
    def obtener_datos(self):
        while self.ejecutando:
            if self.nombre_pc:
                try:
                    respuesta = requests.get(f"{SERVIDOR_URL}/datos", timeout=2)
                    if respuesta.status_code == 200:
                        datos = respuesta.json()
                        if self.nombre_pc in datos:
                            nuevo_tiempo = datos[self.nombre_pc]["tiempo"]
                            
                            # Detectar cuando se asigna nuevo tiempo (para resetear la barra)
                            if nuevo_tiempo > self.tiempo_restante and nuevo_tiempo > 0:
                                self.tiempo_inicial = nuevo_tiempo
                                self.log(f"Nuevo tiempo asignado: {nuevo_tiempo} segundos - Barra al 100%")
                            
                            self.tiempo_restante = nuevo_tiempo
                            self.conectado = True
                            
                            # Actualizar notas
                            nota = datos[self.nombre_pc].get("nota", "")
                            self.actualizar_notas(nota)
                    else:
                        self.conectado = False
                except Exception as e:
                    self.conectado = False
            time.sleep(1)
    
    def actualizar_interfaz(self):
        ultimo_segundo = -1
        while self.ejecutando:
            # Manejar tiempo de gracia
            if self.tiempo_gracia > 0:
                self.tiempo_gracia -= 1
                if self.tiempo_gracia == 0:
                    self.label_estado.config(text="✅ Sistema desbloqueado", fg="#4caf50")
            
            # Determinar tiempo actual a mostrar
            if self.tiempo_gracia > 0:
                tiempo_actual = self.tiempo_gracia
                # Para la barra durante tiempo de gracia
                if self.tiempo_inicial > 0:
                    progreso = (tiempo_actual / self.tiempo_inicial) * 100
                else:
                    progreso = (tiempo_actual / TIEMPO_GRACIA) * 100
                self.progress['value'] = min(100, max(0, progreso))
            else:
                tiempo_actual = self.tiempo_restante
                # Calcular progreso basado en el tiempo inicial
                if self.tiempo_inicial > 0:
                    progreso = (tiempo_actual / self.tiempo_inicial) * 100
                    self.progress['value'] = min(100, max(0, progreso))
                else:
                    self.progress['value'] = 0
            
            # Solo actualizar cada segundo
            if tiempo_actual != ultimo_segundo:
                ultimo_segundo = tiempo_actual
                
                if tiempo_actual > 0:
                    # Formatear tiempo
                    horas = tiempo_actual // 3600
                    minutos = (tiempo_actual % 3600) // 60
                    segundos = tiempo_actual % 60
                    tiempo_texto = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
                    self.label_tiempo.config(text=tiempo_texto)
                    
                    # Cambiar color según tiempo
                    if tiempo_actual < 60:
                        self.label_tiempo.config(fg="#f44336")
                        if self.tiempo_gracia > 0:
                            self.label_estado.config(text="⏰ Tiempo de gracia - Últimos segundos", fg="#ff9800")
                        else:
                            self.label_estado.config(text="🔴 Tiempo por terminar", fg="#f44336")
                    elif tiempo_actual < 300:
                        self.label_tiempo.config(fg="#ff9800")
                        if self.tiempo_gracia > 0:
                            self.label_estado.config(text="⏰ Tiempo de gracia", fg="#ff9800")
                        else:
                            self.label_estado.config(text="⚠️ Poco tiempo", fg="#ff9800")
                    else:
                        self.label_tiempo.config(fg="#4caf50")
                        if self.tiempo_gracia > 0:
                            self.label_estado.config(text="⏰ Tiempo de gracia", fg="#ff9800")
                        else:
                            self.label_estado.config(text="🟢 Activo", fg="#4caf50")
                    
                    # Si hay tiempo, asegurar que no esté bloqueado
                    if self.bloqueado:
                        self.bloqueado = False
                        self.bloqueo_ventana.withdraw()
                        self.ventana.deiconify()
                else:
                    self.label_tiempo.config(text="00:00:00", fg="#f44336")
                    self.label_estado.config(text="⛔ Sin tiempo", fg="#f44336")
                    self.progress['value'] = 0
                    
                    # Bloquear sistema si no hay tiempo y no hay gracia
                    if self.tiempo_restante <= 0 and self.tiempo_gracia <= 0 and not self.bloqueado:
                        self.bloquear_sistema()
                
                # Decrementar tiempo restante (solo si no está en gracia)
                if self.tiempo_gracia == 0 and self.tiempo_restante > 0:
                    self.tiempo_restante -= 1
            
            time.sleep(1)
    
    def iniciar_hilos(self):
        threading.Thread(target=self.registrar, daemon=True).start()
        threading.Thread(target=self.obtener_datos, daemon=True).start()
        threading.Thread(target=self.actualizar_interfaz, daemon=True).start()
    
    def ejecutar(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    print("="*60)
    print("CyberControl Cliente - Control de Tiempo")
    print(f"ID: {ID_EQUIPO}")
    print(f"Servidor: {SERVIDOR_URL}")
    print(f"Contraseña Admin: {CONTRASENA_ADMIN}")
    print("="*60)
    print("✨ Características:")
    print("   • Ventana minimizable")
    print("   • Barra de progreso DINÁMICA (se llena según tiempo asignado)")
    print("   • Bloqueo automático al terminar tiempo")
    print("   • Tiempo de gracia con contraseña")
    print("   • Muestra observaciones del servidor")
    print("="*60)
    
    app = CyberControlCliente()
    app.ejecutar()
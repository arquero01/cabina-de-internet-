# cabina-de-internet-

# 🚀 CyberControl PRO

Sistema de control de tiempo para cibercafés o salas de computo, desarrollado en Python, que permite gestionar múltiples equipos en red local en tiempo real.

---

##  Descripción

CyberControl PRO es una solución cliente-servidor que permite al administrador controlar el uso de computadoras desde un panel central. El sistema asigna tiempo de uso, calcula costos automáticamente y bloquea los equipos cuando el tiempo se agota.

Incluye una interfaz moderna tipo software y sincronización en tiempo real entre servidor y clientes.

---

## ⚙️ Características

* 🖥️ Registro automático de equipos (PC-01, PC-02, etc.)
* 🟢 Detección de PCs online / offline
* ⏱️ Asignación de tiempo en minutos
* 💰 Cálculo automático de costos
* 🔒 Bloqueo automático al terminar el tiempo
* 🔓 Desbloqueo con contraseña (tiempo de gracia)
* 🧾 Registro de consumos adicionales
* 📊 Panel visual moderno tipo aplicación de escritorio
* 🔄 Actualización en tiempo real

---

## 🏗️ Arquitectura

El sistema está dividido en dos componentes:

### 🔹 Servidor

* Panel administrativo
* Control de tiempo y costos
* Gestión de múltiples clientes

### 🔹 Cliente

* Interfaz gráfica para el usuario
* Contador de tiempo en tiempo real
* Bloqueo del sistema cuando el tiempo termina

---

## 🛠️ Tecnologías utilizadas

* **Python**
* **Flask** (API REST / servidor)
* **Tkinter** (interfaz gráfica cliente)
* **PyWebView** (app de escritorio para el servidor)
* **HTML, CSS, JavaScript** (panel administrativo)
* **Requests** (comunicación HTTP)
* **Sockets** (identificación de equipos en red)
* **Multithreading** (ejecución de tareas en paralelo)

---

## 🌐 Funcionamiento

1. El servidor se ejecuta y abre el panel administrativo.
2. Los clientes se conectan automáticamente al servidor.
3. Cada PC recibe un identificador único.
4. El administrador asigna tiempo desde el panel.
5. El cliente muestra el tiempo restante en pantalla.
6. Al finalizar el tiempo:

   * El sistema se bloquea automáticamente
   * Se puede desbloquear con contraseña (tiempo de gracia)

---

## ▶️ Ejecución

### 🔹 Servidor

```bash
python servidor.py
```

### 🔹 Cliente

```bash
python cliente.py
```

---

## 📌 Requisitos

```bash
pip install flask requests pywebview
```

---

## 🚀 Futuras mejoras

* Base de datos persistente (SQLite / PostgreSQL)
* Autenticación de administrador
* Reportes de uso por día
* Soporte para red externa (no solo LAN)
* Mejoras de seguridad en el bloqueo del sistema

---

## 👨‍💻 Autor

Proyecto desarrollado por **Willam Andres Maltes Leon**
Estudiante de Ingeniería de Sistemas

# **Barrabinbarrabarrerash UI**

### Sistema de monitorización y defensa para servidores de videojuegos autogestionados


## **Descripción general**

**Barrabinbarrabarrerash** es una herramienta orientada a administradores de sistemas que gestionan servidores de videojuegos en entornos no gestionados o con imágenes propietarias poco seguras. El objetivo es ofrecer una **capa defensiva intermedia entre los clientes y el servidor de juego**, capaz de detectar y mitigar:

* Ataques DDoS de bajo nivel
* Floods de conexiones
* Scans de puertos
* Tráfico sospechoso
* Patrones anómalos de comportamiento

La interfaz web (UI) proporciona un panel unificado desde el que visualizar actividad, recibir alertas y gestionar IPs bloqueadas.
El sistema está pensado para ser probado en una LAN sobre un servidor de **Project Zomboid**, donde este tipo de ataques es común y la seguridad por defecto es limitada.

---

## **Arquitectura**

La UI forma parte de un sistema dividido en dos capas:

```
Cliente ──> Proxy de seguridad (backend FastAPI) ──> Servidor de juego
                     │
                     ▼
             Barrabinbarrabarrerash UI (Flask)
```

### Componentes

| Componente                    | Descripción                                                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend (FastAPI)**         | Motor de análisis y seguridad. Mantiene el estado: IPs baneadas, contador de ataques, últimos eventos, estadísticas. Expone una REST API. |
| **Frontend (Flask + Jinja2)** | Panel web con dashboard, tabla de eventos, IPs bloqueadas y gráficos en tiempo real (Chart.js).                                           |
| **Chart.js**                  | Gráficos dinámicos para mostrar eventos por minuto.                                                                                       |
| **CSS propio**                | Estilo limpio minimalista sin dependencias externas.                                                                                      |

---

## **Características principales**

* Dashboard centralizado
* Estadísticas de eventos por minuto (actualización automática)
* Contador de ataques diarios
* Lista de IPs bloqueadas y motivo
* Sistema para desbanear IPs desde la propia UI
* Botón de “Reset” del estado
* Diseño modular y extensible para integrar detección real de patrones
* Preparado para integrarse con análisis real de tráfico

---

## **Estructura del proyecto**

```
ui/
 ├── backend/          # API de seguridad (FastAPI)
 │    ├── main.py
 │    └── venv/
 └── frontend/         # Interfaz web (Flask)
      ├── app.py
      ├── config.py
      ├── requirements.txt
      ├── templates/
      │     ├── base.html
      │     ├── dashboard.html
      │     └── bans.html
      ├── static/
      │     └── css/styles.css
      └── venv/
```

---

## **Tecnologías utilizadas**

| Capa                  | Tecnología                        |
| --------------------- | --------------------------------- |
| Frontend              | Flask, Jinja2, Chart.js, HTML/CSS |
| Backend               | FastAPI, Python 3.11+             |
| Comunicaciones        | JSON / REST API                   |
| Desarrollo probado en | Arch Linux                        |

---

## **Requisitos previos**

* Python ≥ 3.10
* pip
* Entorno Linux (Arch Linux recomendado para reproducibilidad)

---

## **Instalación y ejecución (Arch Linux)**

### 1. Clonar el repositorio

```bash
git clone https://github.com/Sfr99/barrabinbarrabarrerash.git
cd barrabinbarrabarrerash/ui
```

---

### 2. Levantar el backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # si existe
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Backend disponible en:

```
http://127.0.0.1:8001
```

---

### 3. Levantar el frontend (Flask)

En otra terminal:

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

UI disponible en:

```
http://127.0.0.1:5000
```

---

## **Cómo usar la interfaz**

### Dashboard

Muestra:

* ataques detectados hoy
* gráfica de eventos por minuto
* tabla de últimos eventos
* resumen de IPs bloqueadas

La gráfica se actualiza automáticamente consultando el backend.

### Gestión de IPs bloqueadas

En la sección *Bans*:

* ver todas las IPs bloqueadas
* desbanear una IP con un clic

### Reset del sistema

Desde el dashboard:

* reset de ataques
* limpieza de eventos
* reinicio de IPs bloqueadas

---

## **Notas de seguridad**

* El backend implementa CORS para permitir la comunicación entre Flask (5000) y FastAPI (8001).
* No incluye autenticación todavía; está pensado para entornos controlados.

---

## **Futuras mejoras**

* Integración con iptables/nftables para bloquear tráfico real
* Modelo de detección basado en patrones de uso
* WebSockets para monitorización en tiempo real
* Control de usuarios y autenticación
* Persistencia en SQLite o Redis
* Modo “producción” con gunicorn + nginx

---

## **Licencia**

*(especificar si queréis MIT, Apache 2.0 o sin licencia → ahora mismo se omite hasta que lo indiquéis)*

---

## **Contacto**

Para dudas o mejoras:

* **Javier Salafranca Pradilla** — [javier.salafranca@gmail.com](mailto:javier.salafranca@gmail.com) — GitHub: [@Sfr99](https://github.com/Sfr99)
* **Jorge Soria Romeo** — [872016@unizar.es](mailto:872016@unizar.es) — GitHub: [@Jorge872016](https://github.com/Jorge872016)


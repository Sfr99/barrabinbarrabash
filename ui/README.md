# README.md — BarrabinBarrabarrerash UI

## 1. Descripción general

**BarrabinBarrabarrerash UI** es la interfaz de monitorización y gestión del sistema de defensa en red desarrollado para proteger servidores de videojuegos autoalojados, particularmente servidores de *Project Zomboid* sensibles a floods, escaneos y tráfico malicioso.

La UI proporciona un **panel de control en tiempo real** donde los administradores pueden:

* Visualizar ataques detectados.
* Consultar y gestionar IPs baneadas.
* Analizar actividad reciente y eventos minuto a minuto.
* Revisar estadísticas del firewall-proxy que protege al servidor.

La interfaz se divide en dos componentes:

* **Backend (FastAPI):** expone una API REST con el estado del firewall y operaciones de gestión.
* **Frontend (Flask):** renderiza dashboards HTML, sirve estáticos y consume la API del backend.


```
ui/
├── backend/        # API FastAPI + lógica de estado + base de datos SQLite
├── frontend/       # Aplicación Flask + templates + estilos
├── requirements.txt
```

---

## 2. Arquitectura de la UI

```
Servidor Zomboid
        │
        v
     Proxy
 (detección, bans,
   filtrado tráfico)
        │
        v
 Backend FastAPI
   (estado, eventos,
    estadísticas)
        │
        v
Frontend Flask
   (dashboard web)
```

La UI **no interactúa directamente con el servidor Zomboid**, sino con el **backend FastAPI**, que es la única fuente de verdad del estado del firewall.

---

## 3. Tecnologías empleadas

### Backend (FastAPI)

* FastAPI
* SQLAlchemy + SQLite
* Pydantic
* CORS Middleware
* Uvicorn

### Frontend (Flask)

* Flask
* Jinja2 templates
* Chart.js para gráficos
* CSS estático propio

---

## 4. Requisitos

* Python **3.10+**
* Entorno virtual recomendado
* Dependencias listadas en `requirements.txt`

Instalación:

```bash
pip install -r requirements.txt
```

---

## 5. Estructura del repositorio

```
backend/
    main.py          # Entrypoint FastAPI
    state.py         # Acceso al estado + estadísticas
    database.py      # Sesión SQLAlchemy
    models.py        # ORM
    firewall.db      # Base de datos SQLite (en desarrollo)

frontend/
    app.py           # Entrypoint Flask
    config.py        # Configuración de rutas y backend URL
    templates/       # HTML del dashboard
    static/css/      # Estilos

requirements.txt
```

---

## 6. Ejecución de la UI

### 6.1. Arrancar Backend (FastAPI)

```bash
cd ui/backend
uvicorn main:app --reload --port 8001
```

El backend quedará escuchando en:

```
http://127.0.0.1:8001
```

Endpoints principales:

* `GET /state` — estado completo (bans, eventos, ataques, chart).
* `POST /ban` — añadir ban.
* `POST /unban/{ip}` — eliminar ban.
* `POST /event` — registrar evento.
* `POST /reset` — resetear estado.
* `GET /chart` — obtener datos del gráfico.

### 6.2. Arrancar Frontend (Flask)

En otra terminal:

```bash
cd ui/frontend
export FLASK_APP=app.py
flask run --port 5000
```

La UI queda disponible en:

```
http://127.0.0.1:5000
```

El frontend consulta automáticamente:

```
http://127.0.0.1:8001/state
```

cada 5 segundos.

---

## 7. Funcionamiento del Dashboard

### 7.1. Sección “Ataques hoy”

Valor incrementado automáticamente cuando el backend recibe un evento con `is_attack = true`.

### 7.2. Tabla “IPs baneadas”

* Scroll automático para lista larga.
* Contenido actualizado dinámicamente via fetch.

### 7.3. Gráfico de eventos por minuto

* Se renderiza con Chart.js.
* Representa actividad de los últimos 10 minutos.
* Actualizado por la API `/chart` incluida dentro de `/state`.

### 7.4. Tabla de últimos eventos

Incluye timestamp, IP, acción (allowed/blocked) y descripción del evento.

---

## 8. API del Backend (resumen técnico)

### POST /ban

**Query params:**

```
ip: str
reason: str
```

Ejemplo:

```bash
curl -X POST "http://127.0.0.1:8001/ban?ip=1.2.3.4&reason=SSH+brute+force"
```

### POST /event

```bash
curl -X POST \
  "http://127.0.0.1:8001/event?ip=8.8.8.8&action=blocked&description=HTTP+flood&is_attack=true"
```

### POST /unban/{ip}

```bash
curl -X POST http://127.0.0.1:8001/unban/1.2.3.4
```

### GET /state

Retorna todo el estado para el dashboard.

---

## 9. Desarrollo y mantenimiento

### Recarga automática

* Backend: `--reload` (Uvicorn)
* Frontend: Flask detecta cambios en plantillas

### Base de datos

La base de datos SQLite `firewall.db` se genera automáticamente.
Puede resetearse mediante:

```
POST /reset
```

### Logs

Uvicorn imprime errores y actividad del backend.
Flask registra peticiones desde la UI.


Aquí tienes el **README del frontend**, profesional, claro y centrado exclusivamente en la UI. No menciona el proxy ni arquitectura global, solo lo necesario para **montar, entender y ejecutar la interfaz**.

Cuando quieras, genero también el README general del proyecto.

---

# **BarrabinBarrabarrerash – Frontend UI**

*Panel web de monitorización y gestión para la herramienta de seguridad en servidores de juegos*

## 1. Descripción general

Este frontend proporciona una **interfaz web ligera**, desarrollada con **Flask** y **Jinja2**, diseñada para visualizar en tiempo real:

* Ataques detectados hoy.
* IPs baneadas y su motivo.
* Historial de eventos recientes.
* Actividad por minuto en un gráfico dinámico (Chart.js).
* Acciones básicas de administración (reset de estado y gestión de bans).

La UI funciona como cliente del **backend FastAPI**, desde el cual obtiene todo el estado del firewall intermedio.

El objetivo de esta interfaz es ofrecer una **visión clara y en vivo del estado del sistema**, permitiendo demostrar fácilmente el funcionamiento del MVP durante el hackathon.

---

## 2. Características principales

### ✔ Actualización automática cada 5 segundos

El dashboard refresca automáticamente:

* Contador de ataques.
* Lista de IPs baneadas.
* Tabla de eventos.
* Gráfico de actividad.

### ✔ Dashboard centralizado

`dashboard.html` es la página principal y muestra:

* **Ataques hoy** (sumatorio diario).
* **Tabla compacta de IPs baneadas**.
* **Gráfico de eventos por minuto**.
* **Últimos eventos**, ordenados por fecha.

### ✔ Gestión básica de bans

Desde el apartado *Bans* se pueden:

* Ver todas las IPs actuales baneadas.
* Desbanear una IP mediante POST al backend.

### ✔ Integración con FastAPI

La UI consume los siguientes endpoints:

* `GET /state` — estado completo (ataques, bans, eventos).
* `GET /chart` — datos para la gráfica.
* `POST /reset` — reinicio del estado.
* `POST /unban/<ip>` — retirar ban.

La URL base se configura en:

```python
API_BASE_URL = "http://localhost:5000"
```

Modifícala en caso necesario.

---

## 3. Estructura del frontend

Extraída del árbol del proyecto :

```
ui/frontend/
├── app.py
├── config.py
├── static/
│   └── css/
│       └── styles.css
└── templates/
    ├── base.html
    ├── dashboard.html
    └── bans.html
```

### Archivos destacados

| Archivo            | Descripción                                                                  |
| ------------------ | ---------------------------------------------------------------------------- |
| **app.py**         | Aplicación Flask. Define rutas, llama al backend y renderiza las plantillas. |
| **dashboard.html** | Página principal con gráfico, estadísticas y tablas dinámicas.               |
| **bans.html**      | Vista para gestionar IPs baneadas.                                           |
| **base.html**      | Plantilla base con estilos y layout común.                                   |
| **styles.css**     | Estilos para tarjetas, tablas, botones y responsive layout.                  |

---

## 4. Requisitos

### Python

* Python ≥ 3.10
* Flask
* Requests

Instalables desde `requirements.txt` localizado en `ui/`:

```
pip install -r requirements.txt
```

(O puedes activar el entorno virtual ya incluido en el repositorio.)

---

## 5. Ejecución del frontend

### 1) Acceder al directorio:

```
cd ui/frontend
```

### 2) Activar entorno virtual (opcional pero recomendado):

Linux/macOS:

```
source ../venv/bin/activate
```

Windows (PowerShell):

```
../venv/Scripts/Activate.ps1
```

### 3) Iniciar el servidor Flask:

```
python app.py
```

Por defecto la UI queda disponible en:

```
http://localhost:8001
```

---

## 6. Funcionamiento interno del dashboard

El dashboard realiza una carga inicial de datos desde Flask y, después, ejecuta este bucle cada 5 segundos:

```javascript
setInterval(fetchState, 5000);
```

`fetchState()` refresca:

* Contador de ataques
* IPs baneadas
* Eventos
* Datos del gráfico

Esto permite mostrar actividad en tiempo real sin necesidad de WebSockets.

---

## 7. Estilos y diseño

El diseño se basa en:

* **tarjetas (cards)** para agrupar secciones
* **tablas responsivas** para eventos y bans
* **contenedor con scroll interno** para IPs baneadas
* estilo limpio, minimalista y orientado a demo técnica

---

## 8. Modificación de la URL del backend

Para apuntar la UI a otra instancia del backend, edita:

```python
API_BASE_URL = "http://localhost:5000"
```

Ejemplos:

* Docker:

  ```
  API_BASE_URL = "http://backend:5000"
  ```
* Remoto:

  ```
  API_BASE_URL = "http://192.168.1.50:5000"
  ```

---

## 9. Limitaciones actuales

* La UI depende 100% del backend FastAPI: sin él, la página no carga.
* No existe autenticación.
* Se asume que la API devuelve datos válidos y formateados.
* La actualización periódica no usa WebSockets (puede producir picos de carga si se amplía).

---

## 10. Mejoras futuras recomendadas

* Autenticación / roles.
* Añadir gráficos adicionales (por tipo de ataque, IPs recurrentes…).
* Historial persistente de días anteriores.
* Integración directa con el proxy para formular reglas.
* Modo oscuro y parametrización visual.

---

Si quieres, te genero también:

* El **README para el backend**
* El **README global del proyecto**
* Un **diagrama en ASCII** del flujo UI → Backend
* Una **sección de troubleshooting** para demos de hackathon

Dime qué siguiente parte necesitas.

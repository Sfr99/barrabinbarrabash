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


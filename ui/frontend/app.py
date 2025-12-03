from datetime import datetime
from flask import Flask, render_template, redirect, url_for
import requests  # para llamar al backend FastAPI

app = Flask(__name__)

# ---------------------------
# URL del backend FastAPI
# ---------------------------
API_BASE_URL = "http://localhost:5000"


# ---------------------------
# Helpers
# ---------------------------

def format_datetime(dt: datetime) -> str:
    """Formatea fecha/hora para mostrarla en la UI."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_api_datetime(dt_str: str) -> str:
    """
    Recibe un datetime ISO8601 desde la API FastAPI
    y lo convierte a un string legible.
    """
    if not dt_str:
        return ""
    try:
        # FastAPI suele devolver algo tipo "2025-01-01T10:15:30.123456"
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return format_datetime(dt)
    except Exception:
        return dt_str


# ---------------------------
# Rutas
# ---------------------------

@app.route("/")
def dashboard():
    # Estado completo (ataques, bans, eventos)
    state_res = requests.get(f"{API_BASE_URL}/state")
    state_res.raise_for_status()
    state = state_res.json()

    # Datos del gráfico
    chart_res = requests.get(f"{API_BASE_URL}/chart")
    chart_res.raise_for_status()
    chart = chart_res.json()
    chart_labels = chart.get("labels", [])
    chart_values = chart.get("values", [])

    banned_ips = [
        {
            "ip": b["ip"],
            "reason": b.get("reason", ""),
            "since": format_api_datetime(b.get("since")),
        }
        for b in state.get("banned_ips", [])
    ]

    events = [
        {
            "timestamp": format_api_datetime(e.get("timestamp")),
            "ip": e.get("ip", ""),
            "action": e.get("action", ""),
            "description": e.get("description", ""),
        }
        for e in sorted(
            state.get("events", []),
            key=lambda x: x.get("timestamp", ""),
            reverse=True,
        )
    ]

    return render_template(
        "dashboard.html",
        attacks_today=state.get("attacks_today", 0),
        banned_ips=banned_ips,
        events=events,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/bans")
def bans():
    # Reutilizamos /state para sacar la lista de bans
    state_res = requests.get(f"{API_BASE_URL}/state")
    state_res.raise_for_status()
    state = state_res.json()

    banned_ips = [
        {
            "ip": b["ip"],
            "reason": b.get("reason", ""),
            "since": format_api_datetime(b.get("since")),
        }
        for b in state.get("banned_ips", [])
    ]

    return render_template("bans.html", banned_ips=banned_ips)


@app.route("/unban/<ip>", methods=["POST"])
def unban(ip):
    # Llamamos al backend FastAPI: POST /unban/{ip}
    res = requests.post(f"{API_BASE_URL}/unban/{ip}")
    # Opcional: comprobar errores con res.status_code
    return redirect(url_for("bans"))


@app.route("/reset", methods=["POST"])
def reset():
    # Llamamos al backend FastAPI: POST /reset
    res = requests.post(f"{API_BASE_URL}/reset")
    # Opcional: comprobar errores con res.status_code
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # Frontend Flask en http://localhost:8001
    app.run(host="0.0.0.0", port=8001, debug=True)

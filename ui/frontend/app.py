from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# ---------------------------
# Estado "fake" en memoria
# En producción esto vendrá de la API del firewall.
# ---------------------------

state = {
    "attacks_today": 12,
    "banned_ips": [
        {
            "ip": "192.168.1.10",
            "reason": "SSH brute force",
            "since": datetime.now() - timedelta(hours=2)
        },
        {
            "ip": "10.0.0.5",
            "reason": "Port scan",
            "since": datetime.now() - timedelta(hours=5)
        },
    ],
    "events": [
        {
            "timestamp": datetime.now() - timedelta(minutes=1),
            "ip": "203.0.113.1",
            "action": "blocked",
            "description": "HTTP flood"
        },
        {
            "timestamp": datetime.now() - timedelta(minutes=3),
            "ip": "198.51.100.2",
            "action": "allowed",
            "description": "Normal traffic"
        },
        {
            "timestamp": datetime.now() - timedelta(minutes=5),
            "ip": "192.0.2.50",
            "action": "blocked",
            "description": "SSH brute force"
        },
    ]
}


def format_datetime(dt: datetime) -> str:
    """Formatea fecha/hora para mostrarla en la UI."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def compute_chart_data():
    """
    Genera datos fake para el gráfico (eventos por minuto en los últimos 10 minutos).
    En un entorno real vendrá de la API.
    """
    now = datetime.now()
    labels = []
    values = []

    for i in range(10, 0, -1):
        minute = now - timedelta(minutes=i)
        # Etiqueta tipo "HH:MM"
        labels.append(minute.strftime("%H:%M"))

        # Contar eventos de ese minuto
        count = sum(
            1 for e in state["events"]
            if e["timestamp"].strftime("%H:%M") == minute.strftime("%H:%M")
        )
        values.append(count)

    return labels, values


# ---------------------------
# Rutas
# ---------------------------

@app.route("/")
def dashboard():
    chart_labels, chart_values = compute_chart_data()

    # Preparamos datos para la plantilla
    banned_ips = [
        {
            "ip": b["ip"],
            "reason": b["reason"],
            "since": format_datetime(b["since"]),
        }
        for b in state["banned_ips"]
    ]

    events = [
        {
            "timestamp": format_datetime(e["timestamp"]),
            "ip": e["ip"],
            "action": e["action"],
            "description": e["description"],
        }
        for e in sorted(state["events"], key=lambda x: x["timestamp"], reverse=True)
    ]

    return render_template(
        "dashboard.html",
        attacks_today=state["attacks_today"],
        banned_ips=banned_ips,
        events=events,
        chart_labels=chart_labels,
        chart_values=chart_values,
    )


@app.route("/bans")
def bans():
    banned_ips = [
        {
            "ip": b["ip"],
            "reason": b["reason"],
            "since": format_datetime(b["since"]),
        }
        for b in state["banned_ips"]
    ]
    return render_template("bans.html", banned_ips=banned_ips)


@app.route("/unban/<ip>", methods=["POST"])
def unban(ip):
    # En producción, aquí llamarías a la API del firewall.
    state["banned_ips"] = [b for b in state["banned_ips"] if b["ip"] != ip]
    return redirect(url_for("bans"))


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset del estado:
    - Pone contador de ataques a 0
    - Limpia IPs baneadas
    - Limpia eventos
    En producción, esto tendría que ir contra el backend real.
    """
    state["attacks_today"] = 0
    state["banned_ips"].clear()
    state["events"].clear()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    # Para desarrollo local
    app.run(host="0.0.0.0", port=5000, debug=True)

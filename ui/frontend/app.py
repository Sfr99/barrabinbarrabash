from flask import Flask, render_template, redirect, url_for, request
import requests
from config import BACKEND_URL

app = Flask(__name__)


# =====================================================
# DASHBOARD
# =====================================================

@app.route("/")
def dashboard():
    """
    Página principal. Obtiene todo lo necesario del backend:
    - estado general (ataques, bans, eventos)
    - datos del gráfico
    """
    try:
        state = requests.get(f"{BACKEND_URL}/state").json()
        chart = requests.get(f"{BACKEND_URL}/chart").json()
    except Exception as e:
        # En caso de que el backend esté caído
        return f"Error conectando con el backend: {e}", 500

    return render_template(
        "dashboard.html",
        attacks_today=state["attacks_today"],
        banned_ips=state["banned_ips"],
        events=state["events"],
        chart_labels=chart["labels"],
        chart_values=chart["values"],
    )


# =====================================================
# BANS
# =====================================================

@app.route("/bans")
def bans():
    """
    Vista para gestionar las IPs baneadas.
    """
    try:
        state = requests.get(f"{BACKEND_URL}/state").json()
    except Exception as e:
        return f"Error conectando con el backend: {e}", 500

    return render_template("bans.html", banned_ips=state["banned_ips"])


# =====================================================
# ACCIONES
# =====================================================

@app.route("/unban/<ip>", methods=["POST"])
def unban(ip):
    """
    Desbanea una IP mediante el backend.
    """
    try:
        requests.post(f"{BACKEND_URL}/unban/{ip}")
    except Exception as e:
        return f"Error conectando con el backend: {e}", 500

    return redirect(url_for("bans"))


@app.route("/reset", methods=["POST"])
def reset():
    """
    Resetea el estado completo en el backend:
    - ataques
    - eventos
    - IPs baneadas
    """
    try:
        requests.post(f"{BACKEND_URL}/reset")
    except Exception as e:
        return f"Error conectando con el backend: {e}", 500

    return redirect(url_for("dashboard"))


# =====================================================
# MAIN (DESARROLLO)
# =====================================================

if __name__ == "__main__":
    # Servidor de desarrollo
    app.run(host="0.0.0.0", port=5000, debug=True)

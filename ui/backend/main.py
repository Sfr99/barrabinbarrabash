from fastapi import FastAPI
from fastapi.responses import JSONResponse

from state import get_state, reset_state, unban_ip, get_chart_data

app = FastAPI(title="Firewall Backend API")


# ------------------------------------------------------
# RUTAS PÚBLICAS PARA EL FRONTEND FLASK
# ------------------------------------------------------

@app.get("/state")
def api_state():
    """Devuelve todo el estado (ataques, bans, eventos)."""
    return JSONResponse(get_state().model_dump())


@app.post("/reset")
def api_reset():
    reset_state()
    return {"status": "ok", "msg": "state reset"}


@app.post("/unban/{ip}")
def api_unban(ip: str):
    unban_ip(ip)
    return {"status": "ok", "msg": f"{ip} unbanned"}


@app.get("/chart")
def api_chart():
    labels, values = get_chart_data()
    return {"labels": labels, "values": values}


# ------------------------------------------------------
# DEV MODE
# ------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)

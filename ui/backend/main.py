from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from state import get_state, reset_state, unban_ip, get_chart_data, init_sample_data, add_ban, add_event, FirewallState
from database import engine
from models import Base

app = FastAPI(title="Firewall Backend API")

origins = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas al arrancar
Base.metadata.create_all(bind=engine)

# ------------------------------------------------------
# RUTAS PÚBLICAS PARA EL FRONTEND FLASK
# ------------------------------------------------------

@app.get("/state", response_model=FirewallState)
def api_state():
    """Devuelve todo el estado (ataques, bans, eventos)."""
    return get_state()

@app.post("/reset")
def api_reset():
    reset_state()
    return {"status": "ok", "msg": "state reset"}

@app.post("/ban")
def api_add_ban(ip: str, reason: str):
    try:
        add_ban(ip, reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "msg": f"IP {ip} baneada"}

@app.post("/unban/{ip}")
def api_unban(ip: str):
    if not unban_ip(ip):
        raise HTTPException(status_code=404, detail="IP not found")
    return {"status": "ok", "msg": f"{ip} unbanned"}

@app.post("/event")
def api_add_event(ip: str, action: str, description: str, is_attack: bool = True):
    try:
        add_event(ip, action, description, is_attack)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok", "msg": "Evento añadido"}

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
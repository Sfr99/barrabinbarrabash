from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Tuple

from database import SessionLocal
from models import BanDB, EventDB, StatsDB

# ------------------------------
# Nuestros modelos
# ------------------------------

class Ban(BaseModel):
    ip: str
    reason: str
    since: datetime

class Event(BaseModel):
    timestamp: datetime
    ip: str
    action: str
    description: str

class ChartData(BaseModel):
    labels: List[str]
    values: List[int]

class FirewallState(BaseModel):
    attacks_today: int
    banned_ips: List[Ban]
    events: List[Event]
    chart: ChartData   

# ------------------------------
# Mapear entre BBDD y clases
# ------------------------------

def _db_to_ban(b: BanDB) -> Ban:
    return Ban(ip=b.ip, reason=b.reason, since=b.since)

def _db_to_event(e: EventDB) -> Event:
    return Event(
        timestamp=e.timestamp,
        ip=e.ip,
        action=e.action,
        description=e.description,
    )

def _get_stats_row(session) -> StatsDB:
    stats = session.query(StatsDB).filter(StatsDB.id == 1).first()
    if not stats:
        stats = StatsDB(id=1, attacks_today=0)
        session.add(stats)
        session.commit()
        session.refresh(stats)
    return stats


# ------------------------------
# Funciones públicas usadas por main.py
# ------------------------------

def get_state() -> FirewallState:
    """
    Devuelve todo el estado desde la BBDD:
    - attacks_today (StatsDB)
    - banned_ips (BanDB)
    - events (EventDB)
    - chart (events/min)
    """
    db = SessionLocal()
    try:
        stats = _get_stats_row(db)
        bans_db = db.query(BanDB).all()
        events_db = db.query(EventDB).order_by(EventDB.timestamp.desc()).all()

        banned_ips = [_db_to_ban(b) for b in bans_db]
        events = [_db_to_event(e) for e in events_db]

        # Obtener datos del gráfico
        labels, values = get_chart_data()

        return FirewallState(
            attacks_today=stats.attacks_today,
            banned_ips=banned_ips,
            events=events,
            chart=ChartData(labels=labels, values=values)
        )
    finally:
        db.close()



def reset_state() -> None:
    """
    Resetea TODO el estado:
    - attacks_today = 0
    - borra todos los bans
    - borra todos los eventos
    """
    db = SessionLocal()
    try:
        stats = _get_stats_row(db)
        stats.attacks_today = 0

        db.query(BanDB).delete()
        db.query(EventDB).delete()

        db.commit()
    finally:
        db.close()


def unban_ip(ip: str) -> bool:
    """
    Elimina una IP de la tabla de bans.
    Devuelve True si existía, False si no.
    """
    db = SessionLocal()
    try:
        row = db.query(BanDB).filter(BanDB.ip == ip).first()
        if not row:
            return False
        db.delete(row)
        db.commit()
        return True
    finally:
        db.close()


def get_chart_data() -> Tuple[List[str], List[int]]:
    """
    Construye (labels, values) para el gráfico de eventos por minuto
    en los últimos 10 minutos, usando EventDB.
    """
    db = SessionLocal()
    try:
        now = datetime.now()
        labels: List[str] = []
        values: List[int] = []

        # Traemos solo los eventos de los últimos 10 minutos (opcional pero eficiente)
        since = now - timedelta(minutes=10)
        events_db = (
            db.query(EventDB)
            .filter(EventDB.timestamp >= since)
            .all()
        )

        for i in range(10, 0, -1):
            minute = now - timedelta(minutes=i)
            label = minute.strftime("%H:%M")
            labels.append(label)

            count = sum(
                1
                for e in events_db
                if e.timestamp.strftime("%H:%M") == label
            )
            values.append(count)

        return labels, values
    finally:
        db.close()

# ------------------------------
# Funciones extra para el futuro
# (por si luego las necesitas)
# ------------------------------

def add_ban(ip: str, reason: str) -> Ban:
    """Añade un ban a la BBDD. Si ya existe, lo devuelve sin duplicar."""
    db = SessionLocal()
    try:
        existing = db.query(BanDB).filter(BanDB.ip == ip).first()
        if existing:
            return _db_to_ban(existing)

        row = BanDB(ip=ip, reason=reason, since=datetime.now())
        db.add(row)
        db.commit()
        db.refresh(row)
        return _db_to_ban(row)
    finally:
        db.close()


def add_event(ip: str, action: str, description: str, is_attack: bool = True) -> Event:
    """Añade un evento a la BBDD. Si is_attack=True, incrementa attacks_today."""
    db = SessionLocal()
    try:
        row = EventDB(
            timestamp=datetime.now(),
            ip=ip,
            action=action,
            description=description,
        )
        db.add(row)

        if is_attack:
            stats = _get_stats_row(db)
            stats.attacks_today += 1

        db.commit()
        db.refresh(row)
        return _db_to_event(row)
    finally:
        db.close()

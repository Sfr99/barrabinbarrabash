from datetime import datetime, timedelta
from typing import List, Dict, Any

from models import Ban, Event, FirewallState


# -----------------------
# Estado simulado
# -----------------------

_attacks_today = 12

_banned_ips: List[Ban] = [
    Ban(ip="192.168.1.10", reason="SSH brute force", since=datetime.now() - timedelta(hours=2)),
    Ban(ip="10.0.0.5", reason="Port scan", since=datetime.now() - timedelta(hours=5)),
]

_events: List[Event] = [
    Event(timestamp=datetime.now() - timedelta(minutes=1), ip="203.0.113.1", action="blocked", description="HTTP flood"),
    Event(timestamp=datetime.now() - timedelta(minutes=3), ip="198.51.100.2", action="allowed", description="Normal traffic"),
    Event(timestamp=datetime.now() - timedelta(minutes=5), ip="192.0.2.50", action="blocked", description="SSH brute force"),
]


def get_state() -> FirewallState:
    return FirewallState(
        attacks_today=_attacks_today,
        banned_ips=_banned_ips,
        events=sorted(_events, key=lambda e: e.timestamp, reverse=True),
    )


def reset_state():
    global _attacks_today, _events, _banned_ips
    _attacks_today = 0
    _events = []
    _banned_ips = []


def unban_ip(ip: str):
    global _banned_ips
    _banned_ips = [b for b in _banned_ips if b.ip != ip]


def get_chart_data():
    """
    Devuelve etiquetas y valores (eventos por minuto).
    """
    now = datetime.now()
    labels = []
    values = []

    # últimos 10 minutos
    for i in range(10, 0, -1):
        minute = now - timedelta(minutes=i)
        labels.append(minute.strftime("%H:%M"))

        count = sum(
            1
            for e in _events
            if e.timestamp.strftime("%H:%M") == minute.strftime("%H:%M")
        )
        values.append(count)

    return labels, values

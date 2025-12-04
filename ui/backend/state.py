from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Tuple

from database import SessionLocal
from models import BanDB, EventDB, StatsDB

# const
MINUTES_FOR_CHART = 10


class Ban(BaseModel):   # represent a banned IP record with reason and since
    ip: str
    reason: str
    since: datetime


class Event(BaseModel):  # represent an event record with details
    timestamp: datetime
    ip: str
    action: str
    description: str

class ChartData(BaseModel): # represent chart data with labels and values
    labels: List[str]
    values: List[int]

class FirewallState(BaseModel):  # represent the overall firewall state
    attacks_today: int
    banned_ips: List[Ban]
    events: List[Event]
    chart: ChartData   



# map between DB models and Pydantic models

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


# Main functions to get and modify state

def get_state() -> FirewallState:
    """
    Returns the complete firewall state from the database:
    - attacks_today (StatsDB)
    - banned_ips (BanDB)
    - events (EventDB)
    - chart (events per minute)
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
    Resets all firewall state in the database.
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
    Removes an IP ban from the database, 
    returning True if it existed, False otherwise.
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
    Builds (labels, values) for the events-per-minute chart
    over the last MINUTES_FOR_CHART minutes, using EventDB.
    """
    db = SessionLocal()
    try:
        now = datetime.now()
        labels: List[str] = []
        values: List[int] = []


        since = now - timedelta(minutes=MINUTES_FOR_CHART)
        events_db = (
            db.query(EventDB)
            .filter(EventDB.timestamp >= since)
            .all()
        )

        for i in range(MINUTES_FOR_CHART, 0, -1):
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


def add_ban(ip: str, reason: str) -> Ban:
    """
    Adds a new ban to the database. If the IP is already banned,
    returns the existing ban. Otherwise returns the newly created Ban.
    """
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


def add_event(ip: str, action: str, description: str, is_attack: bool = False) -> Event:
    """
    Adds an event to the database. If is_attack is True,
    increments attacks_today in StatsDB. Returns the created Event.
    """
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



# Development helper: initialize sample data
def init_sample_data() -> None:
    """
    Fills the database with sample bans and events for testing.
    Does nothing if there are already bans or events.
    Function only for development purposes.
    """
    db = SessionLocal()
    try:
        # Check if there are already bans or events
        has_bans = db.query(BanDB).first()
        has_events = db.query(EventDB).first()
        if has_bans or has_events:
            return

        # Stats: attacks_today
        stats = _get_stats_row(db)
        stats.attacks_today = 12

        now = datetime.now()

        # Sample bans
        bans = [
            BanDB(
                ip="192.168.1.10",
                reason="SSH brute force",
                since=now - timedelta(hours=2),
            ),
            BanDB(
                ip="10.0.0.5",
                reason="Port scan",
                since=now - timedelta(hours=5),
            ),
        ]

        # example events
        events = [
            EventDB(
                timestamp=now - timedelta(minutes=1),
                ip="203.0.113.1",
                action="blocked",
                description="HTTP flood",
            ),
            EventDB(
                timestamp=now - timedelta(minutes=3),
                ip="198.51.100.2",
                action="allowed",
                description="Normal traffic",
            ),
            EventDB(
                timestamp=now - timedelta(minutes=5),
                ip="192.0.2.50",
                action="blocked",
                description="SSH brute force",
            ),
        ]

        db.add_all(bans + events)
        db.commit()
    finally:
        db.close()

from pydantic import BaseModel
from datetime import datetime
from typing import List


class Ban(BaseModel):
    ip: str
    reason: str
    since: datetime


class Event(BaseModel):
    timestamp: datetime
    ip: str
    action: str
    description: str


class FirewallState(BaseModel):
    attacks_today: int
    banned_ips: List[Ban]
    events: List[Event]

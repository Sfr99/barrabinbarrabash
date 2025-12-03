from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class BanDB(Base):
    __tablename__ = "bans"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String, unique=True, index=True, nullable=False)
    reason = Column(String, nullable=False)
    since = Column(DateTime, default=datetime.utcnow)

class EventDB(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip = Column(String, nullable=False)
    action = Column(String, nullable=False)
    description = Column(String, nullable=False)

class StatsDB(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    attacks_today = Column(Integer, default=0)

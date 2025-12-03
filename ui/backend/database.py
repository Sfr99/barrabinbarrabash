from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

URL_BBDD = "sqlite:///./firewall.db"

engine = create_engine(
    URL_BBDD,
    connect_args={"check_same_thread": False},  # necesario para SQLite si hay varios hilos
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
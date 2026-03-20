"""
Connessione a PostgreSQL via SQLAlchemy.
Non ancora agganciato alla pipeline - TODO.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Crea le tabelle se non esistono."""
    Base.metadata.create_all(engine)


def get_session():
    return SessionLocal()

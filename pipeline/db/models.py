"""
Schema del database - SQLAlchemy ORM.

Tabelle:
  - fonti: le pagine web scrapate
  - sagre: una riga per ogni sagra/festa estratta
"""

from sqlalchemy import (
    Column, Integer, String, Text, SmallInteger,
    DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Fonte(Base):
    __tablename__ = "fonti"

    id = Column(Integer, primary_key=True)
    url = Column(Text, nullable=False, unique=True)
    paese_ricerca = Column(String(255))       # frazione/paese che ha generato la ricerca
    regione = Column(String(100))
    scraped_at = Column(DateTime, default=datetime.utcnow)

    sagre = relationship("Sagra", back_populates="fonte")


class Sagra(Base):
    __tablename__ = "sagre"

    id = Column(Integer, primary_key=True)
    nome = Column(String(500), nullable=False)
    comune = Column(String(255))
    regione = Column(String(100))
    tipo = Column(String(50))                 # gastronomica/folkloristica/religiosa/musicale/altro
    mese_inizio = Column(SmallInteger)        # 1-12
    mese_fine = Column(SmallInteger)          # 1-12
    periodo_descrizione = Column(Text)

    fonte_id = Column(Integer, ForeignKey("fonti.id"), nullable=False)
    fonte = relationship("Fonte", back_populates="sagre")

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("nome", "fonte_id", name="uq_sagra_fonte"),
    )

    def __repr__(self):
        return f"<Sagra {self.nome} - {self.comune} ({self.mese_inizio})>"

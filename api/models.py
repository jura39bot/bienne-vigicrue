from sqlalchemy import Column, Integer, Float, Date, DateTime, String
from .database import Base


class DebitJournalier(Base):
    __tablename__ = "debit_journalier"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    debit_moyen = Column(Float, nullable=False)   # m³/s - moyenne journalière
    debit_min = Column(Float, nullable=True)       # m³/s - minimum journalier
    debit_max = Column(Float, nullable=True)       # m³/s - maximum journalier
    nb_mesures = Column(Integer, nullable=True)    # nombre de mesures brutes
    source = Column(String(50), default="vigicrue")
    collecte_le = Column(DateTime, nullable=True)

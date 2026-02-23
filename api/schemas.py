from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class DebitJournalierBase(BaseModel):
    date: date
    debit_moyen: float
    debit_min: Optional[float] = None
    debit_max: Optional[float] = None
    nb_mesures: Optional[int] = None
    source: Optional[str] = "vigicrue"


class DebitJournalierCreate(DebitJournalierBase):
    pass


class DebitJournalier(DebitJournalierBase):
    id: int
    collecte_le: Optional[datetime] = None

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    date_debut: date
    date_fin: date
    nb_jours: int
    debit_moyen: float
    debit_min: float
    debit_max: float
    station: str = "V241403001 - La Bienne à Morez"


class StationInfo(BaseModel):
    code: str = "V241403001"
    nom: str = "La Bienne à Morez"
    cours_deau: str = "La Bienne"
    commune: str = "Morez"
    departement: str = "Jura (39)"
    source: str = "Vigicrue / Hub'Eau"
    unite: str = "m³/s"

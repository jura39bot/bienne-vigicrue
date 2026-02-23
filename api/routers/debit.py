from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import List, Optional

from ..database import get_db
from ..models import DebitJournalier as DebitModel
from ..schemas import DebitJournalier, StatsResponse, StationInfo

router = APIRouter(prefix="/debit", tags=["débit"])


@router.get("/station", response_model=StationInfo)
def station_info():
    """Informations sur la station hydrométrique."""
    return StationInfo()


@router.get("/", response_model=List[DebitJournalier])
def liste_debits(
    date_debut: Optional[date] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[date] = Query(None, description="Date fin (YYYY-MM-DD)"),
    limit: int = Query(30, le=365, description="Nombre de résultats (max 365)"),
    db: Session = Depends(get_db),
):
    """Liste des débits journaliers, du plus récent au plus ancien."""
    q = db.query(DebitModel)
    if date_debut:
        q = q.filter(DebitModel.date >= date_debut)
    if date_fin:
        q = q.filter(DebitModel.date <= date_fin)
    return q.order_by(DebitModel.date.desc()).limit(limit).all()


@router.get("/latest", response_model=DebitJournalier)
def dernier_debit(db: Session = Depends(get_db)):
    """Dernier débit journalier enregistré."""
    entry = db.query(DebitModel).order_by(DebitModel.date.desc()).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Aucune donnée disponible")
    return entry


@router.get("/stats", response_model=StatsResponse)
def statistiques(
    jours: int = Query(30, le=3650, description="Période en jours"),
    db: Session = Depends(get_db),
):
    """Statistiques sur la période."""
    date_fin = date.today()
    date_debut = date_fin - timedelta(days=jours)

    result = db.query(
        func.avg(DebitModel.debit_moyen).label("avg"),
        func.min(DebitModel.debit_min).label("min"),
        func.max(DebitModel.debit_max).label("max"),
        func.count(DebitModel.id).label("count"),
    ).filter(
        DebitModel.date >= date_debut,
        DebitModel.date <= date_fin,
    ).first()

    if not result or result.count == 0:
        raise HTTPException(status_code=404, detail="Pas assez de données sur cette période")

    return StatsResponse(
        date_debut=date_debut,
        date_fin=date_fin,
        nb_jours=result.count,
        debit_moyen=round(result.avg, 3),
        debit_min=round(result.min or 0, 3),
        debit_max=round(result.max or 0, 3),
    )


@router.get("/{date_obs}", response_model=DebitJournalier)
def debit_par_date(date_obs: date, db: Session = Depends(get_db)):
    """Débit journalier pour une date donnée."""
    entry = db.query(DebitModel).filter(DebitModel.date == date_obs).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Aucune donnée pour le {date_obs}")
    return entry

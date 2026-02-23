#!/usr/bin/env python3
"""
Collecteur quotidien — La Bienne à Morez (V241403001)
Récupère les observations Vigicrue et calcule le débit moyen journalier.
Usage: python scripts/collect.py [--date YYYY-MM-DD] [--days N]
"""

import sys
import os
import argparse
import requests
import logging
from datetime import date, datetime, timedelta
from statistics import mean

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, engine
from api.models import DebitJournalier, Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

STATION_CODE = "V241403001"
VIGICRUE_URL = "https://www.vigicrues.gouv.fr/services/observations.json/index.php"


def fetch_observations(nb_jours: int = 2) -> list:
    """Récupère les observations brutes depuis l'API Vigicrue."""
    params = {
        "CdStationHydro": STATION_CODE,
        "GrdSerie": "Q",
        "FormatDate": "iso",
        "NbJours": nb_jours,
    }
    headers = {"User-Agent": "bienne-vigicrue/1.0 (github.com/jura39bot/bienne-vigicrue)"}
    resp = requests.get(VIGICRUE_URL, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get("Serie", {}).get("ObssHydro", [])


def aggregate_by_day(observations: list) -> dict:
    """Agrège les observations par jour (moyenne, min, max)."""
    by_day = {}
    for obs in observations:
        dt_str = obs.get("DtObsHydro", "")
        val = obs.get("ResObsHydro")
        if not dt_str or val is None:
            continue
        try:
            dt = datetime.fromisoformat(dt_str)
            day = dt.date()
            by_day.setdefault(day, []).append(float(val))
        except (ValueError, TypeError):
            continue
    result = {}
    for day, vals in by_day.items():
        result[day] = {
            "debit_moyen": round(mean(vals), 4),
            "debit_min": round(min(vals), 4),
            "debit_max": round(max(vals), 4),
            "nb_mesures": len(vals),
        }
    return result


def upsert_day(db, jour: date, stats: dict) -> bool:
    """Insère ou met à jour un enregistrement journalier. Retourne True si nouveau."""
    existing = db.query(DebitJournalier).filter(DebitJournalier.date == jour).first()
    if existing:
        existing.debit_moyen = stats["debit_moyen"]
        existing.debit_min = stats["debit_min"]
        existing.debit_max = stats["debit_max"]
        existing.nb_mesures = stats["nb_mesures"]
        existing.collecte_le = datetime.utcnow()
        db.commit()
        return False
    entry = DebitJournalier(
        date=jour,
        collecte_le=datetime.utcnow(),
        **stats,
    )
    db.add(entry)
    db.commit()
    return True


def collect(nb_jours: int = 2) -> dict:
    """Collecte principale. Retourne un résumé."""
    log.info(f"Collecte Vigicrue — station {STATION_CODE} ({nb_jours} derniers jours)")
    Base.metadata.create_all(bind=engine)

    obs = fetch_observations(nb_jours)
    log.info(f"  {len(obs)} observations brutes récupérées")

    by_day = aggregate_by_day(obs)
    log.info(f"  {len(by_day)} jours à traiter")

    db = SessionLocal()
    nouveaux, mis_a_jour = 0, 0
    try:
        for jour, stats in sorted(by_day.items()):
            is_new = upsert_day(db, jour, stats)
            if is_new:
                nouveaux += 1
                log.info(f"  + {jour} | moy={stats['debit_moyen']} m³/s | min={stats['debit_min']} max={stats['debit_max']} ({stats['nb_mesures']} mesures)")
            else:
                mis_a_jour += 1
                log.info(f"  ~ {jour} | moy={stats['debit_moyen']} m³/s (mis à jour)")
    finally:
        db.close()

    return {"nouveaux": nouveaux, "mis_a_jour": mis_a_jour, "jours": len(by_day)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collecteur Vigicrue — La Bienne à Morez")
    parser.add_argument("--days", type=int, default=2, help="Nombre de jours à récupérer (défaut: 2)")
    parser.add_argument("--backfill", type=int, default=0, help="Backfill N jours")
    args = parser.parse_args()

    nb = args.backfill if args.backfill > 0 else args.days
    result = collect(nb_jours=nb)
    print(f"\nTerminé — {result['nouveaux']} nouveau(x), {result['mis_a_jour']} mis à jour")

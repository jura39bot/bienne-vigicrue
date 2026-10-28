#!/usr/bin/env python3
"""
Statistiques mensuelles — La Bienne à Morez (V241403001)
Agrège les débits journaliers par mois et écrit data/monthly_stats.csv + data/monthly_stats.md
Usage: python scripts/stats_monthly.py
"""

import os
import sys
from datetime import date
from statistics import mean

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import DebitJournalier

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

MOIS_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
}


def load_rows():
    db = SessionLocal()
    try:
        return db.query(DebitJournalier).order_by(DebitJournalier.date).all()
    finally:
        db.close()


def aggregate(rows):
    months = {}
    for r in rows:
        key = r.date.strftime("%Y-%m")
        months.setdefault(key, []).append(r)
    out = []
    for key in sorted(months):
        vals = months[key]
        out.append({
            "month": key,
            "avg": mean(float(v.debit_moyen) for v in vals),
            "min": min(float(v.debit_min) for v in vals if v.debit_min is not None),
            "max": max(float(v.debit_max) for v in vals if v.debit_max is not None),
            "days": len(vals),
        })
    return out


def fmt(x):
    s = f"{x:.4f}".rstrip("0")
    return s + "0" if s.endswith(".") else s


def write_csv(months):
    path = os.path.join(DATA_DIR, "monthly_stats.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("month,avg_debit,min_debit,max_debit,days\r\n")
        for m in months:
            f.write(f"{m['month']},{fmt(m['avg'])},{fmt(m['min'])},{fmt(m['max'])},{m['days']}\r\n")
    return path


def write_md(months):
    path = os.path.join(DATA_DIR, "monthly_stats.md")
    today = date.today().isoformat()
    lines = [
        "# 📊 Statistiques Hydrologiques — La Bienne",
        f"*Généré le {today}*",
        "",
        "## Débits moyens mensuels",
        "",
        "| Mois | Moy (m³/s) | Min (m³/s) | Max (m³/s) | Jours |",
        "|------|------------|------------|------------|-------|",
    ]
    for m in months:
        y, mo = m["month"].split("-")
        lines.append(
            f"| {m['month']} ({MOIS_FR[int(mo)]}) | {fmt(m['avg'])} | {fmt(m['min'])} | {fmt(m['max'])} | {m['days']} |"
        )

    years = {}
    for m in months:
        years.setdefault(m["month"][:4], []).extend([m["avg"]] * m["days"])
    lines += ["", "## Débits annuels moyens"]
    for y in sorted(years):
        lines.append(f"- **{y}** : {mean(years[y]):.3f} m³/s (moyenne sur {len(years[y])} jours)")

    last = months[-1]
    lines += [
        "",
        f"## {last['month']}",
        "",
        "| Métrique | Valeur |",
        "|---|---|",
        f"| Débit moyen | **{fmt(last['avg'])} m³/s** |",
        f"| Débit min | {fmt(last['min'])} m³/s |",
        f"| Débit max | {fmt(last['max'])} m³/s |",
        f"| Jours de données | {last['days']} |",
        "",
        f"*Actif — mis à jour le {today}*",
        "",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def write_debit_csv(rows):
    path = os.path.join(DATA_DIR, "debit.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("date,debit_moyen,debit_min,debit_max,nb_mesures\r\n")
        for r in rows:
            f.write(
                f"{r.date.isoformat()},{fmt(float(r.debit_moyen))},"
                f"{fmt(float(r.debit_min))},{fmt(float(r.debit_max))},{r.nb_mesures or 0}\r\n"
            )
    return path


def main():
    rows = load_rows()
    if not rows:
        print("Aucune donnée en base.")
        return 1
    months = aggregate(rows)
    write_csv(months)
    write_md(months)
    write_debit_csv(rows)

    last = months[-1]
    print(f"Mois couverts : {months[0]['month']} → {last['month']} ({len(months)} mois)")
    for m in months:
        print(f"  {m['month']}: moy={fmt(m['avg'])} m³/s (min {fmt(m['min'])}, max {fmt(m['max'])}, {m['days']} j)")
    print(f"Dernier mois : {last['month']} — débit moyen {fmt(last['avg'])} m³/s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

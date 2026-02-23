#!/usr/bin/env python3
"""CLI — Bienne Vigicrue"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typer
from datetime import date, timedelta
from rich.console import Console
from rich.table import Table
from rich import box

app = typer.Typer(help="CLI Bienne Vigicrue — La Bienne à Morez (V241403001)")
console = Console()


@app.command()
def collect(
    days: int = typer.Option(2, help="Jours à récupérer depuis Vigicrue"),
    backfill: int = typer.Option(0, help="Backfill N jours d'historique"),
):
    """Collecte les débits depuis l'API Vigicrue et les stocke en base."""
    from scripts.collect import collect as do_collect
    nb = backfill if backfill > 0 else days
    console.print(f"[cyan]Collecte Vigicrue — {nb} jours...[/cyan]")
    result = do_collect(nb_jours=nb)
    console.print(f"[green]✓ {result['nouveaux']} nouveau(x), {result['mis_a_jour']} mis à jour[/green]")


@app.command()
def show(
    limit: int = typer.Option(10, help="Nombre d'entrées à afficher"),
    date_debut: str = typer.Option(None, help="Date début YYYY-MM-DD"),
    date_fin: str = typer.Option(None, help="Date fin YYYY-MM-DD"),
):
    """Affiche les débits journaliers stockés en base."""
    from api.database import SessionLocal
    from api.models import DebitJournalier

    db = SessionLocal()
    try:
        q = db.query(DebitJournalier)
        if date_debut:
            q = q.filter(DebitJournalier.date >= date_debut)
        if date_fin:
            q = q.filter(DebitJournalier.date <= date_fin)
        entries = q.order_by(DebitJournalier.date.desc()).limit(limit).all()
    finally:
        db.close()

    if not entries:
        console.print("[yellow]Aucune donnée en base. Lance 'cli collect' d'abord.[/yellow]")
        return

    table = Table(title="La Bienne à Morez — Débits journaliers", box=box.ROUNDED)
    table.add_column("Date", style="cyan")
    table.add_column("Moy (m³/s)", justify="right", style="green")
    table.add_column("Min (m³/s)", justify="right")
    table.add_column("Max (m³/s)", justify="right", style="red")
    table.add_column("Mesures", justify="right", style="dim")

    for e in entries:
        table.add_row(
            str(e.date),
            f"{e.debit_moyen:.3f}",
            f"{e.debit_min:.3f}" if e.debit_min is not None else "-",
            f"{e.debit_max:.3f}" if e.debit_max is not None else "-",
            str(e.nb_mesures or "-"),
        )

    console.print(table)


@app.command()
def stats(
    jours: int = typer.Option(30, help="Période en jours"),
):
    """Affiche les statistiques sur une période."""
    from api.database import SessionLocal
    from api.models import DebitJournalier
    from sqlalchemy import func

    db = SessionLocal()
    try:
        date_fin = date.today()
        date_debut = date_fin - timedelta(days=jours)
        result = db.query(
            func.avg(DebitJournalier.debit_moyen).label("avg"),
            func.min(DebitJournalier.debit_min).label("min"),
            func.max(DebitJournalier.debit_max).label("max"),
            func.count(DebitJournalier.id).label("count"),
        ).filter(
            DebitJournalier.date >= date_debut,
            DebitJournalier.date <= date_fin,
        ).first()
    finally:
        db.close()

    if not result or result.count == 0:
        console.print("[yellow]Pas assez de données sur cette période.[/yellow]")
        return

    console.print(f"\n[bold]La Bienne à Morez — Statistiques ({jours} derniers jours)[/bold]")
    console.print(f"  Période   : {date_debut} → {date_fin}")
    console.print(f"  Jours     : {result.count}")
    console.print(f"  Débit moy : [green]{result.avg:.3f} m³/s[/green]")
    console.print(f"  Débit min : {result.min:.3f} m³/s")
    console.print(f"  Débit max : [red]{result.max:.3f} m³/s[/red]")


@app.command()
def db_init():
    """Initialise la base de données."""
    from api.database import engine
    from api.models import Base
    Base.metadata.create_all(bind=engine)
    console.print("[green]✓ Base de données initialisée[/green]")


if __name__ == "__main__":
    app()

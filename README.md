# 🌊 bienne-vigicrue

Collecte et API des données hydrologiques de **La Bienne à Morez** (station V241403001).

Données fournies par [Vigicrue](https://www.vigicrues.gouv.fr/) — débit en **m³/s**, collecte quotidienne automatique.

---

## Structure

```
bienne-vigicrue/
├── api/           # FastAPI — endpoints REST
├── cli/           # CLI Typer — collecte & consultation
├── scripts/       # Collecteur Vigicrue
├── web/           # Interface web
├── Dockerfile
└── docker-compose.yml
```

## Démarrage rapide

```bash
# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base
make db-init

# Collecter les 30 derniers jours
make backfill

# Lancer l'API
make run
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger)
```

## CLI

```bash
# Collecter les 2 derniers jours (usage quotidien)
python cli/main.py collect

# Backfill 30 jours
python cli/main.py collect --backfill 30

# Afficher les 10 derniers relevés
python cli/main.py show

# Stats 30 derniers jours
python cli/main.py stats --jours 30
```

## API REST

| Endpoint | Description |
|---|---|
| `GET /api/v1/debit/` | Liste des débits (paramètres: date_debut, date_fin, limit) |
| `GET /api/v1/debit/latest` | Dernier relevé |
| `GET /api/v1/debit/stats?jours=30` | Statistiques sur une période |
| `GET /api/v1/debit/{date}` | Débit pour une date précise |
| `GET /api/v1/debit/station` | Infos station |
| `GET /docs` | Swagger UI |

## Station

- **Code** : V241403001
- **Rivière** : La Bienne
- **Commune** : Morez (Jura, 39)
- **Source** : Vigicrue / Hub'Eau

## Docker

```bash
docker-compose up -d api
docker-compose run --rm collector  # collecte manuelle
```

---

*Données non expertisées, usage indicatif.*

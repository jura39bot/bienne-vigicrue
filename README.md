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

### ⚡ Option 1 — CLI standalone (le plus simple)

```bash
git clone https://github.com/jura39bot/bienne-vigicrue.git
cd bienne-vigicrue

# Environnement virtuel
python3 -m venv .venv && source .venv/bin/activate

# Dépendances
pip install -r requirements.txt

# Initialiser la base et backfill 30 jours
python cli/main.py db-init
python cli/main.py collect --backfill 30

# Afficher les données
python cli/main.py show
python cli/main.py stats
```

> ℹ️ La base SQLite (`bienne.db`) est créée automatiquement. Aucun serveur nécessaire pour le CLI.

### Option 2 — API + Web

```bash
source .venv/bin/activate
uvicorn api.main:app --reload
# → http://localhost:8000      (interface web)
# → http://localhost:8000/docs (Swagger UI)
```

### Option 3 — Docker Compose

```bash
cp .env.example .env
docker-compose up -d api
docker-compose run --rm collector   # collecte initiale
```

## CLI

```bash
# Collecter les 2 derniers jours (usage quotidien)
python cli/main.py collect

# Backfill N jours d'historique
python cli/main.py collect --backfill 30

# Afficher les 10 derniers relevés
python cli/main.py show

# Afficher avec filtre de dates
python cli/main.py show --date-debut 2026-01-01 --date-fin 2026-02-01

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

"""Utilitaires base de données pour la CLI."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import engine
from api.models import Base


def init_db():
    Base.metadata.create_all(bind=engine)
    print("DB initialisée.")


if __name__ == "__main__":
    init_db()

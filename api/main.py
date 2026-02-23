from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

from .database import engine, Base
from .routers import debit

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bienne Vigicrue API",
    description="Données hydrologiques de La Bienne à Morez — station V241403001",
    version="1.0.0",
)

app.include_router(debit.router, prefix="/api/v1")

# Static files (web UI)
static_dir = Path(__file__).parent.parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    html = Path(__file__).parent.parent / "web" / "index.html"
    if html.exists():
        return HTMLResponse(html.read_text())
    return HTMLResponse("<h1>Bienne Vigicrue API</h1><p><a href='/docs'>Swagger</a></p>")


@app.get("/healthz")
def health():
    return {"status": "ok", "station": "V241403001", "riviere": "La Bienne", "lieu": "Morez"}

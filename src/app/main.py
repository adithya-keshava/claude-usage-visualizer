from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_data_dir, has_projects, has_stats_cache
from app.routers import api, overview, projects, sessions, settings

app = FastAPI(title="Claude Usage Visualizer")

# Mount static files (CSS, JS)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Register routers
app.include_router(api.router)
app.include_router(overview.router)
app.include_router(projects.router)
app.include_router(sessions.router)
app.include_router(settings.router)


@app.get("/health")
def health():
    data_dir = get_data_dir()
    return {
        "status": "ok",
        "data_dir": str(data_dir),
        "has_stats_cache": has_stats_cache(),
        "has_projects": has_projects(),
    }

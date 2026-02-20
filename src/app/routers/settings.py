from pathlib import Path

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from jinja2 import Environment, FileSystemLoader

from app.config import get_data_dir, set_data_dir
from app.data.cache import get_cache

router = APIRouter()

# Template setup
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


def validate_data_dir(path_str: str) -> tuple[bool, str]:
    """
    Validate that a path contains stats-cache.json and/or projects/ directory.

    Returns (is_valid, error_message)
    """
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        return False, f"Path does not exist: {path}"
    if not path.is_dir():
        return False, f"Path is not a directory: {path}"

    has_stats_cache = (path / "stats-cache.json").exists()
    has_projects = (path / "projects").is_dir()

    if not (has_stats_cache or has_projects):
        return (
            False,
            "Directory must contain either stats-cache.json or projects/ subdirectory",
        )

    return True, ""


@router.get("/settings", response_class=HTMLResponse)
def settings_page():
    """Render settings form."""
    current_dir = get_data_dir()
    is_valid, _ = validate_data_dir(str(current_dir))

    template = env.get_template("settings.html")
    return template.render(
        current_dir=str(current_dir),
        is_valid=is_valid,
        error=None,
    )


@router.post("/settings")
def update_settings(data_dir: str = Form(...)):
    """Update data directory and invalidate caches."""
    is_valid, error = validate_data_dir(data_dir)
    if not is_valid:
        template = env.get_template("settings.html")
        return template.render(
            current_dir=str(get_data_dir()),
            is_valid=False,
            error=error,
        )

    # Update config and invalidate caches
    set_data_dir(data_dir)
    cache = get_cache()
    cache.invalidate()  # Clear entire cache

    # Redirect to overview
    return RedirectResponse(url="/", status_code=303)

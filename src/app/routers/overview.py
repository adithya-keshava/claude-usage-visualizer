from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.config import get_data_dir
from app.data.loader import build_project_summaries, load_stats_cache
from app.data.pricing import estimate_cost

router = APIRouter()

# Template setup
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


@router.get("/", response_class=HTMLResponse)
def overview():
    """Render overview dashboard with total cost, daily activity, per-model breakdown."""
    overview_stats = load_stats_cache()

    if not overview_stats:
        template = env.get_template("overview.html")
        return template.render(
            overview_stats=None,
            error="No stats-cache.json found. Please configure the data directory in settings.",
        )

    # Compute total cost from project summaries — same source as the projects page,
    # so this number is guaranteed to equal the sum of all project-wise costs.
    project_summaries = build_project_summaries()
    total_cost = sum(
        session.total_cost_usd
        for sessions in project_summaries.values()
        for session in sessions
    )

    # Calculate cache token totals
    total_cache_write = sum(
        stats.cache_creation_input_tokens
        for stats in overview_stats.model_stats.values()
    )
    total_cache_read = sum(
        stats.cache_read_input_tokens for stats in overview_stats.model_stats.values()
    )

    # Prepare model stats for display
    model_rows = []
    for model_id, stats in overview_stats.model_stats.items():
        cost = estimate_cost(
            model_id,
            input_tokens=stats.input_tokens,
            output_tokens=stats.output_tokens,
            cache_creation_input_tokens=stats.cache_creation_input_tokens,
            cache_read_input_tokens=stats.cache_read_input_tokens,
        )
        # Display name mapping
        display_names = {
            "claude-opus-4-6": "Opus 4.6",
            "claude-opus-4-5-20251101": "Opus 4.5",
            "claude-sonnet-4-5-20250929": "Sonnet 4.5",
            "claude-haiku-4-5-20251001": "Haiku 4.5",
        }
        display_name = display_names.get(model_id, model_id)
        model_rows.append(
            {
                "model_id": model_id,
                "display_name": display_name,
                "input_tokens": stats.input_tokens,
                "output_tokens": stats.output_tokens,
                "cache_write_tokens": stats.cache_creation_input_tokens,
                "cache_read_tokens": stats.cache_read_input_tokens,
                "total_tokens": (
                    stats.input_tokens
                    + stats.output_tokens
                    + stats.cache_creation_input_tokens
                    + stats.cache_read_input_tokens
                ),
                "cost_usd": cost,
            }
        )

    template = env.get_template("overview.html")
    return template.render(
        overview_stats=overview_stats,
        total_cost=total_cost,
        total_cache_write=total_cache_write,
        total_cache_read=total_cache_read,
        model_rows=model_rows,
        data_dir=str(get_data_dir()),
        error=None,
    )

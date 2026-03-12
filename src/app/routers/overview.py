import json
import logging
from collections import defaultdict
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.config import get_data_dir
from app.data.loader import build_project_summaries, load_session_messages, load_stats_cache
from app.data.pricing import estimate_cost

logger = logging.getLogger(__name__)

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

    # Calculate model-wise costs and tokens from project summaries (includes subagents)
    # This ensures consistency with total_cost calculation above
    model_stats = defaultdict(lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_write_tokens": 0,
        "cache_read_tokens": 0,
        "cost_usd": 0.0,
    })

    for encoded_path, sessions in project_summaries.items():
        for session in sessions:
            # Load main session messages
            messages = load_session_messages(encoded_path, session.session_id)
            for msg in messages:
                model_stats[msg.model]["input_tokens"] += msg.input_tokens
                model_stats[msg.model]["output_tokens"] += msg.output_tokens
                model_stats[msg.model]["cache_write_tokens"] += msg.cache_creation_input_tokens
                model_stats[msg.model]["cache_read_tokens"] += msg.cache_read_input_tokens
                model_stats[msg.model]["cost_usd"] += msg.cost_usd

            # Load subagent messages (same logic as build_session_summary)
            session_path = get_data_dir() / "projects" / encoded_path / f"{session.session_id}.jsonl"
            subagent_dir = session_path.parent / session.session_id / "subagents"
            if subagent_dir.exists():
                for agent_file in subagent_dir.glob("agent-*.jsonl"):
                    try:
                        with open(agent_file) as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    msg = json.loads(line)
                                    if msg.get("type") != "assistant":
                                        continue
                                    if msg.get("message", {}).get("model") == "<synthetic>":
                                        continue
                                    usage = msg.get("message", {}).get("usage")
                                    if not usage:
                                        continue

                                    model = msg.get("message", {}).get("model", "unknown")
                                    input_tokens = usage.get("input_tokens", 0)
                                    output_tokens = usage.get("output_tokens", 0)
                                    cache_creation = usage.get("cache_creation_input_tokens", 0)
                                    cache_read = usage.get("cache_read_input_tokens", 0)

                                    cost = estimate_cost(
                                        model,
                                        input_tokens=input_tokens,
                                        output_tokens=output_tokens,
                                        cache_creation_input_tokens=cache_creation,
                                        cache_read_input_tokens=cache_read,
                                    )

                                    model_stats[model]["input_tokens"] += input_tokens
                                    model_stats[model]["output_tokens"] += output_tokens
                                    model_stats[model]["cache_write_tokens"] += cache_creation
                                    model_stats[model]["cache_read_tokens"] += cache_read
                                    model_stats[model]["cost_usd"] += cost
                                except json.JSONDecodeError:
                                    continue
                    except IOError as e:
                        logger.warning(f"Failed to read subagent file {agent_file}: {e}")

    # Calculate totals from actual data (includes subagents)
    total_input_tokens = sum(stats["input_tokens"] for stats in model_stats.values())
    total_output_tokens = sum(stats["output_tokens"] for stats in model_stats.values())
    total_cache_write = sum(stats["cache_write_tokens"] for stats in model_stats.values())
    total_cache_read = sum(stats["cache_read_tokens"] for stats in model_stats.values())

    # Prepare model stats for display
    display_names = {
        "claude-opus-4-6": "Opus 4.6",
        "claude-opus-4-5-20251101": "Opus 4.5",
        "claude-sonnet-4-5-20250929": "Sonnet 4.5",
        "claude-haiku-4-5-20251001": "Haiku 4.5",
    }

    model_rows = []
    for model_id, stats in sorted(model_stats.items()):
        display_name = display_names.get(model_id, model_id)
        model_rows.append(
            {
                "model_id": model_id,
                "display_name": display_name,
                "input_tokens": stats["input_tokens"],
                "output_tokens": stats["output_tokens"],
                "cache_write_tokens": stats["cache_write_tokens"],
                "cache_read_tokens": stats["cache_read_tokens"],
                "total_tokens": (
                    stats["input_tokens"]
                    + stats["output_tokens"]
                    + stats["cache_write_tokens"]
                    + stats["cache_read_tokens"]
                ),
                "cost_usd": stats["cost_usd"],
            }
        )

    template = env.get_template("overview.html")
    return template.render(
        overview_stats=overview_stats,
        total_cost=total_cost,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_cache_write=total_cache_write,
        total_cache_read=total_cache_read,
        model_rows=model_rows,
        data_dir=str(get_data_dir()),
        error=None,
    )

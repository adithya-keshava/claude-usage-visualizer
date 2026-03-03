from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.data.loader import build_session_summary, load_history, load_session_messages

router = APIRouter()

# Template setup
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


@router.get("/sessions/{encoded_path}/{session_id}", response_class=HTMLResponse)
def session_detail(encoded_path: str, session_id: str):
    """Render detail view for a single session with per-message breakdown."""
    # Load history to get renamed session names
    history = load_history()

    # Load session summary for metadata
    summary = build_session_summary(encoded_path, session_id, history)

    if not summary:
        template = env.get_template("session_detail.html")
        return template.render(
            session_slug=None,
            messages=None,
            error=f"Session not found: {session_id}",
            back_url=f"/projects/{encoded_path}",
        )

    # Load detailed messages
    messages = load_session_messages(encoded_path, session_id)

    if not messages:
        template = env.get_template("session_detail.html")
        return template.render(
            session_slug=summary.slug,
            project_name=summary.project,
            messages=[],
            message_count=0,
            total_input_tokens=0,
            total_output_tokens=0,
            total_cache_read_tokens=0,
            total_cache_creation_tokens=0,
            total_cost_usd=0.0,
            error=None,
            back_url=f"/projects/{encoded_path}",
            encoded_path=encoded_path,
        )

    # Prepare message rows
    message_rows = []
    total_cache_read = 0
    total_cache_creation = 0

    for msg in messages:
        message_rows.append(
            {
                "timestamp": msg.timestamp,
                "date_time": msg.timestamp.replace("T", " ")[:19] if msg.timestamp else "unknown",
                "model": msg.model,
                "input_tokens": msg.input_tokens,
                "output_tokens": msg.output_tokens,
                "cache_read_tokens": msg.cache_read_input_tokens,
                "cache_creation_tokens": msg.cache_creation_input_tokens,
                "cost_usd": msg.cost_usd,
            }
        )
        total_cache_read += msg.cache_read_input_tokens
        total_cache_creation += msg.cache_creation_input_tokens

    # Calculate message-level totals (main session only)
    message_total_input = sum(m.input_tokens for m in messages)
    message_total_output = sum(m.output_tokens for m in messages)
    message_total_cost = sum(m.cost_usd for m in messages)

    # Use pre-calculated totals from summary (includes subagents)
    # This ensures consistency with project listing page
    total_input = summary.total_input_tokens
    total_output = summary.total_output_tokens
    total_cost = summary.total_cost_usd

    # Show warning if there's a difference (subagents present)
    has_subagents = (total_cost != message_total_cost)

    template = env.get_template("session_detail.html")
    return template.render(
        session_slug=summary.slug,
        project_name=summary.project,
        encoded_path=encoded_path,
        session_id=session_id,
        messages=message_rows,
        message_count=len(messages),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_cache_read_tokens=total_cache_read,
        total_cache_creation_tokens=total_cache_creation,
        total_cost_usd=total_cost,
        has_subagents=has_subagents,
        message_total_cost=message_total_cost,
        models=", ".join(sorted(summary.models_used)) if summary.models_used else "unknown",
        error=None,
        back_url=f"/projects/{encoded_path}",
    )

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader

from app.config import get_data_dir
from app.data.loader import build_project_summaries

router = APIRouter()

# Template setup
templates_dir = Path(__file__).parent.parent / "templates"
env = Environment(loader=FileSystemLoader(templates_dir))


@router.get("/projects", response_class=HTMLResponse)
def projects_list():
    """Render list of all projects with summary statistics."""
    data_dir = get_data_dir()
    projects_dir = data_dir / "projects"

    if not projects_dir.exists():
        template = env.get_template("projects.html")
        return template.render(
            projects=None,
            error="No projects directory found. Please configure the data directory in settings.",
        )

    project_summaries = build_project_summaries()

    if not project_summaries:
        template = env.get_template("projects.html")
        return template.render(
            projects=[],
            error=None,
        )

    # Aggregate project-level statistics
    projects = []
    for encoded_path, sessions in project_summaries.items():
        if not sessions:
            continue

        # Calculate aggregates
        total_input = sum(s.total_input_tokens for s in sessions)
        total_output = sum(s.total_output_tokens for s in sessions)
        total_cost = sum(s.total_cost_usd for s in sessions)

        # Get display name from history or use encoded path
        display_name = None
        date_range = None
        for session in sessions:
            if session.project:
                display_name = session.project
                break

        if not display_name:
            display_name = f"/{encoded_path}"

        # Calculate date range
        if sessions:
            timestamps = [s.timestamp for s in sessions if s.timestamp]
            if timestamps:
                date_range = f"{sorted(timestamps)[0].split('T')[0]} to {sorted(timestamps)[-1].split('T')[0]}"

        projects.append(
            {
                "encoded_path": encoded_path,
                "display_name": display_name,
                "session_count": len(sessions),
                "total_input_tokens": total_input,
                "total_output_tokens": total_output,
                "total_cost_usd": total_cost,
                "date_range": date_range,
            }
        )

    # Sort by cost descending
    projects.sort(key=lambda p: p["total_cost_usd"], reverse=True)

    template = env.get_template("projects.html")
    return template.render(
        projects=projects,
        error=None,
    )


@router.get("/projects/{encoded_name}", response_class=HTMLResponse)
def project_detail(encoded_name: str):
    """Render detail view for a single project showing all sessions."""
    project_summaries = build_project_summaries()

    if encoded_name not in project_summaries:
        template = env.get_template("project_detail.html")
        return template.render(
            project_name=None,
            sessions=None,
            error=f"Project not found: {encoded_name}",
            back_url="/projects",
        )

    sessions = project_summaries[encoded_name]
    if not sessions:
        template = env.get_template("project_detail.html")
        return template.render(
            project_name=None,
            sessions=[],
            error=None,
            back_url="/projects",
        )

    # Get display name from first session's project field
    project_name = None
    for session in sessions:
        if session.project:
            project_name = session.project
            break
    if not project_name:
        project_name = f"/{encoded_name}"

    # Calculate project totals
    total_input = sum(s.total_input_tokens for s in sessions)
    total_output = sum(s.total_output_tokens for s in sessions)
    total_cost = sum(s.total_cost_usd for s in sessions)

    # Prepare session rows
    session_rows = []
    for session in sorted(sessions, key=lambda s: s.timestamp, reverse=True):
        session_rows.append(
            {
                "session_id": session.session_id,
                "slug": session.slug,
                "timestamp": session.timestamp,
                "date": session.timestamp.split("T")[0] if session.timestamp else "unknown",
                "message_count": session.message_count,
                "total_input_tokens": session.total_input_tokens,
                "total_output_tokens": session.total_output_tokens,
                "total_cost_usd": session.total_cost_usd,
                "models": ", ".join(sorted(session.models_used)) if session.models_used else "unknown",
            }
        )

    template = env.get_template("project_detail.html")
    return template.render(
        project_name=project_name,
        encoded_name=encoded_name,
        sessions=session_rows,
        total_sessions=len(sessions),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_cost_usd=total_cost,
        error=None,
        back_url="/projects",
    )

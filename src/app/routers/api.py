from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.data.loader import (
    build_hourly_activity,
    build_project_summaries,
    load_session_messages,
    load_stats_cache,
)
from app.data.pricing import estimate_cost, get_cached_pricing, get_pricing_info, refresh_pricing_cache

router = APIRouter(prefix="/api")


def filter_by_date_range(
    items, start_date: Optional[str], end_date: Optional[str], date_key: str = "date"
):
    """Helper function to filter data by date range."""
    if start_date:
        items = [item for item in items if getattr(item, date_key) >= start_date]
    if end_date:
        items = [item for item in items if getattr(item, date_key) <= end_date]
    return items


@router.get("/daily-activity")
def get_daily_activity(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return daily activity data for Chart.js (messages and sessions per day)."""
    overview_stats = load_stats_cache()
    if not overview_stats:
        raise HTTPException(status_code=404, detail="Stats cache not found")

    activities = filter_by_date_range(
        overview_stats.daily_activity, start_date, end_date
    )

    dates = [activity.date for activity in activities]
    messages = [activity.message_count for activity in activities]
    sessions = [activity.session_count for activity in activities]

    return {
        "labels": dates,
        "datasets": [
            {
                "label": "Messages",
                "data": messages,
                "borderColor": "rgba(139, 92, 246, 1)",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "yAxisID": "y",
                "fill": True,
            },
            {
                "label": "Sessions",
                "data": sessions,
                "borderColor": "rgba(59, 130, 246, 1)",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "yAxisID": "y1",
                "fill": True,
            },
        ],
    }


@router.get("/daily-cost")
def get_daily_cost(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return daily cost data by model for stacked area chart."""
    overview_stats = load_stats_cache()
    if not overview_stats:
        raise HTTPException(status_code=404, detail="Stats cache not found")

    daily_model_tokens = filter_by_date_range(
        overview_stats.daily_model_tokens, start_date, end_date
    )

    dates = [daily.date for daily in daily_model_tokens]

    # Get all unique models
    all_models = set()
    for daily in daily_model_tokens:
        all_models.update(daily.tokens_by_model.keys())
    all_models = sorted(list(all_models))

    # Model display names and colors
    display_names = {
        "claude-opus-4-6": "Opus 4.6",
        "claude-opus-4-5-20251101": "Opus 4.5",
        "claude-sonnet-4-5-20250929": "Sonnet 4.5",
        "claude-haiku-4-5-20251001": "Haiku 4.5",
    }

    colors = {
        "claude-opus-4-6": {"bg": "rgba(168, 85, 247, 0.5)", "border": "rgba(168, 85, 247, 1)"},
        "claude-opus-4-5-20251101": {"bg": "rgba(147, 51, 234, 0.5)", "border": "rgba(147, 51, 234, 1)"},
        "claude-sonnet-4-5-20250929": {"bg": "rgba(59, 130, 246, 0.5)", "border": "rgba(59, 130, 246, 1)"},
        "claude-haiku-4-5-20251001": {"bg": "rgba(16, 185, 129, 0.5)", "border": "rgba(16, 185, 129, 1)"},
    }

    # Build datasets for each model
    datasets = []
    for model_id in all_models:
        costs = []
        for daily in daily_model_tokens:
            tokens = daily.tokens_by_model.get(model_id, 0)
            # Estimate cost for just the input tokens from this model on this day
            # This is approximate since we don't have input/output breakdown per day
            cost = estimate_cost(model_id, input_tokens=tokens // 2, output_tokens=tokens // 2)
            costs.append(round(cost, 2))

        color_info = colors.get(model_id, {"bg": "rgba(100, 100, 100, 0.5)", "border": "rgba(100, 100, 100, 1)"})
        datasets.append(
            {
                "label": display_names.get(model_id, model_id),
                "data": costs,
                "borderColor": color_info["border"],
                "backgroundColor": color_info["bg"],
                "borderWidth": 2,
                "fill": True,
                "tension": 0.3,
            }
        )

    return {
        "labels": dates,
        "datasets": datasets,
    }


@router.get("/model-split")
def get_model_split():
    """Return cost distribution by model for doughnut chart."""
    overview_stats = load_stats_cache()
    if not overview_stats:
        raise HTTPException(status_code=404, detail="Stats cache not found")

    # Calculate cost per model
    model_costs = {}
    for model_id, stats in overview_stats.model_stats.items():
        cost = estimate_cost(
            model_id,
            input_tokens=stats.input_tokens,
            output_tokens=stats.output_tokens,
            cache_creation_input_tokens=stats.cache_creation_input_tokens,
            cache_read_input_tokens=stats.cache_read_input_tokens,
        )
        model_costs[model_id] = round(cost, 2)

    # Model display names
    display_names = {
        "claude-opus-4-6": "Opus 4.6",
        "claude-opus-4-5-20251101": "Opus 4.5",
        "claude-sonnet-4-5-20250929": "Sonnet 4.5",
        "claude-haiku-4-5-20251001": "Haiku 4.5",
    }

    colors = [
        "rgba(168, 85, 247, 0.8)",  # Opus purple
        "rgba(147, 51, 234, 0.8)",  # Opus dark purple
        "rgba(59, 130, 246, 0.8)",  # Sonnet blue
        "rgba(16, 185, 129, 0.8)",  # Haiku emerald
    ]

    labels = [display_names.get(model_id, model_id) for model_id in sorted(model_costs.keys())]
    data = [model_costs[model_id] for model_id in sorted(model_costs.keys())]

    return {
        "labels": labels,
        "datasets": [
            {
                "data": data,
                "backgroundColor": colors[: len(data)],
                "borderColor": [c.replace("0.8", "1") for c in colors[: len(data)]],
                "borderWidth": 2,
            }
        ],
    }


@router.get("/hourly-distribution")
def get_hourly_distribution(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return session start distribution by UTC hour for bar chart."""
    overview_stats = load_stats_cache()
    if not overview_stats:
        raise HTTPException(status_code=404, detail="Stats cache not found")

    # If date filtering is requested, we need to aggregate from session messages
    if start_date or end_date:
        project_summaries = build_project_summaries()
        hourly_counts = {str(i): 0 for i in range(24)}

        for encoded_path, sessions in project_summaries.items():
            for session in sessions:
                session_date = session.timestamp.split("T")[0]
                if start_date and session_date < start_date:
                    continue
                if end_date and session_date > end_date:
                    continue

                # Extract hour from session timestamp (ISO 8601)
                try:
                    hour = session.timestamp.split("T")[1].split(":")[0]
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                except (IndexError, AttributeError):
                    continue

        hours = [str(i) for i in range(24)]
        hour_counts = [hourly_counts.get(h, 0) for h in hours]
    else:
        # Use cached hour_counts
        hours = [str(i) for i in range(24)]
        hour_counts = [overview_stats.hour_counts.get(h, 0) for h in hours]

    return {
        "labels": [f"{h}:00 UTC" for h in hours],
        "datasets": [
            {
                "label": "Session Starts",
                "data": hour_counts,
                "backgroundColor": "rgba(99, 102, 241, 0.8)",
                "borderColor": "rgba(99, 102, 241, 1)",
                "borderWidth": 1,
            }
        ],
    }


@router.get("/project-cost")
def get_project_cost(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return cost per project for horizontal bar chart."""
    project_summaries = build_project_summaries()
    if not project_summaries:
        raise HTTPException(status_code=404, detail="Projects data not found")

    # Calculate cost per project
    project_costs = {}
    for encoded_path, sessions in project_summaries.items():
        # Filter sessions by date if specified
        filtered_sessions = sessions
        if start_date or end_date:
            filtered_sessions = [
                s for s in sessions
                if (not start_date or s.timestamp.split("T")[0] >= start_date)
                and (not end_date or s.timestamp.split("T")[0] <= end_date)
            ]

        total_cost = sum(s.total_cost_usd for s in filtered_sessions)
        # Use last part of path for display
        display_path = encoded_path.split("/")[-1] if "/" in encoded_path else encoded_path
        project_costs[display_path] = round(total_cost, 2)

    # Sort by cost descending
    sorted_projects = sorted(project_costs.items(), key=lambda x: x[1], reverse=True)
    labels = [project for project, _ in sorted_projects]
    costs = [cost for _, cost in sorted_projects]

    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Cost (USD)",
                "data": costs,
                "backgroundColor": "rgba(139, 92, 246, 0.8)",
                "borderColor": "rgba(139, 92, 246, 1)",
                "borderWidth": 1,
            }
        ],
    }


@router.get("/metadata")
def get_metadata():
    """
    Return metadata about available data:
    - Oldest and newest timestamps
    - Available projects
    """
    overview_stats = load_stats_cache()
    if not overview_stats:
        raise HTTPException(status_code=404, detail="Stats cache not found")

    # Find oldest/newest dates from daily activity
    dates = [activity.date for activity in overview_stats.daily_activity]
    oldest_date = min(dates) if dates else None
    newest_date = max(dates) if dates else None

    # Get project list
    project_summaries = build_project_summaries()
    projects = [
        {
            "encoded_path": encoded_path,
            "display_name": encoded_path.split("/")[-1],
            "session_count": len(sessions),
        }
        for encoded_path, sessions in project_summaries.items()
    ]

    return {
        "oldest_date": oldest_date,
        "newest_date": newest_date,
        "total_sessions": overview_stats.total_sessions,
        "total_messages": overview_stats.total_messages,
        "projects": sorted(projects, key=lambda p: p["session_count"], reverse=True),
    }


@router.get("/activity")
def get_activity(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project: Optional[str] = None,
):
    """
    Smart activity endpoint that automatically chooses hourly vs daily granularity.
    Returns hourly data if date range < 1 day, otherwise returns daily data.
    """
    # Determine granularity
    granularity = "daily"

    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            duration = (end - start).days

            if duration < 1:
                granularity = "hourly"
        except ValueError:
            pass

    if granularity == "hourly":
        # Build from session messages
        hourly_data = build_hourly_activity(
            start_date or "1970-01-01", end_date or "2099-12-31", project
        )

        return {
            "labels": [item["hour"] + ":00" for item in hourly_data],
            "datasets": [
                {
                    "label": "Messages",
                    "data": [item["message_count"] for item in hourly_data],
                    "borderColor": "rgba(139, 92, 246, 1)",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "yAxisID": "y",
                    "fill": True,
                    "tension": 0.3,
                    "borderWidth": 2,
                },
                {
                    "label": "Sessions",
                    "data": [item["session_count"] for item in hourly_data],
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "yAxisID": "y1",
                    "fill": True,
                    "tension": 0.3,
                    "borderWidth": 2,
                },
            ],
            "granularity": "hourly",
        }
    else:
        # Use daily aggregation
        overview_stats = load_stats_cache()
        if not overview_stats:
            raise HTTPException(status_code=404, detail="Stats cache not found")

        activities = filter_by_date_range(
            overview_stats.daily_activity, start_date, end_date
        )

        dates = [activity.date for activity in activities]
        messages = [activity.message_count for activity in activities]
        sessions = [activity.session_count for activity in activities]

        return {
            "labels": dates,
            "datasets": [
                {
                    "label": "Messages",
                    "data": messages,
                    "borderColor": "rgba(139, 92, 246, 1)",
                    "backgroundColor": "rgba(139, 92, 246, 0.1)",
                    "borderWidth": 2,
                    "tension": 0.3,
                    "yAxisID": "y",
                    "fill": True,
                },
                {
                    "label": "Sessions",
                    "data": sessions,
                    "borderColor": "rgba(59, 130, 246, 1)",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)",
                    "borderWidth": 2,
                    "tension": 0.3,
                    "yAxisID": "y1",
                    "fill": True,
                },
            ],
            "granularity": "daily",
        }


@router.get("/projects/{encoded_path}/activity")
def get_project_activity(
    encoded_path: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    """Activity chart data for a specific project."""
    project_summaries = build_project_summaries()

    if encoded_path not in project_summaries:
        raise HTTPException(status_code=404, detail="Project not found")

    sessions = project_summaries[encoded_path]

    # Filter by date range
    filtered_sessions = sessions
    if start_date or end_date:
        filtered_sessions = [
            s for s in sessions
            if (not start_date or s.timestamp.split("T")[0] >= start_date)
            and (not end_date or s.timestamp.split("T")[0] <= end_date)
        ]

    # Build daily aggregation
    daily_data = {}
    for session in filtered_sessions:
        date = session.timestamp.split("T")[0]
        if date not in daily_data:
            daily_data[date] = {"message_count": 0, "session_count": 0}
        daily_data[date]["message_count"] += session.message_count
        daily_data[date]["session_count"] += 1

    # Sort by date
    sorted_dates = sorted(daily_data.keys())
    dates = sorted_dates
    messages = [daily_data[d]["message_count"] for d in sorted_dates]
    sessions_count = [daily_data[d]["session_count"] for d in sorted_dates]

    return {
        "labels": dates,
        "datasets": [
            {
                "label": "Messages",
                "data": messages,
                "borderColor": "rgba(139, 92, 246, 1)",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "yAxisID": "y",
                "fill": True,
            },
            {
                "label": "Sessions",
                "data": sessions_count,
                "borderColor": "rgba(59, 130, 246, 1)",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "yAxisID": "y1",
                "fill": True,
            },
        ],
    }


@router.get("/projects/{encoded_path}/cost-breakdown")
def get_project_cost_breakdown(encoded_path: str):
    """Model cost breakdown for a specific project."""
    project_summaries = build_project_summaries()

    if encoded_path not in project_summaries:
        raise HTTPException(status_code=404, detail="Project not found")

    sessions = project_summaries[encoded_path]

    # Aggregate costs by model
    model_costs = defaultdict(float)
    for session in sessions:
        for model in session.models_used:
            messages = load_session_messages(encoded_path, session.session_id)
            for msg in messages:
                if msg.model == model:
                    model_costs[model] += msg.cost_usd

    # Format for doughnut chart
    display_names = {
        "claude-opus-4-6": "Opus 4.6",
        "claude-opus-4-5-20251101": "Opus 4.5",
        "claude-sonnet-4-5-20250929": "Sonnet 4.5",
        "claude-haiku-4-5-20251001": "Haiku 4.5",
    }

    colors = [
        "rgba(168, 85, 247, 0.8)",
        "rgba(147, 51, 234, 0.8)",
        "rgba(59, 130, 246, 0.8)",
        "rgba(16, 185, 129, 0.8)",
    ]

    labels = [display_names.get(m, m) for m in sorted(model_costs.keys())]
    data = [round(model_costs[m], 2) for m in sorted(model_costs.keys())]

    return {
        "labels": labels,
        "datasets": [
            {
                "data": data,
                "backgroundColor": colors[: len(data)],
                "borderColor": [c.replace("0.8", "1") for c in colors[: len(data)]],
                "borderWidth": 2,
            }
        ],
    }


@router.get("/token-usage-trend")
def get_token_usage_trend(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return daily token usage by type (input, output, cache read, cache write) for time series chart."""
    project_summaries = build_project_summaries()
    if not project_summaries:
        raise HTTPException(status_code=404, detail="Projects data not found")

    # Aggregate tokens by date and type
    daily_tokens = defaultdict(lambda: {
        "input": 0,
        "output": 0,
        "cache_read": 0,
        "cache_write": 0
    })

    for encoded_path, sessions in project_summaries.items():
        for session in sessions:
            session_date = session.timestamp.split("T")[0]

            # Filter by date range
            if start_date and session_date < start_date:
                continue
            if end_date and session_date > end_date:
                continue

            # Load messages to get detailed token breakdowns
            messages = load_session_messages(encoded_path, session.session_id)
            for msg in messages:
                msg_date = msg.timestamp.split("T")[0]
                daily_tokens[msg_date]["input"] += msg.input_tokens
                daily_tokens[msg_date]["output"] += msg.output_tokens
                daily_tokens[msg_date]["cache_read"] += msg.cache_read_input_tokens
                daily_tokens[msg_date]["cache_write"] += msg.cache_creation_input_tokens

    # Sort by date
    sorted_dates = sorted(daily_tokens.keys())

    # Prepare datasets
    input_tokens = [daily_tokens[d]["input"] for d in sorted_dates]
    output_tokens = [daily_tokens[d]["output"] for d in sorted_dates]
    cache_read_tokens = [daily_tokens[d]["cache_read"] for d in sorted_dates]
    cache_write_tokens = [daily_tokens[d]["cache_write"] for d in sorted_dates]

    return {
        "labels": sorted_dates,
        "datasets": [
            {
                "label": "Input Tokens",
                "data": input_tokens,
                "borderColor": "rgba(139, 92, 246, 1)",
                "backgroundColor": "rgba(139, 92, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "fill": False,
            },
            {
                "label": "Output Tokens",
                "data": output_tokens,
                "borderColor": "rgba(59, 130, 246, 1)",
                "backgroundColor": "rgba(59, 130, 246, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "fill": False,
            },
            {
                "label": "Cache Read Tokens",
                "data": cache_read_tokens,
                "borderColor": "rgba(16, 185, 129, 1)",
                "backgroundColor": "rgba(16, 185, 129, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "fill": False,
            },
            {
                "label": "Cache Write Tokens",
                "data": cache_write_tokens,
                "borderColor": "rgba(245, 158, 11, 1)",
                "backgroundColor": "rgba(245, 158, 11, 0.1)",
                "borderWidth": 2,
                "tension": 0.3,
                "fill": False,
            },
        ],
    }


@router.get("/pricing")
def get_pricing():
    """Return current pricing cache status (source, model count, timestamp)."""
    return get_pricing_info()


@router.post("/pricing/refresh")
def refresh_pricing():
    """Force-refresh the pricing cache. Returns changed=True if any prices differ."""
    old = dict(get_cached_pricing())
    refresh_pricing_cache()
    new = get_cached_pricing()
    info = get_pricing_info()
    info["changed"] = new != old
    return info

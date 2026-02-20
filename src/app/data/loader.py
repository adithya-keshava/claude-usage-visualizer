import json
import logging
from collections import defaultdict
from typing import Optional

from app.config import get_data_dir
from app.data.cache import get_cache
from app.data.models import (
    DailyActivity,
    DailyModelTokens,
    ModelStats,
    OverviewStats,
    SessionMessage,
    SessionSummary,
)
from app.data.pricing import estimate_cost

logger = logging.getLogger(__name__)


def load_stats_cache() -> OverviewStats | None:
    """
    Load and parse stats-cache.json.

    Returns OverviewStats or None if file missing/malformed.
    Uses cache with TTL + mtime invalidation.
    """
    cache = get_cache()
    cache_key = "stats_cache"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    stats_path = get_data_dir() / "stats-cache.json"
    if not stats_path.exists():
        logger.debug("stats-cache.json not found")
        return None

    try:
        with open(stats_path) as f:
            raw = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load stats-cache.json: {e}")
        return None

    try:
        # Parse daily activity
        daily_activity = [
            DailyActivity(
                date=d["date"],
                message_count=d.get("messageCount", 0),
                session_count=d.get("sessionCount", 0),
                tool_call_count=d.get("toolCallCount", 0),
            )
            for d in raw.get("dailyActivity", [])
        ]

        # Parse daily model tokens
        daily_model_tokens = [
            DailyModelTokens(
                date=d["date"],
                tokens_by_model=d.get("tokensByModel", {}),
            )
            for d in raw.get("dailyModelTokens", [])
        ]

        # Parse per-model stats
        model_stats = {}
        total_input_tokens = 0
        total_output_tokens = 0
        for model_id, usage in raw.get("modelUsage", {}).items():
            stats = ModelStats(
                model_id=model_id,
                input_tokens=usage.get("inputTokens", 0),
                output_tokens=usage.get("outputTokens", 0),
                cache_creation_input_tokens=usage.get("cacheCreationInputTokens", 0),
                cache_read_input_tokens=usage.get("cacheReadInputTokens", 0),
            )
            model_stats[model_id] = stats
            total_input_tokens += stats.input_tokens
            total_output_tokens += stats.output_tokens

        # Build overview stats
        overview = OverviewStats(
            total_sessions=raw.get("totalSessions", 0),
            total_messages=raw.get("totalMessages", 0),
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            first_session_date=raw.get("firstSessionDate"),
            last_computed_date=raw.get("lastComputedDate"),
            daily_activity=daily_activity,
            daily_model_tokens=daily_model_tokens,
            model_stats=model_stats,
            hour_counts={k: int(v) for k, v in raw.get("hourCounts", {}).items()},
        )

        cache.set(cache_key, overview, stats_path)
        return overview
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Failed to parse stats-cache.json: {e}")
        return None


def load_history() -> dict[str, dict]:
    """
    Load history.jsonl and return mapping sessionId -> {project, timestamp, display}.

    Handles /rename commands - uses renamed name if available.
    Returns empty dict if file missing/malformed.
    """
    cache = get_cache()
    cache_key = "history"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    history_path = get_data_dir() / "history.jsonl"
    if not history_path.exists():
        logger.debug("history.jsonl not found")
        return {}

    history = {}
    try:
        with open(history_path) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    session_id = entry.get("sessionId")
                    if session_id:
                        display = entry.get("display", "").strip()

                        # Check if this is a /rename command
                        if display.startswith("/rename"):
                            # Extract the renamed name (everything after /rename)
                            renamed = display[7:].strip()  # Remove "/rename"
                            if renamed:
                                # Update with the renamed value
                                if session_id in history:
                                    history[session_id]["display"] = renamed
                                    history[session_id]["renamed"] = True
                                else:
                                    history[session_id] = {
                                        "project": entry.get("project"),
                                        "timestamp": entry.get("timestamp"),
                                        "display": renamed,
                                        "renamed": True,
                                    }
                        else:
                            # Regular entry - only update if we haven't seen this session yet
                            if session_id not in history:
                                history[session_id] = {
                                    "project": entry.get("project"),
                                    "timestamp": entry.get("timestamp"),
                                    "display": display,
                                    "renamed": False,
                                }
                except json.JSONDecodeError as e:
                    logger.warning(f"history.jsonl line {line_num}: malformed JSON: {e}")
                    continue
    except IOError as e:
        logger.error(f"Failed to read history.jsonl: {e}")
        return {}

    cache.set(cache_key, history, history_path)
    return history


def _parse_message_usage(usage_dict: dict) -> dict:
    """Extract usage from assistant message (handles snake_case)."""
    return {
        "input_tokens": usage_dict.get("input_tokens", 0),
        "output_tokens": usage_dict.get("output_tokens", 0),
        "cache_creation_input_tokens": usage_dict.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": usage_dict.get("cache_read_input_tokens", 0),
    }


def load_session_messages(
    encoded_path: str, session_id: str
) -> list[SessionMessage]:
    """
    Load all assistant messages from a session JSONL.

    Returns list of SessionMessage or empty list if file missing/malformed.
    Handles snake_case field names.
    Skips synthetic models and sidechain messages.
    """
    cache = get_cache()
    cache_key = f"session_{encoded_path}_{session_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    session_path = get_data_dir() / "projects" / encoded_path / f"{session_id}.jsonl"
    if not session_path.exists():
        logger.debug(f"Session {session_id} not found at {session_path}")
        return []

    messages = []
    try:
        with open(session_path) as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                    # Skip non-assistant messages
                    if msg.get("type") != "assistant":
                        continue
                    # Skip synthetic models
                    if msg.get("message", {}).get("model") == "<synthetic>":
                        continue
                    # Skip sidechain (abandoned branches)
                    if msg.get("isSidechain"):
                        continue

                    # Usage is nested inside message object
                    usage = msg.get("message", {}).get("usage")
                    if not usage:
                        continue

                    parsed_usage = _parse_message_usage(usage)
                    model = msg.get("message", {}).get("model", "unknown")
                    cost = estimate_cost(model, **parsed_usage)

                    messages.append(
                        SessionMessage(
                            timestamp=msg.get("timestamp", ""),
                            model=model,
                            input_tokens=parsed_usage["input_tokens"],
                            output_tokens=parsed_usage["output_tokens"],
                            cache_creation_input_tokens=parsed_usage[
                                "cache_creation_input_tokens"
                            ],
                            cache_read_input_tokens=parsed_usage[
                                "cache_read_input_tokens"
                            ],
                            cost_usd=cost,
                        )
                    )
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Session {session_id} line {line_num}: malformed JSON: {e}"
                    )
                    continue
    except IOError as e:
        logger.error(f"Failed to read session {session_id}: {e}")
        return []

    cache.set(cache_key, messages, session_path)
    return messages


def build_session_summary(
    encoded_path: str, session_id: str, history: dict
) -> SessionSummary | None:
    """
    Build a summary of a single session from its JSONL + subagents.

    Merges subagent tokens into parent. Skips sidechains.
    """
    messages = load_session_messages(encoded_path, session_id)
    if not messages:
        return None

    # Compute totals
    total_input = sum(m.input_tokens for m in messages)
    total_output = sum(m.output_tokens for m in messages)
    total_cost = sum(m.cost_usd for m in messages)
    models_used = {m.model for m in messages}

    # Get first message for timestamp and slug
    first_msg_timestamp = messages[0].timestamp if messages else ""

    # Get session slug and project
    session_path = get_data_dir() / "projects" / encoded_path / f"{session_id}.jsonl"
    project = history.get(session_id, {}).get("project", f"/{encoded_path}")

    # Try to use display name from history first (user-friendly), then slug, then session ID
    hist_entry = history.get(session_id, {})
    slug = hist_entry.get("display", "").strip()

    # If renamed, use the renamed name directly (it's already clean)
    if hist_entry.get("renamed"):
        if slug:
            slug = slug[:100]  # Allow slightly longer names for renames
    elif slug:
        # Clean up the display text - truncate and remove newlines
        slug = slug.replace("\n", " ").strip()
        # Skip slash commands and other meta commands - they're not meaningful session names
        if slug.startswith("/") or slug.startswith("!") or slug in ("yes", "Sure", "go ahead"):
            slug = ""
        else:
            slug = slug[:80]  # Truncate to reasonable length

    if not slug:
        # Fall back to slug from JSONL file
        try:
            with open(session_path) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if "slug" in data:
                            slug = data["slug"]
                            break
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass

    # Final fallback: use first 8 chars of session ID
    if not slug:
        slug = session_id[:8]
    # Merge subagent tokens
    subagent_dir = session_path.parent / session_id / "subagents"
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
                            # Usage is nested inside message object
                            usage = msg.get("message", {}).get("usage")
                            if not usage:
                                continue
                            parsed_usage = _parse_message_usage(usage)
                            model = msg.get("message", {}).get("model", "unknown")
                            cost = estimate_cost(model, **parsed_usage)
                            total_input += parsed_usage["input_tokens"]
                            total_output += parsed_usage["output_tokens"]
                            total_cost += cost
                            models_used.add(model)
                        except json.JSONDecodeError:
                            continue
            except IOError as e:
                logger.warning(f"Failed to read subagent file {agent_file}: {e}")

    return SessionSummary(
        session_id=session_id,
        slug=slug,
        project=project,
        timestamp=first_msg_timestamp,
        message_count=len(messages),
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_cost_usd=total_cost,
        models_used=models_used,
    )


def build_project_summaries() -> dict[str, list[SessionSummary]]:
    """
    Build summaries for all projects and sessions.

    Returns: {encoded_path: [SessionSummary, ...], ...}
    """
    cache = get_cache()
    cache_key = "project_summaries"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    projects_dir = get_data_dir() / "projects"
    if not projects_dir.exists():
        return {}

    history = load_history()
    projects = {}

    for encoded_dir in projects_dir.iterdir():
        if not encoded_dir.is_dir():
            continue

        sessions = []
        # Look for {sessionId}.jsonl files directly in this project dir
        for jsonl_file in encoded_dir.glob("*.jsonl"):
            session_id = jsonl_file.stem
            summary = build_session_summary(encoded_dir.name, session_id, history)
            if summary:
                sessions.append(summary)

        if sessions:
            projects[encoded_dir.name] = sessions

    cache.set(cache_key, projects)
    return projects


def build_hourly_activity(
    start_date: str, end_date: str, project: Optional[str] = None
) -> list[dict]:
    """
    Build hourly aggregation from individual session messages.
    Only called when date range is < 1 day.

    Returns list of dicts with: {hour, message_count, session_count}
    """
    project_summaries = build_project_summaries()
    hourly_data = defaultdict(lambda: {"messages": 0, "sessions": set(), "cost": 0.0})

    # Filter projects if specified
    projects_to_process = (
        {project: project_summaries[project]} if project and project in project_summaries
        else project_summaries
    )

    for encoded_path, sessions in projects_to_process.items():
        for session in sessions:
            session_date = session.timestamp.split("T")[0]

            # Skip sessions outside date range
            if session_date < start_date or session_date > end_date:
                continue

            messages = load_session_messages(encoded_path, session.session_id)
            for msg in messages:
                # Extract hour: "2026-02-15T14:30:45Z" -> "2026-02-15T14"
                hour_key = msg.timestamp[:13]
                hourly_data[hour_key]["messages"] += 1
                hourly_data[hour_key]["sessions"].add(session.session_id)
                hourly_data[hour_key]["cost"] += msg.cost_usd

    # Convert to sorted list
    result = []
    for hour_key in sorted(hourly_data.keys()):
        data = hourly_data[hour_key]
        result.append(
            {
                "hour": hour_key,
                "message_count": data["messages"],
                "session_count": len(data["sessions"]),
                "total_cost": round(data["cost"], 2),
            }
        )

    return result

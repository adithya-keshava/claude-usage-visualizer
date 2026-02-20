from dataclasses import dataclass


@dataclass
class TokenUsage:
    """Token counts for a single message or session."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass
class ModelStats:
    """Aggregated stats for a single model (from stats-cache)."""
    model_id: str
    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int = 0
    cache_creation_input_tokens: int = 0


@dataclass
class DailyActivity:
    """Daily activity from stats-cache."""
    date: str
    message_count: int
    session_count: int
    tool_call_count: int


@dataclass
class DailyModelTokens:
    """Daily token totals by model (combined input+output)."""
    date: str
    tokens_by_model: dict[str, int]  # model_id -> total tokens


@dataclass
class OverviewStats:
    """Aggregated overview data for the dashboard."""
    total_sessions: int
    total_messages: int
    total_input_tokens: int
    total_output_tokens: int
    first_session_date: str | None
    last_computed_date: str | None
    daily_activity: list[DailyActivity]
    daily_model_tokens: list[DailyModelTokens]
    model_stats: dict[str, ModelStats]  # model_id -> ModelStats
    hour_counts: dict[str, int]


@dataclass
class SessionMessage:
    """A single assistant message from a session JSONL."""
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    cost_usd: float


@dataclass
class SessionSummary:
    """Summary of a single session."""
    session_id: str
    slug: str
    project: str  # original path from history.jsonl
    timestamp: str
    message_count: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float
    models_used: set[str]


@dataclass
class ProjectSummary:
    """Summary of a project (directory containing multiple sessions)."""
    encoded_path: str
    display_path: str
    session_count: int
    total_input_tokens: int
    total_output_tokens: int
    total_cost_usd: float

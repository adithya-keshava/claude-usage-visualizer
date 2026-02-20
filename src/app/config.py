import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_data_dir: Path | None = None


def get_data_dir() -> Path:
    global _data_dir
    if _data_dir is not None:
        return _data_dir
    env_val = os.getenv("CLAUDE_DATA_DIR")
    if env_val:
        _data_dir = Path(env_val).expanduser().resolve()
    else:
        _data_dir = Path.home() / ".claude"
    return _data_dir


def set_data_dir(path: str) -> Path:
    global _data_dir
    _data_dir = Path(path).expanduser().resolve()
    # Also set env var for consistency
    os.environ["CLAUDE_DATA_DIR"] = str(_data_dir)
    return _data_dir


def has_stats_cache() -> bool:
    return (get_data_dir() / "stats-cache.json").is_file()


def has_projects() -> bool:
    return (get_data_dir() / "projects").is_dir()

# Configuration & Environment Handling

## Overview

The application uses environment variables and a global configuration module to manage the data directory location. Configuration is loaded at startup via `python-dotenv` and cached globally for performance.

**File References:**
- Configuration module: `src/app/config.py`
- Environment setup: `src/app/config.py:4-6`

## Data Directory Resolution

### Get Data Directory

The `get_data_dir()` function at `src/app/config.py:11-20` implements a resolution hierarchy:

```python
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
```

**Resolution order:**

1. **Cached value:** If `_data_dir` is already set, return it (fast path)
   - Used after first call or after explicit `set_data_dir()`

2. **Environment variable:** Check `CLAUDE_DATA_DIR` env var
   - Allows custom data location
   - Supports `~` expansion for home directory
   - Resolution to absolute path for consistency

3. **Default:** `~/.claude/`
   - Standard location for Claude Code data

### Set Data Directory

The `set_data_dir()` function at `src/app/config.py:23-28` allows runtime configuration:

```python
def set_data_dir(path: str) -> Path:
    global _data_dir
    _data_dir = Path(path).expanduser().resolve()
    os.environ["CLAUDE_DATA_DIR"] = str(_data_dir)
    return _data_dir
```

**Behavior:**
- Accepts user-provided path string
- Expands `~` to home directory
- Resolves to absolute path
- Updates both global `_data_dir` cache and `os.environ` for consistency
- Returns resolved Path object
- Called by settings router (see `src/app/routers/settings.py`)

## Data Directory Validation

### Existence Checks

Two boolean checks are provided:

**Has stats-cache.json** (`src/app/config.py:31-32`):
```python
def has_stats_cache() -> bool:
    return (get_data_dir() / "stats-cache.json").is_file()
```

- Returns True if `{data_dir}/stats-cache.json` exists
- Used by health check endpoint and overview router
- Signals whether aggregated statistics are available

**Has projects directory** (`src/app/config.py:35-36`):
```python
def has_projects() -> bool:
    return (get_data_dir() / "projects").is_dir()
```

- Returns True if `{data_dir}/projects/` is a directory
- Used by health check endpoint and projects router
- Signals whether session data is available

## Environment Variable Loading

The `.env` file is loaded at module import time via `src/app/config.py:4-6`:

```python
from dotenv import load_dotenv

load_dotenv()
```

**Loading behavior:**
- Automatically loads `.env` file from current working directory
- Variables can be set before application starts
- Used for `CLAUDE_DATA_DIR` and any other app configuration

**Example .env:**
```
CLAUDE_DATA_DIR=~/IdeaProjects/my-project/claude-data
```

## Global Cache Implementation

The configuration uses a module-level global variable at `src/app/config.py:8`:

```python
_data_dir: Path | None = None
```

**Purpose:**
- Cache the resolved data directory across multiple requests
- Avoid repeated path resolution and validation
- Improve performance for high-request scenarios

**Thread safety note:**
- Global variable is written once per application lifetime
- Python GIL ensures safe reads in subsequent requests
- Not suitable for multi-threaded scenarios with frequent `set_data_dir()` calls

## Data Directory Structure

The application expects the following structure inside the data directory:

```
~/.claude/
├── stats-cache.json        # Aggregated statistics (JSON)
├── history.jsonl           # Session metadata (JSONL)
└── projects/
    └── {encoded_path}/
        ├── {session_id}.jsonl
        ├── {session_id}.jsonl
        └── {session_id}/
            └── subagents/
                ├── agent-*.jsonl
                └── ...
```

**Components:**

| File/Dir | Format | Purpose | Reference |
|----------|--------|---------|-----------|
| `stats-cache.json` | JSON | Pre-aggregated overview statistics | `src/app/data/loader.py:21-101` |
| `history.jsonl` | JSONL | Session metadata with display names | `src/app/data/loader.py:104-167` |
| `projects/{encoded_path}/{session_id}.jsonl` | JSONL | Individual session messages and usage | `src/app/data/loader.py:180-253` |
| `projects/{encoded_path}/{session_id}/subagents/agent-*.jsonl` | JSONL | Subagent messages (merged into parent) | `src/app/data/loader.py:317-345` |

## Configuration Usage Patterns

### In Routers

Each router imports and uses the configuration:

**Example: Overview router** (`src/app/routers/overview.py:7`):
```python
from app.config import get_data_dir
```

Used at `src/app/routers/overview.py:94`:
```python
return template.render(
    ...
    data_dir=str(get_data_dir()),
    ...
)
```

**Example: Health check** (`src/app/main.py:25`):
```python
data_dir = get_data_dir()
```

Used to return current configuration status.

### In Data Loaders

Data loaders use configuration to build file paths:

**Example: Load stats cache** (`src/app/data/loader.py:34`):
```python
stats_path = get_data_dir() / "stats-cache.json"
```

**Example: Load session messages** (`src/app/data/loader.py:196`):
```python
session_path = get_data_dir() / "projects" / encoded_path / f"{session_id}.jsonl"
```

## Error Scenarios

### Missing Data Directory

If `get_data_dir()` returns a non-existent path:
- `has_stats_cache()` returns False
- `has_projects()` returns False
- Overview router renders error message: "No stats-cache.json found"
- Projects router renders error message: "No projects directory found"
- API endpoints return 404 HTTPException

**User action:** Configure data directory via settings page

### Missing Files within Data Directory

If stats-cache.json or projects/ exist but are empty:
- `load_stats_cache()` returns None (see `src/app/data/loader.py:35-37`)
- `build_project_summaries()` returns empty dict (see `src/app/data/loader.py:373-374`)
- UI renders empty state with appropriate messages

### Permission Errors

If data files exist but are not readable:
- File I/O raises IOError/PermissionError
- Caught in try-except blocks in loaders
- Logged with error message
- Function returns None or empty result
- UI renders with error message

**Example:** `src/app/data/loader.py:162-164`
```python
except IOError as e:
    logger.error(f"Failed to read history.jsonl: {e}")
    return {}
```

## Configuration Testing

To test with custom data directory:

```bash
# Set environment variable
export CLAUDE_DATA_DIR=/path/to/test/data

# Or create .env file
echo "CLAUDE_DATA_DIR=/path/to/test/data" > .env

# Run application
python -m uvicorn app.main:app
```

The application will automatically load from the specified directory.

## Future Enhancement: Settings Router

The settings router (imported at `src/app/main.py:20`) will likely provide:

1. **GET /settings** - Render settings page with current configuration
2. **POST /settings** - Update data directory via form submission
3. **GET /api/settings** - JSON endpoint for current settings

Expected to use `set_data_dir()` to update configuration at runtime.
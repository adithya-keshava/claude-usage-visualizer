# Claude Usage Visualizer - Repository Skill

Comprehensive domain knowledge and implementation patterns for the Claude Usage Visualizer FastAPI application.

**Project Type:** Python FastAPI Web Application
**Entry Point:** `src/app/main.py`
**Data Format:** JSON/JSONL parsing from `~/.claude/`
**Frontend:** Jinja2 templates + JavaScript + Chart.js + HTMX
**Status:** 🔄 Under extraction (Phase 1-2 of BUILD_CHECKLIST.md)

---

## Quick Navigation

- **[Architecture Overview](#architecture-overview)** - System design and component structure
- **[Data Layer](#data-layer)** - How data is loaded and cached
- **[API Layer](#api-layer)** - HTTP endpoints and response formats
- **[Frontend Layer](#frontend-layer)** - Templates, JavaScript, styling
- **[Configuration & Environment](#configuration--environment)** - Settings and environment setup
- **[Common Patterns](#common-patterns)** - Reusable code patterns
- **[Development Guide](#development-guide)** - How to add features

---

## Architecture Overview

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                    │
│  (src/app/main.py)                                          │
└────────────────┬────────────────────────────────────────────┘
                 │
         ┌───────┴────────┬──────────┬──────────┐
         ▼                ▼          ▼          ▼
    ┌─────────────┬──────────────┬─────────┬─────────────┐
    │  Routers    │   Config     │ Data    │  Templates  │
    │             │              │ Layer   │  & Static   │
    └─────────────┴──────────────┴─────────┴─────────────┘
         │                │          │          │
         ▼                ▼          ▼          ▼
    ┌──────────────────────────────────────────────────────┐
    │  Routes                                               │
    │  - /              (overview dashboard)                │
    │  - /projects      (project listing)                   │
    │  - /projects/{id} (project details)                   │
    │  - /sessions/...  (session details)                   │
    │  - /settings      (configuration)                     │
    │  - /api/*         (JSON endpoints for charts)         │
    └───┬──────────────────────────────────────────────────┘
        │
        ▼
    ┌──────────────────────────────────────────────────────┐
    │  Data Sources                                         │
    │  - ~/.claude/stats-cache.json    (aggregated totals)  │
    │  - ~/.claude/history.jsonl       (message index)      │
    │  - ~/.claude/projects/*/...      (session details)    │
    └──────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **Application Factory** | `src/app/main.py` | Initialize FastAPI, register routers, mount static files |
| **Configuration** | `src/app/config.py` | Paths, constants, model pricing |
| **Data Loading** | `src/app/data/loader.py` | Parse JSON/JSONL files from ~/.claude/ |
| **Data Models** | `src/app/data/models.py` | Pydantic models for type safety |
| **Pricing Logic** | `src/app/data/pricing.py` | Calculate costs from token counts |
| **Caching** | `src/app/data/cache.py` | In-memory cache with TTL |
| **API Routes** | `src/app/routers/api.py` | JSON endpoints for Chart.js data |
| **Web Routes** | `src/app/routers/overview.py`, etc. | HTML page routes |
| **Templates** | `src/app/templates/` | Jinja2 templates for pages |
| **Static Files** | `src/app/static/` | CSS, JavaScript modules |

---

## Data Layer

### Data Loading Pipeline

**File:** `src/app/data/loader.py`

**Process:**
1. Read `~/.claude/stats-cache.json` for aggregated totals
2. Read `~/.claude/history.jsonl` for session index
3. For each project, read `~/.claude/projects/{encoded}/{sessionId}.jsonl`
4. Optionally merge subagent data from `subagents/agent-*.jsonl`
5. Aggregate and cache results

**Data Flow:**
```
~/.claude/stats-cache.json
        ↓
    Totals (cached)
        ↓
history.jsonl → Project mapping → Session listings
        ↓
projects/{encoded}/*.jsonl → Detailed token counts
        ↓
[Cache] → API → Chart.js
```

### Cache Strategy

**File:** `src/app/data/cache.py`

- **Type:** In-memory dictionary with TTL
- **TTL:** 5 minutes (configurable)
- **Invalidation:** Mtime check on data files
- **Keys:** `(entity_type, entity_id, filters)`

**Example:**
```python
# Cache invalidates when file mtime changes
cache.get("projects")  # Hits cache if TTL valid
cache.get("sessions", project_id="ada")  # Scoped queries
```

### Data Models

**File:** `src/app/data/models.py`

Key Pydantic models:
- `TokenUsage` - Input, output, cache write/read tokens
- `SessionSummary` - Aggregated usage per session
- `ProjectSummary` - Aggregated usage per project
- `MessageDetail` - Individual message with full breakdown

---

## API Layer

### Chart Data Endpoints

**File:** `src/app/routers/api.py`

All endpoints return Chart.js-compatible JSON format:

```json
{
  "labels": ["Jan", "Feb", "Mar"],
  "datasets": [
    {
      "label": "Input Tokens",
      "data": [100, 200, 150],
      "backgroundColor": "rgba(99, 102, 241, 0.1)",
      "borderColor": "rgb(99, 102, 241)"
    }
  ]
}
```

#### Endpoint Reference

| Endpoint | Purpose | Data Grouping |
|----------|---------|---------------|
| `GET /api/overview` | Aggregated usage over time | By day (default) |
| `GET /api/projects-cost` | Cost breakdown by project | Per project |
| `GET /api/models-usage` | Token usage by model | Per model |
| `GET /api/activity?project=X` | Activity timeline | By hour/day |
| `GET /api/sessions-timeline` | Session distribution | By date |

**Query Parameters:**
- `?start_date=YYYY-MM-DD` - Filter from date
- `?end_date=YYYY-MM-DD` - Filter to date
- `?project=<project-name>` - Filter by project
- `?group_by=hourly|daily` - Aggregation level

### Error Handling

Returns standard JSON error responses:
```json
{
  "error": "Not found",
  "detail": "Project 'xyz' not found",
  "status": 404
}
```

---

## Frontend Layer

### Template Structure

**Base Template:** `src/app/templates/base.html`

```html
<!DOCTYPE html>
<html>
  <head>
    <!-- Theme, timezone, charts, HTMX CDN -->
  </head>
  <body>
    <nav><!-- Navigation --></nav>
    <div id="content">
      {% block content %}{% endblock %}
    </div>
    <script>
      <!-- theme.js, timezone.js, charts.js -->
    </script>
  </body>
</html>
```

**Page Templates:**
- `overview.html` - Dashboard with stat cards and charts
- `projects.html` - Project listing with drill-down
- `project_detail.html` - Project-specific analytics
- `session_detail.html` - Message-level detail
- `settings.html` - Configuration page

### JavaScript Modules

**Theme Toggle:** `src/app/static/theme.js`
- Light/dark mode switching
- localStorage persistence
- Chart.js color helper

**Timezone Toggle:** `src/app/static/timezone.js`
- 4-mode cycling (UTC, Local, UTC 12h, Local 12h)
- Timestamp conversion
- Format persistence

**Chart Initialization:** `src/app/static/charts.js`
- Chart.js integration
- Theme-aware colors
- Responsive configuration

**HTMX Config:** `src/app/static/htmx-config.js`
- Loading indicators
- Request/response interception
- Error handling

### CSS Structure

**File:** `src/app/static/style.css`

Features:
- Dual-theme system (light/dark)
- CSS custom properties for colors
- Responsive grid layout
- Chart container styling

---

## Configuration & Environment

### Environment Variables

**File:** `src/app/config.py`

```python
import os
from pathlib import Path

# Primary config
CLAUDE_DATA_DIR = os.getenv("CLAUDE_DATA_DIR", "~/.claude")
DATA_DIR = Path(CLAUDE_DATA_DIR).expanduser().resolve()
```

**Usage:**
```bash
# Use default (~/.claude)
python src/app/main.py

# Use custom location
export CLAUDE_DATA_DIR=~/my-claude-data
python src/app/main.py
```

### Constants & Pricing

**Token Costs (from claude-3 pricing):**
```python
MODEL_COSTS = {
    "claude-3-opus": {
        "input": 15.0 / 1_000_000,      # $15 per 1M
        "output": 75.0 / 1_000_000,     # $75 per 1M
    },
    "claude-3-sonnet": {
        "input": 3.0 / 1_000_000,       # $3 per 1M
        "output": 15.0 / 1_000_000,     # $15 per 1M
    },
    # ... more models
}
```

**Cache Token Costs:**
- Write: 25% of input token cost
- Read: 10% of input token cost

---

## Common Patterns

### Adding a New API Endpoint

**Step 1:** Create function in `src/app/routers/api.py`
```python
@router.get("/api/my-data")
async def get_my_data(project: str = None):
    """Return chart-formatted data."""
    data = loader.get_data(project=project)
    return {
        "labels": [d.date for d in data],
        "datasets": [...]
    }
```

**Step 2:** Add canvas in template
```html
<div id="myChart">
  <canvas id="myChartCanvas"></canvas>
</div>
```

**Step 3:** Initialize in `charts.js`
```javascript
const ctx = document.getElementById('myChartCanvas');
fetch('/api/my-data')
  .then(r => r.json())
  .then(data => {
    new Chart(ctx, {
      type: 'line',
      data: data,
      options: { responsive: true }
    });
  });
```

### Adding a New Page Route

**Step 1:** Create router function
```python
# src/app/routers/my_feature.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/my-page", response_class=HTMLResponse)
async def my_page():
    return templates.TemplateResponse("my_page.html", {})
```

**Step 2:** Register in `main.py`
```python
from .routers import my_feature
app.include_router(my_feature.router)
```

**Step 3:** Create template
```html
<!-- src/app/templates/my_page.html -->
{% extends "base.html" %}
{% block content %}
  <!-- Your content -->
{% endblock %}
```

### Using HTMX for Dynamic Content

**Example:** Pagination with HTMX
```html
<div hx-get="/sessions?page=2" hx-trigger="click" hx-target="this">
  Load more
</div>
```

**Backend:**
```python
@router.get("/sessions")
async def get_sessions(page: int = 1):
    # Return partial HTML (not full page)
    return templates.TemplateResponse("partials/session_table.html", ...)
```

---

## Development Guide

### Local Development Setup

```bash
# Clone and enter directory
cd /path/to/claude-usage-visualizer

# Install with uv
uv sync --python 3.11

# Run application
uv run --python 3.11 src/main.py

# Visit http://localhost:8000/
```

### Adding a Feature

1. **Plan:** Create a new router function in appropriate file
2. **Backend:** Implement API endpoint or page route
3. **Template:** Create or modify template in `templates/`
4. **Frontend:** Add JavaScript/CSS as needed in `static/`
5. **Test:** Verify in browser, check console for errors
6. **Commit:** Push to repository with clear commit message

### Testing

```bash
# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_pricing.py::test_cost_calculation

# Linting
uv run pylint src/
```

### Debugging

**Python (Backend):**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

**JavaScript (Frontend):**
```javascript
console.log("Debug info");
console.table(data);
```

**Browser DevTools:**
- F12 → Console tab for errors
- Network tab to inspect API calls
- Storage tab to check localStorage

---

## Code Examples

### Example: Cost Calculation

**File:** `src/app/data/pricing.py`

```python
def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    cache_write: int = 0,
    cache_read: int = 0
) -> float:
    """Calculate USD cost for token usage."""
    rates = MODEL_COSTS[model]

    # Base cost
    cost = (
        input_tokens * rates["input"] +
        output_tokens * rates["output"]
    )

    # Cache costs
    cost += cache_write * rates["input"] * 0.25
    cost += cache_read * rates["input"] * 0.10

    return cost
```

### Example: Data Loading

**File:** `src/app/data/loader.py`

```python
def load_projects() -> List[ProjectSummary]:
    """Load all projects from ~/.claude/"""
    data_dir = config.DATA_DIR
    projects_dir = data_dir / "projects"

    projects = []
    for project_dir in projects_dir.iterdir():
        project_name = decode_path(project_dir.name)
        usage = aggregate_sessions(project_dir)
        projects.append(ProjectSummary(
            name=project_name,
            usage=usage
        ))

    return projects
```

---

## Phase Status

| Phase | Status | Tasks | Progress |
|-------|--------|-------|----------|
| 1: Architecture | 🔄 Extracting | 4 | In Progress |
| 2: Technical Patterns | ⏳ Pending | 4 | Not Started |
| 3: Skills & Integration | ⏳ Pending | 4 | Not Started |
| 4: Validation | ⏳ Pending | 5 | Not Started |

**To continue:** Run `/agent-ready:resume` in the project directory.

---

## Links & References

- **Project Documentation:** See `docs/` directory
- **Build Checklist:** `BUILD_CHECKLIST.md`
- **Skills Index:** Root `AGENTS.md`
- **Security Audit:** `SECURITY_VALIDATION.md`

---

**Last Updated:** 2026-02-20
**Maintained By:** Agent-readiness extraction pipeline

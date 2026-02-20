# Claude Usage Visualizer - Repository Skill

Comprehensive domain knowledge and implementation patterns for the Claude Usage Visualizer FastAPI application. This skill enables agents to confidently extend and maintain this codebase.

**Project Type:** Python FastAPI Web Application
**Entry Point:** `src/app/main.py` (line 9)
**Data Format:** JSON/JSONL parsing from `~/.claude/`
**Frontend:** Jinja2 templates + JavaScript + Chart.js + HTMX
**Status:** Agent-ready (Phase 3 complete)

---

## Quick Navigation

### Documentation Index
- **[Project Overview](#project-overview)** - What this application does
- **[Architecture Overview](#architecture-overview)** - System design and component structure
- **[Module Documentation](#module-documentation)** - Detailed references to all extracted knowledge
- **[Common Tasks](#common-tasks)** - Step-by-step guides for extending functionality
- **[Key Patterns](#key-patterns)** - Reusable architectural patterns
- **[Data Layer](#data-layer)** - How data is loaded and cached
- **[API Layer](#api-layer)** - HTTP endpoints and response formats
- **[Frontend Layer](#frontend-layer)** - Templates, JavaScript, styling
- **[Configuration & Environment](#configuration--environment)** - Settings and environment setup
- **[Critical Files Reference](#critical-files-reference)** - Quick lookup of key source files

### For Agent Implementation
1. **First time?** Start with [Project Overview](#project-overview)
2. **Extending functionality?** See [Common Tasks](#common-tasks)
3. **Need technical details?** See [Module Documentation](#module-documentation)
4. **Building charts or pages?** See [Frontend Layer](#frontend-layer)
5. **Adding data features?** See [Data Layer](#data-layer)

---

## Project Overview

### What This Application Does

**Claude Usage Visualizer** is a FastAPI web dashboard that tracks and visualizes Claude API token usage and costs over time. It processes JSON/JSONL data from `~/.claude/` directory and presents interactive charts showing:

- **Overall token and cost trends** - Daily/hourly aggregates across all projects
- **Per-model breakdown** - Usage distribution by Claude model (Opus, Sonnet, Haiku)
- **Per-project analytics** - Which projects consume the most tokens
- **Session details** - Message-level token breakdown for debugging
- **Cost estimation** - USD cost calculation with real-time pricing from Anthropic API

### Target Users

Agents building on this codebase should understand:
- Claude API cost tracking and billing
- FastAPI web application patterns
- Data aggregation and caching strategies
- Frontend state management (theme, timezone, filters)
- Token cost calculations across 4 token types (input, output, cache_write, cache_read)

### Technology Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11+, FastAPI, Pydantic |
| **Frontend** | Jinja2 templates, JavaScript (vanilla), Chart.js 4.4+, HTMX |
| **Data** | JSON/JSONL parsing from `~/.claude/` |
| **Styling** | CSS with CSS custom properties (dual theme) |
| **External APIs** | Anthropic API (/models endpoint for pricing) |

### Key Entry Points for Agents

1. **Main Application:** `src/app/main.py:9` - FastAPI app initialization with 5 routers
2. **Data Loading:** `src/app/data/loader.py:40-120` - Main loading logic with caching
3. **API Endpoints:** `src/app/routers/api.py:29-68` - Chart data endpoints
4. **Templates:** `src/app/templates/base.html` - Master template with blocks
5. **Static Files:** `src/app/static/` - CSS theme system and JS modules

---

## Module Documentation

All extracted domain knowledge is organized in the `.agents/skills/repo-skill/modules/` directory. This section provides a quick index to detailed technical documentation.

### Domain Knowledge (modules/domain/)

These documents explain WHAT the application does and WHY decisions were made:

- **Architecture** - How the application is structured
  - `architecture/routing.md` - FastAPI router registration, URL patterns, request flow
  - `architecture/config.md` - Configuration management, data directory resolution, environment variables

- **Data Layer** - How data flows through the system
  - `data/models.md` - All 8 Pydantic models (TokenUsage, SessionMessage, SessionSummary, etc.)
  - `data/loading.md` - JSON/JSONL parsing, file loading patterns, aggregation logic
  - `data/pricing.md` - Cost calculation formulas, Anthropic API integration, fallback pricing

- **Frontend Layer** - User interface and interaction
  - `frontend/templates.md` - Jinja2 template structure, inheritance, page components
  - `frontend/javascript.md` - 5 JavaScript modules, initialization, cross-module communication
  - `frontend/css-theme.md` - CSS variables, dual-theme system (light/dark), responsive design
  - `frontend/static-assets.md` - Asset organization (CSS, JS files), load order
  - `frontend/htmx-integration.md` - HTMX current usage and potential patterns

### Integration Knowledge (modules/integration/)

These documents explain HOW the application interfaces with the outside world:

- **API Endpoints** - HTTP interfaces provided by this application
  - `api/endpoints.md` - All 8 JSON endpoints, response formats, query parameters

- **Page Flows** - User-facing page navigation and interactions
  - `pages/flows.md` - 5 page flows (overview, projects, sessions, settings), data aggregation per page

### Technical Patterns (modules/patterns/)

These documents capture HOW things are implemented at a technical level:

- `patterns/data-loading.md` - 4 major data loading flows, error handling, cache strategy
- `patterns/caching.md` - Cache implementation with TTL and mtime invalidation
- `patterns/js-modules.md` - JavaScript module patterns, lifecycle, event communication
- `patterns/storage.md` - localStorage usage, key management, security considerations

### Integrations (modules/integrations/)

Technical integration with external libraries:

- `integrations/chartjs.md` - Chart.js library usage, 7 chart configurations, theme colors
- `integrations/htmx.md` - HTMX library usage and migration roadmap

**Total Documentation:** 350+ pages with 200+ code references across 21 files.

---

## Common Tasks

This section provides step-by-step guides for the most common development tasks. Each task includes references to relevant documentation and code locations.

### Task 1: Add a New Page (Dashboard Feature)

**Goal:** Create a new page showing daily cost trends.

**Steps:**

1. **Create API endpoint** in `src/app/routers/api.py`
   - Reference: `modules/integration/api/endpoints.md` for response format
   - Example: Copy structure from `/api/overview` endpoint (line 45-68)
   - Return Chart.js-compatible JSON with `labels` and `datasets`

2. **Create page route** in `src/app/routers/` (new file or existing)
   - Reference: `modules/domain/architecture/routing.md` for router pattern
   - Use HTMLResponse with template rendering
   - Pass context data (title, filters, date range)

3. **Create template** in `src/app/templates/`
   - Reference: `modules/domain/frontend/templates.md` for structure
   - Extend `base.html` using `{% extends "base.html" %}`
   - Add canvas element with unique ID for Chart.js

4. **Initialize chart** in `src/app/static/charts.js`
   - Reference: `modules/integrations/chartjs.md` for chart configuration
   - Add initialization function matching your endpoint
   - Hook theme changes via `themeChangeEvent` custom event

5. **Register route** in `src/app/main.py:15-20`
   - Reference: `modules/domain/architecture/routing.md` line 25-30
   - Add `app.include_router()`

6. **Test locally:** `uv run src/app/main.py` and visit `http://localhost:8000/your-page`

### Task 2: Add a New Chart (Data Visualization)

**Goal:** Add a chart showing cost by model on the overview page.

**Steps:**

1. **Create API endpoint** (same as Task 1 Step 1)
   - Reference: `modules/integrations/chartjs.md` lines 156-200 for color scheme
   - Aggregate data by model using `src/app/data/loader.py` functions

2. **Add canvas to template**
   ```html
   <div class="chart-container">
     <canvas id="modelCostChart"></canvas>
   </div>
   ```
   - Reference: `modules/domain/frontend/templates.md` for component structure

3. **Initialize in `charts.js`**
   - Reference: `modules/integrations/chartjs.md` lines 300-350
   - Use doughnut chart type for category breakdown
   - Get colors from theme module via `window.getThemeColors()`

4. **Handle theme switching**
   - Reference: `modules/patterns/js-modules.md` line 145-160
   - Listen to `themeChange` custom event to update chart colors

5. **Test locally** and verify chart updates with theme toggle

### Task 3: Add an API Endpoint (Data Query)

**Goal:** Add endpoint to export usage data as CSV.

**Steps:**

1. **Add route to `src/app/routers/api.py`**
   - Reference: `modules/integration/api/endpoints.md` for parameter patterns
   - Use query params: `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&project=X`
   - Return `StreamingResponse` with CSV content

2. **Load data** using loader functions
   - Reference: `modules/patterns/data-loading.md` for error handling
   - Call `loader.get_sessions()`, `loader.get_projects()` with filters

3. **Format response**
   - Reference: `modules/integration/api/endpoints.md` line 80-120 for JSON format
   - For CSV: use Python `csv.DictWriter` with headers

4. **Handle errors**
   - Reference: `modules/domain/data/loading.md` line 400-420
   - Return 404 if project not found, validate date ranges

5. **Test with curl:**
   ```bash
   curl "http://localhost:8000/api/export-csv?project=ada&start_date=2026-01-01"
   ```

### Task 4: Modify Pricing Calculation

**Goal:** Update token costs when Anthropic changes pricing.

**Steps:**

1. **Update fallback pricing** in `src/app/data/pricing.py`
   - Reference: `modules/domain/data/pricing.md` lines 50-95
   - Update `MODEL_COSTS` dictionary with new rates
   - Format: `{"input": rate_per_1m, "output": rate_per_1m}`

2. **Clear pricing cache** (optional)
   - Reference: `modules/patterns/caching.md` lines 320-350
   - Cache invalidates automatically after 24 hours
   - Or restart application to force reload

3. **Verify calculation**
   - Reference: `modules/domain/data/pricing.md` lines 120-150
   - Cost = (input_tokens * rate) + (output_tokens * rate) + cache adjustments
   - Test with known message to verify new pricing

4. **Check API fallback**
   - Reference: `modules/domain/data/pricing.py:45-95` code location
   - Pricing fetches from Anthropic API first, falls back to hardcoded values

### Task 5: Extend Theme System

**Goal:** Add a new theme variant (e.g., high contrast).

**Steps:**

1. **Add CSS variables** in `src/app/static/style.css`
   - Reference: `modules/domain/frontend/css-theme.md` lines 50-150
   - Define new color scheme for `data-theme="high-contrast"`
   - Include all 34 CSS custom properties

2. **Update theme.js** to support new mode
   - Reference: `modules/patterns/js-modules.md` lines 200-250
   - Add to theme cycling logic or dropdown selector

3. **Add chart colors** for new theme
   - Reference: `modules/integrations/chartjs.md` lines 100-130
   - Update `getThemeColors()` function

4. **Test with all pages**
   - Reference: `modules/domain/frontend/templates.md` for pages that use theme
   - Verify readability on overview, projects, sessions pages

5. **localStorage persistence**
   - Reference: `modules/patterns/storage.md` lines 80-120
   - Update localStorage key to save selected theme

### Task 6: Add JavaScript Functionality

**Goal:** Add client-side validation for date filter inputs.

**Steps:**

1. **Create new JS module** in `src/app/static/`
   - Reference: `modules/patterns/js-modules.md` lines 50-100
   - Use revealing module pattern: `(function() { ... })()`
   - Export via `window.myModule = {...}`

2. **Add initialization hook**
   - Reference: `modules/domain/frontend/javascript.md` lines 300-350
   - Listen to `DOMContentLoaded` event

3. **Communicate with other modules**
   - Reference: `modules/patterns/js-modules.md` lines 150-200
   - Use custom events: `window.dispatchEvent(new CustomEvent(...))`
   - Listen: `window.addEventListener('myEvent', handler)`

4. **Load in template**
   - Reference: `modules/domain/frontend/templates.md` line 195
   - Add `<script src="/static/my-module.js"></script>` to base.html

5. **Test in browser console**
   - Open DevTools (F12), console tab
   - Verify module loads: `console.log(window.myModule)`

---

## Key Patterns

### 1. Caching Strategy

Data is cached in memory with two invalidation mechanisms:

- **TTL (Time-To-Live):** 5-minute default, configurable per cache key
- **mtime (File Modification Time):** Cache invalidates when source files change

**When to use:**
- `/api/overview` endpoint caches stats-cache.json result
- `/api/projects` endpoint caches list of projects
- Pricing data cached for 24 hours

Reference: `modules/patterns/caching.md` (entire file)

### 2. Data Aggregation Levels

Data flows through 4 aggregation levels:

1. **Message Level** - Individual API calls, each message has token breakdown
2. **Session Level** - Sum of all messages in one Claude session
3. **Project Level** - Sum of all sessions in one project
4. **Dashboard Level** - Pre-computed totals in stats-cache.json

**When to use:**
- Use message-level for detailed debugging (session pages)
- Use session-level for per-conversation costs
- Use project-level for project breakdown
- Use dashboard-level for overview charts (fastest)

Reference: `modules/domain/data/loading.md` (entire file)

### 3. Template Inheritance

All pages extend `base.html` which includes:
- Navigation header
- Theme toggle and timezone toggle
- Chart.js and HTMX CDN
- JavaScript module loading
- CSS with theme variables

**Pattern:**
```html
{% extends "base.html" %}
{% block content %}
  <!-- Your content here -->
{% endblock %}
```

Reference: `modules/domain/frontend/templates.md` lines 50-100

### 4. JavaScript Module Communication

5 independent JavaScript modules communicate via custom events:

- **theme.js** - Detects dark mode, broadcasts `themeChange` events
- **timezone.js** - Cycles time formats, broadcasts `timezoneChange` events
- **charts.js** - Listens to both, updates chart colors and formats
- **filters.js** - Manages date/project filters, broadcasts `filterChange` events
- **htmx-config.js** - Handles HTMX loading indicators

**Pattern:**
```javascript
// Broadcast event
window.dispatchEvent(new CustomEvent('themeChange', {
  detail: { theme: 'dark', colors: {...} }
}));

// Listen to event
window.addEventListener('themeChange', (e) => {
  // Update charts with e.detail.colors
});
```

Reference: `modules/patterns/js-modules.md` (entire file)

### 5. Error Handling

Graceful degradation pattern used throughout:

- Return `None` or empty list instead of raising exceptions
- Log errors at appropriate level (debug/warning)
- Show user-friendly message in UI (no stack traces)
- Provide fallback data when possible

**Example:**
```python
try:
    projects = loader.get_projects()
except FileNotFoundError:
    projects = []  # Empty list, not exception
    logger.warning("projects directory not found")
```

Reference: `modules/domain/data/loading.md` lines 400-420

### 6. Theme System with CSS Variables

34 CSS custom properties define all colors:

- Primary, secondary, accent colors
- Background, text, border colors
- Chart color schemes for each model
- Light and dark theme variants

**Pattern:**
```css
:root {
  --primary: #3f3f46;
  --primary-dark: #18181b;
}

[data-theme="dark"] {
  --primary: #18181b;
  --primary-dark: #3f3f46;
}
```

Reference: `modules/domain/frontend/css-theme.md` (entire file)

---

## Critical Files Reference

Quick lookup table for common edits:

| Task | File | Lines | Reference |
|------|------|-------|-----------|
| Add new page | `src/app/main.py` | 15-20 | architecture/routing.md |
| Add new route | `src/app/routers/*.py` | varies | integration/api/endpoints.md |
| Add new API endpoint | `src/app/routers/api.py` | 29-68 | integration/api/endpoints.md |
| Load data | `src/app/data/loader.py` | 40-120 | patterns/data-loading.md |
| Calculate cost | `src/app/data/pricing.py` | 45-95 | domain/data/pricing.md |
| Cache operations | `src/app/data/cache.py` | 1-62 | patterns/caching.md |
| Modify template | `src/app/templates/*.html` | varies | frontend/templates.md |
| Add chart | `src/app/static/charts.js` | varies | integrations/chartjs.md |
| Theme colors | `src/app/static/style.css` | 50-150 | frontend/css-theme.md |
| Theme logic | `src/app/static/theme.js` | varies | patterns/js-modules.md |
| Timezone logic | `src/app/static/timezone.js` | varies | patterns/js-modules.md |
| Config variables | `src/app/config.py` | 11-20 | architecture/config.md |

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
| 0: Discovery | ✅ Complete | 5 | 100% |
| 1: Domain Knowledge | ✅ Complete | 16 | 100% |
| 2: Technical Patterns | ⏳ Partial | 16 | 37.5% |
| 3: Skills & Integration | ✅ Complete | 14 | 100% |
| 4: Validation | ⏳ Pending | 5 | 0% |
| **Total** | **Agent-Ready** | **56** | **67.8%** |

**Status:** Repository is agent-ready with comprehensive documentation. Phase 4 is validation and final packaging.

**For agents:** Use this README as your primary entry point. Reference `.agents/skills/repo-skill/modules/` for detailed technical docs.

---

## Links & References

- **Project Documentation:** See `docs/` directory
- **Build Checklist:** `BUILD_CHECKLIST.md`
- **Skills Index:** Root `AGENTS.md`
- **Security Audit:** `SECURITY_VALIDATION.md`

---

**Last Updated:** 2026-02-20
**Maintained By:** Agent-readiness extraction pipeline

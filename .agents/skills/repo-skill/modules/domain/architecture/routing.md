# Application Routing Architecture

## Overview

The Claude Usage Visualizer uses FastAPI with a modular router-based architecture. Each major feature area (overview, projects, sessions, API, settings) is implemented as a separate router mounted on the main FastAPI application instance.

**File References:**
- Main app setup: `src/app/main.py:1-32`
- Router definitions: `src/app/routers/*.py`

## Routing Structure

### Application Bootstrap

The FastAPI application is initialized with metadata at `src/app/main.py:9`:

```
app = FastAPI(title="Claude Usage Visualizer")
```

### Static File Mounting

Static assets (CSS, JavaScript) are mounted at `src/app/main.py:11-13`:

- **Mount path:** `/static`
- **Directory:** `src/app/static/`
- **Includes:** CSS stylesheets, JavaScript modules, theme files, timezone utilities

### Router Registration

Five routers are registered in order at `src/app/main.py:16-20`:

1. **API Router** (`src/app/routers/api.py:15`)
   - Prefix: `/api`
   - Purpose: JSON endpoints for chart data and metadata
   - Pattern: Fetch stats and project summaries, calculate aggregations, return Chart.js-formatted data

2. **Overview Router** (`src/app/routers/overview.py:11`)
   - Prefix: (none - serves from root)
   - Purpose: Dashboard homepage with total statistics
   - Routes:
     - GET `/` - Renders overview.html with aggregated statistics

3. **Projects Router** (`src/app/routers/projects.py:10`)
   - Prefix: (none)
   - Purpose: Project listing and detail views
   - Routes:
     - GET `/projects` - List all projects with summary statistics
     - GET `/projects/{encoded_name}` - Detail view for single project with sessions

4. **Sessions Router** (`src/app/routers/sessions.py:9`)
   - Prefix: (none)
   - Purpose: Session detail views
   - Routes:
     - GET `/sessions/{encoded_path}/{session_id}` - Detailed message-level breakdown

5. **Settings Router** (`src/app/routers/settings.py:TBD`)
   - Prefix: (none)
   - Purpose: Data directory configuration (not yet extracted)

### Health Check Endpoint

Health endpoint at `src/app/main.py:23-31`:

```
GET /health
```

Returns:
- `status`: "ok"
- `data_dir`: Current data directory path
- `has_stats_cache`: Boolean whether stats-cache.json exists
- `has_projects`: Boolean whether projects/ directory exists

## Template Rendering

Templates are loaded per-router using Jinja2 `FileSystemLoader` at runtime.

**Template setup pattern** (e.g., Overview):
- Base path: `src/app/templates/`
- Environment: `Environment(loader=FileSystemLoader(templates_dir))`
- Reference: `src/app/routers/overview.py:14-15`

## API Response Patterns

All JSON API endpoints return Chart.js-compatible data structures with:

- `labels`: Array of X-axis values (dates, hours, model names, project names)
- `datasets`: Array of data series
  - Each dataset has: `label`, `data`, `backgroundColor`, `borderColor`, `borderWidth`, `fill`, `tension`
  - Optional: `yAxisID` for dual-axis charts

Example: `src/app/routers/api.py:44-68` (daily-activity endpoint)

## Key URL Patterns

| Route | Method | Router | Purpose |
|-------|--------|--------|---------|
| `/health` | GET | Main | Health check |
| `/` | GET | overview | Dashboard homepage |
| `/projects` | GET | projects | List all projects |
| `/projects/{encoded_name}` | GET | projects | Project detail |
| `/sessions/{encoded_path}/{session_id}` | GET | sessions | Session detail |
| `/api/*` | GET | api | Chart data endpoints |
| `/static/*` | GET | Static | CSS, JS assets |

## Dynamic URL Construction

URLs are constructed dynamically from:

1. **Project encoded_path**: URL-safe encoded directory name from `projects/` folder
   - Used in: `/projects/{encoded_name}`, `/api/projects/{encoded_path}/*`
   - Example: If file path is `~/claude/projects/IdeaProjects/my-project/`, encoded_path might be `IdeaProjects%2Fmy-project`

2. **Session ID**: Raw session ID from JSONL filename (without extension)
   - Used in: `/sessions/{encoded_path}/{session_id}`

3. **Query Parameters**: Optional date range and project filters
   - Used in: `/api/*` endpoints
   - Pattern: `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&project={encoded_path}`

## Request Flow Example: Daily Activity Chart

1. **Frontend request:** GET `/api/daily-activity?start_date=2026-02-15&end_date=2026-02-20`
2. **Router handler:** `src/app/routers/api.py:29-68`
   - Load stats cache
   - Filter daily activity by date range
   - Extract dates, message counts, session counts
   - Return Chart.js format with dual Y-axes

3. **Frontend receives:** JSON with labels (dates) and two datasets (messages, sessions)
4. **Chart.js renders:** Line chart with dual axes

## Error Handling in Routing

**Missing data scenarios:**

1. **Stats cache missing:** `src/app/routers/overview.py:23-28`
   - Render template with `overview_stats=None` and error message
   - Status: 200 (still HTML response)

2. **Project not found:** `src/app/routers/projects.py:94-101`
   - Render template with error message
   - Status: 200 (still HTML response)

3. **API endpoint missing data:** `src/app/routers/api.py:34`
   - Raise `HTTPException(status_code=404, detail="Stats cache not found")`
   - Status: 404 with JSON error

## Template Variables

Each router passes context variables to templates:

**Overview context** (`src/app/routers/overview.py:88-96`):
- `overview_stats`: OverviewStats object or None
- `total_cost`: Calculated USD cost
- `total_cache_write`, `total_cache_read`: Cache statistics
- `model_rows`: List of per-model stats with display names
- `data_dir`: Current data directory path
- `error`: Error message or None

**Projects context** (`src/app/routers/projects.py:83-86`):
- `projects`: List of project dicts with stats
- `error`: Error message or None

**Project detail context** (`src/app/routers/projects.py:145-155`):
- `project_name`: Display name of project
- `encoded_name`: URL-safe project identifier
- `sessions`: List of session dicts
- `total_sessions`, `total_input_tokens`, `total_output_tokens`, `total_cost_usd`: Aggregates
- `back_url`: Navigation link

**Session detail context** (`src/app/routers/sessions.py:78-93`):
- `session_slug`: User-friendly session name
- `project_name`: Parent project name
- `encoded_path`: Project encoded path
- `session_id`: Session identifier
- `messages`: List of message dicts
- `message_count`, `total_input_tokens`, `total_output_tokens`: Aggregates
- `total_cache_read_tokens`, `total_cache_creation_tokens`: Cache metrics
- `total_cost_usd`: Session cost
- `models`: Comma-separated model names used
- `back_url`: Navigation link

## Performance Considerations

1. **Caching:** Data loaders (stats-cache, project summaries, session messages) use in-memory cache with TTL
   - Bypass repeated file I/O for same request
   - 5-minute TTL keeps data reasonably fresh (see `src/app/data/cache.py:5`)

2. **Lazy loading:** Session messages and summaries are loaded on-demand
   - Project list page loads only summaries (aggregated stats)
   - Session detail page loads full message list (with costs)

3. **Date filtering:** Early-stage filtering reduces data processing
   - API endpoints accept `start_date` and `end_date` query parameters
   - Data is filtered before aggregation in routers
   - See `src/app/routers/api.py:18-26` (filter helper)

## Extensibility

Adding a new feature involves:

1. Create new router file in `src/app/routers/{feature}.py`
2. Import router in `src/app/main.py`
3. Register with `app.include_router(router)` at `src/app/main.py:16-20`
4. Create template file in `src/app/templates/{feature}.html`
5. Add corresponding endpoint handler in router
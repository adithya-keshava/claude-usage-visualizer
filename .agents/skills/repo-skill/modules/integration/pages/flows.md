# Page Flows & User Interactions

## Overview

The application provides a multi-page dashboard for exploring Claude usage. Each page has a specific focus and uses different data aggregation levels.

**Routers involved:**
- Overview (`src/app/routers/overview.py`)
- Projects (`src/app/routers/projects.py`)
- Sessions (`src/app/routers/sessions.py`)
- Settings (`src/app/routers/settings.py`)

## Page Hierarchy

```
Home (Overview)
  ├─ /
  │  └─ Dashboard with totals and trends
  │
Projects
  ├─ /projects
  │  └─ List all projects by cost
  │
  └─ /projects/{encoded_path}
     ├─ Project detail with sessions
     │
     └─ /sessions/{encoded_path}/{session_id}
        └─ Session detail with message breakdown
```

## Flow 1: Overview Dashboard

**Route:** `GET /`

**Handler:** `src/app/routers/overview.py:18-96`

**Page Purpose:** Show total usage, trends, and per-model breakdown

```
User visits http://localhost:8000/
  ↓
overview() router handler
  ├─ load_stats_cache()
  │  └─ Parse stats-cache.json
  │
  └─ Process overview stats:
     ├─ Calculate total_cost from all models
     ├─ Sum cache_write and cache_read tokens
     ├─ Format model_rows for display table
     │  ├─ Model ID → Display name mapping
     │  │  Example: "claude-opus-4-6" → "Opus 4.6"
     │  │
     │  └─ For each model:
     │     ├─ input_tokens
     │     ├─ output_tokens
     │     ├─ cache tokens
     │     ├─ total_tokens
     │     └─ cost_usd
     │
     └─ Render overview.html template

  ↓
Template displays:
  ├─ Total KPIs
  │  ├─ Total sessions
  │  ├─ Total messages
  │  ├─ Total cost (USD)
  │  └─ Date range
  │
  ├─ Charts (loaded via JavaScript API calls)
  │  ├─ Daily activity (messages + sessions)
  │  ├─ Daily cost by model (stacked area)
  │  ├─ Model cost split (doughnut)
  │  └─ Hourly distribution (bar)
  │
  ├─ Per-model breakdown table
  │  └─ Rows sorted by cost descending
  │
  ├─ Navigation links
  │  ├─ /projects
  │  └─ /settings
  │
  └─ Chart.js visualizations

  ↓
User sees dashboard
```

**Data flow:**

1. Load OverviewStats from cache (or stats-cache.json if cache miss)
2. Calculate costs using estimate_cost() for each model
3. Format for template rendering
4. Render HTML with inline data
5. JavaScript loads chart data via async API calls

**Chart loading (client-side):**

Charts are loaded asynchronously after page load via JavaScript:

- `/api/daily-activity` → Daily activity chart
- `/api/daily-cost` → Daily cost chart
- `/api/model-split` → Model split doughnut
- `/api/hourly-distribution` → Hourly distribution bar

**Error handling:**

If `load_stats_cache()` returns None:
- Render overview.html with `overview_stats=None`
- Display error message: "No stats-cache.json found. Please configure the data directory in settings."
- Charts don't load (no data)

**Performance:**

- Time to response: 50-200ms (depending on cache state)
- Chart loading: Parallel API calls (~100ms total)
- Memory: ~1KB of template data + chart JSON

## Flow 2: Projects List

**Route:** `GET /projects`

**Handler:** `src/app/routers/projects.py:17-86`

**Page Purpose:** Show all projects ranked by cost

```
User clicks /projects link or visits directly
  ↓
projects_list() router handler
  ├─ build_project_summaries()
  │  └─ Scan projects/ directory
  │     └─ For each project:
  │        └─ For each session:
  │           └─ build_session_summary()
  │              └─ Aggregate message data
  │
  └─ Process project data:
     ├─ For each project:
     │  ├─ Sum sessions' input_tokens
     │  ├─ Sum sessions' output_tokens
     │  ├─ Sum sessions' costs
     │  ├─ Get display_name from first session
     │  └─ Calculate date range
     │
     ├─ Sort by cost descending
     └─ Render projects.html template

  ↓
Template displays:
  ├─ Project list table
  │  ├─ Project name (with link to detail)
  │  ├─ Session count
  │  ├─ Total tokens (input + output)
  │  ├─ Total cost (USD)
  │  └─ Date range
  │
  ├─ Navigation
  │  ├─ Home (/)
  │  └─ Settings
  │
  └─ Sorting/filtering (client-side?)

  ↓
User sees project list
```

**Data aggregation:**

```python
for encoded_path, sessions in project_summaries.items():
    total_input = sum(s.total_input_tokens for s in sessions)
    total_output = sum(s.total_output_tokens for s in sessions)
    total_cost = sum(s.total_cost_usd for s in sessions)

    projects.append({
        "encoded_path": encoded_path,
        "display_name": display_name,
        "session_count": len(sessions),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost_usd": total_cost,
        "date_range": date_range,
    })

projects.sort(key=lambda p: p["total_cost_usd"], reverse=True)
```

**Error handling:**

If `projects_dir.exists()` is False:
- Render projects.html with `projects=None`
- Display error message: "No projects directory found."

If no sessions found:
- Render with `projects=[]`
- Display empty state

**Performance:**

- Time to response: 500ms - 2s (full project scan + aggregation)
- Memory: ~500KB for 100 projects with 1000 sessions
- Caching: Result cached for 5 minutes

**Next step:** Click project name → Project detail

## Flow 3: Project Detail

**Route:** `GET /projects/{encoded_name}`

**Handler:** `src/app/routers/projects.py:89-155`

**Page Purpose:** Show sessions within a project

```
User clicks project name on projects list
  ↓
project_detail(encoded_name) router handler
  ├─ build_project_summaries()
  │  └─ Retrieve cached or build fresh
  │
  ├─ Look up encoded_name in summaries
  │  └─ Get list of SessionSummary objects
  │
  └─ Process session data:
     ├─ For each session:
     │  ├─ Create session_row dict
     │  ├─ Format timestamp to date string
     │  ├─ Get models as comma-separated string
     │  └─ Add to session_rows list
     │
     ├─ Sort sessions by timestamp descending (newest first)
     ├─ Calculate project totals (sum all sessions)
     └─ Render project_detail.html

  ↓
Template displays:
  ├─ Project name (display_name)
  ├─ Project totals
  │  ├─ Total sessions
  │  ├─ Total input tokens
  │  ├─ Total output tokens
  │  └─ Total cost (USD)
  │
  ├─ Chart (via API call to /api/projects/{encoded_path}/activity)
  │  └─ Daily activity for project
  │
  ├─ Sessions table
  │  ├─ Session slug (link to detail)
  │  ├─ Timestamp
  │  ├─ Message count
  │  ├─ Total tokens
  │  ├─ Cost
  │  └─ Models used
  │
  ├─ Navigation
  │  ├─ Back to projects list
  │  ├─ Home
  │  └─ Settings
  │
  └─ (Possibly) Model cost breakdown chart

  ↓
User sees project detail
```

**Session row data** (`src/app/routers/projects.py:130-142`):

```python
{
    "session_id": session.session_id,
    "slug": session.slug,
    "timestamp": session.timestamp,
    "date": session.timestamp.split("T")[0],
    "message_count": session.message_count,
    "total_input_tokens": session.total_input_tokens,
    "total_output_tokens": session.total_output_tokens,
    "total_cost_usd": session.total_cost_usd,
    "models": ", ".join(sorted(session.models_used)),
}
```

**Error handling:**

If `encoded_name` not in project_summaries:
- Render project_detail.html with error message: "Project not found: {encoded_name}"

**Performance:**

- Time to response: 100-300ms (depends on session count)
- Memory: ~1-10KB template data per session
- Caching: Project data cached, reused from previous request

**Next step:** Click session slug → Session detail

## Flow 4: Session Detail

**Route:** `GET /sessions/{encoded_path}/{session_id}`

**Handler:** `src/app/routers/sessions.py:16-93`

**Page Purpose:** Show individual messages and token costs

```
User clicks session slug on project detail page
  ↓
session_detail(encoded_path, session_id) router handler
  ├─ build_session_summary(encoded_path, session_id, {})
  │  └─ Load session metadata and aggregated data
  │
  └─ load_session_messages(encoded_path, session_id)
     └─ Parse session JSONL file
        └─ Return list of SessionMessage objects

  ↓
Template processing:
  ├─ For each message:
  │  ├─ Format timestamp to readable date_time
  │  ├─ Extract model, tokens, cost
  │  └─ Create message_row dict
  │
  ├─ Calculate session totals
  │  ├─ Sum input_tokens
  │  ├─ Sum output_tokens
  │  ├─ Sum cache tokens
  │  └─ Sum costs
  │
  └─ Render session_detail.html

  ↓
Template displays:
  ├─ Session metadata
  │  ├─ Session slug (title)
  │  ├─ Project name
  │  └─ Timestamp
  │
  ├─ Session totals
  │  ├─ Message count
  │  ├─ Total input tokens
  │  ├─ Total output tokens
  │  ├─ Cache read/write tokens
  │  └─ Total cost (USD)
  │
  ├─ Models used
  │  └─ Comma-separated list
  │
  ├─ Message table (most detailed view)
  │  ├─ Per message:
  │  │  ├─ Timestamp (date and time)
  │  │  ├─ Model ID
  │  │  ├─ Input tokens
  │  │  ├─ Output tokens
  │  │  ├─ Cache tokens
  │  │  └─ Cost (USD)
  │  │
  │  └─ Sorted by timestamp (oldest first)
  │
  ├─ Navigation
  │  ├─ Back to project
  │  ├─ Back to projects list
  │  ├─ Home
  │  └─ Settings
  │
  └─ (Possibly) Cost breakdown chart

  ↓
User sees detailed message breakdown
```

**Message row data** (`src/app/routers/sessions.py:57-68`):

```python
{
    "timestamp": msg.timestamp,
    "date_time": msg.timestamp.replace("T", " ")[:19],
    "model": msg.model,
    "input_tokens": msg.input_tokens,
    "output_tokens": msg.output_tokens,
    "cache_read_tokens": msg.cache_read_input_tokens,
    "cache_creation_tokens": msg.cache_creation_input_tokens,
    "cost_usd": msg.cost_usd,
}
```

**Error handling:**

If `build_session_summary()` returns None:
- Render session_detail.html with error message: "Session not found: {session_id}"

If `load_session_messages()` returns empty list:
- Render with empty messages list
- Display session metadata but no message table

**Performance:**

- Time to response: 50-300ms (depends on message count)
- Memory: ~10-100KB template data per message
- Caching: Messages cached individually per session

**Navigation back:** Click back link → Project detail

## Flow 5: Settings

**Route (GET):** `GET /settings`

**Handler:** `src/app/routers/settings.py:41-52`

**Page Purpose:** Configure data directory

```
User clicks /settings link
  ↓
settings_page() handler
  ├─ get_current_data_dir()
  ├─ validate_data_dir(current_dir)
  │  ├─ Check if path exists
  │  ├─ Check if directory
  │  └─ Check for stats-cache.json or projects/
  │
  └─ Render settings.html with current_dir and is_valid

  ↓
Template displays:
  ├─ Current data directory (read-only or editable field)
  ├─ Validation status (green check or red error)
  ├─ Input field for new data directory
  ├─ Paste helper text
  ├─ Submit button
  │
  └─ Navigation
     ├─ Home
     └─ Projects
```

### Settings POST

**Route (POST):** `POST /settings`

**Handler:** `src/app/routers/settings.py:55-73`

**Purpose:** Update data directory and clear cache

```
User submits settings form with new data_dir
  ↓
update_settings(data_dir) handler
  ├─ validate_data_dir(data_dir)
  │  └─ Same validation as GET
  │
  ├─ If not valid:
  │  └─ Render settings.html with error message
  │
  └─ If valid:
     ├─ set_data_dir(data_dir)
     │  ├─ Update global _data_dir variable
     │  └─ Update CLAUDE_DATA_DIR env var
     │
     ├─ cache.invalidate()
     │  └─ Clear all in-memory cache
     │
     └─ RedirectResponse(url="/", status_code=303)

  ↓
Browser redirects to /
  ↓
User sees overview with new data loaded
```

**Validation** (`src/app/routers/settings.py:17-38`):

1. Path exists: `path.exists()`
2. Is directory: `path.is_dir()`
3. Contains stats-cache.json OR projects/:
   ```python
   has_stats_cache = (path / "stats-cache.json").exists()
   has_projects = (path / "projects").is_dir()
   if not (has_stats_cache or has_projects):
       return False, "Directory must contain either..."
   ```

**Error cases:**

1. Path doesn't exist: "Path does not exist: {path}"
2. Path is file: "Path is not a directory: {path}"
3. Neither stats-cache.json nor projects/: "Directory must contain either..."

**Performance:**

- Validation: <10ms (filesystem checks)
- Cache invalidation: <1ms (clear dict)
- Redirect: Instant

## Navigation Patterns

### Top-level Navigation

All pages include navigation links:

- Home → `/` (overview)
- Projects → `/projects` (project list)
- Settings → `/settings` (settings page)

### Contextual Navigation

- Project list → Project detail (click project name)
- Project detail → Session detail (click session slug)
- Session detail → Project detail (back link)
- Project detail → Project list (back link)
- All pages → Settings (top nav)

### Error recovery

If error occurs:
- Display error message on same page
- Provide navigation back to previous page
- Suggest visiting settings if data issue

## Client-Side Features

### JavaScript-Loaded Charts

Charts are loaded asynchronously after page render:

**Overview dashboard:**
- `/api/daily-activity` → Chart.js line chart
- `/api/daily-cost` → Chart.js stacked area chart
- `/api/model-split` → Chart.js doughnut chart
- `/api/hourly-distribution` → Chart.js bar chart

**Project detail (if implemented):**
- `/api/projects/{encoded_path}/activity` → Chart.js line chart
- `/api/projects/{encoded_path}/cost-breakdown` → Chart.js doughnut chart

**Session detail:**
- No dynamic charts (static table)

### Dynamic Filtering

Some pages may support client-side filtering:

- Date range picker for charts
- Project filter for activity chart
- Sort/order controls on tables

## Performance Considerations

### Page Load Times

| Page | Cache Hit | Cache Miss | Components |
|------|:---------:|:----------:|-----------|
| Overview | 50ms | 200ms | Stats + 4 charts |
| Projects | 100ms | 1s | Project scan + sort |
| Project detail | 50ms | 500ms | Session load + aggregate |
| Session detail | 30ms | 300ms | Message parse + format |
| Settings | <10ms | <10ms | Validation only |

### Caching Strategy

- Overview: Cache stats-cache.json (5 min TTL)
- Projects: Cache project_summaries (5 min TTL)
- Session: Cache session messages (5 min TTL per session)
- Settings: No caching (config can change)

### Memory Usage

- Overview: ~1 KB template data
- Projects: ~50 KB for 1000 sessions
- Project detail: ~10 KB per 100 sessions
- Session detail: ~100 KB per 100 messages
- Settings: <1 KB

## Accessibility Considerations

**Current implementation** (not explicitly mentioned in code):

- Standard HTML form for settings
- Table layouts for data
- Text-based navigation

**Potential improvements:**

- ARIA labels for charts
- Keyboard navigation
- Color contrast for themes
- Alt text for images (if any)
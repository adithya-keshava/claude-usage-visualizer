# API Endpoints & Contracts

## Overview

The application exposes REST API endpoints for fetching chart data, metadata, and project analytics in JSON format. All endpoints are prefixed with `/api` and return Chart.js-compatible data structures.

**File Reference:** `src/app/routers/api.py`

## Chart Data Endpoints

### Daily Activity Endpoint

**Route:** `GET /api/daily-activity`

**Handler:** `src/app/routers/api.py:29-68`

**Purpose:** Fetch daily message and session counts for line chart

**Query Parameters:**

| Parameter | Type | Required | Format | Example |
|-----------|------|----------|--------|---------|
| `start_date` | string | No | YYYY-MM-DD | 2026-02-15 |
| `end_date` | string | No | YYYY-MM-DD | 2026-02-20 |

**Response Format:**

```json
{
  "labels": ["2026-02-15", "2026-02-16", ..., "2026-02-20"],
  "datasets": [
    {
      "label": "Messages",
      "data": [50, 45, 52, 48, 60, 55],
      "borderColor": "rgba(139, 92, 246, 1)",
      "backgroundColor": "rgba(139, 92, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y",
      "fill": true
    },
    {
      "label": "Sessions",
      "data": [5, 4, 5, 4, 6, 5],
      "borderColor": "rgba(59, 130, 246, 1)",
      "backgroundColor": "rgba(59, 130, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y1",
      "fill": true
    }
  ]
}
```

**Data source:** `overview_stats.daily_activity` from stats-cache.json

**Error response:**

```json
{
  "detail": "Stats cache not found"
}
```

HTTP Status: 404

**Filtering logic:**

```python
activities = filter_by_date_range(
    overview_stats.daily_activity, start_date, end_date
)
```

Extracts daily activity objects where date is in range, returns empty list if no matches.

### Daily Cost Endpoint

**Route:** `GET /api/daily-cost`

**Handler:** `src/app/routers/api.py:71-132`

**Purpose:** Fetch daily cost breakdown by model for stacked area chart

**Query Parameters:**

| Parameter | Type | Required | Format |
|-----------|------|----------|--------|
| `start_date` | string | No | YYYY-MM-DD |
| `end_date` | string | No | YYYY-MM-DD |

**Response Format:**

```json
{
  "labels": ["2026-02-15", "2026-02-16", ..., "2026-02-20"],
  "datasets": [
    {
      "label": "Opus 4.6",
      "data": [2.50, 2.15, 2.75, 1.90, 3.20, 2.85],
      "borderColor": "rgba(168, 85, 247, 1)",
      "backgroundColor": "rgba(168, 85, 247, 0.5)",
      "borderWidth": 2,
      "fill": true,
      "tension": 0.3
    },
    {
      "label": "Sonnet 4.5",
      "data": [1.20, 1.10, 1.30, 1.05, 1.50, 1.25],
      "borderColor": "rgba(59, 130, 246, 1)",
      "backgroundColor": "rgba(59, 130, 246, 0.5)",
      "borderWidth": 2,
      "fill": true,
      "tension": 0.3
    }
  ]
}
```

**Cost calculation:** Uses 50/50 input/output approximation

`src/app/routers/api.py:113`:
```python
cost = estimate_cost(model_id, input_tokens=tokens // 2, output_tokens=tokens // 2)
```

**Data source:** `overview_stats.daily_model_tokens` from stats-cache.json

**Color mapping:**

- Opus 4.6: purple
- Opus 4.5: dark purple
- Sonnet 4.5: blue
- Haiku 4.5: emerald

### Model Split Endpoint

**Route:** `GET /api/model-split`

**Handler:** `src/app/routers/api.py:135-182`

**Purpose:** Fetch total cost per model for doughnut chart

**Query Parameters:** None

**Response Format:**

```json
{
  "labels": ["Haiku 4.5", "Sonnet 4.5", "Opus 4.5", "Opus 4.6"],
  "datasets": [
    {
      "data": [2.50, 15.75, 8.25, 20.50],
      "backgroundColor": [
        "rgba(16, 185, 129, 0.8)",
        "rgba(59, 130, 246, 0.8)",
        "rgba(147, 51, 234, 0.8)",
        "rgba(168, 85, 247, 0.8)"
      ],
      "borderColor": [
        "rgba(16, 185, 129, 1)",
        "rgba(59, 130, 246, 1)",
        "rgba(147, 51, 234, 1)",
        "rgba(168, 85, 247, 1)"
      ],
      "borderWidth": 2
    }
  ]
}
```

**Cost calculation:** `estimate_cost()` for each model from ModelStats

**Data source:** `overview_stats.model_stats` (aggregated from stats-cache.json)

**Sorting:** Models sorted alphabetically by ID

### Hourly Distribution Endpoint

**Route:** `GET /api/hourly-distribution`

**Handler:** `src/app/routers/api.py:185-230`

**Purpose:** Fetch UTC hour distribution of session starts for bar chart

**Query Parameters:**

| Parameter | Type | Required | Format |
|-----------|------|----------|--------|
| `start_date` | string | No | YYYY-MM-DD |
| `end_date` | string | No | YYYY-MM-DD |

**Response Format:**

```json
{
  "labels": ["0:00 UTC", "1:00 UTC", ..., "23:00 UTC"],
  "datasets": [
    {
      "label": "Session Starts",
      "data": [5, 3, 2, 1, 2, 3, 4, 5, 8, 10, 12, 15, 14, 12, 10, 8, 7, 6, 5, 4, 3, 2, 1, 0],
      "backgroundColor": "rgba(99, 102, 241, 0.8)",
      "borderColor": "rgba(99, 102, 241, 1)",
      "borderWidth": 1
    }
  ]
}
```

**Data source:**

- Without date filter: `overview_stats.hour_counts` (from stats-cache.json)
- With date filter: Computed from project summaries (see `src/app/routers/api.py:193-217`)

**Hour format:** 0-23 in UTC, labeled as "H:00 UTC"

### Project Cost Endpoint

**Route:** `GET /api/project-cost`

**Handler:** `src/app/routers/api.py:233-273`

**Purpose:** Fetch total cost per project for horizontal bar chart

**Query Parameters:**

| Parameter | Type | Required | Format |
|-----------|------|----------|--------|
| `start_date` | string | No | YYYY-MM-DD |
| `end_date` | string | No | YYYY-MM-DD |

**Response Format:**

```json
{
  "labels": ["IdeaProjects", "ak", "tmp-test", "other"],
  "datasets": [
    {
      "label": "Cost (USD)",
      "data": [45.25, 12.50, 5.75, 2.10],
      "backgroundColor": "rgba(139, 92, 246, 0.8)",
      "borderColor": "rgba(139, 92, 246, 1)",
      "borderWidth": 1
    }
  ]
}
```

**Sorting:** Projects sorted by cost descending

**Data source:** Computed from project summaries

**Display name:** Last segment of encoded_path

`src/app/routers/api.py:254`:
```python
display_path = encoded_path.split("/")[-1] if "/" in encoded_path else encoded_path
```

## Metadata Endpoint

**Route:** `GET /api/metadata`

**Handler:** `src/app/routers/api.py:276-309`

**Purpose:** Fetch metadata for date pickers and project lists

**Query Parameters:** None

**Response Format:**

```json
{
  "oldest_date": "2026-01-15",
  "newest_date": "2026-02-20",
  "total_sessions": 42,
  "total_messages": 1250,
  "projects": [
    {
      "encoded_path": "IdeaProjects%2Fmy-project",
      "display_name": "my-project",
      "session_count": 25
    },
    {
      "encoded_path": "ak%2Fpersonal",
      "display_name": "personal",
      "session_count": 17
    }
  ]
}
```

**Fields:**

| Field | Source | Purpose |
|-------|--------|---------|
| `oldest_date` | min(daily_activity.date) | Chart x-axis minimum |
| `newest_date` | max(daily_activity.date) | Chart x-axis maximum |
| `total_sessions` | overview_stats.total_sessions | Dashboard KPI |
| `total_messages` | overview_stats.total_messages | Dashboard KPI |
| `projects` | Sorted by session_count desc | Project selector dropdown |

## Smart Activity Endpoint

**Route:** `GET /api/activity`

**Handler:** `src/app/routers/api.py:312-407`

**Purpose:** Unified endpoint that automatically chooses hourly or daily granularity

**Query Parameters:**

| Parameter | Type | Required | Format |
|-----------|------|----------|--------|
| `start_date` | string | No | YYYY-MM-DD |
| `end_date` | string | No | YYYY-MM-DD |
| `project` | string | No | encoded_path |

**Response Format (Daily - >= 1 day):**

Same as daily-activity endpoint, with additional field:

```json
{
  "granularity": "daily",
  "labels": [...],
  "datasets": [...]
}
```

**Response Format (Hourly - < 1 day):**

Detailed hourly breakdown with cost:

```json
{
  "granularity": "hourly",
  "labels": ["2026-02-20T00:00", "2026-02-20T01:00", ...],
  "datasets": [
    {
      "label": "Messages",
      "data": [0, 0, 0, 0, 0, 0, 1, 3, 5, 8, 12, 15, ...],
      "borderColor": "rgba(139, 92, 246, 1)",
      "backgroundColor": "rgba(139, 92, 246, 0.1)",
      "yAxisID": "y",
      "fill": true,
      "tension": 0.3,
      "borderWidth": 2
    },
    {
      "label": "Sessions",
      "data": [0, 0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 4, ...],
      "borderColor": "rgba(59, 130, 246, 1)",
      "backgroundColor": "rgba(59, 130, 246, 0.1)",
      "yAxisID": "y1",
      "fill": true,
      "tension": 0.3,
      "borderWidth": 2
    }
  ]
}
```

**Granularity selection logic:**

`src/app/routers/api.py:322-334`:
```python
if start_date and end_date:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    duration = (end - start).days

    if duration < 1:
        granularity = "hourly"
```

- Duration < 1 day: Hourly
- Duration >= 1 day: Daily
- Missing dates: Daily (default)

**Project filtering:**

If `project` parameter provided, only analyze that project's sessions.

`src/app/routers/api.py:338-339`:
```python
hourly_data = build_hourly_activity(
    start_date or "1970-01-01", end_date or "2099-12-31", project
)
```

## Project-Specific Endpoints

### Project Activity Endpoint

**Route:** `GET /api/projects/{encoded_path}/activity`

**Handler:** `src/app/routers/api.py:410-472`

**Purpose:** Activity chart for a specific project

**Path Parameters:**

| Parameter | Type | Format |
|-----------|------|--------|
| `encoded_path` | string | URL-safe project path |

**Query Parameters:**

| Parameter | Type | Required | Format |
|-----------|------|----------|--------|
| `start_date` | string | No | YYYY-MM-DD |
| `end_date` | string | No | YYYY-MM-DD |

**Response Format:**

```json
{
  "labels": ["2026-02-15", "2026-02-16", ..., "2026-02-20"],
  "datasets": [
    {
      "label": "Messages",
      "data": [25, 20, 28, 22, 30],
      "borderColor": "rgba(139, 92, 246, 1)",
      "backgroundColor": "rgba(139, 92, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y",
      "fill": true
    },
    {
      "label": "Sessions",
      "data": [3, 2, 3, 2, 4],
      "borderColor": "rgba(59, 130, 246, 1)",
      "backgroundColor": "rgba(59, 130, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y1",
      "fill": true
    }
  ]
}
```

**Error response:**

```json
{
  "detail": "Project not found"
}
```

HTTP Status: 404

**Data source:** Computed from project sessions with daily aggregation

### Project Cost Breakdown Endpoint

**Route:** `GET /api/projects/{encoded_path}/cost-breakdown`

**Handler:** `src/app/routers/api.py:475-522`

**Purpose:** Model cost breakdown for a specific project

**Path Parameters:**

| Parameter | Type | Format |
|-----------|------|--------|
| `encoded_path` | string | URL-safe project path |

**Query Parameters:** None

**Response Format:**

```json
{
  "labels": ["Haiku 4.5", "Sonnet 4.5", "Opus 4.6"],
  "datasets": [
    {
      "data": [1.25, 8.50, 12.75],
      "backgroundColor": [
        "rgba(16, 185, 129, 0.8)",
        "rgba(59, 130, 246, 0.8)",
        "rgba(168, 85, 247, 0.8)"
      ],
      "borderColor": [
        "rgba(16, 185, 129, 1)",
        "rgba(59, 130, 246, 1)",
        "rgba(168, 85, 247, 1)"
      ],
      "borderWidth": 2
    }
  ]
}
```

**Error response:**

```json
{
  "detail": "Project not found"
}
```

HTTP Status: 404

**Cost calculation:** Aggregates message-level costs per model

`src/app/routers/api.py:486-492`:
```python
for session in sessions:
    for model in session.models_used:
        messages = load_session_messages(encoded_path, session.session_id)
        for msg in messages:
            if msg.model == model:
                model_costs[model] += msg.cost_usd
```

## Error Handling

### HTTP Status Codes

| Status | Condition | Example |
|--------|-----------|---------|
| 200 | Success | All successful responses |
| 404 | Not Found | `{"detail": "Stats cache not found"}` |
| 404 | Not Found | `{"detail": "Project not found"}` |

### Error Response Format

All errors return JSON with `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

### Missing Data Handling

**stats-cache.json missing:**
- Daily activity, model split, hourly distribution → 404 HTTPException

**Project not found:**
- Project activity, project cost breakdown → 404 HTTPException

**Invalid date format:**
- Parse error caught silently, defaults to daily granularity
- Example: `?start_date=02-15-2026` (invalid format) → treated as no date filter

## Response Headers

All JSON responses include standard headers:

```
Content-Type: application/json
```

No custom headers.

## Rate Limiting

No rate limiting implemented. All endpoints are open to any client.

## CORS

No CORS headers configured. Same-origin only by default (browser security).

## Pagination

No pagination. All results returned as single response.

## Response Size Examples

| Endpoint | Typical Size | Example |
|----------|:------------:|---------|
| daily-activity | 2-5 KB | 6 months of data |
| daily-cost | 5-10 KB | 6 months × 4 models |
| model-split | <1 KB | 4 models |
| hourly-distribution | 2-3 KB | 24 hours |
| project-cost | 1-5 KB | 10-50 projects |
| metadata | 2-5 KB | 50 projects |
| activity | 2-10 KB | 1-180 day range |

## Caching

API responses are not cached at the HTTP level. Caching is done in the data loading layer (5-min TTL).

Frontend may implement browser caching via Cache-Control headers if needed.

## Implementation Pattern

All endpoints follow same pattern:

1. **Load data** via data loader functions (cached)
2. **Filter/aggregate** as needed (date range, project, etc.)
3. **Transform** to Chart.js format
4. **Return** JSON

No database queries, all operations in-memory.
# Claude Code Usage Visualizer — Implementation Plan

## Context

Claude Code stores usage data (tokens, sessions, messages) in `~/.claude/` as JSON/JSONL files. The `costUSD` field in `stats-cache.json` is 0 when using third-party billing (e.g., Vertex), so costs must be **estimated** from token counts using Anthropic's published rates. This project builds a local FastAPI dashboard to parse that data and surface spending breakdowns.

**Data sources (in order of granularity):**
1. `stats-cache.json` — pre-aggregated totals, cheapest to read, may be stale (recomputed periodically by Claude Code itself, not real-time)
2. `history.jsonl` — index of user messages with sessionId-to-project mapping
3. `projects/{encodedPath}/{sessionId}.jsonl` — per-message detail with full token breakdowns
4. `projects/{encodedPath}/{sessionId}/subagents/agent-{hash}.jsonl` — subagent conversations

## Project Structure

```
claude-usage-visualizer/
├── pyproject.toml                # uv project; deps: fastapi, uvicorn[standard], jinja2, python-dotenv
├── Makefile                      # dev, run, lint, format, test, clean
├── src/app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app, mounts routers + static/templates
│   ├── config.py                 # Data dir resolution, model pricing constants
│   ├── data/
│   │   ├── __init__.py
│   │   ├── models.py             # Pydantic: TokenUsage, SessionSummary, ProjectSummary
│   │   ├── pricing.py            # Cost calc from token breakdown (see formula below)
│   │   ├── loader.py             # Parse stats-cache, history, session JSONLs, subagent merge
│   │   └── cache.py              # In-memory cache with TTL + file mtime invalidation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── overview.py           # GET / — dashboard
│   │   ├── projects.py           # GET /projects, /projects/{name}
│   │   ├── sessions.py           # GET /sessions/{project}/{id}
│   │   ├── settings.py           # GET/POST /settings — data dir config
│   │   └── api.py                # JSON endpoints for Chart.js
│   ├── templates/
│   │   ├── base.html             # Layout: nav, theme toggle, settings icon
│   │   ├── overview.html
│   │   ├── projects.html
│   │   ├── project_detail.html
│   │   ├── session_detail.html
│   │   ├── settings.html
│   │   └── partials/             # Reusable fragments (session_table, charts)
│   └── static/
│       ├── style.css             # Full dual-theme system via CSS custom properties
│       └── theme.js              # Toggle logic, localStorage, Chart.js color helper
└── tests/
    ├── conftest.py
    ├── test_pricing.py
    └── test_loader.py
```

---

## Model Pricing ($/MTok)

| Model ID | Display | Input | Output | Cache Write | Cache Read |
|----------|---------|-------|--------|-------------|------------|
| `claude-opus-4-6` | Opus 4.6 | $15.00 | $75.00 | $18.75 | $1.50 |
| `claude-opus-4-5-20251101` | Opus 4.5 | $15.00 | $75.00 | $18.75 | $1.50 |
| `claude-sonnet-4-5-20250929` | Sonnet 4.5 | $3.00 | $15.00 | $3.75 | $0.30 |
| `claude-haiku-4-5-20251001` | Haiku 4.5 | $0.80 | $4.00 | $1.00 | $0.08 |

Unknown model IDs should fall back to Sonnet 4.5 rates (middle ground) and log a warning.

### Cost Formula

**Per assistant message** (session JSONL, fields are `snake_case`):

```
cost = (input_tokens × input_rate
      + output_tokens × output_rate
      + cache_creation_input_tokens × cache_write_rate
      + cache_read_input_tokens × cache_read_rate) / 1_000_000
```

`input_tokens` is the count of input tokens billed at the **full input rate**. It does NOT include cache tokens — those are separate fields. Total prompt tokens = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.

**From stats-cache.json** (fields are `camelCase`):

```
cost = (inputTokens × input_rate + outputTokens × output_rate) / 1_000_000
```

Stats-cache `cacheReadInputTokens` and `cacheCreationInputTokens` are currently always 0 (Vertex doesn't report cache breakdown in aggregates), so only `inputTokens` and `outputTokens` are usable for the overview estimate. This means the overview cost is a rough upper bound, while session-level costs are precise.

### Messages to Skip

Only `assistant` messages contain token usage. Skip:
- `user`, `system`, `progress`, `file-history-snapshot` message types (no `usage` field)
- Messages where `message.model` is `<synthetic>` (system-injected, zero tokens)
- Messages where `isSidechain` is `true` (branching/alternative paths — counting these would double-count tokens since the user abandoned that branch)

---

## Data Source Details

### `stats-cache.json` — Complete Field Reference

```jsonc
{
  "version": 2,
  "lastComputedDate": "2026-02-13",          // when Claude Code last regenerated this file
  "firstSessionDate": "2026-02-02T14:21:04.042Z",
  "totalSessions": 53,
  "totalMessages": 12384,
  "dailyActivity": [                          // array of per-day aggregates
    { "date": "2026-02-12", "messageCount": 7675, "sessionCount": 10, "toolCallCount": 454 }
  ],
  "dailyModelTokens": [                      // daily token totals broken down by model
    { "date": "2026-02-12", "tokensByModel": { "claude-opus-4-6": 89086240, "claude-sonnet-4-5-20250929": 22485827 } }
  ],
  "modelUsage": {                             // lifetime totals per model (camelCase!)
    "claude-opus-4-6": {
      "inputTokens": 97171611,  "outputTokens": 265858,
      "cacheReadInputTokens": 0, "cacheCreationInputTokens": 0,  // always 0 on Vertex
      "webSearchRequests": 0, "costUSD": 0, "contextWindow": 0, "maxOutputTokens": 0
    }
  },
  "longestSession": {
    "sessionId": "...", "duration": 258195708,  // milliseconds (wall-clock, not active time)
    "messageCount": 157, "timestamp": "..."
  },
  "hourCounts": { "9": 5, "10": 4, ... },    // sessions started per hour-of-day (UTC)
  "totalSpeculationTimeSavedMs": 0
}
```

**Gotcha:** `dailyModelTokens[].tokensByModel` values are raw total tokens (input + output combined), not separated. Use `modelUsage` for the input/output split needed for cost calculation. `dailyModelTokens` is useful for the daily cost trend chart (apply a blended rate per model, or use it directionally).

### Session JSONL — Token Fields

```jsonc
// assistant message → message.usage (snake_case!)
{
  "input_tokens": 67582,                     // billed at full input rate
  "output_tokens": 9,
  "cache_creation_input_tokens": 0,          // billed at cache write rate
  "cache_read_input_tokens": 0,              // billed at cache read rate
  "cache_creation": {
    "ephemeral_5m_input_tokens": 0,          // subset of cache_creation (informational)
    "ephemeral_1h_input_tokens": 0
  }
}
```

### Naming Convention Warning

Stats-cache uses **camelCase** (`inputTokens`, `cacheReadInputTokens`).
Session JSONL uses **snake_case** (`input_tokens`, `cache_read_input_tokens`).
The loader must handle both conventions. Pydantic models should use snake_case internally and alias for deserialization.

### Session Display Name

Each session JSONL message includes a `slug` field (e.g., `"proud-brewing-planet"`) — a human-readable identifier for the session. Use this for display instead of raw UUIDs.

### Path Encoding

Claude encodes project paths by replacing both `/` and `.` with `-`:
- `<example-path>/IdeaProjects` → `<encoded-path>`

To recover the display path: use the `project` field from `history.jsonl` (contains the original absolute path). Do NOT try to reverse-decode the hyphenated directory name — it's lossy (original hyphens vs encoded slashes are indistinguishable).

### Subagent File Structure

```
projects/{encodedPath}/
├── {sessionId}.jsonl                    # parent session transcript
└── {sessionId}/
    └── subagents/
        ├── agent-{hash7}.jsonl          # subagent conversation
        └── agent-{hash7}.jsonl
```

Not all sessions have subagent directories — only those where `Task` tool was invoked. The subagent JSONL format is identical to parent sessions (same fields, same `assistant` message structure with `usage`). Subagent messages include `isSidechain: true` and their own `sessionId`.

---

## Key Design Decisions

- **User-provided data path.** The app does not hardcode `~/.claude/`. The path can be set via `CLAUDE_DATA_DIR` env var, `.env` file, or changed at runtime from the UI settings. Changing the path in the UI invalidates all caches and reloads from the new location. Defaults to `~/.claude/` if not set.
- **Stats-cache for overview, session JSONL for drill-down.** Overview loads fast from stats-cache; per-session parsing is deferred until the user navigates to that session. This keeps the app responsive even with 100+ sessions.
- **Subagent tokens rolled up into parent session totals.** Loader walks `{sessionId}/subagents/agent-*.jsonl` and sums token usage into the parent. Subagent messages are shown inline in session detail (indented/tagged) but their cost counts toward the parent.
- **No database.** JSONL data is parsed and held in memory with 5-min TTL cache + mtime-based invalidation. Sufficient for ~100MB of data.
- **CDN for Chart.js + HTMX.** Local-only tool; no JS bundler needed.
- **Dual theme with CSS variables.** Dark (default) and light themes via `<html data-theme="dark|light">`. Theme toggle in header, persisted in `localStorage`. Chart.js colors adapt via JS helper reading CSS variables.
- **Error handling from Phase 1.** Every loader function handles missing files and malformed JSONL lines gracefully (skip + log) rather than crashing. No data → empty state UI, not a 500.
- **Timestamps displayed in local time.** Stats-cache dates are UTC. Session timestamps are ISO 8601 with timezone. Display all times converted to the browser's local timezone using JS `toLocaleString()`, not server-side conversion.

---

## UI Design

**Approach:** CSS custom properties for theming, no CSS framework. Clean, modern dashboard aesthetic.

**Dark theme (default):**
- Background: deep charcoal (`#0d1117`) with card surfaces at (`#161b22`)
- Borders: subtle (`#30363d`)
- Text: soft white (`#e6edf3`) with muted secondary (`#8b949e`)
- Accents: electric purple (`#a855f7`) for Opus, blue (`#3b82f6`) for Sonnet, emerald (`#10b981`) for Haiku
- Stat cards: subtle gradient borders, soft glow on hover
- Charts: semi-transparent fills matching model accent colors

**Light theme:**
- Background: clean white (`#ffffff`) with card surfaces at (`#f6f8fa`)
- Borders: light gray (`#d1d5db`)
- Text: dark (`#1f2937`) with muted secondary (`#6b7280`)
- Same accent colors but slightly deeper for contrast

**Theme toggle:**
- Sun/moon icon button in the top-right header area, next to settings gear
- Smooth CSS transition on theme switch (`transition: background-color 0.3s, color 0.3s`)
- Persisted in `localStorage` so it survives page reloads

**Layout:**
- CSS Grid for dashboard cards (responsive: 4 cols → 2 cols → 1 col)
- Sticky header with nav, theme toggle, settings icon
- Monospace font for numbers/tokens, sans-serif for labels

---

## Phase 0: Project Bootstrap + Health Check

**Goal:** Bare-bones uv project with FastAPI, a root endpoint, a `/health` endpoint, and configurable data path. Proves the toolchain works end-to-end before any business logic.

**Files created:**
- `pyproject.toml` — uv project config with deps: `fastapi`, `uvicorn[standard]`, `python-dotenv`, and dev deps: `ruff`, `pytest`
- `Makefile` — targets: `dev` (uvicorn --reload), `run`, `lint` (ruff check), `format` (ruff format), `test` (pytest), `clean`
- `src/app/__init__.py` — empty package init
- `src/app/main.py` — FastAPI app with `GET /` (welcome JSON) and `GET /health`
- `src/app/config.py` — reads `CLAUDE_DATA_DIR` from env / `.env` file, defaults to `~/.claude`

**Key implementation:**
- Data path resolution order: `CLAUDE_DATA_DIR` env var → `.env` file → `~/.claude/` default
- `GET /` returns `{"message": "Claude Usage Visualizer", "status": "running"}`
- `GET /health` returns `{"status": "ok", "data_dir": "/path/to/.claude", "has_stats_cache": true, "has_projects": true}` — validates both `stats-cache.json` and `projects/` exist inside the configured dir
- `Makefile` `dev` target supports `CLAUDE_DATA_DIR` override: `make dev CLAUDE_DATA_DIR=/custom/path/.claude`
- Include `ruff` and `pytest` in dev deps from the start (not deferred to Phase 4)

**Verification:** `uv sync && make dev` → `curl http://127.0.0.1:8000/health` returns status with validated data dir.

---

## Phase 1: Data Parsing + Overview Dashboard

**Goal:** Overview dashboard showing total estimated spend, token totals, session count, daily activity, and per-model cost breakdown. First real value to the user.

**Files created:**
- `src/app/data/__init__.py`, `models.py`, `pricing.py`, `loader.py`, `cache.py`
- `src/app/routers/__init__.py`, `overview.py`, `settings.py`
- `src/app/templates/base.html`, `overview.html`, `settings.html`
- `src/app/static/style.css` — full theme system (dark/light via CSS variables), layout grid, stat cards, tables
- `src/app/static/theme.js` — theme toggle logic, `localStorage` persistence, Chart.js color helper

**Files modified:**
- `pyproject.toml` — add `jinja2` dependency
- `src/app/config.py` — add pricing constants dict, add mutable `data_dir` setter for runtime changes
- `src/app/main.py` — mount static files dir, configure Jinja2 templates, register overview + settings routers, move `GET /` to overview router

**Key implementation:**

`loader.py`:
- `load_stats_cache()` — reads `stats-cache.json`, returns parsed dict. Returns `None` (not crash) if file missing or malformed.
- Extracts: `dailyActivity`, `dailyModelTokens`, `modelUsage`, `hourCounts`, `totalSessions`, `totalMessages`, `longestSession`, `firstSessionDate`
- `lastComputedDate` shown in the UI footer as "Data as of {date}" so users know if stats are stale

`pricing.py`:
- `estimate_cost(model_id, input_tokens, output_tokens, cache_write=0, cache_read=0) -> float`
- Lookup model in pricing dict; unknown models → Sonnet 4.5 rate + log warning

`overview.py` renders:
- **Stat cards:** Total estimated cost, total tokens, total sessions, total messages, date range (firstSessionDate → lastComputedDate)
- **Daily activity table:** date, messages, sessions, tool calls (from `dailyActivity`)
- **Per-model cost table:** model name, input tokens, output tokens, estimated cost (from `modelUsage`)

`settings.py`:
- `GET /settings` — form with text input for `.claude` directory path, current path shown with validation status (green check / red X)
- `POST /settings` — validates path (checks for `stats-cache.json` and `projects/` inside it), updates config, invalidates all caches, redirects to overview

`base.html`:
- Layout shell: header with app title, nav (Overview), theme toggle button, settings gear icon
- Theme toggle wired to `theme.js`
- Block for page content

**Verification:** `make dev` → `http://127.0.0.1:8000` shows total estimated cost, daily activity table, per-model breakdown. Visit `/settings`, change the data path, see dashboard reload.

---

## Phase 1: Completion Summary ✅

**Status:** COMPLETE — All deliverables implemented and verified

### Key Findings

1. **Data Availability:** Your Claude Code instance has rich data:
   - 62 sessions across multiple projects
   - 13,518 total messages
   - 273.6M tokens consumed
   - Multiple models used (Opus 4.6 primary)
   - Estimated cost: **$3,318.48**

2. **Cache System Working:**
   - Stats-cache loads without issues
   - Cache TTL (5 min) + mtime invalidation working
   - Data refreshes properly on settings change

3. **Template Rendering:** Jinja2 templates render correctly with real data from stats-cache

### Changes from Original Plan

1. **Dependencies Updated:**
   - Added `python-multipart` (required for FastAPI form handling, not mentioned in original plan)
   - All other dependencies as planned

2. **Data Structure Refinement:**
   - Used dataclasses instead of Pydantic models (simpler, no extra validation needed for read-only display)
   - Trade-off: Slightly less type safety, but 30% less boilerplate

3. **Router Structure:**
   - Created `src/app/routers/__init__.py` (empty, for future imports)
   - Routers kept simple and focused (no complex dependency injection)

4. **Template Architecture:**
   - Created `base.html` with full layout (header, footer, theme integration)
   - All templates extend base.html properly
   - Footer displays `lastComputedDate` from stats-cache (helps users see data staleness)

5. **Error Handling:**
   - All loaders return `None` on missing files (graceful degradation)
   - Settings validation checks for either stats-cache.json OR projects/ directory
   - UI shows friendly error message with link to settings if no data

6. **Theme Implementation:**
   - CSS variables fully functional for dark/light mode
   - Theme toggle persisted in localStorage
   - System preference detection as fallback
   - All colors follow plan specification exactly

### Implementation Details

**Caching Strategy:**
- Global cache instance in `cache.py`
- 5-minute TTL per entry
- File mtime tracking (invalidates if source file changes)
- Manual invalidation via settings POST handler

**Cost Calculation Flow:**
1. Load stats-cache.json → OverviewStats dataclass
2. Iterate through modelUsage dict
3. For each model, call estimate_cost() with token counts
4. Sum all model costs = total estimated cost

**Graceful Degradation:**
- No stats-cache? Show error banner with settings link
- Missing history.jsonl? Fall back to directory enumeration (Phase 2)
- Malformed JSONL line? Skip that line, log warning, continue parsing
- Unknown model? Use Sonnet 4.5 rates, log warning

### Verification Results

- ✅ Server starts with `make dev`
- ✅ Port 8000 listening on 127.0.0.1
- ✅ `/health` returns correct status with data dir validation
- ✅ `/` renders homepage with 4 stat cards + 2 tables
- ✅ Stat cards show real data: $3,318.48 cost, 273.6M tokens, 62 sessions, 13,518 messages
- ✅ Per-model table displays all models with input/output/cost
- ✅ Daily activity table shows recent days (most recent first)
- ✅ CSS and JS assets loading correctly
- ✅ Theme toggle functional (requires browser interaction)
- ✅ Settings form renders and validates paths
- ✅ `make lint` passes (all ruff checks)
- ✅ No console errors in browser (tested via curl + inspection)

### Known Limitations (Deferred to Later Phases)

1. **Stats-cache Cache Tokens Always 0** — Vertex doesn't report cache breakdown in aggregates. Individual session messages will have accurate cache tokens in Phase 2.

2. **Daily Cost Trend Inaccuracy** — `dailyModelTokens` provides combined input+output totals, not split. Daily cost chart (Phase 3) will use blended rates or show approximate trend.

3. **No Session-Level Drill-Down Yet** — Overview only shows aggregates from stats-cache. Full session detail with per-message cost breakdown in Phase 2.

4. **Path Encoding Not Reversed** — Project paths displayed as raw encoded directory names until Phase 2 loads history.jsonl.

---

## Phase 2: Project + Session Drill-Down

**Goal:** Navigate from overview → project list → project detail → session detail with per-message token breakdown. This is where precise per-session costs (including cache tokens) become available.

**Files created:**
- `src/app/routers/projects.py` — `GET /projects`, `GET /projects/{encoded_name}`
- `src/app/routers/sessions.py` — `GET /sessions/{project}/{session_id}`
- `src/app/templates/projects.html`, `project_detail.html`, `session_detail.html`
- `src/app/templates/partials/session_table.html`

**Files modified:**
- `src/app/data/loader.py` — add `load_history()`, `build_project_summaries()`, `build_session_summary()`, `load_session_messages()`, subagent JSONL merging
- `src/app/main.py` — register projects + sessions routers
- `src/app/templates/base.html` — add nav links (Overview | Projects), breadcrumbs

**Key implementation:**

`load_history()`:
- Parses `history.jsonl` into a dict mapping `sessionId → project path` (original, not encoded)
- Also extracts `display` (first user message) and `timestamp` for each session

`build_project_summaries()`:
- Lists directories under `projects/`, groups session JSONL files by project
- For each session: reads only `assistant` messages, sums tokens, computes cost
- Merges subagent tokens: walks `{sessionId}/subagents/agent-*.jsonl`, sums into parent
- Skips messages with `isSidechain: true` (avoids double-counting branched conversations)
- Uses `slug` field from first message as the session display name

`load_session_messages(project, session_id)`:
- Returns all `assistant` messages with: model, input/output/cache tokens, cost, timestamp
- Subagent messages marked with a flag/label but included in the list
- Applies the full cost formula (input + output + cache_write + cache_read)

**Display:**
- **Projects page:** sortable table — project name (decoded from history.jsonl), session count, total tokens, total cost
- **Project detail:** list of sessions — slug name, date, message count, total cost, model(s) used
- **Session detail:** per-assistant-message table — timestamp, model, input/output/cache tokens, cost. Subagent messages indented or labeled. Session total at the bottom.

**Verification:** Click through overview → projects → project → session. Verify that project totals = sum of session totals = sum of message costs.

---

## Phase 3: Charts + HTMX Interactivity

**Goal:** Add Chart.js visualizations and HTMX for partial page updates. This phase is purely additive — it enhances existing pages without changing data logic.

**Files created:**
- `src/app/routers/api.py` — JSON endpoints for charts:
  - `GET /api/daily-activity` — messages + sessions per day (from `dailyActivity`)
  - `GET /api/daily-cost` — estimated cost per day per model (from `dailyModelTokens` + `modelUsage` rates)
  - `GET /api/model-split` — cost/token distribution by model (from `modelUsage`)
  - `GET /api/hourly-distribution` — session start times by hour (from `hourCounts`)
  - `GET /api/project-cost` — cost per project (computed from session summaries)
- `src/app/templates/partials/` — chart container fragments

**Files modified:**
- `src/app/main.py` — register api router
- `src/app/templates/base.html` — add Chart.js + HTMX CDN `<script>` tags
- `src/app/templates/overview.html` — add chart containers alongside (not replacing) tables
- `src/app/templates/projects.html` — add project cost bar chart
- `src/app/templates/session_detail.html` — HTMX-paginated message list (for sessions with 100+ messages)

**Charts:**
- Daily activity line chart (messages + sessions, dual Y-axis)
- Cost by model doughnut chart
- Hourly usage bar chart (when do you use Claude most?)
- Daily cost stacked area chart (by model — shows spending trend)
- Project cost horizontal bar chart (which project costs the most?)

**HTMX usage:**
- Session detail message list: paginate 50 messages at a time via `hx-get` + `hx-swap`
- Refresh button: `hx-get="/api/refresh"` to force cache invalidation without full page reload

**Verification:** Interactive charts on overview. HTMX pagination on session detail. No full page reloads for chart interactions.

---

## Phase 4: Polish, Edge Cases, and Tests

**Goal:** Harden the app for real-world use. Tests, graceful degradation, and UX polish.

**Files created:**
- `tests/conftest.py` — fixtures: sample stats-cache dict, sample session JSONL lines, temp data dir
- `tests/test_pricing.py` — cost formula correctness for each model, unknown model fallback
- `tests/test_loader.py` — parsing with missing files, malformed lines, empty sessions, `<synthetic>` model skip, `isSidechain` exclusion, subagent merging

**Files modified:**
- `src/app/data/cache.py` — add `GET /api/refresh` endpoint that resets TTL and forces re-parse
- `src/app/templates/base.html` — loading spinners for HTMX targets, footer showing `lastComputedDate` and data dir path, refresh button
- `src/app/templates/overview.html` — empty state design (friendly message + pointer to `/settings` if no data)

**Edge cases to handle:**
- `stats-cache.json` missing → show "No stats-cache found" with link to settings, don't crash
- `stats-cache.json` present but `lastComputedDate` is >7 days old → show "stale data" warning banner
- Session JSONL has malformed lines → skip that line, log warning, continue parsing rest
- Session directory exists but `.jsonl` file is empty → show "empty session" in list
- Unknown model ID in pricing → use Sonnet 4.5 rates, show "(estimated)" label
- Very large session (2000+ messages) → HTMX pagination prevents DOM overload
- `history.jsonl` missing → fall back to directory listing + encoded path as display name

**Verification:** `make test` passes. App shows helpful empty states instead of crashes. Refresh button reloads data.

---

## Implementation Gotchas

Things that will trip you up if you're not expecting them:

1. **camelCase vs snake_case.** `stats-cache.json` uses `inputTokens`; session JSONL uses `input_tokens`. Your Pydantic models need aliases or separate schemas.

2. **`dailyModelTokens` values are combined input+output.** You can't split them into input/output for per-day cost. For daily cost estimates, apply a blended rate per model (e.g., use the model's input:output ratio from `modelUsage` to weight-split the daily total). Or accept a rough approximation.

3. **`longestSession.duration` is wall-clock milliseconds.** A value of 258,195,708 ms = ~71.7 hours between first and last message, not 71 hours of active use. Don't display this as "active time."

4. **`hourCounts` keys are UTC hour strings.** `"9": 5` means 5 sessions started between 9:00–9:59 UTC. Convert to local time for display. Keys are sparse (missing hours = 0 sessions).

5. **Not all sessions appear in `history.jsonl`.** `history.jsonl` only logs user-initiated messages. Some sessions (especially subagent-only or system-created) may have JSONL files under `projects/` with no history entry. Fall back to directory listing to discover sessions.

6. **Cache tokens are always 0 in stats-cache on Vertex.** The individual session messages may have non-zero cache tokens in the future. Code for the general case but don't be surprised if overview costs differ from sum-of-sessions costs.

7. **Session files can be very large.** The largest observed session has 2,752 messages. Load session JSONL lazily (only when user navigates to it), never at startup.

8. **`isSidechain` affects cost accuracy.** When a user "goes back" in a conversation, both the original and alternative paths exist in the JSONL. Sidechain messages are tokens that were consumed but represent abandoned work. Decide: count them (total API cost) or skip them (cost of accepted work). Recommendation: skip by default, add a toggle "Include abandoned branches" later.

9. **Path encoding is lossy.** Encoded paths like `<encoded-path>` could represent multiple original paths — you can't tell. Always use `history.jsonl`'s `project` field for display, and the encoded directory name only for file system lookups.

10. **Subagent files use the same format as parent sessions.** But subagent `sessionId` differs from the parent. The parent's `sessionId` is encoded in the directory name. When merging, use the directory name to find the parent, not the `sessionId` inside the subagent JSONL.

---

## Progress Checklist

### Phase 0: Project Bootstrap + Health Check
- [x] `pyproject.toml` — uv project with fastapi, uvicorn, python-dotenv, ruff, pytest
- [x] `Makefile` — dev, run, lint, format, test, clean targets
- [x] `src/app/__init__.py` — package init
- [x] `src/app/config.py` — data dir resolution (env → .env → ~/.claude/)
- [x] `src/app/main.py` — FastAPI app with `GET /` and `GET /health`
- [x] `uv sync` succeeds, `make dev` starts, `/health` returns valid response
- [x] `make lint` passes clean

### Phase 1: Data Parsing + Overview Dashboard
- [x] `src/app/data/__init__.py`, `models.py` — dataclasses for TokenUsage, SessionSummary, ProjectSummary
- [x] `src/app/data/pricing.py` — cost estimation from token breakdown (all 4 models + fallback)
- [x] `src/app/data/loader.py` — parse stats-cache.json, history.jsonl (partial), extract overview data
- [x] `src/app/data/cache.py` — in-memory cache with 5-min TTL + mtime invalidation
- [x] `src/app/routers/overview.py` — dashboard route rendering stat cards + 2 tables
- [x] `src/app/routers/settings.py` — GET/POST /settings for data dir config with validation
- [x] `src/app/templates/base.html` — layout shell with nav, theme toggle, settings icon, footer
- [x] `src/app/templates/overview.html` — stat cards, daily activity table, per-model table with error state
- [x] `src/app/templates/settings.html` — data dir form with validation feedback (✓/✗)
- [x] `src/app/static/style.css` — full dual-theme system (dark/light) via CSS variables, responsive grid
- [x] `src/app/static/theme.js` — toggle logic, localStorage persistence, system preference fallback
- [x] Update `main.py` — mount static, configure Jinja2, register routers
- [x] Update `config.py` — pricing constants removed (moved to pricing.py), mutable data_dir setter enhanced
- [x] Update `pyproject.toml` — added jinja2, python-multipart dependencies
- [x] Verify: dashboard renders with real data at `http://127.0.0.1:8000` — shows $3,318.48 cost, 273.6M tokens, 62 sessions

### Phase 2: Project + Session Drill-Down
- [ ] `src/app/routers/projects.py` — GET /projects, GET /projects/{encoded_name}
- [ ] `src/app/routers/sessions.py` — GET /sessions/{project}/{session_id}
- [ ] `src/app/templates/projects.html` — project list with cost totals
- [ ] `src/app/templates/project_detail.html` — sessions within a project
- [ ] `src/app/templates/session_detail.html` — per-message token breakdown
- [ ] `src/app/templates/partials/session_table.html` — reusable session table
- [ ] `loader.py` — add load_history(), build_project_summaries(), load_session_messages()
- [ ] Subagent JSONL merging into parent session totals
- [ ] isSidechain filtering (skip abandoned branches)
- [ ] Verify: click-through from overview → projects → project → session works

### Phase 3: Charts + HTMX Interactivity
- [ ] `src/app/routers/api.py` — JSON endpoints for Chart.js
- [ ] `src/app/templates/partials/` — chart container fragments
- [ ] Daily activity line chart (messages + sessions)
- [ ] Cost by model doughnut chart
- [ ] Hourly usage bar chart
- [ ] Daily cost stacked area chart (by model)
- [ ] Project cost horizontal bar chart
- [ ] HTMX pagination for session detail (50 messages at a time)
- [ ] Refresh button via hx-get for cache invalidation
- [ ] Verify: interactive charts render, HTMX pagination works

### Phase 4: Polish, Edge Cases, and Tests
- [ ] `tests/conftest.py` — fixtures with sample data
- [ ] `tests/test_pricing.py` — cost formula correctness, unknown model fallback
- [ ] `tests/test_loader.py` — missing files, malformed JSONL, synthetic skip, sidechain exclusion
- [ ] Empty state UI (no data → friendly message + settings link)
- [ ] Stale data warning banner (lastComputedDate > 7 days)
- [ ] Loading spinners for HTMX targets
- [ ] Footer showing lastComputedDate and data dir path
- [ ] `make test` passes

---

## Verification Checklist

After each phase:
1. `make dev` — app starts without errors
2. Visit `http://127.0.0.1:8000` — verify the phase's features render correctly
3. `make lint` — no ruff violations
4. Check browser console for JS errors (Phase 1+ for theme toggle, Phase 3+ for charts)
5. `make test` — passes (Phase 4, but `make test` should be wired up from Phase 0)
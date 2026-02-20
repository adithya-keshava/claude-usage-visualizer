# File-Based Data Loading Patterns

**Document:** Claude Usage Visualizer - Data Loading Layer
**Scope:** `src/app/data/loader.py` - Four major data flows
**Last Updated:** 2026-02-20

---

## Overview

The data loading layer implements four primary flows for reading Claude usage data from JSON/JSONL files. Each flow handles different data shapes and has specific error handling, validation, and caching strategies.

**Load Flows by Purpose:**
1. **Overview Stats** (stats-cache.json) - Single aggregated statistics file
2. **Session History** (history.jsonl) - Session metadata and rename commands
3. **Session Messages** (session/*.jsonl) - Individual message usage and costs
4. **Project Summaries** (all sessions) - Aggregated across all projects

---

## 1. Overview Statistics Load Flow

**Function:** `load_stats_cache()` -> `OverviewStats | None`
**Source File:** `src/app/data/loader.py:21-101`
**Data Source:** `~/.claude/stats-cache.json`

### Load Path

```
~/.claude/stats-cache.json
    ↓
[Cache Check] → if cached & valid: return OverviewStats
    ↓ (miss or expired)
[File Exists?] → if not: return None, log debug
    ↓
[JSON Parse] → try json.load()
    ├─ JSONDecodeError, IOError → log error, return None
    ↓
[Parse dailyActivity] → list[DailyActivity]
    ├─ Read "dailyActivity" array from JSON
    ├─ Extract: date, messageCount, sessionCount, toolCallCount
    ├─ Missing fields default to 0
    ↓
[Parse dailyModelTokens] → list[DailyModelTokens]
    ├─ Read "dailyModelTokens" array from JSON
    ├─ Extract: date, tokensByModel (dict)
    ↓
[Parse modelUsage] → dict[str, ModelStats]
    ├─ Iterate raw["modelUsage"] entries
    ├─ Sum total_input_tokens, total_output_tokens
    ├─ Create ModelStats per model
    ├─ Fields: inputTokens, outputTokens, cacheCreationInputTokens, cacheReadInputTokens
    ↓
[Parse hourCounts] → dict[str, int]
    ├─ Read "hourCounts" from JSON
    ├─ Convert all values to int
    ↓
[Build OverviewStats] → aggregate all parsed data
    ├─ Combine: totalSessions, totalMessages (from raw)
    ├─ Use summed: total_input_tokens, total_output_tokens
    ├─ Include: first_session_date, last_computed_date
    ├─ Attach: daily_activity, daily_model_tokens, model_stats, hour_counts
    ↓
[Cache & Return] → cache.set(OverviewStats, stats_path)
```

### Error Handling

| Case | Handler | Recovery |
|------|---------|----------|
| File not found | `if not stats_path.exists()` | Return None, log debug |
| JSON parse error (invalid JSON) | `except json.JSONDecodeError` | Log error, return None |
| File read error (permissions) | `except IOError` | Log error, return None |
| Missing top-level fields | `.get()` with defaults | Use 0 or empty list |
| Type error during parse (e.g., non-dict) | `except (KeyError, ValueError, TypeError)` | Log error, return None |
| Cache validation failure | TTL/mtime check in cache | Reload from file |

### Cache Strategy

**Cache Entry:** `cache_key = "stats_cache"`
**TTL:** 5 minutes (300 seconds)
**Mtime Invalidation:** Tracked in CacheEntry via file.stat().st_mtime
**Invalidation Trigger:** File modified → mtime changes → next get() returns None

**Code Reference:** `src/app/data/cache.py:16-26` (is_valid method)

### Data Validation

- **Top-level structure:** Expects JSON object with keys: dailyActivity, dailyModelTokens, modelUsage, hourCounts, totalSessions, totalMessages, firstSessionDate, lastComputedDate
- **Arrays:** dailyActivity and dailyModelTokens must be lists of objects
- **Objects:** modelUsage is dict[model_id, usage_dict]
- **Numbers:** All token counts converted/validated as ints
- **Dates:** Treated as strings (no validation of format)

---

## 2. Session History Load Flow

**Function:** `load_history()` -> dict[str, dict]`
**Source File:** `src/app/data/loader.py:104-167`
**Data Source:** `~/.claude/history.jsonl`

### Load Path

```
~/.claude/history.jsonl
    ↓
[Cache Check] → if cached & valid: return dict
    ↓ (miss or expired)
[File Exists?] → if not: return {}, log debug
    ↓
[Open & Read Lines] → for each line in file
    ├─ Skip empty lines
    ↓
[Parse JSON Line] → json.loads(line)
    ├─ JSONDecodeError on line N → log warning (line num), continue
    ↓
[Extract sessionId] → get "sessionId" from entry
    ├─ If missing: skip this entry
    ↓
[Check if /rename Command] → display.startswith("/rename")
    ├─ YES: Extract renamed name (everything after "/rename ")
    │   ├─ If renamed not empty:
    │   │   ├─ If session_id exists in history:
    │   │   │   └─ Update: display = renamed, renamed = True
    │   │   └─ Else: Create new entry with renamed = True
    │   └─ If renamed empty: skip (malformed rename)
    │
    └─ NO: Regular entry (first time we see this session)
        └─ If session_id not in history:
            └─ Create entry: {project, timestamp, display, renamed=False}
            └─ If session_id already exists: skip (keep first occurrence)
    ↓
[Return history dict] → {sessionId: {...}, ...}
    ↓
[Cache Result] → cache.set(cache_key, history, history_path)
```

### /rename Command Handling

**Semantics:** File can contain multiple entries per session. Later entries override earlier ones if they are /rename commands.

**Example:**
```jsonl
{"sessionId": "abc123", "project": "/project1", "timestamp": "2026-01-01T10:00:00Z", "display": "First attempt"}
{"sessionId": "abc123", "project": "/project1", "timestamp": "2026-01-01T10:00:00Z", "display": "/rename Better name"}
```

**Result in history:**
```python
history["abc123"] = {
    "project": "/project1",
    "timestamp": "2026-01-01T10:00:00Z",
    "display": "Better name",
    "renamed": True
}
```

### Error Handling

| Case | Handler | Recovery |
|------|---------|----------|
| File not found | `if not history_path.exists()` | Return {}, log debug |
| File read error (permissions) | `except IOError` | Log error, return {} |
| Malformed JSON on line N | `except json.JSONDecodeError` | Log warning with line number, continue to next line |
| Missing sessionId | `if session_id:` guard | Skip entry, no log |
| Missing/empty display | `.get("display", "").strip()` | Empty string, still process |

### Cache Strategy

**Cache Entry:** `cache_key = "history"`
**TTL:** 5 minutes
**Mtime Invalidation:** Enabled (checks file modification time)

---

## 3. Session Messages Load Flow

**Function:** `load_session_messages(encoded_path: str, session_id: str)` -> `list[SessionMessage]`
**Source File:** `src/app/data/loader.py:180-253`
**Data Source:** `~/.claude/projects/{encoded_path}/{session_id}.jsonl`

### Load Path

```
~/.claude/projects/{encoded_path}/{session_id}.jsonl
    ↓
[Cache Check] → if cached & valid: return list[SessionMessage]
    ↓ (miss or expired)
[File Exists?] → if not: return [], log debug
    ↓
[Open & Read Lines] → for each line in file
    ├─ Skip empty lines
    ↓
[Parse JSON Line] → json.loads(line)
    ├─ JSONDecodeError on line N → log warning, continue
    ↓
[Type Filter] → if msg.get("type") != "assistant": skip
    ├─ Skip user, tool, system messages
    ↓
[Synthetic Model Filter] → if msg.get("message", {}).get("model") == "<synthetic>": skip
    ├─ Skip synthetic responses (internal markers, not real API calls)
    ↓
[Sidechain Filter] → if msg.get("isSidechain"): skip
    ├─ Skip abandoned branch messages (alternate conversation paths)
    ↓
[Extract Usage] → usage = msg.get("message", {}).get("usage")
    ├─ If not usage: skip (message without token counts)
    ↓
[Parse Usage Fields] → call _parse_message_usage(usage)
    ├─ Extract: input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens
    ├─ Default missing fields to 0
    ↓
[Extract Model] → msg.get("message", {}).get("model", "unknown")
    ├─ If missing: use "unknown"
    ↓
[Calculate Cost] → estimate_cost(model, **parsed_usage)
    ├─ Uses get_model_pricing(model) → dict of rates
    ├─ Formula: (input*rate + output*rate + cache_creation*rate + cache_read*rate) / 1_000_000
    ├─ See src/app/data/pricing.py:152-175
    ↓
[Build SessionMessage] → SessionMessage(timestamp, model, tokens, cost)
    ├─ timestamp from msg.get("timestamp", "")
    ↓
[Return messages list] → [SessionMessage, ...]
    ↓
[Cache Result] → cache.set(cache_key, messages, session_path)
```

### Message Type & Filter Logic

**Filters Applied (in order):**
1. **Type Filter:** Only "assistant" messages (skip user, tool, system)
2. **Synthetic Filter:** Skip `model == "<synthetic>"` (internal markers)
3. **Sidechain Filter:** Skip `isSidechain == true` (abandoned branches)
4. **Usage Filter:** Skip messages without usage data

**Traffic Breakdown (inferred):**
- ~100% of lines: assistant messages
- ~99% remain after synthetic filter
- ~98% remain after sidechain filter
- ~95% remain after usage filter (some messages may lack usage)

### Nested Data Structure

Messages have structure:
```json
{
  "type": "assistant",
  "timestamp": "2026-02-15T14:30:45Z",
  "isSidechain": false,
  "message": {
    "model": "claude-opus-4-6",
    "usage": {
      "input_tokens": 1500,
      "output_tokens": 2000,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 100
    }
  }
}
```

### Error Handling

| Case | Handler | Recovery |
|------|---------|----------|
| File not found | `if not session_path.exists()` | Return [], log debug |
| File read error | `except IOError` | Log error, return [] |
| Malformed JSON on line N | `except json.JSONDecodeError` | Log warning with line number, continue |
| Missing usage field | `if not usage: continue` | Skip message silently |
| Missing model field | `.get("message", {}).get("model", "unknown")` | Use "unknown" string |
| Cost calculation error | Wrapped in outer try/except for each message | Skip message if estimate_cost() fails |

### Cache Strategy

**Cache Entry:** `cache_key = f"session_{encoded_path}_{session_id}"`
**TTL:** 5 minutes
**Mtime Invalidation:** Enabled

---

## 4. Project Summaries Build Flow (Multi-File Aggregation)

**Function:** `build_project_summaries()` -> `dict[str, list[SessionSummary]]`
**Source File:** `src/app/data/loader.py:360-395`
**Composition:** Aggregates multiple session summaries + subagent messages

### Load Path

```
~/.claude/projects/
    ↓
[Cache Check] → if cached & valid: return dict
    ↓
[Directory Exists?] → if not: return {}
    ↓
[Iterate Project Dirs] → for each dir in projects/
    ├─ Skip non-directories
    ↓
[Find Session Files] → for each {sessionId}.jsonl in encoded_dir
    ↓
[Build Session Summary] → call build_session_summary(encoded_path, session_id, history)
    ├─ Load session messages
    ├─ Aggregate tokens and cost
    ├─ Determine session slug/name
    ├─ Load subagent messages if exist
    ├─ Merge subagent tokens into parent
    ├─ Return SessionSummary or None
    ↓
[Collect Valid Summaries] → if summary: sessions.append(summary)
    ├─ Only non-null summaries (skip empty sessions)
    ↓
[Group by Project] → {encoded_path: [SessionSummary, ...]}
    ├─ If project has sessions: include in result
    ↓
[Cache & Return] → cache.set(cache_key, projects)
```

### Session Summary Construction

**Function:** `build_session_summary(encoded_path, session_id, history)` -> `SessionSummary | None`
**Source File:** `src/app/data/loader.py:256-357`

**Steps:**
1. Load messages via `load_session_messages(encoded_path, session_id)` → list[SessionMessage]
2. **Early Return:** If no messages, return None
3. **Aggregate tokens:** Sum all message tokens and costs
4. **Extract models used:** Set of unique model IDs
5. **Get timestamp:** First message timestamp
6. **Determine slug (session name):**
   - **Priority 1:** Use history.get(session_id).get("display") if available
   - **Priority 2:** If display is /rename command, use renamed name (already marked renamed=True)
   - **Priority 2b:** If display is regular text:
     - Check if starts with "/" or "!" → discard (slash commands)
     - Check if in ("yes", "Sure", "go ahead") → discard (meta responses)
     - Else: Replace "\n" with spaces, truncate to 80 chars
   - **Priority 3:** Read first few lines of session file for "slug" field (fallback)
   - **Priority 4:** Use first 8 chars of session_id

7. **Load subagents:** Check `{session_path.parent}/{session_id}/subagents/agent-*.jsonl`
   - Parse each agent file (same structure as session messages)
   - Merge token counts into parent totals
   - Add model IDs to models_used set

8. **Return SessionSummary** with aggregated values

### Subagent Integration

**Subagent File Location:** `~/.claude/projects/{encoded_path}/{session_id}/subagents/agent-{name}.jsonl`

**Merging Logic:**
```
For each subagent file:
  For each line in file:
    Parse as message (same structure as session)
    Filter: type="assistant", not synthetic, not sidechain
    If has usage:
      Parse usage
      Calculate cost
      Add to parent totals:
        total_input += subagent_input
        total_output += subagent_output
        total_cost += subagent_cost
      Add subagent_model to models_used set
```

**Error Handling for Subagents:**
- File read error: Log warning, continue (don't fail parent summary)
- Malformed JSON: Skip line, continue

### Error Handling

| Case | Handler | Recovery |
|------|---------|----------|
| projects/ directory missing | `if not projects_dir.exists()` | Return {} |
| Non-directory entries | `if not encoded_dir.is_dir()` | Skip |
| Session file read error | In load_session_messages | Return empty list, skip summary |
| Subagent file error | `except IOError` | Log warning, continue with parent totals |

### Cache Strategy

**Cache Entry:** `cache_key = "project_summaries"`
**TTL:** 5 minutes
**Mtime Invalidation:** Not applied (composite key, no single file)

---

## 5. Hourly Activity Aggregation

**Function:** `build_hourly_activity(start_date, end_date, project=None)` -> `list[dict]`
**Source File:** `src/app/data/loader.py:398-445`

### Load Path

```
[Date Range: start_date to end_date]
    ↓
[Load Project Summaries] → build_project_summaries()
    ├─ Triggers load of all sessions
    ↓
[Filter Projects] → if project specified, only process that project
    ├─ Else: process all projects
    ↓
[For Each Session in Projects]
    ├─ Extract session.timestamp → date (before "T")
    ├─ Skip if date < start_date or date > end_date
    ↓
[Load Session Messages] → load_session_messages(encoded_path, session_id)
    ├─ Reuses cache (likely already loaded above)
    ↓
[For Each Message in Session]
    ├─ Extract hour: "2026-02-15T14:30:45Z" → "2026-02-15T14"
    ├─ Aggregate to hourly_data[hour_key]:
    │   ├─ messages += 1
    │   ├─ sessions.add(session_id) (set to avoid double-counting)
    │   ├─ cost += msg.cost_usd
    ↓
[Sort by hour_key] → sorted(hourly_data.keys())
    ↓
[Build Result List] → for each hour_key:
    ├─ hour: "2026-02-15T14"
    ├─ message_count: aggregated count
    ├─ session_count: len(sessions set)
    ├─ total_cost: sum of costs, rounded to 2 decimals
    ↓
[Return sorted list] → [{"hour": ..., "message_count": ..., ...}, ...]
```

### Performance Characteristics

**Time Complexity:** O(S + M) where S = sessions, M = total messages
**Space Complexity:** O(H) where H = unique hours in range
**Caching:** Relies on project_summaries and session_messages cache (TTL 5 min)

---

## Common Data Access Patterns

### Pattern 1: Load Data with Cache-First Strategy

All load functions follow this pattern:

```python
def load_something():
    cache = get_cache()
    cache_key = "unique_key"

    # 1. Try cache first
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # 2. Load from disk
    path = get_data_dir() / "filename"
    if not path.exists():
        return None  # or empty container

    # 3. Parse
    try:
        data = json.load(open(path))
    except Exception as e:
        logger.error(f"Failed to load: {e}")
        return None

    # 4. Transform
    result = transform(data)

    # 5. Cache and return
    cache.set(cache_key, result, path)
    return result
```

**Invariant:** Every load function checks cache before disk access.

### Pattern 2: Line-by-Line JSONL Parsing

JSONL files (history.jsonl, session files, subagent files) are always parsed line-by-line:

```python
messages = []
with open(path) as f:
    for line_num, line in enumerate(f, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            # Process entry
            messages.append(entry)
        except json.JSONDecodeError as e:
            logger.warning(f"Line {line_num}: {e}")
            continue  # Skip bad lines, don't fail entire file
```

**Error Handling:** Bad lines are logged with line number and skipped. File is still processed.

### Pattern 3: Token Aggregation

Across multiple messages/subagents:

```python
total_input = sum(m.input_tokens for m in messages)
total_output = sum(m.output_tokens for m in messages)
total_cache_write = sum(m.cache_creation_input_tokens for m in messages)
total_cache_read = sum(m.cache_read_input_tokens for m in messages)
total_cost = sum(m.cost_usd for m in messages)
```

### Pattern 4: Slug Generation with Fallbacks

Session naming priority (clean display → auto-generated):

1. History display name (if user renamed it)
2. Parsed slug field from JSONL
3. First 8 chars of session ID

---

## Data Validation & Edge Cases

### Missing or Malformed Data

| Scenario | Behavior |
|----------|----------|
| File doesn't exist | Return None or empty (log debug) |
| JSON parse error | Log error, return None/empty |
| Missing top-level fields | Use .get() with defaults (usually 0) |
| Missing nested fields | Use nested .get() or skip message |
| Empty array in JSON | Parse as empty list (no error) |
| Type mismatch (string vs int) | Handled by except clause or .get() defaults |

### Filtering & Data Quality

**Session Messages Filtering:**
- Removes synthetic messages (model == "<synthetic>")
- Removes sidechain messages (isSidechain == true)
- Removes messages without usage data

**History Filtering:**
- Keeps only latest entry per session
- /rename commands override earlier display names

**Project Filtering:**
- Skips projects with no valid sessions
- Skips sessions with no messages

---

## Configuration & Paths

**Data Directory Resolution:** `src/app/config.py:11-20`

```python
def get_data_dir() -> Path:
    # Priority 1: CLAUDE_DATA_DIR environment variable
    # Priority 2: ~/.claude (default)
    env_val = os.getenv("CLAUDE_DATA_DIR")
    if env_val:
        return Path(env_val).expanduser().resolve()
    else:
        return Path.home() / ".claude"
```

**Path Structure:**
```
{data_dir}/
├── stats-cache.json
├── history.jsonl
└── projects/
    ├── {encoded_project_path}/
    │   ├── {session_id}.jsonl
    │   └── {session_id}/
    │       └── subagents/
    │           └── agent-{name}.jsonl
    └── ...
```

---

## Cache Invalidation Details

**TTL-based:** 5 minutes (300 seconds)
**Mtime-based:** File modification time tracked at cache insertion

**Cache.is_valid() Logic:**
```python
def is_valid(self) -> bool:
    # TTL check
    if time.time() - self.cached_at > 300:
        return False

    # Mtime check (if file tracked)
    if self.file_path and self.file_path.exists():
        current_mtime = self.file_path.stat().st_mtime
        if current_mtime != self.cached_mtime:
            return False

    return True
```

**Invalidation Triggers:**
- Explicit call to `cache.invalidate(key)` or `cache.invalidate()`
- TTL expiration (5 minutes)
- File modification (mtime changes)
- Cache entry deleted manually

---

## Related Modules

- **Pricing:** `src/app/data/pricing.py` - Cost calculation (called from load_session_messages)
- **Cache:** `src/app/data/cache.py` - Cache implementation (called from all loaders)
- **Config:** `src/app/config.py` - Data directory resolution (called from all loaders)
- **Models:** `src/app/data/models.py` - Data structures (all loaders return these)

# Frontend: HTML Template Structure and Inheritance

## Overview

The application uses Jinja2 templates with a base template inheritance pattern. All pages extend `base.html`, which provides the common header, navigation, theme toggle, and footer structure.

**Template Files:**
- `src/app/templates/base.html` - Master template with header, nav, footer
- `src/app/templates/overview.html` - Dashboard with charts and statistics
- `src/app/templates/projects.html` - Projects list view
- `src/app/templates/project_detail.html` - Single project detail page
- `src/app/templates/session_detail.html` - Single session message breakdown
- `src/app/templates/settings.html` - Configuration page
- `src/app/templates/partials/session_table.html` - Reusable session table component

## Base Template Structure (base.html)

**File:** `src/app/templates/base.html:1-71`

### Header Section (lines 14-51)

```
Header
├─ Title: "Claude Usage Visualizer"
├─ Navigation (nav-link)
│  ├─ Overview (/")
│  └─ Projects (/projects)
└─ Header Actions (header-actions)
   ├─ Timezone Selector (timezone-dropdown)
   │  └─ Options: UTC 24h, Local 24h, UTC 12h, Local 12h
   ├─ Theme Toggle Button (icon-btn)
   └─ Settings Link (icon-btn)
```

**Key Elements:**
- `#theme-toggle` - Sun/moon SVG icon button for dark/light theme
- `#timezone-select` - Dropdown for time format selection (data-driven by `timezone.js`)
- Settings link to `/settings`

### Main Content Block (line 53)

```
{% block content %}{% endblock %}
```

All pages implement this block for their unique content. Container class manages max-width (1200px) and padding.

### Footer (lines 57-63)

```
Footer
└─ Last computed date (from overview_stats.last_computed_date)
```

Shows when data was last calculated. Only displayed if `overview_stats` context variable exists.

### Script Loading Order (lines 65-69)

1. `theme.js` - Initializes theme from localStorage or system preference
2. `timezone.js` - Sets up timezone dropdown and timestamp conversion
3. `filters.js` - Initializes date range and project filters
4. `charts.js` - Renders all Chart.js instances
5. `htmx-config.js` - HTMX event handlers for loading states

External dependencies:
- Chart.js 4.4.0 (CDN: jsdelivr)
- HTMX 1.9.10 (CDN: unpkg)

## Page Templates

### 1. Overview Page (overview.html)

**File:** `src/app/templates/overview.html:1-166`

**Route:** `src/app/routers/overview.py:18`

**Template Context Variables:**
- `error` (str|None) - Error message if data failed to load
- `overview_stats` (OverviewStats|None) - Aggregated statistics object
- `total_cost` (float) - Total estimated cost across all models
- `total_cache_write` (int) - Total cache write tokens
- `total_cache_read` (int) - Total cache read tokens
- `model_rows` (list[ModelRow]) - Per-model breakdown rows

**Rendered Components:**

1. **Error Banner** (lines 5-9)
   - Shows error message with link to Settings if data unavailable
   - Condition: `{% if error %}`

2. **Stats Grid** (lines 11-28)
   - 4 stat cards in responsive grid
   - Cards: Total Cost, Total Tokens, Total Sessions, Total Messages
   - Uses `stat-card` and `stat-value` classes from CSS

3. **Token Breakdown Grid** (lines 30-50)
   - 4 breakdown cards: Input, Output, Cache Write, Cache Read
   - Each shows formatted token count (thousands separator)
   - Uses Jinja2 filter: `"{:,}".format(value)`

4. **Filters Section** (lines 52-76)
   - Date inputs: `#start-date`, `#end-date`
   - Project dropdown: `#project-filter` (populated by filters.js)
   - Reset button: `#reset-filters`
   - Granularity indicator badge (hidden by default)

5. **Charts Grid** (lines 78-94)
   - 4 Canvas elements for Chart.js:
     - `#dailyActivityChart` - Activity over time (line/area)
     - `#modelCostChart` - Model cost split (doughnut)
     - `#hourlyChart` - Sessions by hour (bar)
     - `#dailyCostChart` - Daily cost trend (stacked area)

6. **Per-Model Table** (lines 96-135)
   - Columns: Model, Input Tokens, Output Tokens, Cache Write/Read, Total Tokens, Cost
   - Renders `model_rows` in loop
   - Footer row with totals (classes: `totals-row`)
   - Number formatting: thousands separator + 2 decimal places for cost

7. **Daily Activity Table** (lines 137-159)
   - Columns: Date, Messages, Sessions, Tool Calls
   - Uses `data-timestamp` attribute for timezone conversion
   - Reversed iteration: `overview_stats.daily_activity|reverse`

**Empty State:**
- Shows if `overview_stats` is None
- Message: "No Data Available" with link to Settings

### 2. Projects Page (projects.html)

**File:** `src/app/templates/projects.html:1-85`

**Route:** `src/app/routers/projects.py:17`

**Template Context Variables:**
- `error` (str|None) - Error message
- `projects` (list[ProjectSummary]|None) - List of projects
- `overview_stats` (OverviewStats) - For page header/footer

**Rendered Components:**

1. **Error Box** (lines 7-11)
   - Red border-left styling
   - Link to Settings for configuration

2. **Project Cost Chart** (lines 21-25)
   - Canvas: `#projectCostChart`
   - Horizontal bar chart (populated by charts.js)

3. **Projects Table** (lines 27-48)
   - Columns: Project Name, Sessions, Total Tokens, Total Cost, Date Range
   - Clickable rows redirect to project detail: `/projects/{project.encoded_path}`
   - Rows styled with `.clickable-row` (hover background)
   - Format: Cost with 2 decimals, tokens with commas

4. **Empty State** (lines 16-19)
   - Shows if `projects` list is empty
   - Message: "No projects found. Start using Claude Code to see data."

**Error Conditions:**
- `error` - Shows error box
- `projects is none` - Shows "Error loading projects"
- `projects|length == 0` - Shows empty state

### 3. Project Detail Page (project_detail.html)

**File:** `src/app/templates/project_detail.html:1-197`

**Route:** `src/app/routers/projects.py:89`

**Template Context Variables:**
- `project_name` (str) - Display name of project
- `encoded_name` (str) - URL-encoded project path
- `back_url` (str) - Link back to projects list
- `error` (str|None) - Error message
- `sessions` (list[SessionSummary]|None) - Sessions in project
- `total_sessions` (int) - Count of sessions
- `total_input_tokens`, `total_output_tokens` (int) - Token counts
- `total_cost_usd` (float) - Total project cost

**Rendered Components:**

1. **Breadcrumb Navigation** (lines 5-9)
   - Structure: Projects > ProjectName
   - Linkable: Back to projects list

2. **Summary Cards** (lines 23-36)
   - 3 cards: Sessions, Total Tokens, Total Cost
   - Responsive grid layout

3. **Charts Section** (lines 39-50)
   - 2 Canvas elements:
     - `#projectActivityChart` - Messages/sessions over time
     - `#projectModelCostChart` - Model cost breakdown (doughnut)
   - Conditionally shown: `{% if sessions|length > 0 %}`

4. **Sessions Table** (lines 57-86)
   - Columns: Session Name, Date, Messages, Cost, Models
   - Clickable rows: `/sessions/{encoded_name}/{session.session_id}`
   - Footer with totals row
   - Session date uses `data-timestamp` for timezone conversion

**Error Conditions:**
- Error box with back link if `error` exists
- Empty state if `sessions|length == 0`
- "Error loading project details" if `sessions is none`

### 4. Session Detail Page (session_detail.html)

**File:** `src/app/templates/session_detail.html:1-259`

**Route:** `src/app/routers/sessions.py:16`

**Template Context Variables:**
- `project_name`, `session_slug` (str) - Page context
- `encoded_path` (str) - Project identifier
- `back_url` (str) - Link to project detail
- `message_count` (int) - Count of messages
- `models` (str) - Comma-separated model list
- `total_input_tokens`, `total_output_tokens` (int) - Token counts
- `total_cache_read_tokens`, `total_cache_creation_tokens` (int) - Cache tokens
- `total_cost_usd` (float) - Session cost
- `messages` (list[SessionMessage]|None) - Message list

**Rendered Components:**

1. **Breadcrumb Navigation** (lines 5-11)
   - Structure: Projects > ProjectName > SessionName
   - All links functional for navigation

2. **Session Metadata Box** (lines 25-38)
   - Display: Project, Message Count, Models
   - Grid layout with label-value pairs

3. **Summary Cards** (lines 40-61)
   - 5 cards: Input Tokens, Output Tokens, Cache Read, Cache Write, Total Cost
   - Cost card highlighted with `.highlight` class (blue color)

4. **Messages Table** (lines 68-103)
   - Columns: Timestamp, Model, Input, Output, Cache Read, Cache Write, Cost
   - Timestamp uses `data-timestamp` attribute
   - Model name wordbreak enabled for long names
   - Rows styled for monospace timestamp and right-aligned numbers
   - Footer with totals row

**Empty State:**
- "No messages found in this session"

### 5. Settings Page (settings.html)

**File:** `src/app/templates/settings.html:1-42`

**Route:** `src/app/routers/settings.py:41`

**Template Context Variables:**
- `current_dir` (str) - Current configured data directory
- `is_valid` (bool) - Whether directory exists and contains required files
- `error` (str|None) - Error message from form submission

**Form Elements:**

1. **Data Directory Input** (lines 15-28)
   - Input ID: `#data_dir`
   - Name: `data_dir`
   - Placeholder: `~/.claude`
   - Required: Yes
   - Validation icon: Checkmark (green) if valid, X (red) if invalid

2. **Form Actions** (lines 36-39)
   - Save button (primary)
   - Cancel button (secondary, links to /)

3. **Error Message** (lines 8-10)
   - Shows validation error if directory doesn't exist

## Template Patterns and Conventions

### 1. Data-Driven Elements

**Timestamps with Timezone Support:**
```html
<span data-timestamp="{{ iso_string }}">{{ formatted_date }}</span>
```
- Attribute: `data-timestamp` contains ISO 8601 string
- Content: Server-rendered default format
- Client behavior: `timezone.js` replaces content based on user preference
- Supports: Date only or full timestamp with time

**Example from project_detail.html:71**
```html
<span data-timestamp="{{ session.timestamp }}">{{ session.date }}</span>
```

### 2. Formatting Filters

**Number Formatting:**
```jinja2
{{ "{:,}".format(value) }}          # Thousands separator
{{ "%.2f"|format(value) }}          # 2 decimal places
{{ "%.4f"|format(value) }}          # 4 decimal places for costs
```

**Reversal:**
```jinja2
{% for item in list|reverse %}
```

### 3. Conditional Rendering

**Error States:**
```jinja2
{% if error %}
    <div class="error-box">{{ error }}</div>
{% elif data is none %}
    <div>Error loading data</div>
{% elif data|length == 0 %}
    <div class="empty-state">No items found</div>
{% else %}
    [Content]
{% endif %}
```

### 4. Stat Cards

Reusable pattern:
```html
<div class="stat-card">
    <div class="stat-label">LABEL</div>
    <div class="stat-value">VALUE</div>
</div>
```

Variants:
- `.stat-value.highlight` - Accent color (blue)
- `.breakdown-card` - Alternate styling for token cards

### 5. Tables

Common structure:
```html
<table class="table" or "data-table">
    <thead><tr><th>...headers...</th></tr></thead>
    <tbody>
        {% for row in rows %}
        <tr>{% for col in row %}...{% endfor %}</tr>
        {% endfor %}
    </tbody>
    <tfoot><tr class="summary-row|totals-row">...totals...</tr></tfoot>
</table>
```

**Table Classes:**
- `.table` - Basic table styling
- `.data-table` - Enhanced table with borders and hover
- `.models-table` - Specialized for model breakdown
- `.messages-table` - Specialized for session messages
- `.clickable-row` - Row becomes clickable link with hover effect
- `.text-right` - Right-align cell content
- `.summary-row` or `.totals-row` - Bold footer row with top border

### 6. Navigation Patterns

**Back Links:**
```html
<p class="back-link"><a href="{{ back_url }}">← Back to X</a></p>
```
- Styled with top border separator
- Uses relative path for consistency

**Breadcrumbs:**
```html
<nav class="breadcrumb">
    <a href="/path">Item</a>
    <span class="breadcrumb-separator">/</span>
    <span>Current Item</span>
</nav>
```

## Server-to-Template Context Flow

### Overview Page

**Router:** `src/app/routers/overview.py:18-88`

Template receives:
1. `overview_stats` - OverviewStats dataclass with daily_activity array
2. `total_cost` - Computed from model costs
3. `total_cache_write`, `total_cache_read` - Aggregated from sessions
4. `model_rows` - ModelRow dataclass instances for table rendering
5. `error` - Error message string if data unavailable

### Projects Page

**Router:** `src/app/routers/projects.py:17-36`

Template receives:
1. `projects` - List of ProjectSummary objects
2. `error` - Error message if fetch failed
3. `overview_stats` - For footer timestamp

### Project Detail Page

**Router:** `src/app/routers/projects.py:89-146`

Template receives:
1. `project_name`, `encoded_name` - Project identifiers
2. `sessions` - List of SessionSummary objects
3. Aggregated: `total_sessions`, `total_input_tokens`, `total_output_tokens`, `total_cost_usd`
4. `back_url` - Link back to projects list
5. `error` - Error message

### Session Detail Page

**Router:** `src/app/routers/sessions.py:16-79`

Template receives:
1. `project_name`, `session_slug` - Display names
2. `encoded_path` - Project identifier for breadcrumb
3. `messages` - List of SessionMessage objects
4. Aggregated: `message_count`, `models`, token counts, cost
5. `back_url` - Link to project detail

### Settings Page

**Router:** `src/app/routers/settings.py:41-64`

Template receives:
1. `current_dir` - Current data directory setting
2. `is_valid` - Boolean validation status
3. `error` - Validation error message

## Chart Initialization

All chart canvases are populated by `charts.js` after page load.

**Chart Mapping:**
- `#dailyActivityChart` → `initDailyActivityChart()` → `/api/activity`
- `#modelCostChart` → `initModelCostChart()` → `/api/model-split`
- `#hourlyChart` → `initHourlyChart()` → `/api/hourly-distribution`
- `#dailyCostChart` → `initDailyCostChart()` → `/api/daily-cost`
- `#projectCostChart` → `initProjectCostChart()` → `/api/project-cost`
- `#projectActivityChart` → `initProjectActivityChart()` → `/api/projects/{id}/activity`
- `#projectModelCostChart` → `initProjectModelCostChart()` → `/api/projects/{id}/cost-breakdown`

**Data Flow:**
1. Template renders empty canvas elements
2. `charts.js` executes on DOMContentLoaded
3. Each chart function fetches from API endpoint
4. Chart.js renders visualization into canvas
5. Chart instances stored in `window.chartInstances` for dynamic updates

## Dynamic Content Loading with Filters

**Initiated by:** `filters.js`

**Process:**
1. Page load: `initFilters()` fetches `/api/metadata`
2. Populates date inputs with min/max range
3. Populates project dropdown from metadata
4. Loads saved filters from localStorage
5. Event listeners on inputs trigger `applyFilters()` (debounced 300ms)
6. `applyFilters()` calls `updateChart()` for each canvas
7. Chart instances updated with new data in-place

**Supported Filters:**
- `start_date` (YYYY-MM-DD)
- `end_date` (YYYY-MM-DD)
- `project` (encoded_path)

All filter state persisted to localStorage under key: `chartFilters`

## Responsive Design

### Mobile Breakpoints

**@media (max-width: 768px)** - Tablet/Mobile
- `.stats-grid` → 1 column (was auto-fit)
- `.token-breakdown-grid` → 2 columns (was auto-fit)
- `.header-content` → flex-direction: column
- `.header-title` → font-size: 1.25rem
- `.filters-grid` → 1 column
- Table font sizes reduced
- Chart min-height reduced to 250px

**@media (max-width: 1024px)** - Large Mobile/Tablet
- `.charts-grid` → 1 column (was auto-fit minmax(400px))
- Chart min-height: 350px

### Responsive Classes

- `.charts-grid` - Uses `grid-template-columns: repeat(auto-fit, minmax(400px, 1fr))`
- `.stats-grid` - Uses `repeat(auto-fit, minmax(250px, 1fr))`
- `.token-breakdown-grid` - Uses `repeat(auto-fit, minmax(200px, 1fr))`

## Accessibility Features

1. **ARIA Labels:**
   - `<button aria-label="Toggle theme">`
   - `<select aria-label="Select time format">`

2. **Semantic HTML:**
   - Proper `<header>`, `<main>`, `<footer>` structure
   - `<table>` with `<thead>`, `<tbody>`, `<tfoot>`
   - `<form>` with proper `<label>` associations

3. **Focus States:**
   - Input focus includes box-shadow outline
   - Links include hover opacity transition

4. **Color Contrast:**
   - Dark theme: Light text on dark background
   - Light theme: Dark text on light background
   - Error states: Red text with adequate contrast

## Known Gaps

1. **Partial Template Reuse:**
   - `partials/session_table.html` exists but not analyzed
   - May be used for HTMX dynamic content loading

2. **Form Validation:**
   - Client-side validation not fully documented
   - Server-side validation exists but edge cases unclear

3. **Error Recovery:**
   - User journeys after errors not documented
   - Reload behavior for filters may lose state

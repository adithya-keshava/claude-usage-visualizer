# Frontend: JavaScript Modules

## Overview

Five JavaScript modules handle client-side functionality: theme management, timezone/time format handling, chart initialization and updates, filters and API communication, and HTMX integration.

**Module Files:**
- `src/app/static/theme.js` - Theme toggle (dark/light)
- `src/app/static/timezone.js` - Time format conversion and dropdown
- `src/app/static/charts.js` - Chart.js initialization and updates
- `src/app/static/filters.js` - Date/project filters and chart updates
- `src/app/static/htmx-config.js` - HTMX event handlers

**Load Order (from base.html:65-69):**
1. `theme.js`
2. `timezone.js`
3. `filters.js`
4. `charts.js`
5. `htmx-config.js`

---

## 1. Theme Module (theme.js)

**File:** `src/app/static/theme.js:1-63`

### Purpose

Manages dark/light theme switching with localStorage persistence and system preference detection.

### Constants

```javascript
THEME_KEY = "claude-visualizer-theme"
DARK_THEME = "dark"
LIGHT_THEME = "light"
```

### Core Functions

**`getSystemTheme() → string`** (lines 7-9)
- Detects system preference via `window.matchMedia("(prefers-color-scheme: dark)")`
- Returns: `"dark"` or `"light"`
- Used as fallback if no theme stored in localStorage

**`initTheme() → void`** (lines 11-18)
- Called on page load (DOMContentLoaded)
- Flow:
  1. Get stored theme from localStorage[THEME_KEY]
  2. If not found, use system preference via `getSystemTheme()`
  3. Apply theme via `applyTheme()`

**`applyTheme(theme: string) → void`** (lines 20-23)
- Sets `data-theme` attribute on `<html>` element
- Saves theme to localStorage
- Triggers CSS variable updates (light/dark colors in style.css)

**`toggleTheme() → void`** (lines 25-30)
- Reads current theme from `document.documentElement.getAttribute("data-theme")`
- Switches to opposite (dark ↔ light)
- Calls `applyTheme()` to persist

### Event Listeners

**Theme Toggle Button** (lines 33-40)
- DOMContentLoaded:
  1. Initialize theme
  2. Find `#theme-toggle` button
  3. Attach click handler → `toggleTheme()`

**System Preference Changes** (lines 43-49)
- Listens to `window.matchMedia("(prefers-color-scheme: dark)")` changes
- Updates theme only if user has not stored explicit preference
- Condition: `!localStorage.getItem(THEME_KEY)`
- Applies new theme when system preference changes

### Helper Function

**`getChartColors() → object`** (lines 52-63)
- Returns color palette based on current theme
- Used by charts.js for proper theming

**Return object:**
```javascript
{
    textColor: "#e6edf3" (dark) or "#1f2937" (light),
    gridColor: "#30363d" (dark) or "#d1d5db" (light),
    opusColor: "#a855f7" (dark) or "#9333ea" (light),
    sonnetColor: "#3b82f6" (dark) or "#2563eb" (light),
    haikuColor: "#10b981" (dark) or "#059669" (light),
}
```

### Data Flow

```
Page Load
  ↓ DOMContentLoaded
  ├─ initTheme()
  │  ├─ localStorage.getItem(THEME_KEY)
  │  └─ applyTheme(theme)
  │     ├─ document.documentElement.setAttribute("data-theme", theme)
  │     └─ localStorage.setItem(THEME_KEY, theme)
  │
  └─ Attach #theme-toggle click listener
       ↓ User clicks toggle
       └─ toggleTheme()
          └─ applyTheme(opposite_theme)
```

### CSS Integration

**Style Hook:** `html[data-theme="dark"]` and `html[data-theme="light"]`

**CSS Variables Updated:**
- `--bg-primary`, `--bg-secondary` - Background colors
- `--text-primary`, `--text-secondary` - Text colors
- `--accent-*` - Brand colors per model
- `--border-color`, `--error-color` - Functional colors

**Location:** `src/app/static/style.css:2-34`

---

## 2. Timezone Module (timezone.js)

**File:** `src/app/static/timezone.js:1-145`

### Purpose

Converts all timestamps on page to user-selected time format (UTC/Local × 24h/12h) with localStorage persistence.

### Constants

```javascript
TIME_FORMATS = ['UTC', 'Local', 'UTC-12h', 'Local-12h']
```

Dropdown selector: `#timezone-select`

### Core Functions

**`initializeTimeFormat() → void`** (lines 12-17)
- Called on DOMContentLoaded
- Retrieves saved format from localStorage['timeFormat'] (default: 'UTC')
- Sets `data-time-format` attribute on `<html>`
- Calls `updateTimeFormatDropdown()` and `convertTimestamps()`

**`updateTimeFormatDropdown(format: string) → void`** (lines 20-25)
- Updates dropdown value to match current format
- Keeps UI in sync with actual format

**`convertTimestamps(format: string) → void`** (lines 28-37)
- Finds all elements with `data-timestamp` attribute
- Iterates through each element
- Gets ISO 8601 string from `data-timestamp` attribute
- Calls `formatTimestamp()` to convert
- Replaces element text content with converted value

**`formatTimestamp(isoString: string, format: string) → string`** (lines 40-83)
- Core conversion function
- Parses ISO 8601 string to Date object
- Determines timezone (isLocal = format.includes('Local'))
- Determines hour format (is12h = format.includes('12h'))
- Extracts date components using appropriate getters (getFullYear, getUTCFullYear, etc.)
- Formats hour:
  - 24h mode: Zero-padded 0-23
  - 12h mode: 1-12 with AM/PM suffix
- Returns: `YYYY-MM-DD HH:MM:SS` or `YYYY-MM-DD HH:MM:SS AM/PM`
- Error handling: Returns original ISO string on parse failure

**`formatDate(isoString: string, format: string) → string`** (lines 86-107)
- Similar to formatTimestamp but returns only date portion
- Returns: `YYYY-MM-DD`
- Used for date-only display in tables

**`changeTimeFormat(newFormat: string) → void`** (lines 110-124)
- Called when dropdown changes
- Saves preference to localStorage['timeFormat']
- Updates `data-time-format` attribute
- Calls `convertTimestamps()` to update all displayed timestamps
- Dispatches custom event: `CustomEvent('timeformatchange')`
  - Event detail: `{ format: newFormat }`
  - Listeners: charts.js and filters.js react to format change

### Event Listeners

**Dropdown Change** (lines 127-138)
- DOMContentLoaded:
  1. Call `initializeTimeFormat()`
  2. Find `#timezone-select` dropdown
  3. Attach change handler → `changeTimeFormat(event.target.value)`

### Exported Functions (lines 140-144)

Made available globally on `window` object:
- `window.formatTimestamp(isoString, format)` - For use in other modules
- `window.formatDate(isoString, format)` - For use in other modules
- `window.getTimeFormat()` - Returns current format from data attribute

### Data Attributes

**HTML Markup Required:**
```html
<span data-timestamp="2024-01-15T14:30:00Z">2024-01-15</span>
```

- `data-timestamp` - Contains ISO 8601 datetime string
- Element content - Replaced with formatted version
- Server renders default format, client converts on load

### Sample Conversions

Input: `2024-01-15T14:30:00Z` (UTC afternoon)

| Format | Output |
|--------|--------|
| UTC | `2024-01-15 14:30:00` |
| Local | `2024-01-15 09:30:00` (EST) |
| UTC-12h | `2024-01-15 02:30:00 PM` |
| Local-12h | `2024-01-15 09:30:00 AM` (EST) |

---

## 3. Charts Module (charts.js)

**File:** `src/app/static/charts.js:1-567`

### Purpose

Initializes Chart.js instances for all visualizations. Handles theme colors, data fetching, and updates on filter/timezone changes.

### Constants

```javascript
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
```

### Color Functions

**`getModelColor(modelId: string, opacity: number = 0.8) → string`** (lines 10-19)
- Returns RGBA hex color for model
- Opacity converted to hex alpha: `Math.round(opacity * 255).toString(16)`

**Color Mapping:**
```javascript
'claude-opus-4-6': '#a855f7'
'claude-opus-4-5-20251101': '#9333ea'
'claude-sonnet-4-5-20250929': '#3b82f6'
'claude-haiku-4-5-20251001': '#10b981'
default: '#6366f1'
```

**`getChartThemeColors() → object`** (lines 22-29)
- Reads current theme from `document.documentElement.getAttribute('data-theme')`
- Returns color palette for dark/light theme:

```javascript
{
    textColor: "#e5e7eb" (dark) or "#1f2937" (light),
    gridColor: "#374151" (dark) or "#e5e7eb" (light),
    backgroundColor: "#1f2937" (dark) or "#ffffff" (light),
}
```

**`formatChartLabels(labels: array) → array`** (lines 32-45)
- Converts chart labels to selected timezone format
- Detects if label is timestamp (contains 'T' or matches YYYY-MM-DD pattern)
- Calls `window.formatTimestamp()` if available
- Returns formatted label array

### Chart Initialization Functions

All follow same pattern:
1. Get canvas element by ID
2. Fetch data from API endpoint
3. Get theme colors
4. Create Chart.js instance
5. Store instance in `window.chartInstances[chartId]`

#### Chart 1: Daily Activity Chart (lines 48-123)

**Canvas:** `#dailyActivityChart`

**API Endpoint:** `/api/activity`
- Auto-selects granularity (hourly vs daily) based on date range

**Chart Type:** Line chart with dual Y-axes

**Configuration:**
- Responsive, maintains aspect ratio
- Interaction: index mode, not intersect
- Legend at top
- Title shows granularity: "Hourly Activity" or "Daily Activity"
- Y-axis (left): Messages
- Y1-axis (right): Sessions (no grid)
- X-axis: Time labels

**Data Structure:** (from `/api/activity`)
```javascript
{
    granularity: "hourly" | "daily",
    labels: ["2024-01-15", "2024-01-16", ...],
    datasets: [
        { label: "Messages", data: [...], yAxisID: "y" },
        { label: "Sessions", data: [...], yAxisID: "y1" }
    ]
}
```

#### Chart 2: Model Cost Chart (lines 126-179)

**Canvas:** `#modelCostChart`

**API Endpoint:** `/api/model-split`

**Chart Type:** Doughnut (pie)

**Configuration:**
- Legend at bottom
- Title: "Model Cost Distribution"
- Tooltip callback: Shows cost and percentage

**Data Structure:**
```javascript
{
    labels: ["Claude Opus 4.6", "Claude Sonnet 4.5", ...],
    datasets: [{
        label: "Cost",
        data: [50.25, 30.10, ...],
        backgroundColor: [model_colors]
    }]
}
```

#### Chart 3: Hourly Distribution Chart (lines 182-242)

**Canvas:** `#hourlyChart`

**API Endpoint:** `/api/hourly-distribution`

**Chart Type:** Bar chart (vertical)

**Configuration:**
- Title: "Session Starts by Hour (UTC)"
- X-axis: Hours 0-23
- Y-axis: Number of sessions
- Rotation: 45 degrees for labels

**Data Structure:**
```javascript
{
    labels: ["00:00", "01:00", ..., "23:00"],
    datasets: [{
        label: "Sessions",
        data: [5, 3, 8, ...],
        backgroundColor: [model_color]
    }]
}
```

#### Chart 4: Daily Cost Chart (lines 245-315)

**Canvas:** `#dailyCostChart`

**API Endpoint:** `/api/daily-cost`

**Chart Type:** Stacked area/line chart

**Configuration:**
- Responsive, maintains aspect ratio
- Interaction: index mode
- Legend at top
- Title: "Daily Cost Trend by Model"
- Y-axis: Stacked, currency formatted
- Y-axis tick formatter: `$${value.toFixed(2)}`

**Data Structure:**
```javascript
{
    labels: ["2024-01-01", "2024-01-02", ...],
    datasets: [
        { label: "Claude Opus 4.6", data: [...], fill: true },
        { label: "Claude Sonnet 4.5", data: [...], fill: true },
        ...
    ]
}
```

#### Chart 5: Project Cost Chart (lines 318-380)

**Canvas:** `#projectCostChart`

**API Endpoint:** `/api/project-cost`

**Chart Type:** Horizontal bar chart (indexAxis: 'y')

**Configuration:**
- Horizontal bars for project names
- Title: "Cost per Project"
- X-axis: Cost in USD (formatted with `$`)

#### Chart 6: Project Activity Chart (lines 383-459)

**Canvas:** `#projectActivityChart`

**Route Extraction:**
- Parses URL pathname: `/projects/([^\/]+)$`
- Extracts `encodedPath` from URL

**API Endpoint:** `/api/projects/{encodedPath}/activity`

**Chart Type:** Line chart with dual Y-axes (like daily activity)

**Configuration:**
- Title: "Project Activity Over Time"
- Y-axis: Messages
- Y1-axis: Sessions

#### Chart 7: Project Model Cost Chart (lines 462-517)

**Canvas:** `#projectModelCostChart`

**Route Extraction:** Same as project activity

**API Endpoint:** `/api/projects/{encodedPath}/cost-breakdown`

**Chart Type:** Doughnut

**Configuration:**
- Title: "Model Cost Distribution"
- Tooltip: Percentage calculation

### Initialization (lines 520-544)

**`initAllCharts() → void`** (lines 520-534)
- Called automatically at module load time (line 537)
- Checks if DOM is ready, waits for DOMContentLoaded if needed
- Calls all 7 init functions:
  1. `initDailyActivityChart()`
  2. `initModelCostChart()`
  3. `initHourlyChart()`
  4. `initDailyCostChart()`
  5. `initProjectCostChart()`
  6. `initProjectActivityChart()`
  7. `initProjectModelCostChart()`

### Dynamic Updates

**Theme Change Listener** (lines 540-544)
- Listens for custom event: `themechange`
- Reloads page after 200ms delay to refresh charts with new colors
- Future optimization: Update colors dynamically without reload

**Timezone Format Change Listener** (lines 547-566)
- Listens for custom event: `timeformatchange` (dispatched by timezone.js)
- Flow:
  1. Get new format from event detail
  2. Call `window.convertTimestamps()` to update DOM timestamps
  3. Update all chart labels via `formatChartLabels()`
  4. Call `chart.update()` on each instance to animate changes

### Data Flow

```
Page Load
  ↓
initAllCharts()
  ├─ initDailyActivityChart()
  │  ├─ fetch('/api/activity')
  │  ├─ Chart.js constructor
  │  └─ window.chartInstances['dailyActivityChart'] = chart
  ├─ initModelCostChart()
  │  └─ ... (similar)
  └─ ... (5 more)

User Actions:
  ├─ Theme Toggle
  │  └─ themechange event → page reload (200ms)
  │
  └─ Timezone Change
     └─ timeformatchange event
        ├─ convertTimestamps(newFormat)
        └─ Update all chart labels + chart.update()

Filter Changes (from filters.js):
  └─ updateChart(chartId, newApiUrl)
     ├─ fetch(newApiUrl)
     └─ Chart.getChart(canvas)
        └─ chart.data.labels/datasets = newData
           └─ chart.update('active')
```

---

## 4. Filters Module (filters.js)

**File:** `src/app/static/filters.js:1-187`

### Purpose

Manages date range and project filters, updates charts dynamically via API calls, persists filter state to localStorage.

### Helper Functions

**`debounce(func: function, wait: number) → function`** (lines 7-13)
- Returns debounced version of function
- Prevents excessive API calls while user types
- Default wait: 300ms (used in initFilters)

### Core Functions

**`initFilters() → Promise<void>`** (lines 16-77)
- Called on page load
- Flow:
  1. Fetch `/api/metadata` to get date range and project list
  2. Set min/max attributes on date inputs
  3. Load saved filters from localStorage['chartFilters']
  4. Populate `#project-filter` dropdown with projects
  5. Restore saved filter values to inputs
  6. Attach event listeners with debouncing (300ms)
  7. Apply saved filters if any exist

**`applyFilters() → Promise<void>`** (lines 80-127)
- Called when any filter changes
- Saves current filter state to localStorage['chartFilters']:
  ```javascript
  {
      start_date: "2024-01-01",
      end_date: "2024-12-31",
      project: "encoded_path"
  }
  ```
- Builds URLSearchParams with non-empty filters
- Updates 5 charts in parallel via `Promise.all()`:
  - dailyActivityChart
  - dailyCostChart
  - modelCostChart
  - hourlyChart
  - projectCostChart
- Checks `/api/activity` for granularity (hourly vs daily)
- Shows/hides granularity badge if data is hourly

**`updateChart(chartId: string, apiUrl: string) → Promise<void>`** (lines 130-148)
- Updates single chart with new data
- Flow:
  1. Get canvas element by ID
  2. Fetch data from provided API URL
  3. Find existing Chart.js instance via `Chart.getChart(canvas)`
  4. Update chart data in-place:
     - `chart.data.labels = newLabels`
     - `chart.data.datasets = newDatasets`
  5. Animate update: `chart.update('active')`
  6. Error handling: Logs error if update fails

**`resetFilters() → void`** (lines 151-164)
- Clears all filter inputs
- Removes localStorage['chartFilters']
- Reloads page to reset charts

### Event Listeners

**Filter Inputs** (lines 58-64)
- Date input change: `startInput.addEventListener('change', debouncedApply)`
- Date input change: `endInput.addEventListener('change', debouncedApply)`
- Project select change: `projectSelect.addEventListener('change', debouncedApply)`
- Reset button click: `resetBtn.addEventListener('click', resetFilters)`

**Timezone Format Change** (lines 167-179)
- Listens for custom event: `timeformatchange`
- Re-applies filters (triggers chart updates with new timezone in labels)

### API Contracts

All chart APIs accept query parameters:
- `?start_date=YYYY-MM-DD`
- `?end_date=YYYY-MM-DD`
- `?project=encoded_path`

**Endpoints:**
- `/api/activity` - Returns granularity info
- `/api/daily-cost`
- `/api/model-split`
- `/api/hourly-distribution`
- `/api/project-cost`
- `/api/metadata` - Returns date range and projects list

### Data Flow

```
Page Load
  ↓ DOMContentLoaded
  initFilters()
    ├─ fetch('/api/metadata')
    ├─ Populate date inputs with min/max
    ├─ Load localStorage['chartFilters']
    ├─ Populate project dropdown
    └─ Attach event listeners (debounced 300ms)

User Changes Filter
  ↓ change event (debounced)
  applyFilters()
    ├─ Save to localStorage['chartFilters']
    ├─ Build URLSearchParams
    └─ Promise.all([
        updateChart('dailyActivityChart', ...),
        updateChart('dailyCostChart', ...),
        updateChart('modelCostChart', ...),
        updateChart('hourlyChart', ...),
        updateChart('projectCostChart', ...)
      ])
      └─ Chart.getChart(canvas)
         ├─ chart.data.labels = newLabels
         ├─ chart.data.datasets = newDatasets
         └─ chart.update('active')

User Resets Filters
  ↓ click reset button
  resetFilters()
    ├─ Clear all inputs
    ├─ localStorage.removeItem('chartFilters')
    └─ window.location.reload()
```

### localStorage Persistence

**Key:** `chartFilters`

**Schema:**
```javascript
{
    start_date?: string,  // YYYY-MM-DD
    end_date?: string,    // YYYY-MM-DD
    project?: string      // encoded_path
}
```

**Behavior:**
- Loaded on page init
- Saved on every filter change
- Cleared on reset
- Survives page reload

---

## 5. HTMX Configuration Module (htmx-config.js)

**File:** `src/app/static/htmx-config.js:1-32`

### Purpose

Minimal HTMX event handlers for loading indicators and error handling.

### Event Handlers

**`htmx:configRequest`** (lines 7-9)
- Fires before HTMX request sent
- Current: Empty, available for custom headers

**`htmx:xhr:loadstart`** (lines 12-17)
- Fires when HTMX request starts
- Adds class `htmx-loading` to target element
- CSS class triggers opacity and loading spinner (style.css:653-686)

**`htmx:xhr:loadend`** (lines 20-25)
- Fires when HTMX request completes
- Removes class `htmx-loading` from target element
- Clears loading state

**`htmx:responseError`** (lines 28-31)
- Fires when HTMX response errors
- Logs error details to console
- Comment notes: Could show user-facing error message

### CSS Loading States

**Class:** `htmx-loading`

**Styles** (src/app/static/style.css:653-686):
- Opacity: 0.6
- Pointer events: none
- After pseudo-element spinner:
  - Position: center
  - Border spinner animation
  - Border-top color: accent-sonnet (blue)
  - Animation duration: 0.8s linear infinite

### Current Usage

HTMX is loaded but not heavily used in current implementation:
- No `hx-*` attributes in templates
- Load functions configured for future dynamic content

### Future Use Cases

Potential for:
1. Dynamic table pagination (`hx-get="/api/items?page=2"`)
2. Filter results without page reload (`hx-post="/filter"`)
3. Inline form validation
4. Lazy-load chart data

---

## Module Initialization Order

```
Page Load
  ↓
base.html loads scripts in order:
  1. theme.js
     └─ DOMContentLoaded: initTheme()

  2. timezone.js
     └─ DOMContentLoaded: initializeTimeFormat()

  3. filters.js
     └─ DOMContentLoaded: initFilters()

  4. charts.js
     └─ Immediate: initAllCharts()
        └─ Async: fetch API endpoints

  5. htmx-config.js
     └─ HTMX event listeners registered

  ↓
All listeners ready for user interaction
```

---

## Cross-Module Communication

### Custom Events

**`timeformatchange` Event**
- Emitted by: `timezone.js` (line 122)
- Listened by: `charts.js` (line 547), `filters.js` (line 167)
- Detail: `{ format: string }`
- Behavior:
  - Charts: Updates labels, calls chart.update()
  - Filters: Re-applies filters to update chart data

**`themechange` Event**
- Currently: Not emitted
- Comment in charts.js (line 541) suggests future use
- Would trigger page reload to refresh chart colors

### Global Functions/Objects

**From theme.js:**
- `window.getChartColors()` - Called by charts.js (line 22 context suggests use)

**From timezone.js:**
- `window.formatTimestamp(isoString, format)`
- `window.formatDate(isoString, format)`
- `window.getTimeFormat()`

**From charts.js:**
- `window.chartInstances = { [chartId]: Chart }` - Object storing all chart instances
- Used by filters.js to access charts for updates

**From filters.js:**
- `window.convertTimestamps(format)` - Called by charts.js on timezone change

---

## Dependencies

### External Libraries

1. **Chart.js 4.4.0**
   - Location: CDN (jsdelivr)
   - Used by: charts.js
   - Functions: `Chart.defaults`, `new Chart(ctx, config)`

2. **HTMX 1.9.10**
   - Location: CDN (unpkg)
   - Used by: htmx-config.js
   - Functions: `htmx.find()`, event listeners

### DOM Elements Required

**Must exist for initialization:**
- `<html>` element - For data-theme and data-time-format attributes
- `#theme-toggle` - Button for theme toggle
- `#timezone-select` - Dropdown for time format
- Chart canvases - Various IDs (dailyActivityChart, etc.)
- Filter inputs - #start-date, #end-date, #project-filter, #reset-filters

### API Endpoints Required

**Must be available:**
- `/api/metadata` - Metadata for filters
- `/api/activity` - Daily/hourly activity data
- `/api/daily-cost` - Daily cost trend
- `/api/model-split` - Model cost breakdown
- `/api/hourly-distribution` - Session hour distribution
- `/api/project-cost` - Project cost breakdown
- `/api/projects/{encoded_path}/activity` - Project-specific activity
- `/api/projects/{encoded_path}/cost-breakdown` - Project model breakdown

---

## Known Limitations

1. **Theme Change Reload:**
   - Full page reload on theme toggle (charts.js:543)
   - Could optimize to update chart colors dynamically

2. **Filter Reset:**
   - Full page reload (filters.js:163)
   - Could update charts without reload

3. **No Offline Support:**
   - All functionality depends on API endpoints
   - No caching or fallback modes

4. **HTMX Unused:**
   - Infrastructure in place but not integrated into templates
   - Partial HTML updates not yet implemented

5. **Error Recovery:**
   - API failures logged to console
   - No user-facing error messages for failed chart loads
   - Filters silently fail if API returns error

6. **Timezone Precision:**
   - Format changes don't update existing chart data
   - Only affects label display, not data values
   - Data always stored in UTC, conversion is display-only

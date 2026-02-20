# JavaScript Module Patterns

**Document:** Claude Usage Visualizer - JavaScript Module Architecture
**Scope:** All JavaScript files in `src/app/static/` - Module initialization, events, state management
**Last Updated:** 2026-02-20

---

## Overview

The JavaScript codebase implements a modular architecture with 5 independent modules that communicate via custom events. Each module:
- Initializes on `DOMContentLoaded`
- Manages its own state (mostly via localStorage)
- Exposes public functions via `window` object
- Listens to and emits custom events

**Modules:**
1. **theme.js** - Theme toggle (light/dark)
2. **timezone.js** - Time format conversion (UTC/Local, 24h/12h)
3. **filters.js** - Date range and project filtering
4. **charts.js** - Chart initialization and rendering
5. **htmx-config.js** - AJAX request handling

---

## Module Initialization Pattern

### Lifecycle

All modules follow this pattern:

```javascript
// 1. Define module state and constants
const CONSTANT = "value";
let moduleState = null;

// 2. Define private helper functions
function privateHelper() { }

// 3. Define public API functions
function publicFunction() { }

// 4. Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
    initializeModule();
});

// 5. Export public API to window
window.publicFunction = publicFunction;
```

### DOMContentLoaded vs Script Execution

**Pattern Used:**

```javascript
// Option 1: Check readyState (filters.js)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilters);
} else {
    initFilters();
}

// Option 2: Register listener (theme.js, timezone.js, charts.js)
document.addEventListener('DOMContentLoaded', function () {
    initializeModule();
});
```

**Difference:**
- **Option 1:** Avoids event if DOM already loaded (faster if script runs late)
- **Option 2:** Simpler, always works (slight delay if already loaded)

**Current Distribution:**
- filters.js: Option 1
- theme.js, timezone.js, charts.js: Option 2
- htmx-config.js: No init (event listeners only)

---

## Theme Module

**File:** `src/app/static/theme.js:1-63`

### Constants & State

**Lines:** `src/app/static/theme.js:3-5`

```javascript
const THEME_KEY = "claude-visualizer-theme";
const DARK_THEME = "dark";
const LIGHT_THEME = "light";
```

**Storage Key:** `claude-visualizer-theme`
**Values:** `"dark"` or `"light"`
**Persistence:** localStorage

### Initialization Flow

**Function:** `initTheme()` - Lines 11-18

```javascript
function initTheme() {
    // Get stored theme or use system preference
    let theme = localStorage.getItem(THEME_KEY);
    if (!theme) {
        theme = getSystemTheme();  // Detect OS preference
    }
    applyTheme(theme);
}
```

**Priority:**
1. Check localStorage for saved preference
2. Fall back to system preference
3. Apply selected theme

### Applying Theme

**Function:** `applyTheme(theme)` - Lines 20-23

```javascript
function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
}
```

**Effects:**
1. Set DOM attribute: `<html data-theme="dark">` or `data-theme="light"`
2. Save to localStorage (persistent across sessions)
3. CSS uses attribute for styling (no inline styles)

### Toggle Functionality

**Function:** `toggleTheme()` - Lines 25-30

```javascript
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute("data-theme");
    const newTheme = current === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    applyTheme(newTheme);
}
```

**Logic:**
- Get current theme from DOM attribute
- Flip to opposite (dark ↔ light)
- Apply and persist

### System Theme Detection

**Function:** `getSystemTheme()` - Lines 7-9

```javascript
function getSystemTheme() {
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? DARK_THEME : LIGHT_THEME;
}
```

**Browser Feature:** `window.matchMedia()` queries CSS media queries
**Usage:** Detect if user has OS-level dark mode enabled

### System Theme Change Listener

**Lines:** `src/app/static/theme.js:43-49`

```javascript
if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
        if (!localStorage.getItem(THEME_KEY)) {
            applyTheme(e.matches ? DARK_THEME : LIGHT_THEME);
        }
    });
}
```

**Behavior:**
- If user changes OS theme preference
- AND user hasn't manually set theme in app (no localStorage)
- THEN update app theme to match OS

**Note:** Manual preference takes precedence over OS changes.

### Theme Toggle Button Setup

**Lines:** `src/app/static/theme.js:33-40`

```javascript
document.addEventListener("DOMContentLoaded", function () {
    initTheme();

    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", toggleTheme);
    }
});
```

**HTML Requirement:** `<button id="theme-toggle">...</button>`
**Event:** Click toggles theme

### Chart Color Helper

**Function:** `getChartColors()` - Lines 52-63

```javascript
function getChartColors() {
    const theme = document.documentElement.getAttribute("data-theme");
    const isDark = theme === DARK_THEME;

    return {
        textColor: isDark ? "#e6edf3" : "#1f2937",
        gridColor: isDark ? "#30363d" : "#d1d5db",
        opusColor: isDark ? "#a855f7" : "#9333ea",
        sonnetColor: isDark ? "#3b82f6" : "#2563eb",
        haikuColor: isDark ? "#10b981" : "#059669",
    };
}
```

**Usage:** Helper for charts.js (though charts.js has its own color functions).

**Unused:** This function is defined but not called from charts.js.

### State Management

**Persistence:** localStorage
**Memory State:** None (read from DOM attribute on demand)
**Update Trigger:** User clicks theme button or OS theme changes

---

## Timezone Module

**File:** `src/app/static/timezone.js:1-145`

### Constants & State

**Lines:** `src/app/static/timezone.js:8-9`

```javascript
const TIME_FORMATS = ['UTC', 'Local', 'UTC-12h', 'Local-12h'];
```

**Modes:** 4 formats (cycles through on each toggle)

**Storage Key:** `timeFormat` (from localStorage.getItem on line 13)

### Initialization Flow

**Function:** `initializeTimeFormat()` - Lines 12-17

```javascript
function initializeTimeFormat() {
    const savedFormat = localStorage.getItem('timeFormat') || 'UTC';
    document.documentElement.setAttribute('data-time-format', savedFormat);
    updateTimeFormatDropdown(savedFormat);
    convertTimestamps(savedFormat);
}
```

**Steps:**
1. Get saved format or default to 'UTC'
2. Set DOM attribute: `<html data-time-format="UTC">`
3. Sync dropdown to current format
4. Format all timestamps on page

### Format Conversion

**Function:** `formatTimestamp(isoString, format)` - Lines 40-83

```javascript
function formatTimestamp(isoString, format) {
    const date = new Date(isoString);
    const isLocal = format.includes('Local');
    const is12h = format.includes('12h');

    // Extract components based on timezone (Local or UTC)
    let year, month, day, hours, minutes, seconds;
    if (isLocal) {
        // Use getFullYear(), getMonth(), getHours(), etc.
    } else {
        // Use getUTCFullYear(), getUTCMonth(), getUTCHours(), etc.
    }

    // Format hours based on 12h/24h preference
    let timeStr;
    if (is12h) {
        const ampm = hours >= 12 ? 'PM' : 'AM';
        const hours12 = hours % 12 || 12;
        return `${hours12Str}:${minutes}:${seconds} ${ampm}`;
    } else {
        return `${hoursStr}:${minutes}:${seconds}`;
    }

    return `${year}-${month}-${day} ${timeStr}`;
}
```

**Format Examples:**

| Format | Example | Logic |
|--------|---------|-------|
| UTC | 2026-02-20 14:30:45 | UTC, 24-hour |
| Local | 2026-02-20 09:30:45 | Local TZ, 24-hour |
| UTC-12h | 2026-02-20 02:30:45 PM | UTC, 12-hour |
| Local-12h | 2026-02-20 09:30:45 AM | Local TZ, 12-hour |

**Date Extraction:**
- **Local:** `getFullYear()`, `getMonth()`, `getHours()`
- **UTC:** `getUTCFullYear()`, `getUTCMonth()`, `getUTCHours()`

### Batch Timestamp Conversion

**Function:** `convertTimestamps(format)` - Lines 28-37

```javascript
function convertTimestamps(format) {
    const timestamps = document.querySelectorAll('[data-timestamp]');
    timestamps.forEach((element) => {
        const isoString = element.getAttribute('data-timestamp');
        if (isoString) {
            const formatted = formatTimestamp(isoString, format);
            element.textContent = formatted;
        }
    });
}
```

**HTML Pattern:** `<span data-timestamp="2026-02-20T14:30:45Z">raw ISO</span>`

**Process:**
1. Find all elements with `data-timestamp` attribute
2. Read ISO string from attribute
3. Format using selected format
4. Update element text content

### Date-Only Formatting

**Function:** `formatDate(isoString, format)` - Lines 86-107

```javascript
function formatDate(isoString, format) {
    const date = new Date(isoString);
    const isLocal = format.includes('Local');

    // Extract YYYY-MM-DD components
    // Format as "YYYY-MM-DD"
}
```

**Usage:** For date inputs and charts that don't need time.

### Format Change Handler

**Function:** `changeTimeFormat(newFormat)` - Lines 110-124

```javascript
function changeTimeFormat(newFormat) {
    // 1. Save preference
    localStorage.setItem('timeFormat', newFormat);

    // 2. Update DOM and dropdown
    document.documentElement.setAttribute('data-time-format', newFormat);
    updateTimeFormatDropdown(newFormat);

    // 3. Convert all timestamps on page
    convertTimestamps(newFormat);

    // 4. Dispatch custom event for other modules
    const event = new CustomEvent('timeformatchange', { detail: { format: newFormat } });
    document.dispatchEvent(event);
}
```

**Broadcasting:** Emits `timeformatchange` event so charts.js can update labels.

### Dropdown Integration

**Lines:** `src/app/static/timezone.js:127-138`

```javascript
document.addEventListener('DOMContentLoaded', () => {
    initializeTimeFormat();

    const dropdown = document.getElementById('timezone-select');
    if (dropdown) {
        dropdown.addEventListener('change', (e) => {
            changeTimeFormat(e.target.value);
        });
    }
});
```

**HTML Requirement:** `<select id="timezone-select">` with 4 options

### Public API (Window Exports)

**Lines:** `src/app/static/timezone.js:140-145`

```javascript
window.formatTimestamp = formatTimestamp;
window.formatDate = formatDate;
window.getTimeFormat = () =>
  document.documentElement.getAttribute('data-time-format') || 'UTC';
```

**Exported Functions:**
- `formatTimestamp(isoString, format)` - Format full timestamp
- `formatDate(isoString, format)` - Format date only
- `getTimeFormat()` - Get current format setting

---

## Filters Module

**File:** `src/app/static/filters.js:1-187`

### Constants & Helpers

**Lines:** `src/app/static/filters.js:6-13`

```javascript
function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
```

**Debounce Pattern:** Delays function execution until input stops.

**Usage:** Prevent API calls on every keystroke.

### Initialization Flow

**Function:** `initFilters()` - Lines 16-77

```javascript
async function initFilters() {
    // 1. Fetch metadata (date range, projects)
    let metadata = await fetch('/api/metadata').then((r) => r.json());

    // 2. Set date input constraints
    const startInput = document.getElementById('start-date');
    const endInput = document.getElementById('end-date');
    startInput.min = metadata.oldest_date;
    startInput.max = metadata.newest_date;

    // 3. Load saved filters from localStorage
    const savedFilters = JSON.parse(localStorage.getItem('chartFilters') || '{}');
    startInput.value = savedFilters.start_date || '';

    // 4. Populate project dropdown
    const projectSelect = document.getElementById('project-filter');
    metadata.projects.forEach((project) => {
        const option = document.createElement('option');
        option.value = project.encoded_path;
        option.textContent = `${project.display_name} (${project.session_count} sessions)`;
        projectSelect.appendChild(option);
    });

    // 5. Add event listeners with debouncing
    const debouncedApply = debounce(applyFilters, 300);
    startInput.addEventListener('change', debouncedApply);
    endInput.addEventListener('change', debouncedApply);
    projectSelect.addEventListener('change', debouncedApply);

    // 6. Apply saved filters on load
    if (savedFilters.start_date || savedFilters.end_date || savedFilters.project) {
        applyFilters();
    }
}
```

**Initialization Steps:**
1. Fetch metadata (server-side endpoints)
2. Constrain date inputs to available range
3. Restore previous filter selections
4. Populate project list dynamically
5. Set up event listeners with debouncing
6. Reapply filters from previous session

### Applying Filters

**Function:** `applyFilters()` - Lines 80-127

```javascript
async function applyFilters() {
    // 1. Get current filter values
    const startDate = document.getElementById('start-date')?.value;
    const endDate = document.getElementById('end-date')?.value;
    const project = document.getElementById('project-filter')?.value;

    // 2. Save to localStorage
    localStorage.setItem('chartFilters', JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        project: project,
    }));

    // 3. Build query params
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);
    if (project) params.set('project', project);

    // 4. Update all charts in parallel
    await Promise.all([
        updateChart('dailyActivityChart', `/api/activity?${params}`),
        updateChart('dailyCostChart', `/api/daily-cost?${params}`),
        // ... update other charts
    ]);

    // 5. Check and display granularity indicator
    const activityData = await fetch(`/api/activity?${params}`).then((r) => r.json());
    if (activityData.granularity === 'hourly') {
        document.getElementById('granularity-indicator').style.display = 'block';
    }
}
```

**Process:**
1. Read current filter values from DOM
2. Save to localStorage (persistent)
3. Build URL query parameters
4. Update all 5 charts in parallel (Promise.all)
5. Check if hourly granularity active and show indicator

### Chart Updates

**Function:** `updateChart(chartId, apiUrl)` - Lines 130-148

```javascript
async function updateChart(chartId, apiUrl) {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;

    try {
        const data = await fetch(apiUrl).then((r) => r.json());

        // Get existing chart instance
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            // Update existing chart data
            existingChart.data.labels = data.labels;
            existingChart.data.datasets = data.datasets;
            existingChart.update('active'); // Smooth animation
        }
    } catch (error) {
        console.error(`Failed to update ${chartId}:`, error);
    }
}
```

**Key Insight:** Updates existing Chart.js instances instead of destroying/recreating.

**Chart.js API:**
- `Chart.getChart(canvas)` - Get instance from canvas
- `chart.data.labels = ...` - Update labels
- `chart.data.datasets = ...` - Update data
- `chart.update('active')` - Re-render with smooth animation

### Reset Filters

**Function:** `resetFilters()` - Lines 151-164

```javascript
function resetFilters() {
    // Clear all input values
    document.getElementById('start-date').value = '';
    document.getElementById('end-date').value = '';
    document.getElementById('project-filter').value = '';

    // Clear localStorage
    localStorage.removeItem('chartFilters');

    // Full page reload to reset charts
    window.location.reload();
}
```

**Behavior:** Full page reload (charts.js re-initializes fresh).

**Alternative:** Could update charts without reload (more efficient).

### Timezone Integration

**Lines:** `src/app/static/filters.js:167-179`

```javascript
document.addEventListener('timeformatchange', (event) => {
    const newFormat = event.detail.format;
    applyFilters();
});
```

**Listening to:** Custom event from timezone.js

**Behavior:** Re-apply filters when timezone format changes (refreshes chart labels).

### Initialization Entry Point

**Lines:** `src/app/static/filters.js:182-187`

```javascript
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFilters);
} else {
    initFilters();
}
```

---

## Charts Module

**File:** `src/app/static/charts.js:1-567`

### Initialization Pattern

All 7 chart functions follow this pattern:

```javascript
function initChartName() {
    const canvas = document.getElementById('canvasId');
    if (!canvas) return;  // Exit if element doesn't exist

    fetch('/api/endpoint')
        .then(res => {
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            return res.json();
        })
        .then(data => {
            const theme = getChartThemeColors();
            const ctx = canvas.getContext('2d');

            const chart = new Chart(ctx, {
                type: 'chart-type',
                data: data,
                options: { /* configured with theme colors */ },
            });

            // Store instance for updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['canvasId'] = chart;
        })
        .catch(err => console.error('Failed to load chart:', err));
}
```

### Public API

**Lines:** `src/app/static/charts.js:520-537`

```javascript
function initAllCharts() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllCharts);
        return;
    }

    initDailyActivityChart();
    initModelCostChart();
    initHourlyChart();
    initDailyCostChart();
    initProjectCostChart();
    initProjectActivityChart();
    initProjectModelCostChart();
}

initAllCharts();
```

**Entry Point:** Calls all 7 chart init functions.

### Event Listeners

**Theme Change Event (Lines 540-544):**

```javascript
document.addEventListener('themechange', () => {
    setTimeout(() => window.location.reload(), 200);
});
```

**Behavior:** Reload page on theme change.

**Note:** Full reload because Chart.js colors are set at init time. Could be optimized to update colors dynamically.

**Timezone Change Event (Lines 547-566):**

```javascript
document.addEventListener('timeformatchange', (event) => {
    const newFormat = event.detail.format;

    if (window.convertTimestamps) {
        window.convertTimestamps(newFormat);  // From timezone.js
    }

    if (window.chartInstances) {
        Object.values(window.chartInstances).forEach(chart => {
            if (chart && chart.data && chart.data.labels) {
                const formattedLabels = formatChartLabels(chart.data.labels);
                chart.data.labels = formattedLabels;
                chart.update();
            }
        });
    }
});
```

**Behavior:** Update chart labels without reload.

**Uses:** `formatChartLabels()` helper to convert timestamps.

---

## HTMX Config Module

**File:** `src/app/static/htmx-config.js:1-32`

### Architecture

HTMX module has NO initialization. Instead, it registers 3 global event handlers:

```javascript
// 1. Request config hook (empty, ready for use)
document.addEventListener('htmx:configRequest', ...);

// 2. Show loading state
document.addEventListener('htmx:xhr:loadstart', ...);

// 3. Hide loading state
document.addEventListener('htmx:xhr:loadend', ...);

// 4. Error handling
document.addEventListener('htmx:responseError', ...);
```

**No window exports** - Purely event-based.

---

## Cross-Module Communication

### Communication Patterns

**Pattern 1: Custom Events**

```javascript
// Emitter (timezone.js)
const event = new CustomEvent('timeformatchange', { detail: { format: newFormat } });
document.dispatchEvent(event);

// Listeners (charts.js, filters.js)
document.addEventListener('timeformatchange', (event) => {
    const newFormat = event.detail.format;
    // React to change
});
```

**Advantages:**
- Loose coupling
- Modules don't need to reference each other
- Easy to add new listeners

**Events Used:**
- `timeformatchange` - Emitted by timezone.js, listened by charts.js and filters.js
- `themechange` - Not emitted anywhere! (comment says "For now, a simple page reload works best")

### Window Object Exports

**Timezone Module:**
```javascript
window.formatTimestamp = formatTimestamp;
window.formatDate = formatDate;
window.getTimeFormat = () => ...;
```

**Filters Module:** No exports (internal use only).

**Charts Module:**
```javascript
window.chartInstances = {};  // Mutable state, accessed by filters.js
window.chartInstances['dailyActivityChart'] = chart;
```

**Usage:**
- `filters.js` accesses `window.chartInstances` to update charts
- `charts.js` calls `window.formatTimestamp` and `window.getTimeFormat`

### Implicit Dependencies

| Module | Depends On | How |
|--------|-----------|-----|
| charts.js | timezone.js | Calls `window.formatTimestamp()` |
| filters.js | charts.js | Accesses `Chart.getChart()` and `window.chartInstances` |
| filters.js | timezone.js | Listens to `timeformatchange` event |

---

## State Management

### localStorage Keys

| Module | Key | Value Type | Values |
|--------|-----|-----------|--------|
| theme.js | `claude-visualizer-theme` | String | `"dark"` or `"light"` |
| timezone.js | `timeFormat` | String | `"UTC"`, `"Local"`, `"UTC-12h"`, `"Local-12h"` |
| filters.js | `chartFilters` | JSON object | `{start_date, end_date, project}` |

### DOM Attributes Used

| Module | Attribute | Values |
|--------|-----------|--------|
| theme.js | `data-theme` on `<html>` | `"dark"` or `"light"` |
| timezone.js | `data-time-format` on `<html>` | `"UTC"`, `"Local"`, etc. |
| timezone.js | `data-timestamp` on elements | ISO 8601 strings |

### In-Memory State

| Module | State | Type | Scope |
|--------|-------|------|-------|
| filters.js | `metadata` | Object | Local variable (fetched once) |
| charts.js | `chartInstances` | Object | `window.chartInstances` (mutable) |

---

## Module Dependencies Graph

```
timezone.js
    ├─ Emits: timeformatchange
    └─ Exports: formatTimestamp(), formatDate(), getTimeFormat()
            ↓ (used by)
        charts.js
            ├─ Listens to: timeformatchange
            ├─ Stores: window.chartInstances
            └─ Exports: (implicit)
                    ↓ (used by)
                filters.js
                    ├─ Accesses: window.chartInstances, Chart.getChart()
                    └─ Listens to: timeformatchange

theme.js
    └─ No dependencies (standalone)

htmx-config.js
    └─ No dependencies (event-based)
```

---

## Lifecycle Summary

### Page Load Sequence

```
1. Page starts loading
   ├─ HTML parsed, <script> tags loaded
   ├─ theme.js runs
   │   └─ initTheme() called on DOMContentLoaded
   ├─ timezone.js runs
   │   └─ initializeTimeFormat() called on DOMContentLoaded
   ├─ filters.js runs
   │   └─ initFilters() called (checks readyState)
   └─ charts.js runs
       └─ initAllCharts() called on DOMContentLoaded

2. DOM Content Loaded
   ├─ theme.js initializes
   ├─ timezone.js initializes
   ├─ filters.js initializes (waits for metadata API)
   └─ charts.js initializes (fetches chart data for each chart)

3. All charts rendered
   ├─ Interactive (filters, theme toggle, timezone toggle work)
   └─ Ready for user interaction
```

### User Interaction Examples

**Change Theme:**
```
User clicks theme button
    → toggleTheme() called
    → applyTheme() sets data-theme attribute
    → CSS updated (background, text colors change)
    → themechange event NOT dispatched (page reload used instead)
    → Charts reload on next navigation
```

**Change Timezone Format:**
```
User selects timezone dropdown
    → changeTimeFormat() called
    → localStorage updated
    → DOM attribute updated
    → convertTimestamps() updates all <span data-timestamp> elements
    → timeformatchange event dispatched
    → charts.js listens and updates chart labels
    → filters.js listens and calls applyFilters()
```

**Change Date Range/Project:**
```
User selects date or project
    → applyFilters() called (debounced 300ms)
    → localStorage updated
    → All 5 charts updated via Promise.all()
    → Chart instances updated in-place (no destroy/recreate)
```

---

## Performance Characteristics

### Bundle Size

**Estimated:**
- theme.js: ~1.5 KB
- timezone.js: ~4 KB
- filters.js: ~5 KB
- charts.js: ~16 KB (includes 7 chart initializations)
- htmx-config.js: ~0.8 KB
- **Total:** ~27 KB (minified)

### Initial Load

**Chart API Calls:**
- Overview page: 5 calls (activity, daily-cost, model-split, hourly-distribution, project-cost)
- Project page: 2 calls (activity, cost-breakdown)

**Metadata Fetch:**
- 1 call (filters.js)

### Event Frequency

**High-frequency:**
- Timezone dropdown change → formatTimestamps() on ~100+ elements

**Medium-frequency:**
- Date range change → updateChart() on 5 charts

**Low-frequency:**
- Theme toggle → page reload
- Page navigation

---

## Testing Module Behavior

### Check Stored State

```javascript
// In browser console
console.log(localStorage.getItem('claude-visualizer-theme'));
console.log(localStorage.getItem('timeFormat'));
console.log(localStorage.getItem('chartFilters'));
```

### Verify Event Flow

```javascript
// In browser console
document.addEventListener('timeformatchange', (e) => {
    console.log('Timezone changed to:', e.detail.format);
});
document.addEventListener('htmx:responseError', (e) => {
    console.log('HTMX error:', e.detail);
});
```

### Check Chart Instances

```javascript
// In browser console
console.log(window.chartInstances);
Object.values(window.chartInstances).forEach(chart => {
    console.log(chart.data.labels);
});
```

---

## Related Modules

- **styles/** - CSS implementation of data-theme and data-time-format
- **routers/api.py** - Endpoints for chart data and metadata
- **templates/** - HTML elements with IDs matching JavaScript queries

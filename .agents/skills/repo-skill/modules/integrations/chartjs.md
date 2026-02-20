# Chart.js Integration

**Document:** Claude Usage Visualizer - Chart.js Configuration and Usage
**Scope:** `src/app/static/charts.js` and API routers - Chart initialization and data formats
**Last Updated:** 2026-02-20

---

## Overview

Chart.js is used for data visualization across the application. The integration consists of:
1. **Backend:** API endpoints in `src/app/routers/api.py` that return Chart.js-compatible JSON
2. **Frontend:** JavaScript initialization in `src/app/static/charts.js` that creates Chart instances
3. **Styling:** Dynamic theme colors based on document's `data-theme` attribute
4. **Interactivity:** Theme switching and timezone format changes update chart data

**Key Characteristics:**
- 7 total charts across 2 pages (overview + project detail)
- 4 chart types: line, area, doughnut, bar
- 4 models with dedicated color scheme
- Responsive layouts with theme awareness
- Dynamic label formatting for timezones

---

## Chart Initialization Architecture

**File:** `src/app/static/charts.js:1-567`

### Global Configuration

**Lines:** `src/app/static/charts.js:6-7`

```javascript
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
```

Sets default font family globally for all Chart instances. Uses system font stack for native appearance.

### Theme Color Management

**Function:** `getChartThemeColors()` - Lines 22-29

```javascript
function getChartThemeColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        textColor: isDark ? '#e5e7eb' : '#1f2937',  // Gray-200 or Gray-900
        gridColor: isDark ? '#374151' : '#e5e7eb',  // Gray-700 or Gray-200
        backgroundColor: isDark ? '#1f2937' : '#ffffff',
    };
}
```

**Usage:** Called by every chart initialization to get theme-aware colors.

**Color Mapping:**
| Element | Light Mode | Dark Mode |
|---------|-----------|-----------|
| Text | #1f2937 (gray-900) | #e5e7eb (gray-200) |
| Grid | #e5e7eb (gray-200) | #374151 (gray-700) |
| Background | #ffffff | #1f2937 (gray-900) |

### Model Color Assignment

**Function:** `getModelColor(modelId, opacity = 0.8)` - Lines 10-19

```javascript
function getModelColor(modelId, opacity = 0.8) {
    const opacityInt = Math.round(opacity * 255).toString(16).padStart(2, '0');
    const colors = {
        'claude-opus-4-6': `#a855f7${opacityInt}`,           // Purple-500
        'claude-opus-4-5-20251101': `#9333ea${opacityInt}`,  // Purple-600
        'claude-sonnet-4-5-20250929': `#3b82f6${opacityInt}`,// Blue-500
        'claude-haiku-4-5-20251001': `#10b981${opacityInt}`, // Emerald-500
    };
    return colors[modelId] || `#6366f1${opacityInt}`;         // Indigo-500 fallback
}
```

**Opacity Calculation:** Converts decimal opacity (0.0-1.0) to hex (00-ff).
- Example: `0.8 * 255 = 204` → `0xcc` → result is `#a855f7cc`

**Color Scheme:**
| Model | Color | Hex |
|-------|-------|-----|
| Opus 4.6 | Light Purple | #a855f7 |
| Opus 4.5 | Dark Purple | #9333ea |
| Sonnet 4.5 | Blue | #3b82f6 |
| Haiku 4.5 | Emerald | #10b981 |
| Unknown | Indigo (fallback) | #6366f1 |

**Usage Pattern:** Not currently used in charts.js (hardcoded colors in API responses instead).

---

## Chart Types & Initialization Patterns

### Pattern: Fetch → Theme → Create

All chart initializations follow this pattern:

```javascript
function initChartName() {
    const canvas = document.getElementById('canvasId');
    if (!canvas) return;  // Exit if canvas not in DOM

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
                data: data,  // From API
                options: { /* theme colors applied */ },
            });

            // Store instance for dynamic updates
            window.chartInstances = window.chartInstances || {};
            window.chartInstances['chartName'] = chart;
        })
        .catch(err => console.error('Failed to load chart:', err));
}
```

---

## Chart #1: Daily Activity (Line Chart with Dual Axis)

**Function:** `initDailyActivityChart()` - Lines 48-123
**Canvas ID:** `dailyActivityChart`
**API Endpoint:** `/api/activity`
**Chart Type:** Line (with dual Y-axes)
**Pages:** Overview dashboard

### Data Format

**Endpoint Response:** `src/app/routers/api.py:312-407`

```json
{
  "labels": ["2026-02-01", "2026-02-02", ...],
  "datasets": [
    {
      "label": "Messages",
      "data": [100, 150, ...],
      "borderColor": "rgba(139, 92, 246, 1)",
      "backgroundColor": "rgba(139, 92, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y",      // LEFT axis
      "fill": true
    },
    {
      "label": "Sessions",
      "data": [10, 12, ...],
      "borderColor": "rgba(59, 130, 246, 1)",
      "backgroundColor": "rgba(59, 130, 246, 0.1)",
      "borderWidth": 2,
      "tension": 0.3,
      "yAxisID": "y1",     // RIGHT axis
      "fill": true
    }
  ],
  "granularity": "daily" | "hourly"
}
```

### Configuration

**Lines:** `src/app/static/charts.js:62-116`

```javascript
new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },  // Show both series on hover
        plugins: {
            legend: { labels: { color, padding: 15 } },
            title: { display: true, text: ..., color, font: { size: 14, weight: 'bold' } },
        },
        scales: {
            y: { position: 'left', title: { text: 'Messages' }, ... },
            y1: { position: 'right', title: { text: 'Sessions' }, drawOnChartArea: false },
            x: { ticks: { color }, grid: { color } },
        }
    }
});
```

**Key Options:**
- **Dual Axis:** `y` (left) for messages, `y1` (right) for sessions
- **Interaction:** `index` mode shows both series on hover
- **Tension:** 0.3 (smooth curves)
- **Fill:** Enabled for visual emphasis

### Smart Granularity

**Logic:** `src/app/routers/api.py:322-335`

```python
if start_date and end_date:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    duration = (end - start).days

    if duration < 1:
        granularity = "hourly"  # < 1 day: show hourly
    else:
        granularity = "daily"   # >= 1 day: show daily
```

**Response Includes:** `"granularity": "daily"` or `"granularity": "hourly"`

**Title Updated:** `data.granularity === 'hourly' ? 'Hourly Activity' : 'Daily Activity'` (Line 81)

---

## Chart #2: Model Cost Distribution (Doughnut Chart)

**Function:** `initModelCostChart()` - Lines 126-179
**Canvas ID:** `modelCostChart`
**API Endpoint:** `/api/model-split`
**Chart Type:** Doughnut
**Pages:** Overview dashboard

### Data Format

**Endpoint Response:** `src/app/routers/api.py:135-182`

```json
{
  "labels": ["Opus 4.6", "Opus 4.5", "Sonnet 4.5", "Haiku 4.5"],
  "datasets": [
    {
      "data": [245.50, 123.25, 87.75, 12.40],  // USD
      "backgroundColor": [
        "rgba(168, 85, 247, 0.8)",
        "rgba(147, 51, 234, 0.8)",
        "rgba(59, 130, 246, 0.8)",
        "rgba(16, 185, 129, 0.8)"
      ],
      "borderColor": [
        "rgba(168, 85, 247, 1)",
        "rgba(147, 51, 234, 1)",
        "rgba(59, 130, 246, 1)",
        "rgba(16, 185, 129, 1)"
      ],
      "borderWidth": 2
    }
  ]
}
```

### Configuration

**Lines:** `src/app/static/charts.js:139-172`

```javascript
new Chart(ctx, {
    type: 'doughnut',
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { position: 'bottom', labels: { color, padding: 15 } },
            title: { display: true, text: 'Model Cost Distribution', ... },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const value = context.parsed;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `$${value.toFixed(2)} (${percentage}%)`;
                    }
                }
            }
        }
    }
});
```

**Custom Tooltip:** Shows absolute cost and percentage for each slice.

### Cost Calculation

**Endpoint Logic:** `src/app/routers/api.py:144-151`

```python
for model_id, stats in overview_stats.model_stats.items():
    cost = estimate_cost(
        model_id,
        input_tokens=stats.input_tokens,
        output_tokens=stats.output_tokens,
        cache_creation_input_tokens=stats.cache_creation_input_tokens,
        cache_read_input_tokens=stats.cache_read_input_tokens,
    )
    model_costs[model_id] = round(cost, 2)
```

---

## Chart #3: Hourly Distribution (Bar Chart)

**Function:** `initHourlyChart()` - Lines 182-242
**Canvas ID:** `hourlyChart`
**API Endpoint:** `/api/hourly-distribution`
**Chart Type:** Bar (vertical)
**Pages:** Overview dashboard

### Data Format

**Endpoint Response:** `src/app/routers/api.py:185-230`

```json
{
  "labels": ["0:00 UTC", "1:00 UTC", ..., "23:00 UTC"],
  "datasets": [
    {
      "label": "Session Starts",
      "data": [5, 8, 3, ..., 12],
      "backgroundColor": "rgba(99, 102, 241, 0.8)",
      "borderColor": "rgba(99, 102, 241, 1)",
      "borderWidth": 1
    }
  ]
}
```

### Configuration

**Lines:** `src/app/static/charts.js:195-235`

**Key Features:**
- Single dataset for session count
- X-axis: 24 hours (0-23)
- Y-axis: Number of sessions
- Labels rotated: maxRotation: 45

---

## Chart #4: Daily Cost Trend (Stacked Area Chart)

**Function:** `initDailyCostChart()` - Lines 245-315
**Canvas ID:** `dailyCostChart`
**API Endpoint:** `/api/daily-cost`
**Chart Type:** Line (stacked area)
**Pages:** Overview dashboard

### Data Format

**Endpoint Response:** `src/app/routers/api.py:71-132`

```json
{
  "labels": ["2026-02-01", "2026-02-02", ...],
  "datasets": [
    {
      "label": "Opus 4.6",
      "data": [50.25, 65.40, ...],
      "borderColor": "rgba(168, 85, 247, 1)",
      "backgroundColor": "rgba(168, 85, 247, 0.5)",
      "borderWidth": 2,
      "fill": true,
      "tension": 0.3
    },
    {
      "label": "Opus 4.5",
      "data": [30.10, 35.20, ...],
      "borderColor": "rgba(147, 51, 234, 1)",
      "backgroundColor": "rgba(147, 51, 234, 0.5)",
      ...
    },
    ...
  ]
}
```

### Configuration

**Lines:** `src/app/static/charts.js:258-308`

```javascript
scales: {
    y: {
        stacked: true,  // KEY: Stack all datasets
        title: { text: 'Cost (USD)' },
        ticks: {
            callback: (value) => '$' + value.toFixed(2)
        }
    }
}
```

**Cost Estimation (Approximation):** `src/app/routers/api.py:113`

```python
# Estimate cost for input/output breakdown per day
cost = estimate_cost(model_id, input_tokens=tokens // 2, output_tokens=tokens // 2)
```

**Note:** Uses token total per day without input/output breakdown. Splits 50/50 as approximation.

---

## Chart #5: Project Cost (Horizontal Bar Chart)

**Function:** `initProjectCostChart()` - Lines 318-380
**Canvas ID:** `projectCostChart`
**API Endpoint:** `/api/project-cost`
**Chart Type:** Bar (horizontal)
**Pages:** Overview dashboard

### Data Format

**Endpoint Response:** `src/app/routers/api.py:233-273`

```json
{
  "labels": ["project-a", "project-b", "project-c"],
  "datasets": [
    {
      "label": "Cost (USD)",
      "data": [1234.56, 567.89, 123.45],
      "backgroundColor": "rgba(139, 92, 246, 0.8)",
      "borderColor": "rgba(139, 92, 246, 1)",
      "borderWidth": 1
    }
  ]
}
```

### Configuration

**Lines:** `src/app/static/charts.js:331-373`

```javascript
{
    type: 'bar',
    options: {
        indexAxis: 'y',  // KEY: Makes bars horizontal
        scales: { x: { title: { text: 'Cost (USD)' }, ... } }
    }
}
```

**Key Features:**
- `indexAxis: 'y'` rotates bar orientation
- Sorted by cost descending (from API)
- Cost-formatted ticks: `'$' + value.toFixed(2)`

---

## Chart #6: Project Activity (Line Chart with Dual Axis)

**Function:** `initProjectActivityChart()` - Lines 383-459
**Canvas ID:** `projectActivityChart`
**API Endpoint:** `/api/projects/{encoded_path}/activity`
**Chart Type:** Line (dual Y-axis)
**Pages:** Project detail page

### Data Format

**Endpoint Response:** `src/app/routers/api.py:410-472`

```json
{
  "labels": ["2026-02-01", "2026-02-02", ...],
  "datasets": [
    { "label": "Messages", "data": [100, 120, ...], "yAxisID": "y", ... },
    { "label": "Sessions", "data": [10, 12, ...], "yAxisID": "y1", ... }
  ]
}
```

### URL Parsing

**Lines:** `src/app/static/charts.js:387-391`

```javascript
const pathMatch = window.location.pathname.match(/\/projects\/([^\/]+)$/);
if (!pathMatch) return;
const encodedPath = pathMatch[1];
```

Extracts project path from URL: `/projects/{encoded_path}` → uses encoded_path for API call.

---

## Chart #7: Project Model Cost Breakdown (Doughnut Chart)

**Function:** `initProjectModelCostChart()` - Lines 462-517
**Canvas ID:** `projectModelCostChart`
**API Endpoint:** `/api/projects/{encoded_path}/cost-breakdown`
**Chart Type:** Doughnut
**Pages:** Project detail page

### Data Format

**Endpoint Response:** `src/app/routers/api.py:475-522`

```json
{
  "labels": ["Opus 4.6", "Sonnet 4.5", "Haiku 4.5"],
  "datasets": [
    {
      "data": [345.67, 234.56, 12.34],
      "backgroundColor": [...],
      "borderColor": [...]
    }
  ]
}
```

### Cost Aggregation

**Endpoint Logic:** `src/app/routers/api.py:486-492`

```python
model_costs = defaultdict(float)
for session in sessions:
    for model in session.models_used:
        messages = load_session_messages(encoded_path, session.session_id)
        for msg in messages:
            if msg.model == model:
                model_costs[model] += msg.cost_usd
```

**Note:** Loops through all messages for each model in each session. Could be optimized to cache per-message model costs.

---

## Lifecycle & Event Handling

### Initialization Flow

**Lines:** `src/app/static/charts.js:520-544`

```javascript
function initAllCharts() {
    // Wait for DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAllCharts);
        return;
    }

    // Initialize all chart functions
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

**Execution:**
1. Check if DOM loaded
2. If not: Register listener, defer execution
3. If yes: Call all 7 init functions
4. Each init function fetches data, creates chart

### Theme Change Event

**Lines:** `src/app/static/charts.js:540-544`

```javascript
document.addEventListener('themechange', () => {
    setTimeout(() => window.location.reload(), 200);
});
```

**Behavior:** Page reload on theme change (current approach).

**Future:** Could update chart colors dynamically without reload.

### Timezone Format Change Event

**Lines:** `src/app/static/charts.js:547-566`

```javascript
document.addEventListener('timeformatchange', (event) => {
    const newFormat = event.detail.format;

    // Call global timezone converter
    if (window.convertTimestamps) {
        window.convertTimestamps(newFormat);
    }

    // Update chart labels
    if (window.chartInstances) {
        Object.values(window.chartInstances).forEach(chart => {
            if (chart && chart.data && chart.data.labels) {
                const formattedLabels = formatChartLabels(chart.data.labels);
                chart.data.labels = formattedLabels;
                chart.update();  // Re-render with new labels
            }
        });
    }
});
```

**Behavior:** Reformats timestamp labels without reloading page.

**Uses:** `formatChartLabels(labels)` function (Lines 32-45).

---

## Label Formatting

**Function:** `formatChartLabels(labels)` - Lines 32-45

```javascript
function formatChartLabels(labels) {
    const timeFormat = document.documentElement.getAttribute('data-time-format') || 'UTC';

    return labels.map(label => {
        if (label && (label.includes('T') || label.match(/^\d{4}-\d{2}-\d{2}$/))) {
            // Label looks like timestamp
            if (window.formatTimestamp) {
                return window.formatTimestamp(label, timeFormat);
            }
        }
        return label;
    });
}
```

**Detects:** ISO timestamps or dates
**Conversion:** Calls `window.formatTimestamp(label, timeFormat)` if available
**Fallback:** Returns original label if conversion not available

---

## Error Handling

All chart initialization functions use try/catch pattern:

```javascript
fetch('/api/endpoint')
    .then(res => {
        if (!res.ok) throw new Error(`API error: ${res.status}`);
        return res.json();
    })
    .then(data => { /* create chart */ })
    .catch(err => console.error('Failed to load chart:', err));
```

**Behavior:**
- HTTP error → throw error
- Parse error → catch handler
- Network error → catch handler
- Logs to console, doesn't crash page

**No User Feedback:** Errors logged to console only. Consider toast notifications.

---

## Data Format Consistency

**Standard Chart.js Format (all endpoints):**

```json
{
  "labels": [...],
  "datasets": [
    {
      "label": "...",
      "data": [...],
      "backgroundColor": "...",
      "borderColor": "...",
      ...
    }
  ]
}
```

**Common Fields:**
- `labels`: X-axis values
- `datasets`: Array of data series
- `data`: Y-axis values (per series)
- `backgroundColor`: Fill color
- `borderColor`: Line/border color
- `borderWidth`: Line thickness
- `label`: Legend entry

**Optional Fields (per chart):**
- `yAxisID`: For dual-axis charts
- `fill`: For area charts
- `tension`: Curve smoothing
- `stacked`: For stacked charts
- `indexAxis`: For horizontal bars

---

## Colors & Styling

### Fixed Model Colors

Set in API responses (not using `getModelColor()` function):

| Model | Background | Border |
|-------|-----------|--------|
| Opus 4.6 | rgba(168, 85, 247, 0.5) | rgba(168, 85, 247, 1) |
| Opus 4.5 | rgba(147, 51, 234, 0.5) | rgba(147, 51, 234, 1) |
| Sonnet 4.5 | rgba(59, 130, 246, 0.5) | rgba(59, 130, 246, 1) |
| Haiku 4.5 | rgba(16, 185, 129, 0.5) | rgba(16, 185, 129, 1) |

### Activity Chart Colors

| Series | Background | Border |
|--------|-----------|--------|
| Messages | rgba(139, 92, 246, 0.1) | rgba(139, 92, 246, 1) |
| Sessions | rgba(59, 130, 246, 0.1) | rgba(59, 130, 246, 1) |

---

## Performance Considerations

### Chart Instance Caching

**Lines:** `src/app/static/charts.js:119-120, 174-176, etc.`

```javascript
window.chartInstances = window.chartInstances || {};
window.chartInstances['dailyActivityChart'] = chart;
```

**Purpose:** Store references for dynamic updates (timezone change).

**Cost:** Minimal (7 chart objects in memory).

### API Calls

- **Overview page:** 5 API calls (activity, daily-cost, model-split, hourly-distribution, project-cost)
- **Project page:** 2 API calls (activity, cost-breakdown)
- **Caching:** Relies on server-side cache (5-minute TTL)

### DOM Ready Check

**Lines:** `src/app/static/charts.js:522-525`

Avoids initializing charts before canvas elements exist.

---

## Related Modules

- **API Routers:** `src/app/routers/api.py` - Data endpoints
- **Overview Router:** `src/app/routers/overview.py` - Dashboard rendering
- **Projects Router:** `src/app/routers/projects.py` - Project detail page
- **Theme Module:** `src/app/static/theme.js` - Theme change events
- **Timezone Module:** `src/app/static/timezone.js` - Timezone format changes

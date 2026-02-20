# Frontend: Static Assets and Template Structure (Task 1.1.4)

## Asset Organization

**Directory:** `src/app/static/`

**Files:**
```
static/
├── style.css          (855 lines) - Main stylesheet with themes
├── theme.js           (63 lines)  - Dark/light theme toggle
├── timezone.js        (145 lines) - Time format conversion
├── charts.js          (567 lines) - Chart.js initialization
├── filters.js         (187 lines) - Filter state and chart updates
└── htmx-config.js     (32 lines)  - HTMX event handlers
```

**Total:** 6 files, ~1,850 lines of static assets

---

## CSS Organization (style.css)

### File Structure

**Sections (by line numbers):**

1. **CSS Custom Properties** (lines 2-34) - Theme variables
   - Dark theme variables
   - Light theme variables
   - Color palette (brand, functional)

2. **Global Styles** (lines 36-62)
   - Reset (box-sizing, margin, padding)
   - HTML/body defaults
   - Link styling

3. **Header Component** (lines 64-175)
   - Header container and layout
   - Title, navigation, actions
   - Timezone dropdown styling
   - Icon button styling

4. **Main Content Layout** (lines 177-188)
   - Container max-width and centering
   - Padding and minimum height

5. **Component Styles** (lines 190-403)
   - Stat cards and grids
   - Sections and headings
   - Tables (standard and specialized)
   - Forms and inputs
   - Buttons (primary, secondary, load-more)
   - Error states and empty states

6. **Advanced Components** (lines 406-676)
   - Token breakdown cards
   - Models table styling
   - Charts section and grid
   - HTMX loading indicators
   - Pagination controls
   - Filters section

7. **Responsive Design** (lines 551-855)
   - Mobile breakpoints (768px, 1024px)
   - Responsive grid adjustments
   - Font size reductions
   - Layout changes

### CSS Sections Detail

#### 1. Variables System (2-34)

**Pattern:** CSS custom properties with theme selectors

**Dark Theme (lines 2-17):**
```css
html[data-theme="dark"] {
    --bg-primary: #0d1117;
    --text-primary: #e6edf3;
    --accent-color: #3b82f6;
    ...
}
```

**Light Theme (lines 19-34):**
```css
html[data-theme="light"] {
    --bg-primary: #ffffff;
    --text-primary: #1f2937;
    --accent-color: #2563eb;
    ...
}
```

**Color Palette:**
- Backgrounds: primary, secondary
- Text: primary, secondary
- Accents: opus (purple), sonnet (blue), haiku (green)
- Functional: border, link, error

#### 2. Header (64-175)

**Layout Structure:**

```
.header (sticky container)
├─ .header-content (flex row)
│  ├─ .header-title (flex: 1)
│  ├─ .header-nav (flex row, gap 1.5rem)
│  │  ├─ .nav-link (hover: underline)
│  │  └─ .nav-link
│  └─ .header-actions (flex row)
│     ├─ .timezone-selector
│     │  └─ .timezone-dropdown
│     ├─ #theme-toggle (icon-btn)
│     └─ Settings link (icon-btn)
```

**Sticky Behavior:**
```css
position: sticky;
top: 0;
z-index: 100;
```

Stays visible on scroll, overlays content.

**Responsive (mobile):**
```css
@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    .header-title { font-size: 1.25rem; }
    .header-nav { margin: 0; }
}
```

#### 3. Stat Cards (191-224)

**Three Levels of Hierarchy:**

Level 1: `.stats-grid` - Container
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
gap: 1.5rem;
```

Responsive: 1-4 columns depending on width

Level 2: `.stat-card` - Individual card
```css
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 1.5rem;
transition: all 0.3s;
```

Hover effect:
```css
border-color: var(--accent-sonnet);
box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
```

Level 3: Content
- `.stat-label` - Uppercase, secondary text, small
- `.stat-value` - Large, monospace font, primary text

#### 4. Tables (240-300)

**Two Table Classes:**

1. `.table` - Basic styling
2. `.data-table` - Enhanced with borders/hover

**Base Styling:**
```css
width: 100%;
border-collapse: collapse;
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
overflow: hidden;
```

**Header Styling:**
```css
thead {
    background-color: var(--border-color);
    border-bottom: 1px solid var(--border-color);
}
th {
    padding: 1rem;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
}
```

**Row Styling:**
```css
td {
    padding: 1rem;
    font-size: 0.9rem;
    color: var(--text-primary);
}

tbody tr {
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s;
}

tbody tr:hover {
    background-color: var(--hover-bg);
}
```

**Special Rows:**
- `.clickable-row` - cursor: pointer, hover effect
- `.summary-row`, `.totals-row` - font-weight: 600, top border

#### 5. Forms (303-370)

**Input Focus Pattern:**
```css
.input-group input:focus {
    outline: none;
    border-color: var(--accent-sonnet);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

Blue outline on focus (not default browser outline).

**Validation Icons:**
- `.validation-icon.valid` - Green checkmark
- `.validation-icon.invalid` - Red X

**Form Layout:**
```css
.settings-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    max-width: 600px;
}
```

#### 6. Buttons (373-403)

**Base Button:**
```css
.btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}
```

**Three Variants:**

1. `.btn-primary` - Blue background, white text
   - Hover: opacity 0.9, translateY(-1px)

2. `.btn-secondary` - Secondary background, border
   - Hover: darker background

3. `.btn-load-more` - Same as primary
   - Disabled: opacity 0.5, cursor not-allowed

**Lift Effect on Hover:**
```css
transform: translateY(-1px);
```

Subtle elevation animation for tactile feedback.

#### 7. Charts (613-676)

**Grid Layout:**
```css
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 2rem;
}
```

Responsive: 1-3 columns

**Chart Wrapper:**
```css
.chart-wrapper {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1.5rem;
    position: relative;
    min-height: 300px;
}
```

`position: relative` for loading spinner positioning.

**Canvas:**
```css
.chart-wrapper canvas {
    max-height: 300px;
}
```

#### 8. HTMX Loading (653-686)

**Loading State:**
```css
.htmx-loading {
    opacity: 0.6;
    pointer-events: none;
}
```

Dims element and disables interaction.

**Spinner Animation:**
```css
.htmx-loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color);
    border-top-color: var(--accent-sonnet);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: translate(-50%, -50%) rotate(360deg);
    }
}
```

Blue spinning border (accent color).

#### 9. Filters Section (754-855)

**Container:**
```css
.filters-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
}
```

**Grid:**
```css
.filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    align-items: end;
}
```

Align-items: end - Buttons line up with input bottoms.

**Granularity Badge:**
```css
.granularity-badge {
    margin-top: 1rem;
    padding: 0.5rem 1rem;
    background-color: var(--accent-sonnet);
    color: white;
    border-radius: 4px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}
```

Shows when data is hourly (not daily).

### Responsive Design Points

**Mobile (max-width: 768px):**
- Single-column layouts
- Reduced padding
- Smaller fonts
- Simplified grids

**Tablet (max-width: 1024px):**
- Charts: 1 column instead of multi-column
- Increased min-height for chart readability

**Key Media Queries:**
```css
@media (max-width: 768px) {
    .stats-grid { grid-template-columns: 1fr; }
    .token-breakdown-grid { grid-template-columns: 1fr 1fr; }
    .filters-grid { grid-template-columns: 1fr; }
}

@media (max-width: 1024px) {
    .charts-grid { grid-template-columns: 1fr; }
}
```

---

## JavaScript Module Summary

### 1. theme.js (63 lines)

**Function:** Dark/light theme toggle with localStorage persistence

**API:**
- `initTheme()` - Initialize on page load
- `applyTheme(theme)` - Apply and persist
- `toggleTheme()` - Switch between dark/light
- `getChartColors()` - Get theme-aware colors

**State:**
- localStorage['claude-visualizer-theme']
- `<html data-theme="dark"|"light">`

**Listeners:**
- DOMContentLoaded
- System preference changes (if user hasn't set explicit preference)

### 2. timezone.js (145 lines)

**Function:** Time format conversion (UTC/Local × 24h/12h)

**API:**
- `initializeTimeFormat()` - Load saved format
- `convertTimestamps(format)` - Convert all on-page timestamps
- `formatTimestamp(isoString, format)` - Convert single timestamp
- `formatDate(isoString, format)` - Convert date only
- `changeTimeFormat(newFormat)` - Change and persist

**State:**
- localStorage['timeFormat']
- `<html data-time-format="UTC"|"Local"|"UTC-12h"|"Local-12h">`

**Data Attributes:**
- `data-timestamp="ISO8601"` - Elements with timestamps

**Events:**
- Emits: `CustomEvent('timeformatchange')`
- Listeners: charts.js, filters.js

### 3. charts.js (567 lines)

**Function:** Chart.js initialization for 7 charts

**Charts:**
1. dailyActivityChart - Line chart (messages/sessions over time)
2. modelCostChart - Doughnut (model cost split)
3. hourlyChart - Bar chart (sessions by hour)
4. dailyCostChart - Stacked area (daily cost trend)
5. projectCostChart - Horizontal bar (cost per project)
6. projectActivityChart - Line chart (project activity)
7. projectModelCostChart - Doughnut (project model breakdown)

**API Endpoints:**
- `/api/activity`
- `/api/model-split`
- `/api/hourly-distribution`
- `/api/daily-cost`
- `/api/project-cost`
- `/api/projects/{id}/activity`
- `/api/projects/{id}/cost-breakdown`

**Features:**
- Theme colors (dark/light)
- Model color mapping (Opus/Sonnet/Haiku)
- Timezone-aware labels (from timezone.js)
- Dynamic updates on filter/theme changes

**State:**
- `window.chartInstances` - Stores Chart.js instances

### 4. filters.js (187 lines)

**Function:** Date range and project filtering with localStorage

**Filters:**
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- project (encoded_path)

**API Endpoints:**
- `/api/metadata` - Get date range and projects
- Chart endpoints (with query params)

**Features:**
- Debounced input change (300ms)
- localStorage persistence
- Multi-chart updates (Promise.all)
- In-place chart updates (no page reload)
- Granularity detection (hourly vs daily)

**State:**
- localStorage['chartFilters']

### 5. htmx-config.js (32 lines)

**Function:** HTMX event handlers for loading states

**Event Handlers:**
- `htmx:configRequest` - Before request (empty, for future use)
- `htmx:xhr:loadstart` - Start: Add `.htmx-loading` class
- `htmx:xhr:loadend` - End: Remove `.htmx-loading` class
- `htmx:responseError` - Error: Log to console

**CSS Integration:**
- Uses `.htmx-loading` class from style.css
- Spinner animation via ::after pseudo-element

---

## Template Files

**Directory:** `src/app/templates/`

**Files:**
```
templates/
├── base.html              (71 lines) - Master template
├── overview.html          (166 lines) - Dashboard
├── projects.html          (85 lines) - Projects list
├── project_detail.html    (197 lines) - Single project
├── session_detail.html    (259 lines) - Session messages
├── settings.html          (42 lines) - Configuration
└── partials/
    └── session_table.html - (Not analyzed, potentially unused)
```

**Total:** 820 lines of templates

### Template Inheritance Chain

```
base.html (header, footer, scripts)
├─ overview.html ({% block content %})
├─ projects.html
├─ project_detail.html
├─ session_detail.html
└─ settings.html
```

All pages extend base.html, implement `{% block content %}`.

### Key Elements in Templates

#### base.html (71 lines)

**Header:**
- Title: "Claude Usage Visualizer"
- Navigation: Overview, Projects
- Actions: Timezone dropdown, Theme toggle, Settings link

**Main Content:**
- `{% block content %}` - Page-specific content

**Footer:**
- Last computed date (conditional)

**Scripts (load order):**
1. Chart.js (CDN)
2. HTMX (CDN)
3. theme.js (local)
4. timezone.js (local)
5. filters.js (local)
6. charts.js (local)
7. htmx-config.js (local)

#### overview.html (166 lines)

**Sections:**
1. Error banner (if error)
2. Stats grid (4 cards)
3. Token breakdown grid (4 cards)
4. Filters section (date inputs, project dropdown, reset button)
5. Charts grid (4 canvases)
6. Per-model table (with totals row)
7. Daily activity table (reversed chronologically)

#### projects.html (85 lines)

**Sections:**
1. Error box (if error)
2. Project cost chart (horizontal bar)
3. Projects table (clickable rows, 5 columns)
4. Empty state (if no projects)

#### project_detail.html (197 lines)

**Sections:**
1. Breadcrumb navigation
2. Summary cards (3: sessions, tokens, cost)
3. Charts section (2 charts, conditional)
4. Sessions table (clickable rows, 5 columns, totals row)
5. Back link

#### session_detail.html (259 lines)

**Sections:**
1. Breadcrumb navigation
2. Session metadata box (project, messages, models)
3. Summary cards (5: input, output, cache read/write, cost)
4. Messages table (7 columns, totals row)
5. Back link

#### settings.html (42 lines)

**Form:**
- Data directory input (with validation icon)
- Form actions (Save, Cancel)
- Error message display

---

## CSS Variables Quick Reference

### Color Variables

```css
/* Backgrounds */
--bg-primary: #0d1117 (dark) / #ffffff (light)
--bg-secondary: #161b22 (dark) / #f6f8fa (light)
--card-bg: #161b22 (dark) / #f6f8fa (light)
--hover-bg: #0d1117 (dark) / #e5e7eb (light)

/* Text */
--text-primary: #e6edf3 (dark) / #1f2937 (light)
--text-secondary: #8b949e (dark) / #6b7280 (light)

/* Accent Colors */
--accent-opus: #a855f7 (dark) / #9333ea (light)
--accent-sonnet: #3b82f6 (dark) / #2563eb (light)
--accent-haiku: #10b981 (dark) / #059669 (light)
--accent-color: #3b82f6 (dark) / #2563eb (light) [default]

/* Functional */
--border-color: #30363d (dark) / #d1d5db (light)
--link-color: #3b82f6 (dark) / #2563eb (light)
--error-color: #ef4444 (dark) / #dc2626 (light)
--error-bg: rgba(239, 68, 68, 0.1) (dark) / rgba(220, 38, 38, 0.1) (light)
```

---

## Asset Loading Flow

```
Page Load
  ↓
base.html script tags (in order):
  1. Chart.js (CDN) - Needed by charts.js
  2. HTMX (CDN) - Needed by htmx-config.js
  3. theme.js - Initializes theme on DOMContentLoaded
  4. timezone.js - Initializes time format on DOMContentLoaded
  5. filters.js - Initializes filters on DOMContentLoaded
  6. charts.js - Initializes charts on DOMContentLoaded
  7. htmx-config.js - Registers HTMX event listeners

Document Ready (DOMContentLoaded)
  ├─ theme.js: Reads localStorage, applies theme
  ├─ timezone.js: Reads localStorage, converts timestamps
  ├─ filters.js: Fetches metadata, populates dropdowns
  └─ charts.js: Fetches data, renders 7 charts

All listeners ready for user interaction
```

---

## Asset File Sizes (Approximate)

| File | Lines | Est. Size |
|------|-------|-----------|
| style.css | 855 | 28 KB |
| charts.js | 567 | 15 KB |
| timezone.js | 145 | 4.5 KB |
| filters.js | 187 | 5.5 KB |
| theme.js | 63 | 2 KB |
| htmx-config.js | 32 | 1 KB |
| **Total** | **1,849** | **~56 KB** |

**Plus External:**
- Chart.js 4.4.0 - ~50 KB (minified)
- HTMX 1.9.10 - ~14 KB (minified)
- **Grand Total: ~120 KB**

---

## Development Patterns

### CSS Variable Usage

Every color reference uses variables:
```css
background-color: var(--bg-primary);
color: var(--text-secondary);
border-color: var(--border-color);
```

Benefits:
- Single source of truth for colors
- Easy theme switching (just change --property value)
- No hardcoded colors (maintainable)

### Responsive Design Pattern

Mobile-first approach with enhancement:
```css
.container {
    /* Mobile defaults */
    grid-template-columns: 1fr;
}

@media (min-width: 768px) {
    .container {
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    }
}
```

### Animation Pattern

Consistent timing across interactions:
- Quick (0.2s) - Color, border, opacity
- Medium (0.3s) - Theme switch
- Slow (0.8s) - Spinner rotation

### Event Pattern (JavaScript)

Custom events for cross-module communication:
```javascript
// Emitter
document.dispatchEvent(
    new CustomEvent('timeformatchange', { detail: { format } })
);

// Listener
document.addEventListener('timeformatchange', (event) => {
    const format = event.detail.format;
});
```

---

## Known Asset Gaps

1. **No Sprite Sheet:**
   - Icons embedded in HTML as SVG
   - Could optimize with sprite/icon font

2. **No Asset Bundling:**
   - Scripts loaded separately
   - Could use webpack/vite to bundle and minify

3. **No Web Fonts:**
   - Uses system fonts only
   - Good for performance, but may look different across platforms

4. **No Image Optimization:**
   - No images currently, but process would be needed

5. **No Service Worker:**
   - No offline support
   - All assets require network

6. **Partial HTMX Usage:**
   - Infrastructure in place but not integrated
   - Event handlers configured but not used

# Repository Skill Changelog

This file tracks significant changes to the codebase that affect the agent-readiness documentation.

## Version 6 (2026-03-03)

### Major UI/UX Improvements

#### 1. Theme System Refinement
**Files Changed:**
- `src/app/static/theme.js` - Added `dispatchEvent` parameter to `applyTheme()`
- `src/app/static/charts.js` - Simplified theme change handler to immediate reload
- `src/app/static/style.css` - Complete design system overhaul

**Changes:**
- Theme change event now only dispatched on actual toggle, not initial page load
- Prevents unnecessary page reloads on first visit
- Chart text remains visible during theme transitions
- Page reloads immediately when theme toggle is clicked

**Code Reference:**
```javascript
// theme.js - Only dispatch event on toggle
function applyTheme(theme, dispatchEvent = false) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);

    if (dispatchEvent) {  // Only when toggling!
        window.dispatchEvent(new CustomEvent('themechange', {
            detail: { theme: theme }
        }));
    }
}

// charts.js - Immediate reload
document.addEventListener('themechange', () => {
    window.location.reload();  // No delay needed
});
```

#### 2. Professional Design System
**Files Changed:**
- `src/app/static/style.css` - 34 CSS custom properties updated

**Dark Theme Colors:**
- `--bg-primary: #0a0e14` (deep black)
- `--bg-secondary: #151a21` (refined gray)
- `--accent-primary: #60a5fa` (professional blue)
- Shadow system with proper depth

**Light Theme Colors:**
- `--bg-primary: #ffffff` (clean white)
- `--bg-secondary: #f8fafc` (soft gray)
- `--accent-primary: #3b82f6` (vibrant blue)
- Subtle shadows for depth

**Design Improvements:**
- Gradient backgrounds for cards
- Shadow system (--shadow-sm, --shadow-md, --shadow-lg)
- Smooth transitions (0.3s ease)
- Professional color palette
- Better contrast ratios

#### 3. Chart Maximize Feature
**Files Created:**
- `src/app/static/chart-maximize.js` - NEW fullscreen modal functionality

**Features:**
- Hover-only maximize button on all charts
- Fullscreen modal with chart cloning
- ESC key and click-outside to close
- Multiple initialization attempts (500ms, 1500ms, 3000ms)
- Handles async-loaded charts on project detail pages

**Code Reference:**
```javascript
// Button visibility - hover only
.chart-maximize-btn {
    opacity: 0;
    visibility: hidden;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.chart-wrapper:hover .chart-maximize-btn {
    opacity: 1;
    visibility: visible;
}
```

**File:** `src/app/static/chart-maximize.js:48-73`

#### 4. Chart Sizing Optimization
**Files Changed:**
- `src/app/static/style.css` - Chart wrapper heights
- `src/app/static/charts.js` - Chart.js defaults

**Changes:**
- Desktop: `min-height: 420px` + `height: 420px`
- Large screens: `min-height: 450px` + `height: 450px`
- Mobile: `min-height: 320px` + `height: 320px`
- Canvas: `max-width: 100%; max-height: 100%`
- Chart.js `aspectRatio: 2` (was 2.2)
- Explicit `height` property (not just min-height)

**Code Reference:**
```css
.chart-wrapper {
    min-height: 420px;
    height: 420px;  /* Explicit for proper Chart.js sizing */
}
```

**File:** `src/app/static/style.css:360-370`

#### 5. Token Usage Time Series Chart
**Files Changed:**
- `src/app/routers/api.py` - New endpoint `/api/token-usage-trend`
- `src/app/static/charts.js` - New chart initialization function
- `src/app/templates/overview.html` - New canvas element

**Purpose:**
Shows daily token usage by type (input, output, cache_read, cache_write) over time.

**API Endpoint:**
```python
@router.get("/token-usage-trend")
def get_token_usage_trend(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Return daily token usage by type for time series chart."""
    # Returns {"labels": [...], "datasets": [...]}
```

**File:** `src/app/routers/api.py:265-310`

**Chart Initialization:**
```javascript
function initTokenUsageTrendChart() {
    const canvas = document.getElementById('tokenUsageTrendChart');
    // 4 datasets: input, output, cache_read, cache_write
}
```

**File:** `src/app/static/charts.js:450-510`

#### 6. Cost Calculation Fix (Subagent Support)
**Files Changed:**
- `src/app/routers/sessions.py` - Use pre-calculated totals

**Issue:**
Cost numbers differed between project list and session detail pages.

**Root Cause:**
Session detail was only summing message-level costs, missing subagent costs.

**Fix:**
Use `summary.total_cost_usd` which includes all subagent costs from aggregation.

**Code Reference:**
```python
# Use pre-calculated totals (includes subagents)
total_input = summary.total_input_tokens
total_output = summary.total_output_tokens
total_cost = summary.total_cost_usd  # Includes subagent costs

has_subagents = (total_cost != message_total_cost)
```

**File:** `src/app/routers/sessions.py:45-55`

### Cache Version Updates

**All Static Assets:**
- Updated from `?v=5` to `?v=6` in `src/app/templates/base.html`
- Files: style.css, theme.js, timezone.js, filters.js, charts.js, chart-maximize.js, htmx-config.js

### Documentation Created

**FINAL_FIXES_v6.md:**
- Comprehensive documentation of all v6 fixes
- Testing instructions
- Troubleshooting guide
- Expected behavior for each fix
- Performance notes

---

## Version 5 (2026-02-28)

### Initial Feature Implementation
- Token usage trend chart added
- Maximize button initial implementation
- Theme system enhancements
- Chart sizing improvements (incomplete)

---

## Version 4 (2026-02-27)

### Design System v1
- Professional color palette (initial version)
- Maximize button visibility fixes
- CSS cascade improvements

---

## Version 3 (2026-02-26)

### UI Redesign
- Complete color palette overhaul
- Redesigned maximize button (hover-only concept)
- Shadow system added
- Gradient backgrounds

---

## Version 2 (2026-02-25)

### Bug Fixes
- Renamed session titles in detail pages
- Cost consistency across pages
- Cache busting implementation

---

## Version 1 (2026-02-20)

### Initial Agent-Ready Setup
- Phase 0-3 completion
- Domain knowledge extraction
- AGENTS.md and repo-skill created
- 21 module files with 350+ pages

---

## Key Patterns to Maintain

### 1. Theme Change Pattern
**MUST:** Only dispatch `themechange` event on actual toggle
**MUST:** Reload page immediately on theme change
**REASON:** Chart.js cannot dynamically update all colors

### 2. Chart Initialization Pattern
**MUST:** Use multiple retry attempts for button addition
**MUST:** Check for existing buttons before adding
**REASON:** Charts load asynchronously on some pages

### 3. Chart Sizing Pattern
**MUST:** Set both `min-height` and `height` on chart-wrapper
**MUST:** Use `max-width: 100%; max-height: 100%` on canvas
**REASON:** Chart.js needs explicit container heights

### 4. Cost Calculation Pattern
**MUST:** Use pre-calculated totals from summary objects
**REASON:** Totals include subagent costs from aggregation

### 5. CSS Cascade Pattern
**MUST:** Define base state before hover state
**EXAMPLE:** `.chart-maximize-btn` before `.chart-wrapper:hover .chart-maximize-btn`
**REASON:** Proper CSS specificity and cascade

---

## Testing Checklist for Future Changes

When modifying these systems, always test:

1. **Theme Switching:**
   - Click toggle → immediate reload
   - All chart text visible in both themes
   - No double-reload on initial page load

2. **Chart Sizing:**
   - Charts fill ~90% of container
   - Minimal white space
   - Responsive on different screen sizes

3. **Maximize Button:**
   - Only visible on hover
   - Works on overview page
   - Works on project detail pages (wait 3-4 seconds)
   - Fullscreen modal displays correctly

4. **Cost Numbers:**
   - Consistent between project list and session detail
   - Info banner shows when subagents present
   - Totals include all subagent costs

5. **Cache Busting:**
   - Increment version number in base.html
   - Hard refresh required for testing
   - Check all static assets load new version

---

**Last Updated:** 2026-03-03
**Current Version:** v6
**Status:** All critical issues resolved

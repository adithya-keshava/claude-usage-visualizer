# Phase 4 Quick Start Guide

## What's New

Phase 4 adds **interactive filtering** and **project-specific analytics** to the Claude Usage Visualizer.

### New Features

1. **Date Range Filtering** - Select custom start/end dates
2. **Auto Granularity** - Hourly data for < 1 day, daily otherwise
3. **Project Filtering** - Isolate analytics to specific projects
4. **Filter Persistence** - Filters saved to browser localStorage
5. **Project Charts** - View activity and cost breakdown per project

## Quick Demo

### 1. Filter Overview Page Charts

1. Open the app and navigate to **Overview**
2. Scroll down to the **Filters** section
3. Select a date range: `start_date: 2026-02-14`, `end_date: 2026-02-14`
4. Watch charts update automatically
5. Notice the badge: **"📊 Showing Hourly Data"** (< 1 day range)
6. Now select a longer range: `start_date: 2026-02-10`, `end_date: 2026-02-14`
7. Charts switch to daily view, badge disappears

### 2. Filter by Project

1. In the Filters section, select a project from the dropdown
2. All charts now show data only for that project
3. Project dropdown shows session count per project
4. Click **Reset to All Time** to clear all filters

### 3. View Project-Specific Analytics

1. Click **Projects** in the navigation
2. Click on any project to view its detail page
3. Scroll down to **Project Analytics** section
4. Two new charts appear:
   - **Project Activity Over Time** - Messages/sessions timeline
   - **Model Cost Distribution** - Which models were used and costs

### 4. Filter Persistence

1. Set filters (date range, project)
2. Refresh the page - filters persist
3. Close browser and reopen - filters are still there
4. Click **Reset to All Time** to clear saved filters

## API Endpoints (For Developers)

### New Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/metadata` | Get date range, projects, and session counts |
| `GET /api/activity` | Smart endpoint (hourly/daily auto-select) |
| `GET /api/projects/{path}/activity` | Project-specific activity |
| `GET /api/projects/{path}/cost-breakdown` | Project model cost breakdown |

### Modified Endpoints (Now Support Filtering)

All these now accept optional `start_date` and `end_date` query params:
- `GET /api/daily-activity`
- `GET /api/daily-cost`
- `GET /api/hourly-distribution`
- `GET /api/project-cost`

### Example Requests

```bash
# Get available date range and projects
curl http://localhost:8000/api/metadata

# Get hourly activity for single day
curl "http://localhost:8000/api/activity?start_date=2026-02-14&end_date=2026-02-14"

# Get daily activity for date range
curl "http://localhost:8000/api/activity?start_date=2026-02-10&end_date=2026-02-14"

# Get activity for specific project
curl "http://localhost:8000/api/activity?project=-Users-adithya-k-IdeaProjects-ada"

# Get project-specific activity chart
curl "http://localhost:8000/api/projects/-Users-adithya-k-IdeaProjects-ada/activity"

# Get project cost breakdown by model
curl "http://localhost:8000/api/projects/-Users-adithya-k-IdeaProjects-ada/cost-breakdown"
```

## Frontend Architecture

### New Files

- **`src/app/static/filters.js`** - Filter management module
  - Fetches metadata on page load
  - Manages filter state and localStorage
  - Updates charts on filter change
  - 300ms debounce prevents excessive API calls

### Modified Files

- **`src/app/templates/overview.html`** - Added filters section before charts
- **`src/app/templates/project_detail.html`** - Added project analytics charts
- **`src/app/templates/base.html`** - Included filters.js script
- **`src/app/static/charts.js`** - Updated chart init, added project charts
- **`src/app/static/style.css`** - Added filter UI styles

## How Filtering Works

### 1. Page Load

```
filters.js loads
  ↓
Fetch /api/metadata
  ↓
Initialize date inputs (min/max from metadata)
  ↓
Populate project dropdown
  ↓
Load filters from localStorage
  ↓
Apply saved filters to charts
```

### 2. User Changes Filter

```
User changes date or project
  ↓
Debounce (300ms)
  ↓
Save to localStorage
  ↓
Fetch updated chart data with new filters
  ↓
updateChart() updates each chart canvas
  ↓
Check granularity, show/hide hourly badge
```

### 3. Hourly vs Daily Selection

```
JavaScript checks date range
  ↓
if (end - start < 1 day):
    Call /api/activity → hourly aggregation
    Show granularity badge
else:
    Call /api/activity → daily aggregation
    Hide badge
```

## Browser Developer Tools Testing

### Check Filter State
```javascript
// View saved filters
JSON.parse(localStorage.getItem('chartFilters'))

// Clear saved filters
localStorage.removeItem('chartFilters')

// View chart instances
window.chartInstances
```

### Test API Calls
Open DevTools Network tab and:
1. Change a filter
2. Watch `/api/activity?start_date=...` request
3. See chart update with response data

## Customization Ideas

### Change Debounce Delay
In `filters.js`, find:
```javascript
const debouncedApply = debounce(applyFilters, 300);
```
Change `300` to your desired milliseconds.

### Add More Project Filters
In `get_metadata()` endpoint, add more fields to project object:
```python
"created_at": session[0].timestamp if sessions else None,
"language": project.language,  # if tracked
```

### Change Hourly Threshold
In `charts.js`, find the `/api/activity` call and modify the logic:
```python
# Change this in api.py:
if duration < 1:  # < 1 day
    # Change to: if duration < 7: for weekly threshold
```

## Performance Tips

1. **Large Date Ranges**: Hourly is only calculated for < 1 day ranges. Longer ranges use daily cache (fast).

2. **Many Projects**: Metadata endpoint returns sorted by session count. High-activity projects appear first.

3. **localStorage**: Filters stored as JSON string. Manual localStorage cleanup available in DevTools.

## Known Limitations

1. **Hourly Aggregation**: Reads individual session messages, slower for very large datasets
2. **Project Names**: Uses last segment of encoded path (e.g., `...ada-dsl` → `ada-dsl`)
3. **Project Filtering**: Filters only on session date, not individual message dates
4. **Mobile**: Filter grid collapses to single column on mobile

## Testing Checklist

- [ ] Filters section appears above charts on Overview page
- [ ] Date inputs have correct min/max values
- [ ] Project dropdown populates with projects
- [ ] Selecting date range updates charts
- [ ] Hourly badge appears for < 1 day ranges
- [ ] Filters persist after page refresh
- [ ] Reset button clears filters
- [ ] Project detail page shows new charts
- [ ] No console errors in DevTools
- [ ] All charts render without errors

## Troubleshooting

### Filters don't appear
- Check that filters.js is loaded (DevTools Sources)
- Verify `/api/metadata` returns data
- Check browser console for errors

### Charts not updating
- Open DevTools Network tab
- Change a filter
- Verify API request is made
- Check response contains data
- Look for console errors

### Date inputs have no range
- Verify `/api/metadata` returns `oldest_date` and `newest_date`
- Check HTML shows `min` and `max` attributes on date inputs

### localStorage errors
- Check if localStorage is enabled in browser
- Try clearing site data and reloading

## Next Steps

See `PHASE4_IMPLEMENTATION.md` for complete documentation and architecture decisions.

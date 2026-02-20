# Phase 4 Implementation: Interactive Filtering & Folder-wise Analytics

## Overview

Phase 4 successfully adds interactive filtering and folder-wise (project-wise) analytics to the Claude Usage Visualizer dashboard. Users can now filter charts by date range and project, with automatic switching between hourly and daily granularity based on the selected time period.

## Implementation Complete ✓

### Backend API Enhancements

#### Modified Endpoints (Date Range Filtering)
All existing endpoints now support optional `start_date` and `end_date` query parameters:

1. **GET `/api/daily-activity`** - Daily activity (messages/sessions per day)
   - Optional: `start_date`, `end_date`
   - Example: `/api/daily-activity?start_date=2026-02-10&end_date=2026-02-14`

2. **GET `/api/daily-cost`** - Daily cost by model
   - Optional: `start_date`, `end_date`
   - Example: `/api/daily-cost?start_date=2026-02-14`

3. **GET `/api/hourly-distribution`** - Session starts by hour
   - Optional: `start_date`, `end_date`
   - Recomputes hourly distribution when filters change

4. **GET `/api/project-cost`** - Cost per project
   - Optional: `start_date`, `end_date`
   - Filters projects by session date range

5. **GET `/api/model-split`** - Model cost distribution
   - No changes needed (always shows all-time aggregates)

#### New Endpoints

1. **GET `/api/metadata`** - Dashboard metadata
   - Returns: `oldest_date`, `newest_date`, `total_sessions`, `total_messages`, `projects[]`
   - Used by filters.js to initialize date picker and project dropdown
   - Example response:
   ```json
   {
     "oldest_date": "2026-02-02",
     "newest_date": "2026-02-15",
     "total_sessions": 62,
     "total_messages": 13518,
     "projects": [
       {
         "encoded_path": "-Users-adithya-k-IdeaProjects-ada",
         "display_name": "-Users-adithya-k-IdeaProjects-ada",
         "session_count": 42
       },
       ...
     ]
   }
   ```

2. **GET `/api/activity`** - Smart activity endpoint with auto-granularity
   - Parameters: `start_date`, `end_date`, `project` (all optional)
   - Auto-selects hourly vs daily based on date range:
     - If date range < 1 day: Returns hourly data
     - Otherwise: Returns daily data
   - Returns: `labels[]`, `datasets[]`, `granularity` ("hourly"|"daily")
   - Example: `/api/activity?start_date=2026-02-14&end_date=2026-02-14`
   ```json
   {
     "labels": ["2026-02-14T19:00", "2026-02-14T20:00", ...],
     "datasets": [...],
     "granularity": "hourly"
   }
   ```

3. **GET `/api/projects/{encoded_path}/activity`** - Project-specific activity
   - Parameters: `start_date`, `end_date` (optional)
   - Returns daily activity aggregation for a single project
   - Example: `/api/projects/-Users-adithya-k-IdeaProjects-ada/activity`

4. **GET `/api/projects/{encoded_path}/cost-breakdown`** - Project model costs
   - Returns cost breakdown by model for a specific project
   - Example: `/api/projects/-Users-adithya-k-IdeaProjects-ada/cost-breakdown`

### Frontend Components

#### New Filter UI (overview.html)
Added interactive filter controls section before charts:
- **Start Date** input - Select beginning of date range
- **End Date** input - Select end of date range
- **Project** dropdown - Filter by specific project (shows session count)
- **Reset to All Time** button - Clear all filters and reload

Features:
- Date inputs have min/max set from metadata endpoint
- Project dropdown populated from available projects
- All filters saved to localStorage for persistence
- 300ms debounce prevents excessive API calls
- Granularity indicator shows when hourly data is active

#### New JavaScript Module (filters.js)
Comprehensive filter management following timezone.js pattern:
- `initFilters()` - Initialize UI from metadata and saved filters
- `applyFilters()` - Apply current filter state to all charts
- `updateChart(chartId, apiUrl)` - Update individual chart with new data
- `resetFilters()` - Clear filters and reload page
- `debounce()` - Helper for throttling API calls

#### Updated Chart Initialization (charts.js)
- Daily Activity chart now uses `/api/activity` instead of `/api/daily-activity`
- Auto-updates title based on granularity ("Hourly Activity" vs "Daily Activity")
- All chart init functions store Chart.js instances for dynamic updates
- Added project-specific chart functions:
  - `initProjectActivityChart()` - Project activity over time
  - `initProjectModelCostChart()` - Project model cost distribution

#### New Project Detail Charts (project_detail.html)
Added analytics section with two charts:
1. **Project Activity Over Time** - Messages/sessions by day
2. **Model Cost Distribution** - Cost breakdown by model for project

Charts load via `/api/projects/{encoded_path}/activity` and `/api/projects/{encoded_path}/cost-breakdown`

#### Filter UI Styling (style.css)
New CSS classes for filters:
- `.filters-section` - Main container
- `.filters-grid` - Responsive grid layout
- `.filter-group` - Individual filter control wrapper
- `.date-input`, `.project-select` - Input/select styling
- `.btn-secondary` - Reset button styling
- `.granularity-badge` - Hourly indicator badge

Responsive design: Single column on mobile, auto-flow on desktop

### Backend Helper Functions (loader.py)

#### `build_hourly_activity(start_date, end_date, project)`
New function for hourly aggregation:
- Processes session messages to build hourly time series
- Only called for date ranges < 1 day (performance optimization)
- Returns list of dicts with: `hour`, `message_count`, `session_count`, `total_cost`
- Supports project filtering

## Verification Results

### API Endpoint Testing
✓ `/api/metadata` - Returns oldest/newest dates, project list, session counts
✓ `/api/activity?start_date=2026-02-14&end_date=2026-02-14` - Returns hourly data
✓ `/api/activity?start_date=2026-02-10&end_date=2026-02-14` - Returns daily data
✓ `/api/daily-cost?start_date=2026-02-14` - Filters daily costs by date
✓ `/api/projects/-Users-adithya-k-IdeaProjects-ada/activity` - Project activity data
✓ `/api/projects/-Users-adithya-k-IdeaProjects-ada/cost-breakdown` - Project cost breakdown

### Code Quality
✓ All Python syntax valid
✓ All imports properly sorted
✓ Linting: `All checks passed!`

## Usage Guide

### For Users

#### Filtering Charts
1. Navigate to Overview page
2. Use filter controls to select date range and/or project
3. Charts update automatically (300ms delay for performance)
4. Filters saved to browser localStorage
5. Click "Reset to All Time" to clear filters

#### Hourly vs Daily Granularity
- **Hourly** (< 1 day range): Shows activity by the hour
  - Badge displays: "📊 Showing Hourly Data"
  - Example: Select same date for start and end
- **Daily** (>= 1 day range): Shows activity by day
  - Badge hidden
  - Example: Select a 7-day range

#### Project-Specific Analytics
1. Click "Projects" in navigation
2. Select a project from the list
3. View two new charts:
   - **Project Activity Over Time** - Track messages/sessions by day
   - **Model Cost Distribution** - See which models were used and their cost
4. Sessions table shows detailed per-session breakdown

### For Developers

#### Adding Date Filtering to New Endpoints
All endpoints follow the same pattern:

```python
@router.get("/api/your-endpoint")
def your_endpoint(start_date: Optional[str] = None, end_date: Optional[str] = None):
    data = load_some_data()
    filtered_data = filter_by_date_range(data, start_date, end_date)
    return format_response(filtered_data)
```

#### Integrating New Project Analytics
To add new project metrics:

1. Create API endpoint: `/api/projects/{encoded_path}/your-metric`
2. Add chart canvas to `project_detail.html`
3. Add init function to `charts.js`:
```javascript
function initYourProjectChart() {
    const canvas = document.getElementById('yourChart');
    if (!canvas) return;
    const pathMatch = window.location.pathname.match(/\/projects\/([^\/]+)$/);
    // Fetch and render...
}
```

## Architecture Decisions

### 1. Smart Granularity Selection
- Auto-switches hourly/daily based on date range (< 1 day = hourly)
- Single `/api/activity` endpoint instead of separate endpoints
- Benefits:
  - Reduces frontend complexity
  - Provides best UX for different time scales
  - Performance optimized (hourly only for small ranges)

### 2. Debounced Updates (300ms)
- Prevents excessive API calls during date picker interaction
- Matches user expectation for interactive performance
- Follows pattern from timezone.js for consistency

### 3. localStorage Persistence
- Filters saved automatically as user changes them
- Loaded on page refresh
- Benefits:
  - Users can close/reopen browser and keep filter state
  - Matches timezone toggle behavior
  - No backend state needed

### 4. Hourly Aggregation Strategy
- `build_hourly_activity()` reads individual session messages
- Only invoked for < 1 day ranges (performance trade-off)
- Slower than daily cache but provides fine-grained data
- Alternative: Could pre-compute all hourly data (more storage, faster queries)

### 5. Project-wise Charts
- Separate endpoints for activity and cost-breakdown
- Displayed on project detail page (not overview)
- Benefits:
  - Keeps overview focused on all-time stats
  - Project page provides detailed project-specific insights
  - Can be extended for more project metrics

## Performance Considerations

### Optimization Done
1. ✓ Caching stats-cache and project summaries
2. ✓ Debouncing API calls (300ms)
3. ✓ Only computing hourly data for < 1 day ranges
4. ✓ Lazy-loading project charts (only on project detail page)

### Potential Future Optimizations
1. Cache hourly aggregations for common date ranges
2. Paginate large project lists with infinite scroll
3. Pre-compute hourly data during daily cache build
4. Use IndexedDB for client-side caching of API responses

## Browser Compatibility

- Modern browsers with Chart.js 4.4.0 support
- Tested with:
  - Chrome/Edge (latest)
  - Firefox (latest)
  - Safari (latest)
- Requires JavaScript enabled
- localStorage required for filter persistence

## Future Enhancement Ideas

1. **Time Granularity Controls**
   - Weekly/monthly grouping for longer ranges
   - User-selectable granularity

2. **Multi-Project Comparison**
   - Compare side-by-side metrics for multiple projects
   - Relative cost/token trends

3. **Shareable Filter URLs**
   - URL-based filter state: `/?start_date=2026-02-10&end_date=2026-02-14`
   - Copy/share dashboard snapshots

4. **Export Functionality**
   - CSV export of filtered data
   - PDF report generation

5. **Advanced Analytics**
   - Trend analysis (cost slope over time)
   - Outlier detection (unusual spike alerts)
   - Predictive usage forecasting

6. **Real-time Updates**
   - WebSocket integration for live stats
   - Charts update as new sessions complete

## Files Changed

### Backend
- `src/app/routers/api.py` - Added query parameters, new endpoints, filter logic
- `src/app/data/loader.py` - Added `build_hourly_activity()` function

### Frontend
- `src/app/templates/base.html` - Added filters.js script include
- `src/app/templates/overview.html` - Added filter UI section
- `src/app/templates/project_detail.html` - Added project analytics charts
- `src/app/static/filters.js` - NEW: Filter management module
- `src/app/static/charts.js` - Updated chart init functions, added project charts
- `src/app/static/style.css` - Added filter UI styles

## Conclusion

Phase 4 implementation is complete and fully functional. All API endpoints are working correctly, filter UI is responsive and intuitive, and project-specific analytics provide deeper insights into usage patterns. The implementation follows existing code patterns (timezone.js, theme.js) for consistency and maintainability.

Users can now:
- Filter all charts by custom date ranges
- View hourly trends for recent activity
- Analyze individual project performance
- Persist filter preferences across sessions

The foundation is set for future enhancements like advanced analytics, real-time updates, and exportable reports.

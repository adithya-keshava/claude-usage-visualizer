# HTMX Integration Patterns

**Document:** Claude Usage Visualizer - HTMX Configuration and Usage
**Scope:** `src/app/static/htmx-config.js` - Event handlers and potential endpoints
**Last Updated:** 2026-02-20

---

## Overview

HTMX is installed and configured for dynamic HTML updates without full page reloads. Currently, the configuration is in place but minimal HTMX attributes are used in templates. The setup includes:

**Implemented:**
- Global event handlers for loading states
- Error handling for AJAX failures
- Request configuration hooks

**Not Yet Implemented:**
- Dynamic table filtering
- Lazy-loaded content
- Form submissions without page reload
- Paginated results
- Real-time data updates

---

## HTMX Configuration

**File:** `src/app/static/htmx-config.js:1-32`

### Request Configuration Hook

**Lines:** `src/app/static/htmx-config.js:7-9`

```javascript
document.addEventListener('htmx:configRequest', (detail) => {
    // Add any custom headers if needed
});
```

**Purpose:** Intercept all HTMX requests before sending.

**Current Usage:** Hook present but empty (no custom headers added).

**Potential Usage Patterns:**
- Add CSRF tokens if form validation implemented
- Add authentication headers
- Add custom content negotiation headers
- Log request metrics

---

## Loading State Management

### Show Loading Indicator

**Lines:** `src/app/static/htmx-config.js:12-17`

```javascript
document.addEventListener('htmx:xhr:loadstart', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.add('htmx-loading');
    }
});
```

**Trigger:** Fires when HTMX request starts.

**Behavior:**
1. Get event details from HTMX
2. Find target element by selector
3. Add `htmx-loading` CSS class

**CSS Integration:** Expected CSS class in stylesheets:
```css
.htmx-loading {
    opacity: 0.6;
    cursor: wait;
    /* or spinner animation */
}
```

**Current State:** CSS class added but styling not verified.

### Hide Loading Indicator

**Lines:** `src/app/static/htmx-config.js:20-25`

```javascript
document.addEventListener('htmx:xhr:loadend', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.remove('htmx-loading');
    }
});
```

**Trigger:** Fires when HTMX request completes (success or error).

**Behavior:** Removes `htmx-loading` class from target element.

---

## Error Handling

### Response Error Handler

**Lines:** `src/app/static/htmx-config.js:28-31`

```javascript
document.addEventListener('htmx:responseError', (event) => {
    console.error('HTMX request failed:', event.detail);
    // Could show user-facing error message here
});
```

**Trigger:** Fires on HTTP error status (4xx, 5xx).

**Current Behavior:**
- Log error to browser console
- Comment shows potential for toast/modal notifications

**Improvement Opportunities:**
- Show error toast/notification to user
- Specific handling for 404 vs 500
- Retry logic for transient failures
- Error analytics/logging

**Error Details Available:** `event.detail` includes:
- `xhr`: XMLHttpRequest object
- `target`: Target element
- `status`: HTTP status code
- `statusText`: Status message

---

## Potential HTMX Integration Points

### Pattern 1: Dynamic Table Filtering

**Scenario:** Projects table with search/filter

```html
<!-- Hypothetical usage -->
<input
    type="text"
    name="search"
    placeholder="Search projects..."
    hx-post="/api/search-projects"
    hx-target="#project-table"
    hx-trigger="keyup delay:500ms"
/>

<table id="project-table">
    <!-- Populated by HTMX response -->
</table>
```

**Benefits:**
- Instant search feedback
- Reduces page reloads
- Natural progressive enhancement

**Required Endpoint:** `/api/search-projects` POST
- Accepts: `?search=query`
- Returns: HTML table body rows

### Pattern 2: Pagination

**Scenario:** Sessions table with next/previous

```html
<!-- Hypothetical usage -->
<div id="sessions-list">
    <!-- Session rows -->
</div>

<button
    hx-get="/api/sessions?page=2"
    hx-target="#sessions-list"
    hx-swap="innerHTML"
>
    Load More
</button>
```

**Benefits:**
- Load content on demand
- Improve initial page load
- Infinite scroll capability

### Pattern 3: Form Submission

**Scenario:** Settings form without page reload

```html
<!-- Current form (would need HTMX) -->
<form method="post" action="/settings" class="settings-form">
    <input type="text" name="data_dir" required>
    <button type="submit">Save</button>
</form>

<!-- With HTMX attributes -->
<form
    method="post"
    action="/settings"
    hx-post="/settings"
    hx-target="this"
    hx-swap="outerHTML"
    class="settings-form"
>
    <input type="text" name="data_dir" required>
    <button type="submit">Save</button>
</form>
```

**Benefits:**
- Form submission without page reload
- Show success/error inline
- Preserve form state on error

**Server Response:** Return HTML to replace form or error message.

### Pattern 4: Lazy Loading Content

**Scenario:** Load project details on demand

```html
<!-- Hypothetical usage -->
<div
    hx-get="/projects/{{ encoded_path }}/lazy-load"
    hx-trigger="revealed"
    hx-swap="innerHTML"
>
    Loading project details...
</div>
```

**Trigger Options:**
- `revealed`: When scrolled into view
- `click`: On element click
- `load`: On page load with delay
- Custom events

---

## Current Template HTMX Usage

### Search Results

**File:** `src/app/templates/settings.html`

**Current State:** No HTMX attributes found.

**Form Structure:**
- Method: POST to `/settings`
- Full page reload on submit
- Traditional form handling

**Potential Enhancement:**
```html
<form
    method="post"
    action="/settings"
    hx-post="/settings"
    hx-target="this"
    hx-swap="outerHTML swap:1s"
>
    <!-- inputs -->
</form>
```

---

## HTMX Event Flow

### Request Lifecycle

```
User Action (click, input, etc.)
    ↓
htmx:trigger
    ↓
htmx:configRequest
    ├─ Add headers, modify request
    ↓
htmx:xhr:loadstart
    ├─ Show loading indicator
    ↓
[Network Request]
    ↓
200 OK Response (HTML)
    ├─ htmx:xhr:loadend
    ├─ htmx:beforeSwap
    ├─ [Update DOM]
    ├─ htmx:afterSwap
    ├─ htmx:afterSettle
    ↓
OR

4xx/5xx Error Response
    ├─ htmx:xhr:loadend
    ├─ htmx:responseError
    ├─ Log error, show notification
```

### Event Handlers in Use

| Event | Handler | Current Behavior |
|-------|---------|-----------------|
| `htmx:configRequest` | Line 7 | Empty (ready for custom headers) |
| `htmx:xhr:loadstart` | Line 12 | Add `htmx-loading` class |
| `htmx:xhr:loadend` | Line 20 | Remove `htmx-loading` class |
| `htmx:responseError` | Line 28 | Log to console |
| Other events | None | Not handled |

---

## API Endpoint Structure for HTMX

### Response Format

HTMX expects HTML fragments (not JSON) for swap operations.

**Example Endpoint (hypothetical):**

```python
@router.post("/search-projects")
def search_projects(search: str = ""):
    # Fetch matching projects
    projects = build_project_summaries()
    filtered = {k: v for k, v in projects.items() if search.lower() in k.lower()}

    # Return HTML fragment (rendered template)
    template = env.get_template("partials/project_rows.html")
    return template.render(projects=filtered)
```

**Returns:** HTML rows (no wrapper)
```html
<tr><td>project-a</td><td>$123.45</td></tr>
<tr><td>project-b</td><td>$456.78</td></tr>
```

**Client:** HTMX inserts into target element using specified swap strategy.

### Swap Strategies

**Common HTMX `hx-swap` values:**

| Value | Effect |
|-------|--------|
| `innerHTML` | Replace contents of target |
| `outerHTML` | Replace entire target element |
| `beforebegin` | Insert before target |
| `afterbegin` | Insert at start of contents |
| `beforeend` | Insert at end of contents |
| `afterend` | Insert after target |
| `delete` | Remove target |
| `none` | Don't update DOM |

**Current Patterns:** Not used in templates yet.

---

## Loading Indicators

### CSS Class Management

**Class Added:** `htmx-loading`
**Trigger:** Before AJAX request
**Removed:** After request completes

**Typical CSS Implementation:**

```css
/* Fade out element during loading */
.htmx-loading {
    opacity: 0.5;
    pointer-events: none;
}

/* Show spinner overlay */
.htmx-loading::after {
    content: '';
    display: inline-block;
    width: 16px;
    height: 16px;
    margin-left: 8px;
    border: 2px solid rgba(99, 102, 241, 0.3);
    border-radius: 50%;
    border-top-color: rgba(99, 102, 241, 1);
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

**Status:** CSS class infrastructure in place, but visual styling not implemented.

---

## Error Recovery Patterns

### Current Implementation

```javascript
document.addEventListener('htmx:responseError', (event) => {
    console.error('HTMX request failed:', event.detail);
});
```

**Behavior:** Log only, no user-facing feedback.

### Recommended Enhancement

```javascript
document.addEventListener('htmx:responseError', (event) => {
    const {xhr, target, status} = event.detail;

    // Show error notification
    const notification = document.createElement('div');
    notification.className = 'error-notification';
    notification.textContent = `Failed to load data (${status}). Please try again.`;
    document.body.appendChild(notification);

    // Auto-dismiss after 5 seconds
    setTimeout(() => notification.remove(), 5000);

    // Log for debugging
    console.error(`HTMX error (${status}):`, xhr.response);
});
```

---

## Performance Considerations

### Request Volume

**Per HTMX Attribute:**
- Each `hx-trigger` generates API request
- Default trigger: form submit or element click
- Can add debouncing: `hx-trigger="keyup delay:500ms"`

**Optimization Strategies:**
- Debounce rapid triggers (search input)
- Throttle scroll-triggered loads
- Cache HTMX responses (server-side cache already in place)
- Pagination over infinite scroll (reduces payload)

### Payload Size

**Current State:**
- JSON API responses: ~1-10 KB per request
- HTML fragments (if used): Similar size
- No gzip compression mentioned

**Optimization:**
- Compress HTML responses
- Send only changed data
- Minimize CSS/JS in HTMX responses

---

## Browser Compatibility

**HTMX Support:**
- Modern browsers (Chrome, Firefox, Safari, Edge)
- IE not supported
- Graceful degradation not implemented (forms would still POST, causing page reload)

**Current Fallback:** Traditional form submission (acceptable for this app).

---

## Integration with Other Modules

### Theme System

HTMX works with `src/app/static/theme.js`:
- HTMX can emit custom events after swap
- Theme module listens to those events
- Update theme colors for new content

**Example:**
```javascript
htmx.on('htmx:afterSettle', (event) => {
    // Re-apply theme to newly inserted content
    applyCurrentTheme();
});
```

### Timezone System

Similar integration with `src/app/static/timezone.js`:
- Format timestamps in HTMX responses
- HTMX responses already formatted by server

---

## Testing HTMX

### Manual Testing

1. **Load Indicator Test:**
   - Add `hx-get` to element
   - Trigger request
   - Verify `htmx-loading` class added/removed
   - Check network tab for request

2. **Error Handling Test:**
   - Trigger request to non-existent endpoint (404)
   - Verify error logged to console
   - Verify `htmx-loading` class removed

3. **Response Processing:**
   - Verify HTML fragment inserted correctly
   - Check for JavaScript errors in console
   - Verify styling applied to new elements

### Browser DevTools

**HTMX Debugging:**
```javascript
// In console
htmx.logAll()  // Enable verbose logging
```

**Event Inspection:**
```javascript
// In console
document.addEventListener('htmx:*', (event) => {
    console.log(event.type, event.detail);
});
```

---

## Migration Path (When Ready)

### Phase 1: Settings Form
```html
<form hx-post="/settings" hx-target="this" hx-swap="outerHTML">
    <!-- existing form -->
</form>
```

### Phase 2: Search/Filter
```html
<input
    type="text"
    name="search"
    hx-post="/api/search-projects"
    hx-target="#results"
    hx-trigger="keyup delay:500ms"
/>
```

### Phase 3: Pagination
```html
<button hx-get="/projects?page=2" hx-target="#projects" hx-swap="innerHTML">
    Load More
</button>
```

### Phase 4: Real-time Updates
```html
<div hx-get="/api/activity" hx-trigger="every 30s" hx-swap="innerHTML">
    <!-- auto-updating activity -->
</div>
```

---

## Related Modules

- **Theme:** `src/app/static/theme.js` - Event integration
- **Timezone:** `src/app/static/timezone.js` - Format conversion
- **Settings Router:** `src/app/routers/settings.py` - Form handling endpoint
- **API Router:** `src/app/routers/api.py` - Potential HTMX endpoints

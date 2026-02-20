# Frontend: HTMX Integration Points

## Overview

HTMX 1.9.10 is loaded in the application but currently minimally integrated. Infrastructure is in place for future dynamic content loading without full page reloads.

**Files:**
- `src/app/static/htmx-config.js` - Event handlers and configuration
- `src/app/templates/base.html:11` - HTMX script CDN

---

## Current HTMX Configuration

**File:** `src/app/static/htmx-config.js:1-32`

### Event Handlers

#### 1. Config Request Hook (lines 7-9)

```javascript
document.addEventListener('htmx:configRequest', (detail) => {
    // Add any custom headers if needed
});
```

**Purpose:** Fires before every HTMX request

**Current State:** Empty, available for custom headers
- Could add: CSRF tokens, authorization headers, request ID tracking

**Example Usage (if needed):**
```javascript
document.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-Request-ID'] = generateRequestId();
    event.detail.headers['Authorization'] = `Bearer ${token}`;
});
```

#### 2. XHR Load Start (lines 12-17)

```javascript
document.addEventListener('htmx:xhr:loadstart', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.add('htmx-loading');
    }
});
```

**Purpose:** Fires when HTMX request starts

**Behavior:**
1. Finds target element from XHR request
2. Adds class `htmx-loading` to apply loading state

**CSS Effect** (style.css:653-686):
- Opacity: 0.6 (dims content)
- Pointer-events: none (disables interaction)
- After pseudo-element: Spinning loader animation
  - Border spinner with blue top
  - 0.8s linear infinite rotation

#### 3. XHR Load End (lines 20-25)

```javascript
document.addEventListener('htmx:xhr:loadend', (event) => {
    const target = htmx.find(event.detail.xhr.target);
    if (target) {
        target.classList.remove('htmx-loading');
    }
});
```

**Purpose:** Fires when HTMX request completes (success or error)

**Behavior:**
1. Finds target element
2. Removes `htmx-loading` class
3. Restores interaction

#### 4. Response Error (lines 28-31)

```javascript
document.addEventListener('htmx:responseError', (event) => {
    console.error('HTMX request failed:', event.detail);
    // Could show user-facing error message here
});
```

**Purpose:** Fires when HTMX response has error (4xx or 5xx status)

**Current State:** Logs to console only

**Future Enhancement (noted in comment):**
- Could display user-facing error toast
- Could retry failed requests
- Could redirect to error page

---

## HTMX Attributes Not Yet Used

These attributes are not currently in templates but could be integrated:

### 1. Core Request Attributes

**`hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`**

```html
<button hx-get="/api/endpoint">Load Data</button>
```

Sends HTTP request on trigger event.

**Usage Opportunity:**
- Dynamic filter updates (instead of full page reload)
- Pagination (load more button)
- Form submission with inline response

**Example for Filters:**
```html
<button id="reset-filters" hx-get="/" hx-target="#main-content">
    Reset to All Time
</button>
```

### 2. Target and Swap Attributes

**`hx-target`** - Where to insert response

```html
<button hx-get="/data" hx-target="#result">Load</button>
```

**`hx-swap`** - How to swap content

```html
<button hx-get="/data" hx-swap="innerHTML">Replace Content</button>
<button hx-get="/item" hx-swap="outerHTML">Replace Element</button>
<button hx-get="/item" hx-swap="afterbegin">Prepend</button>
<button hx-get="/item" hx-swap="beforeend">Append</button>
```

**Current Pattern (example):**
```
Charts section updates:
- Full page reload on filter change
- Could instead: hx-get="/api/activity" hx-target="#dailyActivityChart" hx-swap="outerHTML"
```

### 3. Trigger Attributes

**`hx-trigger`** - Event that triggers request

```html
<input type="text" hx-get="/search" hx-trigger="keyup changed delay:500ms">
<select hx-get="/filter" hx-trigger="change">
```

**Current Pattern (example):**
```
Date filter inputs:
- JavaScript debounced change listener (300ms)
- Could instead: hx-trigger="change delay:300ms"
```

### 4. Dynamic Content Loading

**`hx-load`, `hx-boost`**

```html
<a href="/page2" hx-boost="true">Load Page</a>
```

**Usage Opportunity:**
- Navigation without full page reload
- Preserve scroll position
- Keep JavaScript state (theme, timezone)

**Current Pattern:**
```
Projects list → Project detail:
- Full navigation, page reload
- Could: <a href="/projects/{{ id }}" hx-boost="true">
```

### 5. Form Submission with HTMX

**`hx-post` on forms**

```html
<form hx-post="/settings" hx-target="#response">
    <input type="text" name="data_dir">
    <button type="submit">Save</button>
</form>
```

**Current Pattern:**
```
Settings form uses standard form submission (POST to /settings)
- Full page reload on submit
- Could use HTMX for smoother UX
```

### 6. Out of Band Swap

**`hx-swap-oob`** - Update multiple elements from single response

```html
<!-- Response contains: -->
<div id="main-content">...</div>
<div id="status" hx-swap-oob="true">Updated Status</div>
```

Both elements update from one request.

---

## Loading Indicator Implementation

### CSS Classes

**`.htmx-loading`** - Applied during HTMX request

```css
.htmx-loading {
    opacity: 0.6;
    pointer-events: none;
}

.htmx-loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color);
    border-top-color: var(--accent-sonnet);  /* Blue */
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to {
        transform: translate(-50%, -50%) rotate(360deg);
    }
}
```

**Effect:**
1. Content becomes semi-transparent
2. User can't click elements
3. Spinner appears in center
4. Smooth 0.8s rotation animation

**Color:** Accent blue (#3b82f6 dark, #2563eb light)

### Standalone Spinner

**`.loading-spinner`** - For inline loaders

```css
.loading-spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid var(--border-color);
    border-top-color: var(--accent-sonnet);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}
```

**Usage:**
```html
<div class="loading-spinner"></div>  <!-- Shows inline spinner -->
```

---

## API Endpoints for HTMX Integration

These endpoints are already in the codebase and could be used with HTMX:

### 1. Activity Data (Dynamic)

**Endpoint:** `GET /api/activity`

**Query Parameters:**
- `?start_date=YYYY-MM-DD` - Filter start date
- `?end_date=YYYY-MM-DD` - Filter end date
- `?project=encoded_path` - Filter by project

**Response:** JSON with chart data

**HTMX Use:** Replace chart data dynamically

```html
<canvas id="dailyActivityChart"
    hx-get="/api/activity"
    hx-trigger="filter-change from:body"
    hx-swap="outerHTML">
</canvas>
```

### 2. Model Cost Data

**Endpoint:** `GET /api/model-split`

Same query parameters as /api/activity.

### 3. Daily Cost Data

**Endpoint:** `GET /api/daily-cost`

Same query parameters.

### 4. Hourly Distribution

**Endpoint:** `GET /api/hourly-distribution`

Same query parameters.

### 5. Project Cost

**Endpoint:** `GET /api/project-cost`

Same query parameters.

### 6. Metadata

**Endpoint:** `GET /api/metadata`

**Response:**
```javascript
{
    oldest_date: "2024-01-01",
    newest_date: "2024-12-31",
    projects: [
        {
            encoded_path: "path1",
            display_name: "Project 1",
            session_count: 10
        }
    ]
}
```

**HTMX Use:** Populate filter dropdowns

```html
<select id="project-filter"
    hx-get="/api/metadata"
    hx-trigger="load"
    hx-swap="innerHTML">
</select>
```

---

## Potential HTMX Integration Points

### 1. Filter Updates Without Page Reload

**Current Flow:**
1. User changes filter
2. JavaScript builds query params
3. Fetches chart data from API
4. Updates chart in-place
5. All charts update via Promise.all()

**HTMX Alternative:**
```html
<div id="filters-section" class="filters-section">
    <input type="date" id="start-date"
        hx-get="/api/activity"
        hx-trigger="change delay:300ms"
        hx-target="#dailyActivityChart"
        hx-swap="outerHTML">

    <input type="date" id="end-date"
        hx-get="/api/daily-cost"
        hx-trigger="change delay:300ms"
        hx-target="#dailyCostChart"
        hx-swap="outerHTML">
</div>
```

**Advantage:** Replaces filters.js with declarative HTML

### 2. Project/Session Navigation

**Current Flow:**
```html
<tr class="clickable-row" onclick="window.location.href='/projects/...">
```

**HTMX Alternative:**
```html
<tr hx-get="/projects/{{ id }}" hx-boost="true">
```

**Advantages:**
- No full page reload
- Preserves theme, timezone, filter state
- Smoother user experience

### 3. Settings Form Submission

**Current Flow:**
```html
<form method="post" action="/settings">
    <!-- Standard form submission -->
</form>
```

**HTMX Alternative:**
```html
<form hx-post="/settings"
      hx-target="#settings-form"
      hx-swap="outerHTML">
    <input type="text" name="data_dir" required>
    <button type="submit">Save</button>
</form>
```

**Response Structure:**
```html
<form id="settings-form">
    <!-- Updated form or success message -->
    <div class="success-message">Settings saved!</div>
</form>
```

### 4. Pagination for Long Tables

**Current:** All data loaded at once

**HTMX Alternative:**
```html
<table class="data-table">
    <!-- First 50 rows -->
</table>

<button hx-get="/api/sessions?page=2"
        hx-target="table"
        hx-swap="beforeend">
    Load More
</button>
```

### 5. Search/Filter Results

**Use Case:** Quick session search on session_detail

```html
<input type="text"
       placeholder="Search messages..."
       hx-get="/api/sessions/{{ id }}/search"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#messages-list"
       hx-swap="innerHTML">

<div id="messages-list">
    <!-- Results appear here -->
</div>
```

---

## HTMX Attributes Reference

### Request Attributes

| Attribute | Function |
|-----------|----------|
| `hx-get` | Sends GET request |
| `hx-post` | Sends POST request |
| `hx-put` | Sends PUT request |
| `hx-patch` | Sends PATCH request |
| `hx-delete` | Sends DELETE request |
| `hx-ajax` | Custom AJAX call |

### Target & Swap

| Attribute | Function |
|-----------|----------|
| `hx-target` | Element to receive content |
| `hx-swap` | How to swap: innerHTML, outerHTML, beforebegin, afterbegin, beforeend, afterend, delete, none |
| `hx-swap-oob` | Out-of-band swap (multiple targets from one response) |

### Triggers

| Attribute | Function |
|-----------|----------|
| `hx-trigger` | Event that triggers request |
| Modifiers | `changed`, `delay:Xms`, `throttle:Xms`, `from:selector` |
| Examples | `keyup changed`, `change delay:500ms`, `click from:#parent` |

### Loading & Polling

| Attribute | Function |
|-----------|----------|
| `hx-load` | Load content on page load |
| `hx-poll` | Poll endpoint repeatedly |
| `hx-boost` | Enhance links/forms for AJAX |

### Validation

| Attribute | Function |
|-----------|----------|
| `hx-validate` | Validate form before submit |
| `hx-confirm` | Show confirmation before request |

---

## Event System

### HTMX Events Fired

| Event | When |
|-------|------|
| `htmx:configRequest` | Before request sent |
| `htmx:beforeRequest` | Before request sent |
| `htmx:xhr:loadstart` | Request starts |
| `htmx:xhr:loadend` | Request completes |
| `htmx:xhr:progress` | Upload progress |
| `htmx:responseError` | Response is error |
| `htmx:beforeSwap` | Before DOM swap |
| `htmx:afterSwap` | After DOM swap |
| `htmx:afterSettle` | After animations settle |
| `htmx:trigger` | On trigger event |
| `htmx:load` | Initial load |
| `htmx:abort` | Request aborted |

### Event Listener Pattern

```javascript
document.addEventListener('htmx:afterSettle', (event) => {
    // Re-initialize JavaScript for newly added elements
    initializeNewContent(event.detail.xhr.responseText);
});
```

---

## Roadmap for HTMX Integration

### Phase 1: Minimal (No Breaking Changes)
1. Add loading indicators to existing filter updates
2. Keep current filters.js but enhance with HTMX

### Phase 2: Moderate
1. Replace filter input change handlers with `hx-trigger`
2. Use `hx-boost` on project/session navigation links
3. Add `hx-post` to settings form

### Phase 3: Advanced
1. Implement pagination for long tables
2. Add search/filter capabilities
3. Use OOB swaps for status indicators

### Benefits
- Reduced client-side JavaScript complexity
- Declarative UI behavior
- Built-in loading states
- Progressive enhancement
- Better server-side control

---

## Known Limitations

1. **No Server-Side Integration:**
   - Routers don't return partial HTML
   - All responses are full pages
   - Would need to create `hx-endpoints` that return HTML fragments

2. **Form Handling:**
   - Settings form validation happens on client + server
   - HTMX forms would need server-side validation error HTML responses

3. **Chart Integration:**
   - Chart.js instances not automatically re-initialized
   - Would need `htmx:afterSettle` listener to reinitialize charts

4. **State Management:**
   - Theme and timezone state tied to DOM attributes
   - HTMX swaps could lose state if not careful
   - Need to preserve `<html data-theme>` and `data-time-format`

5. **Error Handling:**
   - No user-facing error UI yet
   - Comment in htmx-config.js: "Could show user-facing error message here"

---

## Code Examples for Future Implementation

### Example 1: HTMX-Based Filter Update

```html
<!-- Current: filters.js with JavaScript -->
<input type="date" id="start-date" class="date-input">

<!-- HTMX Version: Declarative -->
<input type="date"
       name="start_date"
       hx-get="/api/activity"
       hx-trigger="change delay:300ms"
       hx-target="#dailyActivityChart"
       hx-swap="outerHTML">
```

### Example 2: Smart Project Navigation

```html
<!-- Current: onclick JavaScript -->
<tr onclick="window.location.href='/projects/{{ id }}'">

<!-- HTMX Version: Smooth navigation -->
<tr hx-get="/projects/{{ id }}"
    hx-boost="true"
    hx-indicator=".htmx-loading">
```

### Example 3: Settings Form with Validation

```html
<!-- Current: Standard form submission -->
<form method="post" action="/settings">

<!-- HTMX Version: Inline error handling -->
<form hx-post="/settings"
      hx-target="this"
      hx-swap="outerHTML">
    <input type="text" name="data_dir" required
           hx-post="/validate-path"
           hx-trigger="blur"
           hx-indicator=".validation-spinner">
    <button type="submit">Save</button>
</form>
```

### Example 4: Session Search

```html
<input type="text"
       placeholder="Search messages..."
       hx-get="/api/sessions/{{ id }}/messages"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#messages-table tbody"
       hx-swap="innerHTML">

<table class="messages-table" id="messages-table">
    <tbody>
        <!-- Results appear here -->
    </tbody>
</table>
```

---

## Integration Checklist for Future Work

- [ ] Identify critical user flows that would benefit from HTMX
- [ ] Create `hx-` endpoints in routers that return HTML fragments
- [ ] Add `htmx:afterSettle` listeners for Chart.js re-initialization
- [ ] Implement error handling in `htmx:responseError` listener
- [ ] Test state preservation (theme, timezone) across AJAX requests
- [ ] Add `hx-boost` to primary navigation links
- [ ] Replace filter change listeners with HTMX declarative syntax
- [ ] Implement search/pagination for tables using HTMX
- [ ] Add form validation feedback without page reload
- [ ] Document HTMX-specific routes and expected HTML structure

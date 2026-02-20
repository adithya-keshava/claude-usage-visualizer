# localStorage Usage Patterns

**Document:** Claude Usage Visualizer - Client-Side Storage Architecture
**Scope:** localStorage API usage across JavaScript modules
**Last Updated:** 2026-02-20

---

## Overview

The application uses localStorage for three types of persistent data:
1. **User Preferences** - Theme and timezone format
2. **Filter State** - Date ranges and project selection
3. **None:** Session data, authentication tokens, large datasets

**Total Storage Used:** ~500 bytes typical (below 5 MB limit)

**Storage Reliability:** localStorage persists across browser restarts but is per-origin.

---

## localStorage Keys Inventory

### Complete Key Mapping

| Module | Key | Type | Size | Cleanup |
|--------|-----|------|------|---------|
| theme.js | `claude-visualizer-theme` | String | ~10 bytes | Manual toggle |
| timezone.js | `timeFormat` | String | ~12 bytes | Manual select |
| filters.js | `chartFilters` | JSON | ~50-100 bytes | Manual reset or left indefinitely |

**Total:** ~120-150 bytes typical (very small).

---

## Theme Persistence

**File:** `src/app/static/theme.js`

### Storage Key

```javascript
const THEME_KEY = "claude-visualizer-theme";
```

**Key Name:** `claude-visualizer-theme`
**Namespace:** Prefixed to avoid collisions with other apps
**Values:** `"dark"` or `"light"` (strings)

### Writing Theme

**Function:** `applyTheme(theme)` - Lines 20-23

```javascript
function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
}
```

**Trigger Points:**
1. Initial load with system preference
2. User clicks theme toggle button
3. System theme preference changes (if not manually set)

**Every Write:**
- Update DOM attribute immediately
- Save to localStorage synchronously

### Reading Theme

**Function:** `initTheme()` - Lines 11-18

```javascript
function initTheme() {
    let theme = localStorage.getItem(THEME_KEY);  // Read from storage
    if (!theme) {
        theme = getSystemTheme();  // Fallback to system
    }
    applyTheme(theme);
}
```

**Read Priority:**
1. localStorage (user preference)
2. System preference (OS dark mode setting)
3. (Implicit default: light if no system preference detected)

### Storage Workflow

```
First Visit:
    localStorage empty
    → Check system preference
    → system: dark-mode enabled
    → Apply "dark"
    → Save to localStorage
    → Next visit: restore "dark"

User Toggles Theme:
    Current: "dark" (from localStorage)
    User clicks button
    → toggleTheme() flips to "light"
    → applyTheme("light") writes to localStorage
    → Page style updates
    → Next visit: restore "light"

User Changes OS Theme:
    localStorage has value → ignored
    System theme changes
    → listener detects change
    → But localStorage.getItem() returns existing value
    → No update (manual preference takes precedence)

User Clears Browser Data:
    localStorage cleared
    → Next visit: reads empty
    → Falls back to system preference
    → Fresh state (as if first visit)
```

### Serialization

**Format:** Raw string (no JSON)
**Valid Values:** `"dark"` or `"light"` (2 enum values)
**Fallback:** Empty string → treated as no preference

---

## Timezone Format Persistence

**File:** `src/app/static/timezone.js`

### Storage Key

```javascript
localStorage.getItem('timeFormat')  // Used directly (no const defined)
```

**Key Name:** `timeFormat`
**Namespace:** Generic name (could conflict in shared origin)
**Values:** `"UTC"`, `"Local"`, `"UTC-12h"`, `"Local-12h"` (4 enum values)

### Writing Format

**Function:** `changeTimeFormat(newFormat)` - Line 112

```javascript
localStorage.setItem('timeFormat', newFormat);
```

**Trigger Points:**
1. User selects different format from dropdown
2. Programmatic call to changeTimeFormat()

**Write Pattern:**
- Write first (pessimistic)
- Then update DOM and dispatch event
- If write fails, other components already updated (inconsistent state possible)

**Improvement Opportunity:** Save after successfully updating DOM, not before.

### Reading Format

**Function:** `initializeTimeFormat()` - Lines 12-17

```javascript
const savedFormat = localStorage.getItem('timeFormat') || 'UTC';
document.documentElement.setAttribute('data-time-format', savedFormat);
```

**Default:** `'UTC'` if localStorage empty or unset

### Storage Workflow

```
First Visit:
    localStorage empty
    → Default to "UTC"
    → Save "UTC"
    → Set data-time-format="UTC"
    → Convert all timestamps to UTC 24h format

User Selects Local 12h:
    → changeTimeFormat("Local-12h") called
    → Save to localStorage
    → Update DOM attribute
    → Emit timeformatchange event
    → Charts update labels

Next Visit:
    → Read "Local-12h" from localStorage
    → Apply immediately on page load
    → Timestamps shown in Local 12h format
```

### Serialization

**Format:** Raw string (no JSON)
**Valid Values:** Enum of 4 strings
**Fallback:** Defaults to "UTC" if missing or unrecognized

---

## Chart Filters Persistence

**File:** `src/app/static/filters.js`

### Storage Key

```javascript
localStorage.setItem('chartFilters', JSON.stringify({...}));
localStorage.getItem('chartFilters') || '{}'
```

**Key Name:** `chartFilters`
**Serialization:** JSON (object with 3 properties)

### Data Structure

**JSON Schema:**

```json
{
  "start_date": "2026-02-10",
  "end_date": "2026-02-20",
  "project": "home/projects/myproject"
}
```

**Fields:**
- `start_date`: ISO date string (YYYY-MM-DD) or empty
- `end_date`: ISO date string (YYYY-MM-DD) or empty
- `project`: Encoded project path from API or empty

**All fields optional** - Can be partially filled.

### Writing Filters

**Function:** `applyFilters()` - Lines 85-93

```javascript
const startDate = document.getElementById('start-date')?.value;
const endDate = document.getElementById('end-date')?.value;
const project = document.getElementById('project-filter')?.value;

localStorage.setItem(
    'chartFilters',
    JSON.stringify({
        start_date: startDate,
        end_date: endDate,
        project: project,
    })
);
```

**Trigger Points:**
1. Date range input changed
2. Project dropdown changed
3. User applies filters manually

**Write Behavior:**
- Always overwrites entire object
- Includes all 3 fields (some may be empty strings)
- JSON stringified (safe for storage)

### Reading Filters

**Function:** `initFilters()` - Lines 36-41

```javascript
const savedFilters = JSON.parse(
    localStorage.getItem('chartFilters') || '{}'
);
if (savedFilters.start_date) startInput.value = savedFilters.start_date;
if (savedFilters.end_date) endInput.value = savedFilters.end_date;
```

**Process:**
1. Get value from localStorage (default to empty object)
2. Parse JSON
3. Extract individual fields
4. Apply to form inputs only if truthy

**Defensive:** Uses optional chaining and truthy checks.

### Storage Workflow

```
First Visit:
    localStorage empty
    → initFilters() reads empty object
    → Date inputs: no min/max constraint
    → Project dropdown: populated from API
    → Form shows defaults (empty fields)

User Sets Dates & Project:
    → Changes start-date input
    → applyFilters() called (debounced 300ms)
    → Fetch metadata and update charts
    → Save all 3 fields to localStorage
    → Charts update with filtered data

Next Visit:
    → initFilters() reads saved values
    → Populate form inputs with saved values
    → Apply saved filters on page load
    → Charts show filtered data immediately

User Clears Filters:
    → resetFilters() called
    → Clear all inputs
    → localStorage.removeItem('chartFilters')
    → window.location.reload()
    → Page reloads with defaults
```

### JSON Serialization Edge Cases

**Truthy/Falsy Checks:**

```javascript
if (savedFilters.start_date) startInput.value = savedFilters.start_date;
```

**Behavior:**
- `start_date: ""` (empty string) → falsy → skipped
- `start_date: "2026-02-10"` → truthy → applied
- `start_date: undefined` → falsy → skipped

**Implication:** Empty date inputs treated as "no filter" (correct behavior).

### Size Constraints

**Typical Size:**
- Empty: 2 bytes (`{}`)
- Typical: 60 bytes (`{"start_date":"2026-02-10","end_date":"2026-02-20","project":"home/projects/test"}`)
- Maximum: ~100 bytes (very long project name)

**Well Below Limit:** localStorage has ~5 MB limit per origin.

---

## Data Consistency & Synchronization

### Single-Tab Consistency

**Normal Scenario:** User has one browser tab open.

**Consistency:** Always consistent.
- Read at page load
- Write on user action
- Read from same tab

### Multi-Tab Scenario

**Scenario:** User opens same site in 2 tabs.

**Race Condition:**
```
Tab 1: User changes theme to "dark"
  → localStorage.setItem('theme', 'dark')
  → DOM updated

Tab 2: Still showing "light" theme
  → No storage event listener to detect change
  → Must reload to see new theme
```

**Current Implementation:** No storage event listeners (no cross-tab sync).

**Limitations:**
- Theme not synced across tabs
- Timezone format not synced across tabs
- Filter state not synced across tabs

**Improvement Opportunity:**
```javascript
window.addEventListener('storage', (event) => {
    if (event.key === 'claude-visualizer-theme') {
        applyTheme(event.newValue);  // Update this tab
    }
});
```

### Private/Incognito Mode

**Behavior:** localStorage still works but is cleared when browser session ends.

**No Special Handling:** Application doesn't detect or warn about private mode.

---

## localStorage API Usage Patterns

### Pattern 1: Simple Key-Value (Theme)

```javascript
const key = "claude-visualizer-theme";
const value = "dark";

// Write
localStorage.setItem(key, value);

// Read
const stored = localStorage.getItem(key);

// Check existence
if (stored) { ... }

// Delete
localStorage.removeItem(key);
```

**Use Case:** Simple enums or strings.
**Type Safety:** None (all values are strings).

### Pattern 2: JSON Serialization (Filters)

```javascript
const key = "chartFilters";
const value = { start_date: "2026-02-10", end_date: "2026-02-20", project: "" };

// Write
localStorage.setItem(key, JSON.stringify(value));

// Read
const stored = JSON.parse(localStorage.getItem(key) || '{}');

// Update partial field
stored.start_date = "2026-02-15";
localStorage.setItem(key, JSON.stringify(stored));
```

**Use Case:** Complex objects.
**Type Safety:** None (JSON.parse returns `any` type).
**Parsing:** Always wrap in try/catch for production.

### Pattern 3: Fallback Chain (Theme)

```javascript
// Priority 1: User preference in localStorage
let value = localStorage.getItem(key);

// Priority 2: System preference
if (!value) {
    value = getSystemPreference();
}

// Priority 3: Hard default
if (!value) {
    value = "light";
}
```

**Use Case:** Graceful degradation with defaults.

### Pattern 4: Null Coalescing (Timezone)

```javascript
const savedFormat = localStorage.getItem('timeFormat') || 'UTC';
```

**Pattern:** `getItem() || default`
**Works When:** Default is falsy (empty string, null, undefined).
**Caveat:** Can't distinguish between "not set" and "set to empty string".

---

## Data Validation & Error Handling

### Theme Validation

**Current:** No validation.

```javascript
// Potential vulnerability: accepts any string
localStorage.setItem('theme', userInput);  // Could be "dark", "blue", "purple", etc.

// Should validate:
const validThemes = ['dark', 'light'];
if (validThemes.includes(newTheme)) {
    localStorage.setItem(THEME_KEY, newTheme);
}
```

### Filters Validation

**Current:** No validation at write.

```javascript
// Potential issues:
// - Invalid date format
// - Non-existent project
// - Very long strings
localStorage.setItem('chartFilters', JSON.stringify(userData));

// Should validate:
const filters = {
    start_date: isValidDate(startDate) ? startDate : '',
    end_date: isValidDate(endDate) ? endDate : '',
    project: projectExists(project) ? project : '',
};
localStorage.setItem('chartFilters', JSON.stringify(filters));
```

### JSON Parse Errors

**Current:** No error handling.

```javascript
// Could throw if corrupted:
const filters = JSON.parse(localStorage.getItem('chartFilters'));

// Should wrap:
let filters = {};
try {
    const stored = localStorage.getItem('chartFilters');
    if (stored) {
        filters = JSON.parse(stored);
    }
} catch (e) {
    console.error('Failed to parse filters:', e);
    localStorage.removeItem('chartFilters');  // Clear corrupted data
}
```

---

## localStorage Lifecycle

### Creation

**When:** First time user visits (browser detects localStorage available).

**Initial State:**
- `claude-visualizer-theme`: Not set (created on first theme apply)
- `timeFormat`: Not set (created on first page load)
- `chartFilters`: Not set (created when filters applied)

### Reading

**When:** Every page load.

**Cost:** ~1-3 milliseconds per read (very fast).

### Writing

**When:** User changes settings or filters.

**Cost:** ~1-3 milliseconds per write (synchronous).

### Expiration

**Policy:** No automatic expiration.

**Lifespan:**
- `theme`: Until user clears browsing data or manually resets
- `timeFormat`: Until user clears browsing data or manually resets
- `chartFilters`: Until user clears browsing data, resets filters, or manually deletes

### Clearing

**Manual:** User clears browser data (Settings → Clear browsing data → Cookies and other site data).

**Programmatic:**
```javascript
localStorage.removeItem('chartFilters');  // Remove one key
localStorage.clear();  // Remove all
```

**Current Usage:** Only chartFilters has programmatic clear (resetFilters function).

---

## Security Considerations

### XSS Attacks

**Risk:** If user input is stored and later rendered unsanitized.

**Current Code:** Stores values from form inputs:
```javascript
const startDate = document.getElementById('start-date').value;
localStorage.setItem('chartFilters', JSON.stringify({start_date}));
```

**Protection:** Form inputs from `<input type="date">` are automatically validated by browser.

**Risk Level:** Low (input type="date" restricts to YYYY-MM-DD format).

### CSRF / XSRF

**Risk:** If localStorage is read and used to generate requests.

**Current Code:** Stored values used as API query parameters:
```javascript
const params = new URLSearchParams();
if (startDate) params.set('start_date', startDate);
```

**Protection:** Query parameters are URL-encoded automatically.

**Risk Level:** Low (standard URL encoding).

### Quota & Denial of Service

**Risk:** Malicious code filling localStorage to cause DoS.

**Current Code:** No quota validation.

**Current Usage:** ~150 bytes typical (0.003% of 5 MB limit).

**Risk Level:** Low (application doesn't store large data).

---

## Testing localStorage

### Manual Testing

**Check Stored Values:**
```javascript
// In browser console
console.log(localStorage.getItem('claude-visualizer-theme'));
console.log(localStorage.getItem('timeFormat'));
console.log(JSON.parse(localStorage.getItem('chartFilters')));
```

**Clear Specific Key:**
```javascript
localStorage.removeItem('chartFilters');
```

**Clear All:**
```javascript
localStorage.clear();
```

### Browser DevTools

**Application Tab:**
1. DevTools → Application tab
2. Left sidebar → Storage → Local Storage
3. Select origin → View all keys

**DevTools Console:**
1. DevTools → Console tab
2. Type commands directly
3. Inspect keys and values

### Programmatic Tests

```javascript
// Check default behavior
const theme = localStorage.getItem('claude-visualizer-theme');
console.assert(!theme, 'Theme not set on first visit');

// Simulate user action
localStorage.setItem('claude-visualizer-theme', 'dark');
console.assert(localStorage.getItem('claude-visualizer-theme') === 'dark', 'Theme saved');

// Simulate clear
localStorage.removeItem('claude-visualizer-theme');
console.assert(!localStorage.getItem('claude-visualizer-theme'), 'Theme cleared');
```

---

## Storage Comparison

| Approach | Use Case | Limits | Persistence | Current Usage |
|----------|----------|--------|-------------|---------------|
| localStorage | Client-side preferences, filters | 5 MB per origin | Until manual clear or browser reset | Yes (3 keys) |
| sessionStorage | Temporary session state | 5 MB per origin | Until tab closed | No |
| IndexedDB | Large structured data | 50+ MB per origin | Until manual clear | No |
| Cookies | Server-side sessions, auth | 4 KB per cookie | Configurable expiry | No |
| Memory | Runtime state | RAM | Until page reload | Yes (theme colors, chart instances) |

**Current Choice:** localStorage for user preferences is appropriate (persistent, small data).

---

## Related Modules

- **theme.js** - Uses `claude-visualizer-theme` key
- **timezone.js** - Uses `timeFormat` key
- **filters.js** - Uses `chartFilters` key

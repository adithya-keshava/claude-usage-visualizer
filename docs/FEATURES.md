# Features Documentation

## Token Breakdown (Overview Page)

### Overview

The Overview page displays comprehensive token usage across all models and sessions.

### Visual Components

#### Token Breakdown Section
4 stat cards showing totals:
- **Input Tokens** - Regular input to Claude
- **Output Tokens** - Claude's responses
- **Cache Write Tokens** - Writing to prompt cache
- **Cache Read Tokens** - Reading from prompt cache

#### Per-Model Breakdown Table
7-column table showing per-model statistics:
1. Model - Model name (e.g., claude-opus-4-6)
2. Input Tokens - Input tokens used by model
3. Output Tokens - Output tokens generated
4. Cache Write - Tokens written to cache
5. Cache Read - Tokens read from cache
6. Total Tokens - Sum of all 4 types
7. Estimated Cost - Dollar cost in USD

#### Daily Activity Table
Shows daily usage:
- Date (with timezone toggle support)
- Message count
- Session count
- Tool call count

### Cost Calculation

**Formula:**
```
Cost USD = (input_tokens × 0.003 +
            output_tokens × 0.015 +
            cache_write_tokens × 0.00375 +
            cache_read_tokens × 0.0003) / 1,000,000
```

**Pricing Varies by Model:**
Different models have different rates. See `src/app/data/pricing.py` for current pricing.

### Data Flow

```
stats-cache.json
    ↓
Parse JSON
    ↓
Extract messages by session
    ↓
Aggregate by model
    ↓
Calculate totals
    ↓
Render template with data
```

### UI Locations

- **Top Section** - Stat cards (Total Cost, Total Tokens, Total Sessions, Total Messages)
- **Token Breakdown Section** - 4 breakdown cards
- **Per-Model Table** - Detailed model breakdown
- **Daily Activity Table** - Activity by date

---

## Timezone Toggle Feature

### Purpose

Allow users to view timestamps in their preferred timezone (UTC or local) and time format (24-hour or 12-hour AM/PM).

### Features

✅ **4 Cycling Modes**
```
UTC 24h → Local 24h → UTC 12h → Local 12h → (repeats)
```

✅ **Consistent Formatting**
- All modes use: `YYYY-MM-DD HH:MM:SS [AM/PM]`
- Only time values change, format stays same

✅ **Intelligent Cycling**
- One click advances to next mode
- Tooltip explains current mode and next action

✅ **Persistent Preference**
- Saved to localStorage
- Remembered across page reloads
- Applied across all pages

✅ **No Dependencies**
- Pure JavaScript
- No external libraries
- Works without build step

### Button Location

**Header** - Top-right corner, next to theme toggle button

### Visual Feedback

**Button Label:**
- "UTC" - UTC 24-hour mode
- "Local" - Local 24-hour mode
- "UTC 12h" - UTC with AM/PM
- "Local 12h" - Local with AM/PM

**Tooltip (Hover):**
```
UTC: "UTC 24h format. Click to switch to Local time."
Local: "Local time 24h format. Click to switch to UTC 12h format."
UTC 12h: "UTC 12h format with AM/PM. Click to switch to Local 12h format."
Local 12h: "Local time 12h format with AM/PM. Click to switch to UTC 24h format."
```

### Time Conversions

#### UTC vs Local
```
UTC Mode:   Uses getUTCHours(), getUTCMinutes(), getUTCSeconds()
Local Mode: Uses getHours(), getMinutes(), getSeconds()
```

Example (UTC+5:30 timezone):
```
2026-02-15 14:30:45 UTC  →  2026-02-15 19:45:45 Local
```

#### 24-Hour vs 12-Hour
```
24h Mode: HH:MM:SS (00:00 - 23:59)
12h Mode: HH:MM:SS AM/PM (12:00 AM - 11:59 PM)
```

**Conversion Logic:**
```javascript
const ampm = hours >= 12 ? 'PM' : 'AM';
const hours12 = hours % 12 || 12;
```

**Edge Cases:**
| 24h Time | 12h Time | Logic |
|----------|----------|-------|
| 00:00 | 12:00 AM | Midnight: 0 % 12 \|\| 12 = 12 |
| 01:00 | 01:00 AM | `1 % 12 \|\| 12` = 1 |
| 11:00 | 11:00 AM | `11 % 12 \|\| 12` = 11 |
| 12:00 | 12:00 PM | Noon: `12 % 12 \|\| 12` = 12 |
| 13:00 | 01:00 PM | `13 % 12 \|\| 12` = 1 |
| 23:00 | 11:00 PM | `23 % 12 \|\| 12` = 11 |

### Pages with Timestamp Support

1. **Overview Page**
   - Daily Activity table (dates)

2. **Project Detail Page**
   - Session list (session dates)

3. **Session Detail Page**
   - Message list (message timestamps)

### Implementation Details

#### Data Attributes
```html
<span data-timestamp="2026-02-15T14:30:45Z">
  2026-02-15 14:30:45
</span>
```

- `data-timestamp` - ISO 8601 timestamp (never changes)
- Text content - Updated when mode changes

#### JavaScript Processing
```
1. Read data-timestamp attribute
2. Parse into Date object
3. Extract timezone (UTC or Local)
4. Extract format (24h or 12h)
5. Get date/time components
6. Format as YYYY-MM-DD HH:MM:SS [AM/PM]
7. Update element text
```

#### localStorage Persistence
- **Key:** `'timeFormat'`
- **Values:** `'UTC'`, `'Local'`, `'UTC-12h'`, `'Local-12h'`
- **Scope:** Cross-page, cross-session
- **Fallback:** Defaults to 'UTC' if not found

### Example Outputs

#### Same Moment, Different Formats

**Original (UTC):** `2026-02-15T14:30:45Z`

| Mode | Display |
|------|---------|
| UTC 24h | 2026-02-15 14:30:45 |
| Local 24h | 2026-02-15 19:45:45 |
| UTC 12h | 2026-02-15 02:30:45 PM |
| Local 12h | 2026-02-15 07:45:45 PM |

(Assuming UTC+5:30 timezone)

---

## Theme Toggle (Existing Feature)

While not part of Phase 3, the timezone toggle follows the same pattern as the existing theme toggle.

**Both provide:**
- Client-side preference management
- localStorage persistence
- Immediate UI updates
- Multiple modes cycling
- Helpful tooltips

---

## Data Sources

### Claude Stats Cache
Location: `~/.config/Claude/stats-cache.json`

Contains:
- Session data with timestamps
- Message usage by model
- Token counts (input, output, cache read, cache write)
- Timestamps in ISO 8601 format

### Pricing Data
File: `src/app/data/pricing.py`

Contains:
- Per-model token rates
- Input, output, cache write, cache read rates
- Cost calculation formulas

---

## Browser Support

### Required Features
- `localStorage` - ES5 (IE8+)
- `document.querySelectorAll()` - All modern browsers
- `String.padStart()` - ES2017 (all modern browsers)
- `Date.getUTCHours()` / `Date.getHours()` - All browsers

### Tested On
- Chrome 120+
- Firefox 121+
- Safari 17+
- Edge 120+

### Fallback Behavior
If JavaScript disabled:
- Token breakdown still displays (server-rendered)
- Timestamps show server-rendered fallback (no timezone conversion)
- Theme toggle unavailable
- Timezone toggle unavailable

---

## Performance

### Token Breakdown
- Zero runtime cost
- Pure server-side aggregation
- No client-side calculation

### Timezone Toggle
- Single DOM traversal per click
- No network requests
- <50ms per conversion (10+ timestamps)
- Minimal memory usage

---

## Accessibility

### Timezone Toggle
- `aria-label="Toggle timezone"` - Screen reader support
- Keyboard accessible - Standard button behavior
- Helpful tooltips - Explain each mode
- Clear visual feedback - Button label changes

### Color Contrast
- All text meets WCAG AA standards
- Dark/light theme support
- Color not sole indicator of state

---

## Future Enhancement Ideas

Not implemented, but possible:
- 📅 Date range picker
- 📊 Cost trend chart
- 🔍 Advanced filtering
- 📥 Export to CSV
- 📱 Mobile app
- 🔔 Cost alerts

---

**For testing instructions, see TESTING.md**
**For implementation details, see GUIDE.md**

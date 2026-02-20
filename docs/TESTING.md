# Testing & Validation Guide

## Quick Start

### 1. Start Server
```bash
cd <project-root>
uv run --python 3.11 src/main.py
```

### 2. Open Application
Navigate to: `http://localhost:8000/`

---

## Testing Sections

- [Overview Page](#overview-page)
- [Timezone Toggle](#timezone-toggle)
- [Navigation](#navigation)
- [Cross-Page Testing](#cross-page-testing)
- [Validation Checklist](#validation-checklist)

---

## Overview Page

### Token Breakdown Section

**Expected:** 4 stat cards showing token totals

1. Navigate to Overview page
2. Scroll to "Token Breakdown" section
3. Verify 4 cards display:
   - Input Tokens (count)
   - Output Tokens (count)
   - Cache Write Tokens (count)
   - Cache Read Tokens (count)

**Status:** ✅ Pass / ❌ Fail

### Per-Model Breakdown Table

**Expected:** Model table has 7 columns with cache tokens

1. On Overview page, scroll to "Per-Model Token & Cost Breakdown"
2. Verify columns (left to right):
   1. Model (name)
   2. Input Tokens
   3. Output Tokens
   4. Cache Write
   5. Cache Read
   6. Total Tokens (sum of all 4)
   7. Estimated Cost

3. Verify totals row shows correct sums

**Status:** ✅ Pass / ❌ Fail

### Total Tokens Card

**Expected:** Top stat card includes all 4 token types

1. On Overview page, top section shows stat cards
2. "Total Tokens" card should equal:
   - Input + Output + Cache Write + Cache Read
3. Not just Input + Output

**Status:** ✅ Pass / ❌ Fail

---

## Timezone Toggle

### Button Visibility

**Expected:** Button visible in header

1. Look top-right of header
2. Button should be next to theme toggle
3. Shows "UTC" initially

**Status:** ✅ Pass / ❌ Fail

### Mode Cycling

**Expected:** Clicking cycles through 4 modes

1. Initial state: "UTC"
2. Click 1: "Local"
3. Click 2: "UTC 12h"
4. Click 3: "Local 12h"
5. Click 4: "UTC" (cycles back)

**Status:** ✅ Pass / ❌ Fail

### Timestamp Conversion

**Expected:** Timestamps change with timezone

1. Note a timestamp in UTC mode (e.g., `14:30:45`)
2. Click to Local mode
3. Time should change (e.g., `19:45:45` if UTC+5:30)
4. Click to UTC 12h: should show `02:30:45 PM`
5. Click to Local 12h: should show time in local TZ with AM/PM

**Status:** ✅ Pass / ❌ Fail

### Format Consistency

**Expected:** Date format stays YYYY-MM-DD

1. Cycle through all 4 modes
2. Date should always be: `YYYY-MM-DD`
3. Never switch to MM/DD/YYYY or other formats
4. Only time part changes (hh:mm:ss vs hh:mm:ss AM/PM)

**Status:** ✅ Pass / ❌ Fail

### 12-Hour Edge Cases

**Expected:** Proper AM/PM conversion

1. Set to UTC 12h mode
2. Find timestamps and verify:
   - 00:xx:xx → 12:xx:xx AM (midnight)
   - 12:xx:xx → 12:xx:xx PM (noon)
   - 13:xx:xx → 01:xx:xx PM
   - 23:xx:xx → 11:xx:xx PM

**Status:** ✅ Pass / ❌ Fail

### Tooltips

**Expected:** Hovering shows helpful tooltip

1. Hover over button in each mode:
   - UTC: "UTC 24h format. Click to switch to Local time."
   - Local: "Local time 24h format. Click to switch to UTC 12h format."
   - UTC 12h: "UTC 12h format with AM/PM. Click to switch to Local 12h format."
   - Local 12h: "Local time 12h format with AM/PM. Click to switch to UTC 24h format."

**Status:** ✅ Pass / ❌ Fail

---

## Navigation

### Projects Page

**Expected:** Timezone button visible, timestamps update

1. Navigate to `/projects`
2. Verify timezone button visible
3. Click timezone button
4. "Date" column timestamps should update

**Status:** ✅ Pass / ❌ Fail

### Session Detail Page

**Expected:** Timezone button visible, message timestamps update

1. On Projects page, click a project
2. Click a session
3. Verify timezone button visible
4. Check "Timestamp" column in messages table
5. Click timezone button
6. Timestamps should update

**Status:** ✅ Pass / ❌ Fail

---

## Cross-Page Testing

### Preference Persistence

**Expected:** Setting remembered across page reloads

1. On Overview page, click timezone button until "Local 12h"
2. **Refresh page** (Cmd+R or F5)
3. Button should still show "Local 12h"
4. Timestamps should still be Local 12h

**Status:** ✅ Pass / ❌ Fail

### Cross-Page Consistency

**Expected:** Setting applies across all pages

1. On Overview, set to "UTC 12h"
2. Navigate to Projects page
3. Button should show "UTC 12h"
4. Navigate to a session
5. Button should still show "UTC 12h"
6. Navigate back to Overview
7. Button should still show "UTC 12h"

**Status:** ✅ Pass / ❌ Fail

### Persistence After Browser Close

**Expected:** Setting survives closing and reopening browser

1. Set timezone to "Local" mode
2. Close browser completely
3. Reopen and navigate to app
4. Button should show "Local"

**Status:** ✅ Pass / ❌ Fail

---

## Error Handling

### Invalid Timestamps

**Expected:** No errors if timestamp invalid

1. Open browser DevTools (F12)
2. Go to Console tab
3. Click timezone button multiple times
4. Navigate between pages
5. Should see no red error messages

**Status:** ✅ Pass / ❌ Fail

### localStorage Disabled

**Expected:** App works even if localStorage disabled

1. Open browser DevTools
2. Go to Application/Storage tab
3. Disable localStorage
4. Refresh page
5. Timezone button should still work
6. Will default to 'UTC' each refresh

**Status:** ✅ Pass / ❌ Fail

---

## Validation Checklist

### Token Breakdown
- [ ] Token Breakdown section visible
- [ ] 4 cards show correct counts
- [ ] Totals row shows correct sums
- [ ] Total Tokens includes all 4 types
- [ ] Model costs calculated correctly

### Timezone Toggle - General
- [ ] Button visible in header
- [ ] Button shows correct initial mode
- [ ] Button clickable
- [ ] Label changes with each click

### Timezone Toggle - Modes
- [ ] Mode 1: UTC (24h format, no AM/PM)
- [ ] Mode 2: Local (24h format, no AM/PM)
- [ ] Mode 3: UTC 12h (has AM/PM)
- [ ] Mode 4: Local 12h (has AM/PM)
- [ ] Cycles back after 4th click

### Timezone Toggle - Conversions
- [ ] UTC time correct
- [ ] Local time correct
- [ ] AM/PM conversions correct
- [ ] Midnight (00:00 → 12:00 AM)
- [ ] Noon (12:00 → 12:00 PM)
- [ ] Format stays YYYY-MM-DD

### Persistence & Sync
- [ ] Preference saved to localStorage
- [ ] Survives page reload
- [ ] Works across pages
- [ ] All pages show same mode
- [ ] Tooltips accurate

### Pages & Features
- [ ] Overview page displays tokens
- [ ] Projects page shows dates
- [ ] Session page shows timestamps
- [ ] All pages have timezone button
- [ ] All pages update on button click

### Quality
- [ ] No console errors
- [ ] No broken styling
- [ ] Works without JavaScript (fallback)
- [ ] Accessible (aria-labels)
- [ ] Responsive (mobile friendly)

---

## Troubleshooting

**Q: Button not appearing?**
A: Check base.html has button element. Check browser console for errors. Clear cache.

**Q: Timestamps not updating?**
A: Verify templates have `data-timestamp` attributes. Check timezone.js loads. Check console for errors.

**Q: Time seems wrong?**
A: Remember local time differs from UTC by timezone offset. Both show same instant.

**Q: Setting not persisting?**
A: localStorage may be disabled. Try disabling privacy/incognito mode. Clear browser data.

**Q: Seeing errors in console?**
A: Check that data-timestamp values are valid ISO 8601 dates. Check timezone.js syntax.

---

## Browser Testing Matrix

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browser

---

## Performance Check

**Expected:** No noticeable slowdown

1. Open DevTools (F12)
2. Go to Performance tab
3. Record for 5 seconds while clicking timezone button
4. Performance should show <50ms for each conversion

**Status:** ✅ Pass / ❌ Fail

---

## Final Validation

**All tests passing?**

✅ Ready for production deployment

**Some tests failing?**

❌ Review failures, check GUIDE.md for implementation details, check console for errors

---

**For detailed implementation information, see GUIDE.md**

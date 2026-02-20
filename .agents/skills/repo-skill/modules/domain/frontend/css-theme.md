# Frontend: CSS Structure and Theme System

## Overview

Single CSS file implements complete styling with CSS custom properties (variables) for light/dark theme support, responsive design, and component styling.

**File:** `src/app/static/style.css` (855 lines)

---

## CSS Custom Properties (Variables)

### Theme-Specific Variables

**Dark Theme Selector:** `html[data-theme="dark"]` (lines 2-17)

```css
--bg-primary: #0d1117          /* Page background */
--bg-secondary: #161b22        /* Cards, sections background */
--border-color: #30363d        /* Borders, dividers */
--text-primary: #e6edf3        /* Main text */
--text-secondary: #8b949e      /* Secondary text, labels */

/* Model-specific accent colors */
--accent-opus: #a855f7         /* Purple - Opus models */
--accent-sonnet: #3b82f6       /* Blue - Sonnet models */
--accent-haiku: #10b981        /* Green - Haiku models */
--accent-color: #3b82f6        /* Default accent (Sonnet blue) */

/* Functional colors */
--card-bg: #161b22
--hover-bg: #0d1117
--link-color: #3b82f6
--error-color: #ef4444
--error-bg: rgba(239, 68, 68, 0.1)
```

**Light Theme Selector:** `html[data-theme="light"]` (lines 19-34)

```css
--bg-primary: #ffffff
--bg-secondary: #f6f8fa
--border-color: #d1d5db
--text-primary: #1f2937
--text-secondary: #6b7280

--accent-opus: #9333ea
--accent-sonnet: #2563eb
--accent-haiku: #059669
--accent-color: #2563eb

--card-bg: #f6f8fa
--hover-bg: #e5e7eb
--link-color: #2563eb
--error-color: #dc2626
--error-bg: rgba(220, 38, 38, 0.1)
```

**Switching Mechanism:**
- Controlled by `data-theme` attribute on `<html>` element
- Set by `theme.js` via: `document.documentElement.setAttribute("data-theme", theme)`
- No media queries needed for theme (explicit user choice takes precedence)

### Variable Usage Pattern

All color references use `var(--property-name)`:
```css
body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
}
```

Enables instant theme switching without JavaScript recalculation.

---

## Global Styles (lines 36-62)

### Reset
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
```

### Smooth Scrolling
```css
html { scroll-behavior: smooth; }
```

### Body
```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
    transition: background-color 0.3s, color 0.3s;  /* Smooth theme transitions */
}
```

### Links
```css
a {
    color: var(--accent-sonnet);
    text-decoration: none;
}

a:hover { opacity: 0.8; }
```

---

## Layout Components

### Header (lines 64-175)

**Container:** `.header`
```css
background-color: var(--bg-secondary);
border-bottom: 1px solid var(--border-color);
padding: 1rem 0;
position: sticky;
top: 0;
z-index: 100;
```

Sticky positioned, overlays content on scroll.

**Content Wrapper:** `.header-content`
- Max-width: 1200px
- Margin: 0 auto (centered)
- Padding: 0 2rem (horizontal spacing)
- Display: flex
- Justify-content: space-between (title on left, actions on right)

**Title:** `.header-title`
- Font-size: 1.5rem
- Font-weight: 700
- Letter-spacing: -0.02em (tighter spacing)
- Flex: 1 (takes available space)

**Navigation:** `.header-nav`
- Display: flex
- Gap: 1.5rem
- Margin: 0 2rem (between title and actions)

**Nav Links:** `.nav-link`
- Color: primary text
- Font-size: 0.95rem
- Padding: 0.5rem 0
- Border-bottom: 2px transparent (underline animation)
- Transition: border-color 0.2s
- Hover: border-bottom-color becomes accent

**Actions Container:** `.header-actions`
- Display: flex
- Gap: 0.5rem

**Icon Buttons:** `.icon-btn`
- Background: none (transparent)
- Border: none
- Color: secondary text
- Cursor: pointer
- Padding: 0.5rem
- Display: flex (centering)
- Border-radius: 4px
- Transition: color 0.2s
- Hover: color becomes primary, background becomes primary background

### Timezone Dropdown (lines 131-157)

**Container:** `.timezone-selector`
- Display: flex
- Align-items: center

**Dropdown:** `.timezone-dropdown`
```css
padding: 0.5rem 0.75rem;
background-color: var(--bg-primary);
color: var(--text-primary);
border: 1px solid var(--border-color);
border-radius: 4px;
font-size: 0.9rem;
font-weight: 500;
cursor: pointer;
transition: border-color 0.2s, background-color 0.2s;
```

- Hover: border-color → accent, background → secondary
- Focus: outline none, border → accent, box-shadow: rgba(accent, 0.1)

### Main Content (lines 177-188)

**Container:** `.main-content`
- Max-width: 1200px
- Margin: 0 auto
- Padding: 2rem
- Min-height: calc(100vh - 120px) (fills viewport)

**Content Wrapper:** `.container`
- Display: flex
- Flex-direction: column
- Gap: 2rem

---

## Component Styles

### Stat Cards (lines 191-224)

**Stats Grid:** `.stats-grid`
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
gap: 1.5rem;
```

Responsive grid: 1-4 columns depending on screen width.

**Card:** `.stat-card`
```css
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 1.5rem;
transition: all 0.3s;
```

Hover state:
```css
.stat-card:hover {
    border-color: var(--accent-sonnet);
    box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
}
```

**Label:** `.stat-label`
```css
font-size: 0.875rem;
color: var(--text-secondary);
font-weight: 500;
text-transform: uppercase;
letter-spacing: 0.05em;
margin-bottom: 0.75rem;
```

**Value:** `.stat-value`
```css
font-size: 2rem;
font-weight: 700;
font-family: "Monaco", "Courier New", monospace;  /* Monospace for numbers */
color: var(--text-primary);
```

### Sections (lines 227-237)

**Section:** `.section`
```css
display: flex;
flex-direction: column;
gap: 1.5rem;
```

**Heading:** `.section h2`
```css
font-size: 1.25rem;
font-weight: 600;
color: var(--text-primary);
```

### Tables (lines 240-300)

**Table Classes:** `.table` and `.data-table`
```css
width: 100%;
border-collapse: collapse;
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
overflow: hidden;
```

**Header:** `thead`
```css
background-color: var(--border-color);
border-bottom: 1px solid var(--border-color);
```

**Table Header Cell:** `th`
```css
padding: 1rem;
text-align: left;
font-size: 0.875rem;
font-weight: 600;
text-transform: uppercase;
letter-spacing: 0.05em;
color: var(--text-secondary);
```

**Table Cell:** `td`
```css
padding: 1rem;
font-size: 0.9rem;
color: var(--text-primary);
```

**Body Row:** `tbody tr`
```css
border-bottom: 1px solid var(--border-color);
transition: background-color 0.2s;
```

Row hover:
```css
tbody tr:hover {
    background-color: var(--hover-bg);
}
```

**Clickable Row:** `.clickable-row`
```css
cursor: pointer;
transition: background-color 0.2s;
```

Hover background inherited from tbody tr:hover.

**Footer:** `tfoot tr`
```css
border-top: 2px solid var(--border-color);
```

**Summary/Totals Row:** `.summary-row`, `.totals-row`
```css
font-weight: 600;
background-color: var(--hover-bg);
```

### Forms (lines 303-370)

**Form Container:** `.settings-form`
```css
display: flex;
flex-direction: column;
gap: 1.5rem;
max-width: 600px;
```

**Form Group:** `.form-group`
```css
display: flex;
flex-direction: column;
gap: 0.5rem;
```

**Label:** `.form-group label`
```css
font-weight: 600;
color: var(--text-primary);
font-size: 0.95rem;
```

**Input Group:** `.input-group`
```css
position: relative;
display: flex;
align-items: center;
```

**Input:** `.input-group input`
```css
flex: 1;
padding: 0.75rem;
border: 1px solid var(--border-color);
border-radius: 6px;
background-color: var(--bg-secondary);
color: var(--text-primary);
font-size: 0.95rem;
transition: border-color 0.2s;
```

Focus:
```css
.input-group input:focus {
    outline: none;
    border-color: var(--accent-sonnet);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
```

**Validation Icon:** `.validation-icon`
```css
position: absolute;
right: 1rem;
font-weight: 700;
font-size: 1.2rem;
```

- `.validation-icon.valid` - Color: haiku green (#10b981)
- `.validation-icon.invalid` - Color: red (#ef4444)

**Help Text:** `.form-help`
```css
font-size: 0.85rem;
color: var(--text-secondary);
margin-top: 0.25rem;
```

**Form Actions:** `.form-actions`
```css
display: flex;
gap: 1rem;
padding-top: 0.5rem;
```

### Buttons (lines 373-403)

**Base Button:** `.btn`
```css
padding: 0.75rem 1.5rem;
border: none;
border-radius: 6px;
font-size: 0.95rem;
font-weight: 600;
cursor: pointer;
transition: all 0.2s;
text-decoration: none;
display: inline-block;
```

**Primary Button:** `.btn-primary`
```css
background-color: var(--accent-sonnet);
color: white;
```

Hover:
```css
opacity: 0.9;
transform: translateY(-1px);  /* Lift effect */
```

**Secondary Button:** `.btn-secondary`
```css
background-color: var(--bg-secondary);
color: var(--text-primary);
border: 1px solid var(--border-color);
```

Hover:
```css
background-color: var(--border-color);
```

**Load More Button:** `.btn-load-more`
```css
padding: 0.75rem 1.5rem;
background-color: var(--accent-sonnet);
color: white;
border: none;
border-radius: 6px;
font-size: 0.95rem;
font-weight: 600;
cursor: pointer;
transition: all 0.2s;
```

Hover: opacity 0.9, transform translateY(-1px)
Disabled: opacity 0.5, cursor not-allowed

### Token Breakdown Cards (lines 469-497)

**Grid:** `.token-breakdown-grid`
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 1.5rem;
```

**Card:** `.breakdown-card`
```css
background-color: var(--card-bg);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 1.5rem;
text-align: center;
```

**Label:** `.breakdown-label`
```css
font-size: 0.9rem;
color: var(--text-secondary);
margin-bottom: 0.75rem;
text-transform: uppercase;
letter-spacing: 0.05em;
font-weight: 500;
```

**Value:** `.breakdown-value`
```css
font-size: 1.75rem;
font-weight: 600;
color: var(--accent-color);
```

### Models Table Styling (lines 500-543)

**Table:** `.models-table`
```css
width: 100%;
border-collapse: collapse;
```

**Header:** `.models-table thead`
```css
background-color: var(--bg-secondary);
border-bottom: 2px solid var(--border-color);
```

**Heading Cell:** `.models-table th`
```css
padding: 1rem;
text-align: left;
font-weight: 600;
color: var(--text-primary);
font-size: 0.9rem;
text-transform: uppercase;
letter-spacing: 0.05em;
```

**Cell:** `.models-table td`
```css
padding: 1rem;
border-bottom: 1px solid var(--border-color);
color: var(--text-primary);
```

**Row Hover:** `.models-table tbody tr:hover`
```css
background-color: var(--hover-bg);
```

**Right-Aligned:** `.models-table .text-right`
```css
text-align: right;
font-family: monospace;
font-size: 0.9rem;
```

**Footer:** `.models-table tfoot`
```css
background-color: var(--bg-secondary);
border-top: 2px solid var(--border-color);
```

**Totals Row:** `.models-table .totals-row`
```css
font-weight: 600;
```

Cell color: accent-color (blue)

### Error States (lines 406-427)

**Error Banner:** `.error-banner`
```css
background-color: rgba(239, 68, 68, 0.1);
border: 1px solid rgba(239, 68, 68, 0.3);
border-radius: 8px;
padding: 1.5rem;
margin-bottom: 2rem;
display: flex;
align-items: center;
justify-content: space-between;
gap: 1rem;
color: #ef4444;
```

**Error Message:** `.error-message`
```css
background-color: rgba(239, 68, 68, 0.1);
border: 1px solid rgba(239, 68, 68, 0.3);
border-radius: 6px;
padding: 0.75rem 1rem;
margin-bottom: 1rem;
color: #ef4444;
font-size: 0.9rem;
```

### Empty State (lines 430-446)

**Empty State:** `.empty-state`
```css
text-align: center;
padding: 3rem 2rem;
background-color: var(--bg-secondary);
border: 1px dashed var(--border-color);
border-radius: 8px;
```

Heading and paragraph styling with secondary text color.

### Footer (lines 449-466)

**Footer:** `.footer`
```css
background-color: var(--bg-secondary);
border-top: 1px solid var(--border-color);
padding: 1.5rem 0;
margin-top: 2rem;
```

**Content:** `.footer-content`
```css
max-width: 1200px;
margin: 0 auto;
padding: 0 2rem;
text-align: center;
```

**Text:** `.footer-text`
```css
font-size: 0.85rem;
color: var(--text-secondary);
```

---

## Charts Section (lines 613-676)

**Chart Container:** `.chart-container`
```css
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 1.5rem;
margin-bottom: 2rem;
```

**Charts Grid:** `.charts-grid`
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
gap: 2rem;
margin-bottom: 2rem;
```

Responsive: 1-3 columns depending on screen width.

**Chart Wrapper:** `.chart-wrapper`
```css
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
padding: 1.5rem;
position: relative;
min-height: 300px;
```

**Canvas:** `.chart-wrapper canvas`
```css
max-height: 300px;
```

**Charts Section Heading:** `.charts-section h2`
```css
font-size: 1.25rem;
font-weight: 600;
color: var(--text-primary);
margin-bottom: 1.5rem;
```

### HTMX Loading State (lines 653-686)

**Loading Class:** `.htmx-loading`
```css
opacity: 0.6;
pointer-events: none;
```

**Spinner (Pseudo-element):** `.htmx-loading::after`
```css
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
```

**Spinner Animation:** `@keyframes spin`
```css
to {
    transform: translate(-50%, -50%) rotate(360deg);
}
```

**Standalone Spinner:** `.loading-spinner`
```css
display: inline-block;
width: 20px;
height: 20px;
border: 3px solid var(--border-color);
border-top-color: var(--accent-sonnet);
border-radius: 50%;
animation: spin 0.8s linear infinite;
```

### Pagination (lines 689-716)

**Controls:** `.pagination-controls`
```css
display: flex;
justify-content: center;
gap: 1rem;
margin-top: 2rem;
```

(Documented under buttons section)

### Messages List (lines 719-721)

**Container:** `#messages-list`
```css
margin: 2rem 0;
```

### Filters Section (lines 754-855)

**Container:** `.filters-section`
```css
margin-bottom: 2rem;
padding: 1.5rem;
background-color: var(--bg-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;
```

**Heading:** `.filters-section h2`
```css
font-size: 1.1rem;
margin-bottom: 1rem;
color: var(--text-primary);
```

**Filters Grid:** `.filters-grid`
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 1.5rem;
align-items: end;
```

**Filter Group:** `.filter-group`
```css
display: flex;
flex-direction: column;
gap: 0.5rem;
```

**Label:** `.filter-group label`
```css
font-size: 0.9rem;
font-weight: 600;
color: var(--text-secondary);
text-transform: uppercase;
letter-spacing: 0.05em;
```

**Date Input:** `.date-input`
```css
padding: 0.75rem;
border: 1px solid var(--border-color);
border-radius: 6px;
background-color: var(--bg-primary);
color: var(--text-primary);
font-size: 0.95rem;
transition: border-color 0.2s;
```

Focus:
```css
outline: none;
border-color: var(--accent-sonnet);
box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
```

**Project Select:** `.project-select`
```css
(Same as .date-input)
cursor: pointer;
```

**Filter Actions:** `.filter-actions`
```css
display: flex;
align-items: flex-end;
```

**Granularity Badge:** `.granularity-badge`
```css
margin-top: 1rem;
padding: 0.5rem 1rem;
background-color: var(--accent-sonnet);
color: white;
border-radius: 4px;
font-size: 0.85rem;
font-weight: 600;
display: inline-block;
```

**Badge Content:** `.badge`
```css
display: flex;
align-items: center;
gap: 0.5rem;
```

---

## Responsive Design

### Medium Screens (max-width: 1024px)

**Charts Grid:** `grid-template-columns: 1fr`
- Single column layout
- Min-height: 350px

### Small Screens (max-width: 768px)

**Stats Grid:** `grid-template-columns: 1fr`
- Single column

**Token Breakdown Grid:** `grid-template-columns: 1fr 1fr`
- Two columns (width-constrained)

**Header Content:**
```css
flex-direction: column;
gap: 1rem;
```
- Vertical stacking
- Title: font-size 1.25rem

**Header Nav:**
```css
margin: 0;
```

**Main Content:**
```css
padding: 1rem;
```

**Stat Cards:**
```css
padding: 1.25rem;
```

**Stat Value:** `font-size: 1.5rem`

**Breakdown Cards:**
```css
padding: 1.25rem;
```

**Breakdown Value:** `font-size: 1.5rem`

**Tables:**
```css
font-size: 0.85rem;
```

Header/cell padding: 0.75rem

**Models Table:**
```css
th, td: padding 0.75rem;
.text-right: font-size 0.8rem;
```

**Chart Container:**
```css
padding: 1rem;
```

**Chart Wrapper:**
```css
padding: 1rem;
min-height: 250px;
canvas max-height: 250px;
```

**Filters Grid:**
```css
grid-template-columns: 1fr;
```
- Single column on mobile

---

## Color Scheme Summary

### Dark Theme Palette

| Purpose | Color | Use |
|---------|-------|-----|
| Background | #0d1117 | Page background |
| Surface | #161b22 | Cards, sections |
| Border | #30363d | Dividers, borders |
| Text Primary | #e6edf3 | Main text |
| Text Secondary | #8b949e | Labels, hints |
| Accent (Blue) | #3b82f6 | Primary interactive |
| Opus (Purple) | #a855f7 | Claude Opus |
| Sonnet (Blue) | #3b82f6 | Claude Sonnet |
| Haiku (Green) | #10b981 | Claude Haiku |
| Error | #ef4444 | Error states |

### Light Theme Palette

| Purpose | Color | Use |
|---------|-------|-----|
| Background | #ffffff | Page background |
| Surface | #f6f8fa | Cards, sections |
| Border | #d1d5db | Dividers, borders |
| Text Primary | #1f2937 | Main text |
| Text Secondary | #6b7280 | Labels, hints |
| Accent (Blue) | #2563eb | Primary interactive |
| Opus (Purple) | #9333ea | Claude Opus |
| Sonnet (Blue) | #2563eb | Claude Sonnet |
| Haiku (Green) | #059669 | Claude Haiku |
| Error | #dc2626 | Error states |

---

## Typography

### Font Stack

```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
```

System fonts for optimal performance (no external font loading).

**Monospace (for numbers/code):**
```css
font-family: "Monaco", "Courier New", monospace;
```

### Size Hierarchy

| Element | Size | Weight |
|---------|------|--------|
| Page Title (.header-title) | 1.5rem | 700 |
| Section Heading (h2) | 1.25rem | 600 |
| Filter Heading (.filters-section h2) | 1.1rem | 600 |
| Stat Value | 2rem | 700 |
| Stat Label | 0.875rem | 500 |
| Button | 0.95rem | 600 |
| Nav Link | 0.95rem | normal |
| Table Cell | 0.9rem | normal |
| Table Header | 0.875rem | 600 |
| Small Text (.form-help) | 0.85rem | normal |

### Text Treatments

**Uppercase Labels:**
```css
text-transform: uppercase;
letter-spacing: 0.05em;
font-weight: 600;
```

Used for: Stat labels, table headers, form labels, filter labels.

**Monospace Numbers:**
```css
font-family: "Monaco", "Courier New", monospace;
```

Used for: Stat values, table numbers.

---

## Animation & Transitions

### Transition Durations

- Quick interactions: 0.2s (hover effects, color changes)
- Medium interactions: 0.3s (theme changes, opacity)
- Slow interactions: 0.8s (spinning loaders)

### Transition Properties

```css
transition: all 0.2s;           /* All properties animate */
transition: border-color 0.2s;  /* Specific property */
transition: background-color 0.3s, color 0.3s;  /* Multiple */
```

### Animations

**Spin Animation** (for loading spinners)
```css
@keyframes spin {
    to {
        transform: translate(-50%, -50%) rotate(360deg);
    }
}
```

Duration: 0.8s, linear, infinite.

### Transform Effects

**Button Hover (lift effect):**
```css
transform: translateY(-1px);
```

Gives tactile feedback on hover.

---

## Known Styling Patterns

### Consistent Padding

- Container horizontal: 2rem
- Component padding: 1.5rem
- Small padding: 0.75rem
- Tight padding: 0.5rem

### Consistent Gap

- Major sections: gap 2rem
- Grid items: gap 1.5rem
- Flex items: gap 0.5rem
- Table padding: 1rem

### Consistent Border Radius

- Large elements: 8px
- Inputs: 6px
- Icons: 4px

### Consistent Shadows

Only on hover states (box-shadow, not drop-shadow):
```css
box-shadow: 0 0 16px rgba(59, 130, 246, 0.1);
```

Focus states:
```css
box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
```

---

## Known Gaps

1. **Print Styles:**
   - No @media print rules
   - Charts may not print well

2. **High Contrast Mode:**
   - No @media (prefers-contrast: more) rules
   - May have contrast issues for some users

3. **Reduced Motion:**
   - No @media (prefers-reduced-motion: reduce) rules
   - Animations play for all users

4. **SVG Icon Styling:**
   - Icons hardcoded in HTML
   - No separate SVG stylesheet

5. **Dark Mode Auto-Detection:**
   - Only affects initial load
   - System preference changes during session won't update theme unless user hasn't set one

6. **Tablet Breakpoints:**
   - Only 768px and 1024px breakpoints
   - Gap between breakpoints might cause layout issues on some tablets

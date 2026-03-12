# Claude Code Usage Visualizer - Documentation

**Status:** Phase 4.1 Complete | **Last Updated:** February 15, 2026

## Quick Overview

A web application that visualizes Claude Code API usage across projects and sessions with comprehensive token tracking and timezone support.

### Key Features

- 📊 **Overview Dashboard** - Total cost, token breakdown, daily activity
- 🔍 **Project Drill-Down** - View sessions per project with costs
- 💬 **Session Details** - Message-level token usage breakdown
- 🌍 **Timezone Toggle** - UTC/Local time, 24h/12h format (4 modes)
- 💰 **Token Tracking** - Input, Output, Cache Read, Cache Write tokens
- 💾 **Data Persistence** - User preferences saved in localStorage

## Project Structure

```
src/
├── app/
│   ├── routers/       # FastAPI routes (overview, projects, sessions)
│   ├── templates/     # Jinja2 HTML templates
│   ├── static/        # CSS and JavaScript
│   └── data/          # Data models and pricing logic
├── main.py            # FastAPI application entry point
└── config.py          # Configuration

docs/
├── README.md          # This file
├── GUIDE.md           # Implementation guide (all phases)
├── TESTING.md         # Testing guide and validation
└── FEATURES.md        # Detailed feature documentation
```

## Getting Started

### Prerequisites
- Python 3.11+
- uv package manager

### Installation

```bash
git clone <repo>
cd claude-usage-visualizer
make setup
```

### Running the Application

```bash
# Development (auto-reload)
make dev

# Production
make run

# Stop the server
make stop
```

Navigate to: `http://127.0.0.1:8000/`

### Configuration

Set Claude data directory via environment variable:
```bash
export CLAUDE_DATA_DIR="/path/to/claude/data"
```

Or configure in the app settings UI at `/settings`

## Documentation Map

| Document | Purpose |
|----------|---------|
| **README.md** | This overview |
| **PHASE4.md** | Phase 4 & 4.1 features and quick start |
| **GUIDE.md** | Implementation guide (all phases) |
| **TESTING.md** | Testing scenarios and validation |
| **FEATURES.md** | Feature specifications |
| **_archive/** | Detailed technical docs (if needed) |

---

## Phase Summary

### Phase 1: Foundation
- ✅ Data parsing from Claude stats-cache.json
- ✅ Overview dashboard with stats and tables
- ✅ Database of model pricing

### Phase 2: Navigation
- ✅ Project drill-down with session list
- ✅ Session detail with message-level breakdown
- ✅ Dynamic routing and data flow

### Phase 2.1: Enhancements
- ✅ Overview token breakdown (4 token types)
- ✅ Model-wise token segregation
- ✅ Timezone toggle (4 modes: UTC/Local × 24h/12h)
- ✅ localStorage persistence
- ✅ Cross-page consistency

### Phase 3: Charts + HTMX Interactivity
- ✅ Interactive Chart.js visualizations (5 charts)
- ✅ HTMX infrastructure for dynamic loading
- ✅ API endpoints for chart data

### Phase 4: Interactive Filtering & Folder-wise Analytics
- ✅ Date range filtering for charts
- ✅ Project-specific filtering and analytics
- ✅ Auto-granularity (hourly < 1 day, daily otherwise)
- ✅ Filter persistence via localStorage
- ✅ Project detail charts

### Phase 4.1: UI Refinements & Timezone Integration
- ✅ Timezone selector dropdown (4 options)
- ✅ Analytics auto-update on timezone change
- ✅ All timestamps update instantly
- ✅ Documentation consolidated

---

## Key Technologies

- **Backend:** FastAPI (Python)
- **Frontend:** Jinja2 templates, vanilla JavaScript, CSS
- **Styling:** Custom CSS with dark/light theme support
- **Data:** JSON-based from Claude stats-cache.json
- **Storage:** Browser localStorage for preferences

---

## Features at a Glance

### Token Breakdown
View all token types on overview page:
- Input Tokens
- Output Tokens
- Cache Write Tokens
- Cache Read Tokens

### Timezone Selector (Phase 4.1)
Dropdown in header with 4 options:
1. **UTC 24h** - `2026-02-15 14:30:45`
2. **Local 24h** - `2026-02-15 19:45:30`
3. **UTC 12h** - `2026-02-15 02:30:45 PM`
4. **Local 12h** - `2026-02-15 07:45:30 PM`

### Interactive Filters (Phase 4)
- **Date Range** - Select custom start/end dates
- **Project Filter** - Isolate analytics to specific project
- **Auto Granularity** - Hourly for <1 day, daily for longer
- **Smart Charts** - 5 interactive Chart.js visualizations

---

## Testing

See `TESTING.md` for comprehensive testing guide with 10+ scenarios.

Quick validation:
1. Start server: `make dev`
2. Open: `http://127.0.0.1:8000/`
3. Test timezone button in header
4. Test navigation between pages
5. Check localStorage persistence

---

## File Guide

**Key Implementation Files:**
- `src/app/routers/overview.py` - Overview page data
- `src/app/routers/projects.py` - Projects/sessions navigation
- `src/app/static/timezone.js` - Timezone toggle logic
- `src/app/static/style.css` - Application styling
- `src/app/templates/overview.html` - Overview page
- `src/app/templates/project_detail.html` - Projects page
- `src/app/templates/session_detail.html` - Session page

---

## Architecture

```
Request → FastAPI Router → Data Processing → Template Rendering
                ↓
         Token calculations
         Price estimation
         Data aggregation
                ↓
         Jinja2 Template + data-timestamp attributes
                ↓
         Browser (timezone.js converts timestamps)
```

---

## Next Steps

1. **Testing** - Follow TESTING.md for comprehensive validation
2. **Customization** - Adjust theme, colors, or layout in CSS
3. **Deployment** - Deploy FastAPI app to production
4. **Monitoring** - Track user preferences and feedback

---

## Quick Links

**Want to know about Phase 4?** → See `PHASE4.md`
**Need implementation details?** → See `GUIDE.md`
**How to test?** → See `TESTING.md`
**Feature specifications?** → See `FEATURES.md`
**Need detailed technical docs?** → Check `_archive/` folder

---

**Status: Production Ready ✅**

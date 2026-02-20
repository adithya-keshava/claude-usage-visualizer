# Agent Configuration Index

**Project:** Claude Usage Visualizer
**Language:** Python (FastAPI)
**Status:** 🔄 Agent-Ready (In Progress)
**Last Updated:** 2026-02-20

This file enables AI coding agents (Claude Code, Cursor, Gemini CLI) to understand and work effectively with this repository. Skills are indexed below for reliable triggering.

---

## Quick Start for Agents

### Clone & Setup
```bash
cd /path/to/claude-usage-visualizer
uv sync --python 3.11
```

### Run Application
```bash
uv run --python 3.11 src/main.py
# Application available at http://localhost:8000/
```

### Project Structure
```
.
├── src/app/
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration and constants
│   ├── routers/                # API and page routes
│   │   ├── overview.py         # Dashboard
│   │   ├── projects.py         # Project listing and details
│   │   ├── sessions.py         # Session details
│   │   ├── settings.py         # Settings page
│   │   └── api.py              # JSON API endpoints
│   ├── static/                 # JavaScript and CSS
│   │   ├── theme.js            # Theme toggle
│   │   ├── timezone.js         # Timezone conversion
│   │   ├── charts.js           # Chart.js initialization
│   │   ├── htmx-config.js      # HTMX setup
│   │   └── style.css           # Styling
│   └── templates/              # Jinja2 templates
│       ├── base.html           # Base layout
│       ├── overview.html       # Overview page
│       ├── projects.html       # Projects page
│       ├── session_detail.html # Session details
│       └── partials/           # Reusable components
├── pyproject.toml              # Python project metadata
├── BUILD_CHECKLIST.md          # Agent-readiness extraction tasks
└── AGENTS.md                   # This file
```

---

## Skills Index

### 🔧 Core Development Skills

#### Code Security Review
**Triggers:** `code-security`, `security review`, `vulnerability`, `injection`
**Purpose:** Review code for security vulnerabilities (OWASP Top 10, injection, XSS, CSRF)
**When to Use:**
- Adding new API endpoints
- Modifying user input handling
- Adding authentication/authorization
- Handling sensitive data

**Example Invocation:**
```
Review the API endpoints in src/app/routers/api.py for security vulnerabilities
```

#### Application Security
**Triggers:** `application-security`, `auth`, `credentials`, `secrets`
**Purpose:** Apply security best practices for authentication, credential handling, and data protection
**When to Use:**
- Implementing user authentication
- Adding API key management
- Handling password/token storage
- Implementing access control

---

### 📊 Frontend Development Skills

#### Web Artifacts Builder
**Triggers:** `web-artifacts`, `frontend`, `ui components`, `react`, `tailwind`
**Purpose:** Build and enhance frontend interfaces using React, Tailwind CSS, shadcn/ui
**When to Use:**
- Creating new dashboard visualizations
- Building interactive components
- Enhancing user interface
- Adding responsive design

**Example Invocation:**
```
Create a new filter component for the charts using Tailwind CSS
```

#### Canvas Design
**Triggers:** `canvas`, `design`, `visualization`, `poster`, `art`
**Purpose:** Create visual designs and data visualizations
**When to Use:**
- Designing custom charts
- Creating dashboard layouts
- Building visual presentations
- Designing infographics

---

### 📚 Documentation & Specification Skills

#### Tech Spec Reviewer
**Triggers:** `tech-spec`, `specification`, `design`, `architecture`
**Purpose:** Review and improve technical specifications and design documents
**When to Use:**
- Writing API specifications
- Documenting architecture decisions
- Creating implementation plans
- Reviewing technical proposals

**Example Invocation:**
```
Review the API specification in docs/GUIDE.md for completeness
```

#### SOP Generator
**Triggers:** `sop`, `procedure`, `workflow`, `process`
**Purpose:** Generate and improve standard operating procedures
**When to Use:**
- Creating deployment procedures
- Documenting troubleshooting steps
- Writing operational guidelines
- Creating runbooks

---

### 🔍 Analysis & Investigation Skills

#### Problem Clustering
**Triggers:** `problem-clustering`, `categorize`, `group issues`, `ticket analysis`
**Purpose:** Analyze and cluster related issues or tickets
**When to Use:**
- Analyzing user feedback
- Categorizing bug reports
- Identifying patterns in issues
- Grouping related work items

#### Ticket Resolution Analyzer
**Triggers:** `ticket-resolution`, `issue analysis`, `resolve`, `similar issues`
**Purpose:** Analyze tickets and find similar historical resolutions
**When to Use:**
- Finding similar past issues
- Recommending solutions based on history
- Identifying repeated problems
- Learning from resolved tickets

---

### 📋 Content & Configuration Skills

#### PDF Manipulation
**Triggers:** `pdf`, `document`, `extract`, `merge`, `form`
**Purpose:** Create, extract, and manipulate PDF documents
**When to Use:**
- Generating PDF reports
- Extracting data from PDFs
- Creating documentation PDFs
- Filling PDF forms

#### Spreadsheet (XLSX) Tools
**Triggers:** `spreadsheet`, `xlsx`, `excel`, `csv`, `data analysis`
**Purpose:** Create and analyze Excel spreadsheets
**When to Use:**
- Exporting analytics data
- Creating data reports
- Analyzing CSV data
- Building spreadsheet-based dashboards

#### Document (DOCX) Tools
**Triggers:** `docx`, `word`, `document`, `report`
**Purpose:** Create and edit Word documents
**When to Use:**
- Generating documentation
- Creating reports
- Building proposal documents
- Creating technical guides

#### Presentation (PPTX) Tools
**Triggers:** `pptx`, `powerpoint`, `presentation`, `slides`
**Purpose:** Create and edit PowerPoint presentations
**When to Use:**
- Creating project presentations
- Building demo slides
- Creating training materials
- Preparing project summaries

---

### 🎨 Creative & Design Skills

#### Algorithmic Art
**Triggers:** `algorithmic-art`, `generative art`, `p5.js`, `visualization`, `particles`
**Purpose:** Create generative art using p5.js with interactive parameters
**When to Use:**
- Creating data visualizations
- Building interactive art
- Generating visual effects
- Creating animated visualizations

#### Brand Guidelines
**Triggers:** `brand`, `styling`, `theme`, `design system`
**Purpose:** Apply brand colors and typography to artifacts
**When to Use:**
- Applying company branding
- Maintaining design consistency
- Creating branded materials
- Applying corporate styling

#### Theme Factory
**Triggers:** `theme`, `styling`, `colors`, `fonts`
**Purpose:** Apply and manage design themes
**When to Use:**
- Creating themed layouts
- Managing color schemes
- Applying typography
- Designing dark/light modes

---

## Repository-Specific Skills

### 💰 Pricing Update Handler
**Triggers:** `pricing`, `update pricing`, `anthropic pricing`, `model costs`
**Purpose:** Fetch latest Claude model pricing from Anthropic API and update pricing.py
**Implementation:** `src/app/data/pricing.py`
**When to Use:**
- New Claude models are released
- Pricing changes occur
- Annual pricing review
- Keeping cost estimates accurate

**How It Works:**
1. Calls `_fetch_pricing_from_api()` to get latest pricing from Anthropic's models API
2. Parses response and normalizes to $/MTok (million tokens) format
3. Falls back to hardcoded pricing if API unavailable
4. Caches result for 24 hours to avoid rate limiting
5. Logs warnings for unknown models

**Recent Changes (Feb 20, 2026):**
- Added automatic API-based pricing fetching
- Implemented 24-hour caching with TTL
- Graceful fallback to hardcoded prices if requests library unavailable
- Added `requests>=2.31.0` to dependencies

**To Update Pricing:**
```python
# Manual cache refresh (clears 24-hour TTL)
from src.app.data.pricing import get_cached_pricing
pricing = get_cached_pricing()  # Fetches fresh from API if cache expired
```

---

## Repository Skills (Domain-Specific)

> **Note:** Repository skills are auto-generated from domain knowledge extraction. These will be populated in `.agents/skills/repo-skill/` during Phase 3 of agent-readiness.

### Expected Repository Skill Coverage

- **Architecture Documentation:** FastAPI routing, component structure, data flow
- **Data Layer Patterns:** JSON/JSONL parsing, caching, token calculations, pricing
- **Frontend Patterns:** Template inheritance, JavaScript modules, HTMX integration
- **API Design:** Endpoint structure, response formats, error handling
- **Configuration Management:** Environment variables, settings patterns
- **Testing Patterns:** Test setup, fixtures, validation
- **Deployment:** Environment-specific configuration, Docker setup
- **Pricing Management:** Dynamic pricing from Anthropic API with fallback

---

## Integration Points

### External Services
- **Chart.js** - Client-side charting (CDN-based)
- **HTMX** - Dynamic content loading (CDN-based)
- **python-dotenv** - Environment variable management

### Data Sources
- **~/.claude/** - Local Claude Code usage data (JSON/JSONL files)

### Target Browsers
- Chrome, Firefox, Safari, Edge (latest versions)

---

## Common Development Tasks

### Adding a New Chart

1. **Create API endpoint** in `src/app/routers/api.py`
   - Return Chart.js-compatible JSON format
   - Include data, labels, colors

2. **Add canvas element** in appropriate template
   - `src/app/templates/overview.html` for overview charts
   - `src/app/templates/projects.html` for project-specific

3. **Initialize chart** in `src/app/static/charts.js`
   - Pass data from API
   - Apply theme colors
   - Configure chart options

4. **Style the container** in `src/app/static/style.css`
   - Add responsive sizing
   - Add borders/shadows
   - Mobile optimization

### Adding a New Feature

1. **Create router** in `src/app/routers/`
2. **Add template** in `src/app/templates/`
3. **Add JavaScript** in `src/app/static/` if needed
4. **Add styling** to `src/app/static/style.css`
5. **Register route** in `src/app/main.py`

### Debugging

**View application logs:**
```bash
uv run --python 3.11 src/main.py
```

**Browser DevTools:**
- Console: Check JavaScript errors
- Network: Verify API responses
- Storage: Check localStorage (theme, timezone)

**API Testing:**
```bash
curl http://localhost:8000/api/overview
curl http://localhost:8000/api/projects-cost
```

---

## Testing

Run existing tests:
```bash
uv run pytest
```

Test categories:
- Unit tests: Data parsing, calculations
- Integration tests: API endpoints, template rendering
- Frontend tests: Browser-based functionality

---

## Documentation

- **`docs/README.md`** - Project overview and phases
- **`docs/FEATURES.md`** - Feature specifications
- **`docs/GUIDE.md`** - Implementation guide
- **`docs/TESTING.md`** - Testing procedures
- **`SECURITY_VALIDATION.md`** - Security audit results
- **`BUILD_CHECKLIST.md`** - Agent-readiness extraction tasks

---

## Contributing as an Agent

### Code Quality Standards

✅ **Required:**
- Follow PEP 8 for Python code
- Add docstrings to new functions
- Test new functionality
- Update documentation

❌ **Avoid:**
- Hardcoded paths or credentials
- Breaking existing functionality
- Adding unnecessary dependencies
- Complex abstractions for single use

### Testing Before Commit

```bash
# Run linting
uv run pylint src/

# Run tests
uv run pytest

# Manual testing
uv run --python 3.11 src/main.py
# Visit http://localhost:8000/
```

---

## Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Phase 1 (Architecture) | ✅ Complete | Main app, routers, templates documented |
| Phase 2 (Charts/HTMX) | ✅ Complete | 5 chart types, dynamic loading working |
| Phase 3 (Token Breakdown) | ✅ Complete | Cache write/read tokens added |
| Phase 4 (Filtering) | 🔄 Planned | Grouping, date range filters |
| Agent-Readiness | 🔄 In Progress | BUILD_CHECKLIST.md active |

---

## Next Steps for Agent-Readiness

1. **Complete domain knowledge extraction** (Phase 1-2 tasks in BUILD_CHECKLIST.md)
2. **Create repo skill** with consolidated architecture documentation
3. **Generate nested AGENTS.md** files for each major component
4. **Validate skill triggering** and documentation completeness
5. **Mark as fully agent-ready** once BUILD_CHECKLIST.md shows 100%

To continue: `/agent-ready:resume` or `/agent-ready:init-python`

---

**Last Updated:** 2026-02-20
**Agent-Ready Version:** 1.0
**Maintained By:** Automatic generation

# Agent-Readiness Build Checklist

**Project:** Claude Usage Visualizer
**Language:** Python (FastAPI)
**Status:** ⏳ In Progress
**Last Updated:** 2026-02-20

---

## Phase 0: Discovery & Planning

- [x] **0.1** - Detect Python project markers (pyproject.toml, setup.py, etc.)
- [x] **0.2** - Create .agents/ directory structure
- [x] **0.3** - Install agentfill configuration
- [ ] **0.4** - Conduct domain discovery interview
- [ ] **0.5** - Identify key entities and integrations

**Phase 0 Progress:** 3/5 (60%)

---

## Phase 1: Domain Knowledge Extraction

### 1.1 - Application Architecture
- [ ] **1.1.1** - Document main.py structure and routing
- [ ] **1.1.2** - Extract config.py patterns and environment handling
- [ ] **1.1.3** - Map routers (overview, projects, sessions, settings, api)
- [ ] **1.1.4** - Document static assets and template structure

**1.1 Progress:** 0/4

### 1.2 - Data Layer
- [ ] **1.2.1** - Extract data models (TokenUsage, SessionSummary, ProjectSummary)
- [ ] **1.2.2** - Document data parsing logic (JSON/JSONL loaders)
- [ ] **1.2.3** - Extract pricing calculations and token cost formulas
- [ ] **1.2.4** - Document cache mechanism and invalidation strategy

**1.2 Progress:** 0/4

### 1.3 - Frontend Layer
- [ ] **1.3.1** - Document HTML template structure and inheritance
- [ ] **1.3.2** - Extract JavaScript modules (theme, timezone, charts, filters)
- [ ] **1.3.3** - Document CSS structure and theme system
- [ ] **1.3.4** - Document HTMX integration points

**1.3 Progress:** 0/4

### 1.4 - API Layer
- [ ] **1.4.1** - Extract API endpoints and their contracts
- [ ] **1.4.2** - Document JSON response formats for charts
- [ ] **1.4.3** - Document query parameter handling
- [ ] **1.4.4** - Extract error handling patterns

**1.4 Progress:** 0/4

**Phase 1 Total Progress:** 0/16 (0%)

---

## Phase 2: Technical Patterns & Integrations

### 2.1 - Database & State Management
- [ ] **2.1.1** - Document file-based data loading patterns
- [ ] **2.1.2** - Extract cache implementation details
- [ ] **2.1.3** - Document in-memory state management
- [ ] **2.1.4** - Extract TTL and invalidation logic

**2.1 Progress:** 0/4

### 2.2 - Third-Party Integrations
- [ ] **2.2.1** - Document Chart.js integration (configuration, data format)
- [ ] **2.2.2** - Extract HTMX patterns and usage
- [ ] **2.2.3** - Document Jinja2 template features used
- [ ] **2.2.4** - Extract python-dotenv usage

**2.2 Progress:** 0/4

### 2.3 - Frontend Patterns
- [ ] **2.3.1** - Extract JavaScript module patterns
- [ ] **2.3.2** - Document localStorage usage (theme, timezone persistence)
- [ ] **2.3.3** - Extract DOM manipulation patterns
- [ ] **2.3.4** - Document event handling

**2.3 Progress:** 0/4

### 2.4 - Cross-Cutting Concerns
- [ ] **2.4.1** - Document error handling strategy
- [ ] **2.4.2** - Extract logging patterns
- [ ] **2.4.3** - Document configuration management
- [ ] **2.4.4** - Extract testing setup and patterns

**2.4 Progress:** 0/4

**Phase 2 Total Progress:** 0/16 (0%)

---

## Phase 3: Skills & Agent Integration

### 3.1 - Core Skills Setup
- [ ] **3.1.1** - Install/verify code-security skill
- [ ] **3.1.2** - Install/verify application-security skill
- [ ] **3.1.3** - Install/verify tech-spec-reviewer skill
- [ ] **3.1.4** - Fetch optional domain-specific skills

**3.1 Progress:** 0/4

### 3.2 - Repo Skill Creation
- [ ] **3.2.1** - Create repo-skill README structure
- [ ] **3.2.2** - Populate architecture documentation
- [ ] **3.2.3** - Populate data layer documentation
- [ ] **3.2.4** - Populate integration documentation
- [ ] **3.2.5** - Create code examples for key patterns

**3.2 Progress:** 0/5

### 3.3 - AGENTS.md Generation
- [ ] **3.3.1** - Generate root AGENTS.md with Skills Index
- [ ] **3.3.2** - Create nested AGENTS.md for src/app/
- [ ] **3.3.3** - Create nested AGENTS.md for src/app/routers/
- [ ] **3.3.4** - Create nested AGENTS.md for src/app/static/
- [ ] **3.3.5** - Create nested AGENTS.md for src/app/templates/

**3.3 Progress:** 0/5

**Phase 3 Total Progress:** 0/14 (0%)

---

## Phase 4: Validation & Finalization

- [ ] **4.1** - Verify all AGENTS.md files are consistent
- [ ] **4.2** - Test skill triggering from root AGENTS.md
- [ ] **4.3** - Validate repo-skill documentation completeness
- [ ] **4.4** - Create agent-readiness summary document
- [ ] **4.5** - Mark repository as agent-ready

**Phase 4 Progress:** 0/5 (0%)

---

## Overall Progress Summary

| Phase | Tasks | Complete | Progress |
|-------|-------|----------|----------|
| Phase 0 | 5 | 3 | 60% |
| Phase 1 | 16 | 0 | 0% |
| Phase 2 | 16 | 0 | 0% |
| Phase 3 | 14 | 0 | 0% |
| Phase 4 | 5 | 0 | 0% |
| **Total** | **56** | **3** | **5%** |

---

## Next Steps

1. **Conduct domain discovery interview** (Phase 0.4)
   - Identify key data entities
   - List external integrations
   - Map main user flows

2. **Extract application architecture** (Phase 1.1)
   - Document routing structure
   - Map component relationships
   - Extract key patterns

3. **Build domain knowledge** (Phase 1.2-1.4)
   - Extract data models
   - Document API contracts
   - Capture frontend patterns

4. **Create repo skill** (Phase 3.2)
   - Consolidate architecture docs
   - Add code examples
   - Create implementation guides

5. **Generate AGENTS.md** (Phase 3.3)
   - Create Skills Index
   - Make skills easily discoverable
   - Enable reliable skill triggering

---

## Notes

- This checklist is generated by `/agent-ready:init-python`
- Each task can be completed by specialized extraction agents
- Use `/agent-ready:resume` to continue extraction after this phase
- Estimated completion: 10-15 tasks per session

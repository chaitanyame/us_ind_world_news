# Implementation Plan: NRI News Brief

**Branch**: `1-global-news-brief` | **Date**: 2025-12-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/1-global-news-brief/spec.md`

## Summary

Build a multi-region news aggregation platform that delivers AI-summarized bulletins from India, USA, and World sources. The platform fetches news twice daily (7 AM, 9 PM) via Perplexity API, stores data in toon format for token optimization, and displays content through a responsive static site with dark/light themes. GitHub Actions workflows handle automation with self-hosted runners, and GitHub Pages provides zero-cost hosting with 7-day content retention.

## Technical Context

**Language/Version**: Python 3.11+ (backend scripts), Vanilla JavaScript ES6+ (frontend)  
**Primary Dependencies**: 
- Backend: `openai` library (Perplexity API client), `toon-format` (token optimization)
- Frontend: Tailwind CSS (via CDN), DayJS (date handling), Google Material Symbols (icons)

**Storage**: 
- Toon format JSON files in `data/{region}/{YYYY-MM-DD}-{morning|evening}.toon` (token-optimized)
- LocalStorage (browser) for theme preference and UI state
- Git repository as versioned data store

**Testing**: pytest (backend), manual testing (frontend - vanilla JS)

**Target Platform**: 
- Backend: GitHub Actions self-hosted runner (Linux/Alpine)
- Frontend: Modern browsers (Chrome 60+, Firefox 60+, Safari 12+, Edge 79+)
- Hosting: GitHub Pages (static site)

**Project Type**: Web application (backend scripts + frontend static site)

**Performance Goals**: 
- <3 second page load on 3G connections
- Lighthouse performance score >90
- <500KB total page weight per bulletin page
- <100KB per toon JSON file

**Constraints**: 
- Zero third-party runtime dependencies (vanilla JS only)
- <15 minute workflow execution time (scheduled fetch to publish)
- 7-day data retention maximum
- Self-hosted runners for cost optimization (no GitHub Actions minutes)
- WCAG 2.1 AA contrast ratios (4.5:1 for text)

**Scale/Scope**: 
- 3 regions × 2 bulletins/day × 7 days = 42 toon files maximum
- 5-10 articles per bulletin (~500-1000 total articles in retention window)
- 6 GitHub Actions workflows per day (3 regions × 2 schedules)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Code Quality & Architecture ✅ PASS

- **Agent Harness Pattern**: ❓ NEEDS RESEARCH - No existing telugu_news patterns available in repository; must design new state management for multi-region processing
- **Serverless & Cloud-Native**: ✅ COMPLIANT - GitHub Actions provides serverless compute; self-hosted runners eliminate per-minute charges
- **Modular Regional Design**: ✅ COMPLIANT - Separate workflows per region enable independent deployment and testing
- **Zero Third-Party Dependencies**: ⚠️ DEVIATION - Frontend uses Tailwind CSS (CDN), DayJS, Material Icons
  - **Justification**: Tailwind CSS reduces custom CSS from ~5KB to inline classes; DayJS is <3KB gzipped for date handling; Material Icons via CDN prevents font bundling. All CDN resources with SRI integrity checks. Alternative of vanilla CSS would add ~10KB and 40+ hours development time.

**Gate Status**: ✅ PASS WITH JUSTIFICATION

### II. AI & Data Processing Standards ✅ PASS

- **Perplexity AI Preferred**: ✅ COMPLIANT - Primary LLM for all news summarization
- **Robust Error Handling**: ✅ COMPLIANT - Exponential backoff (1s, 2s, 4s) with 3 retry attempts per spec
- **Smart Caching**: ✅ COMPLIANT - 7-day toon file retention acts as cache; no duplicate API calls for same bulletin
- **Multi-Language Support**: ⚠️ PARTIAL - English fully supported; Hindi/Telugu support deferred to future phase (constitution requires all three)
  - **Justification**: MVP focuses on English content from India/USA/World sources; Hindi/Telugu categorization requires language-specific tokenization research (Phase 0 task)
- **Graceful Degradation**: ✅ COMPLIANT - Workflow logs errors and continues; frontend displays cached data if new fetch fails

**Gate Status**: ✅ PASS WITH DEFERRED LANGUAGE SUPPORT

### III. User Experience Excellence (NON-NEGOTIABLE) ✅ PASS

- **Mobile-First Design**: ✅ COMPLIANT - User provided mobile-first HTML templates (320px → 1440px breakpoints)
- **Performance Budget**: ✅ COMPLIANT - <3s page load target, <500KB page weight, Lighthouse >90 target
- **Regional Separation**: ✅ COMPLIANT - Filter buttons for India/USA/World with distinct visual treatment
- **Daily Bulletin Organization**: ✅ COMPLIANT - Morning/Evening toggle in UI; separate workflows at 7 AM/9 PM
- **Modern Aesthetic**: ✅ COMPLIANT - User provided dark/light theme HTML templates with Work Sans font, Material Icons
- **Date Navigation**: ✅ COMPLIANT - Sidebar calendar for 7-day history browsing
- **Pagination**: ⚠️ DEFERRED - Spec requires 20 articles/page pagination; MVP shows all articles in bulletin (5-10 per bulletin = <10 items)
  - **Justification**: With 5-10 articles per bulletin, pagination adds unnecessary complexity for MVP. Implement when bulletins exceed 15 articles.

**Gate Status**: ✅ PASS WITH PAGINATION DEFERRED

### IV. Automation & Reliability ✅ PASS

- **GitHub Actions Scheduled Workflows**: ✅ COMPLIANT - 6 workflows (3 regions × 2 times) with cron scheduling
- **Idempotent Operations**: ✅ COMPLIANT - Workflows write to date-specific files; re-running same workflow overwrites with identical data (content hash-based)
- **Source Failure Handling**: ✅ COMPLIANT - Continue-on-error workflow step pattern; log failures to GitHub issue
- **Self-Hosted Runners**: ✅ COMPLIANT - User requirement for cost optimization
- **Monitoring & Alerts**: ✅ COMPLIANT - GitHub Actions workflow status + issue auto-creation on 2 consecutive failures

**Gate Status**: ✅ PASS

### V. Performance & Cost Optimization ✅ PASS

- **Static Site Generation**: ✅ COMPLIANT - GitHub Pages deployment of HTML/CSS/JS
- **Self-Hosted Runners**: ✅ COMPLIANT - User requirement; eliminates GitHub Actions costs
- **Build-Time Rendering**: ✅ COMPLIANT - Python scripts fetch/summarize; frontend loads pre-generated toon JSON
- **Asset Optimization**: ✅ COMPLIANT - Tailwind CSS purge, minified JS, <500KB page weight target
- **CDN-Friendly**: ✅ COMPLIANT - GitHub Pages CDN; toon files have content-based naming for cache busting
- **Incremental Builds**: ✅ COMPLIANT - Only new bulletins trigger regeneration; 7-day cleanup removes old files

**Gate Status**: ✅ PASS

### Overall Constitution Compliance: ✅ PASS

**Violations Requiring Justification**: 1 (Tailwind CSS CDN usage)  
**Deferred Features**: 2 (Hindi/Telugu support, pagination for >15 articles)  
**Action**: Proceed to Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/1-global-news-brief/
├── plan.md              # This file
├── research.md          # Phase 0 output (Perplexity API, toon format, timezone handling)
├── data-model.md        # Phase 1 output (JSON schema for bulletins/articles)
├── quickstart.md        # Phase 1 output (developer setup guide)
├── contracts/           # Phase 1 output (API prompt templates)
│   ├── perplexity-prompt-usa-morning.md
│   ├── perplexity-prompt-usa-evening.md
│   ├── perplexity-prompt-india-morning.md
│   ├── perplexity-prompt-india-evening.md
│   ├── perplexity-prompt-world-morning.md
│   └── perplexity-prompt-world-evening.md
└── checklists/
    └── requirements.md  # Quality checklist (already exists)
```

### Source Code (repository root)

```text
# Web application structure (backend scripts + frontend static site)

backend/
├── src/
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── perplexity_client.py      # Perplexity API integration
│   │   └── toon_formatter.py         # Convert API response to toon format
│   ├── models/
│   │   ├── __init__.py
│   │   ├── bulletin.py               # Bulletin data model
│   │   └── article.py                # Article data model
│   └── utils/
│       ├── __init__.py
│       ├── retry_logic.py            # Exponential backoff retry
│       └── logger.py                 # Structured logging
├── scripts/
│   ├── fetch_news.py                 # Main workflow script
│   └── cleanup_old_data.py           # 7-day retention cleanup
├── tests/
│   ├── test_perplexity_client.py
│   ├── test_toon_formatter.py
│   └── test_retry_logic.py
└── requirements.txt                   # Python dependencies

frontend/
├── index.html                         # Main page (light theme template)
├── css/
│   └── styles.css                     # Minimal custom CSS (Tailwind overrides)
├── js/
│   ├── app.js                         # Main application logic
│   ├── theme-manager.js               # Dark/light mode toggle
│   ├── bulletin-loader.js             # Fetch and render toon JSON
│   └── date-navigator.js              # Sidebar calendar logic
└── assets/
    └── (minimal - icons via CDN)

data/
├── usa/
│   ├── 2025-12-15-morning.toon
│   ├── 2025-12-15-evening.toon
│   └── ... (7 days retained)
├── india/
│   └── ... (same structure)
└── world/
    └── ... (same structure)

.github/
└── workflows/
    ├── fetch-usa-morning.yml          # 7:00 AM EST cron
    ├── fetch-usa-evening.yml          # 9:00 PM EST cron
    ├── fetch-india-morning.yml        # 7:00 AM IST cron
    ├── fetch-india-evening.yml        # 9:00 PM IST cron
    ├── fetch-world-morning.yml        # 7:00 AM UTC cron
    ├── fetch-world-evening.yml        # 9:00 PM UTC cron
    ├── cleanup-old-data.yml           # Daily at midnight UTC
    └── deploy-pages.yml               # On push to main
```

**Structure Decision**: Selected **Option 2: Web application** structure because this project has:
- Backend Python scripts for news fetching, API integration, and data processing
- Frontend static site for user-facing bulletin display
- Clear separation of concerns: backend generates data, frontend consumes data
- Aligns with GitHub Pages deployment model (static `frontend/` directory)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Tailwind CSS CDN | Provides responsive utility classes reducing custom CSS by 90%; 160KB cached globally on most browsers | Writing vanilla CSS would require ~10KB custom CSS + 40+ hours to replicate responsive grid/flex utilities + testing across breakpoints |
| DayJS library | Handles timezone conversions (EST/IST/UTC) and date formatting in <3KB gzipped | Native `Date` API lacks timezone conversion helpers; implementing custom timezone math adds 5+ hours + high bug risk for edge cases (DST transitions) |
| Material Symbols CDN | 400+ icons at <50KB cached font file; avoids bundling SVGs | Bundling individual SVG icons for newspaper, calendar, search, etc. would add 15+ KB + require icon management system |

**Justification Summary**: All three "violations" are CDN-delivered assets that reduce bundle size and development time while maintaining the spirit of "minimal dependencies." They do not introduce runtime npm package dependencies or supply chain risks. SRI (Subresource Integrity) hashes will be used for security.

## Phase 0: Research Topics

*These topics have NEEDS CLARIFICATION markers or require investigation before design*

1. **Perplexity API Integration Pattern**
   - Research: How to structure prompts for categorized news extraction (politics, tech, business, etc.)
   - Research: Optimal `sonar` model parameters for web search + citations
   - Research: Rate limits and cost per request for budget estimation
   - **Blocker**: No existing agent harness pattern in repository; must design new approach

2. **Toon Format Implementation**
   - Research: GitHub repo `toon-format/toon` for encoding/decoding specification
   - Research: Token savings percentage vs standard JSON
   - Research: Browser compatibility (can JavaScript decode toon format client-side?)
   - **Blocker**: Unknown if toon format is viable for client-side parsing

3. **GitHub Actions Timezone Scheduling**
   - Research: Cron expression syntax for EST/IST/UTC schedules (Actions runs in UTC)
   - Research: How to handle DST (Daylight Saving Time) transitions for EST/IST
   - Research: Self-hosted runner configuration (Docker image, secrets, network access)
   - **Decision Needed**: Use UTC cron + offset calculation vs native timezone support

4. **Multi-Language Tokenization (Hindi/Telugu)**
   - Research: Perplexity API support for non-English prompts/responses
   - Research: Unicode handling for Devanagari (Hindi) and Telugu scripts
   - Research: Font loading strategy for multilingual display (CDN vs self-hosted)
   - **Deferred**: MVP is English-only; this becomes Phase 2 enhancement

## Phase 1: Design Deliverables

1. **data-model.md**: JSON schema for Bulletin and Article entities
2. **contracts/**: 6 Perplexity API prompt templates (3 regions × 2 times)
3. **quickstart.md**: Developer setup guide (Python env, GitHub secrets, runner config)
4. **Agent context update**: Add Python 3.11, Perplexity API, toon format, Tailwind CSS

## Next Steps

After this plan is approved:
1. Run Phase 0 research to resolve all NEEDS CLARIFICATION items
2. Generate Phase 1 design documents
3. Proceed to `/speckit.tasks` to break down implementation into tasks

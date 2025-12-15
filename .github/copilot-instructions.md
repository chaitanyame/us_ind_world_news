# Global News Aggregation Platform Development Guidelines

Auto-generated from feature plans. Last updated: 2025-12-15

## Active Technologies

### Backend
- **Python 3.11+**: Backend scripts for news fetching and data processing
- **OpenAI Python Library**: Client for Perplexity API integration
- **Pydantic**: Data validation and schema enforcement
- **Perplexity API (sonar model)**: LLM for news summarization with citations

### Frontend
- **Vanilla JavaScript (ES6+)**: No framework dependencies
- **Tailwind CSS**: Utility-first CSS framework (CDN-delivered)
- **DayJS**: Lightweight date manipulation library
- **Google Material Symbols**: Icon library (CDN-delivered)

### Infrastructure
- **GitHub Actions**: Scheduled workflows for automation
- **Self-Hosted Runners**: Alpine Linux Docker for cost optimization
- **GitHub Pages**: Static site hosting
- **Git Repository**: Data storage with 7-day retention

### Data Format
- **JSON**: Standard JSON format for bulletin storage (toon format deferred)
- **UTF-8 Encoding**: Multi-language support (English, future: Hindi/Telugu)

## Project Structure

```text
us_ind_world_news/
├── backend/
│   ├── src/
│   │   ├── fetchers/
│   │   │   ├── perplexity_client.py  # Perplexity API wrapper
│   │   │   └── toon_formatter.py     # JSON formatting
│   │   ├── models/
│   │   │   ├── bulletin.py           # Bulletin data model (Pydantic)
│   │   │   └── article.py            # Article data model (Pydantic)
│   │   └── utils/
│   │       ├── retry_logic.py        # Exponential backoff (1s, 2s, 4s)
│   │       └── logger.py             # Structured logging
│   ├── scripts/
│   │   ├── fetch_news.py             # Main CLI: --region --period
│   │   └── cleanup_old_data.py       # 7-day retention cleanup
│   ├── tests/
│   │   └── test_*.py                 # pytest tests
│   └── requirements.txt              # openai, pydantic, python-dotenv
├── frontend/
│   ├── index.html                    # Main page (light/dark theme templates provided)
│   ├── css/
│   │   └── styles.css                # Minimal custom CSS overrides
│   ├── js/
│   │   ├── app.js                    # Main application logic
│   │   ├── theme-manager.js          # Dark/light mode toggle + system detection
│   │   ├── bulletin-loader.js        # Fetch and render JSON bulletins
│   │   └── date-navigator.js         # Sidebar calendar (7-day history)
│   └── assets/                       # Minimal (icons via CDN)
├── data/
│   ├── usa/
│   │   ├── YYYY-MM-DD-morning.json   # USA morning bulletins
│   │   └── YYYY-MM-DD-evening.json   # USA evening bulletins
│   ├── india/
│   │   └── ... (same structure)
│   ├── world/
│   │   └── ... (same structure)
│   └── index.json                    # Index of all bulletins for fast navigation
├── .github/
│   └── workflows/
│       ├── fetch-usa-morning.yml     # 7:00 AM EST (cron: 55 11/10 * * *)
│       ├── fetch-usa-evening.yml     # 9:00 PM EST (cron: 55 1/0 * * *)
│       ├── fetch-india-morning.yml   # 7:00 AM IST (cron: 25 1 * * *)
│       ├── fetch-india-evening.yml   # 9:00 PM IST (cron: 25 15 * * *)
│       ├── fetch-world-morning.yml   # 7:00 AM UTC (cron: 55 6 * * *)
│       ├── fetch-world-evening.yml   # 9:00 PM UTC (cron: 55 20 * * *)
│       ├── cleanup-old-data.yml      # Daily at midnight UTC
│       └── deploy-pages.yml          # On push to main
└── specs/
    └── 1-global-news-brief/
        ├── spec.md                   # Feature specification
        ├── plan.md                   # Implementation plan
        ├── research.md               # Phase 0 research findings
        ├── data-model.md             # JSON schema definitions
        ├── quickstart.md             # Developer onboarding guide
        └── contracts/                # Perplexity API prompt templates
```

## Commands

### Python Backend

```bash
# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

# Run news fetcher
python backend/scripts/fetch_news.py --region usa --period morning
python backend/scripts/fetch_news.py --region india --period evening

# Run cleanup (7-day retention)
python backend/scripts/cleanup_old_data.py

# Run tests
cd backend && pytest -v
cd backend && pytest tests/test_perplexity_client.py -v
```

### Frontend Development

```bash
# Start local server
cd frontend && python3 -m http.server 8000
# Open http://localhost:8000

# No build step required (vanilla JS + Tailwind CDN)
```

### GitHub Actions

```bash
# Test workflows locally with Act
act -j fetch-usa-morning --secret PERPLEXITY_API_KEY=xxx

# Manual workflow trigger (add to workflow YAML)
# on:
#   workflow_dispatch:
```

### Data Management

```bash
# View all bulletins
ls -lh data/*/

# View index
cat data/index.json | jq .

# Clean all data
rm -rf data/*/
```

## Code Style

### Python (PEP 8)

```python
# Use Pydantic for data models
from pydantic import BaseModel, Field, HttpUrl

class Article(BaseModel):
    title: str = Field(..., max_length=120)
    summary: str = Field(..., min_length=40, max_length=500)
    category: str = Field(..., regex="^(politics|economy|technology|...)$")
    source: Source
    citations: List[Citation] = Field(..., min_items=1, max_items=3)

# Perplexity API client pattern
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["PERPLEXITY_API_KEY"],
    base_url="https://api.perplexity.ai"
)

response = client.chat.completions.create(
    model="sonar",
    temperature=0.3,
    max_tokens=1000,
    search_recency_filter="day",
    messages=[...]
)

# Exponential backoff retry pattern
for attempt in range(3):
    try:
        response = client.chat.completions.create(...)
        break
    except RateLimitError:
        if attempt < 2:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
        raise
```

### JavaScript (ES6+, Vanilla)

```javascript
// Use async/await for data loading
async function loadBulletin(region, date, period) {
    const response = await fetch(`/data/${region}/${date}-${period}.json`);
    if (!response.ok) throw new Error(`Bulletin not found`);
    return await response.json();
}

// Use const/let, no var
const articles = bulletin.articles;
let selectedRegion = 'usa';

// Destructuring for objects
const { title, summary, category } = article;

// Template literals for strings
const filename = `${region}-${date}-${period}.json`;

// Arrow functions for callbacks
articles.forEach(article => renderCard(article));

// LocalStorage for theme preference
localStorage.setItem('theme', 'dark');
const theme = localStorage.getItem('theme') || 'light';
```

### CSS (Tailwind Utilities)

```html
<!-- Use Tailwind utility classes, minimal custom CSS -->
<div class="bg-card-dark rounded-xl border border-border-dark p-4">
  <h3 class="text-xl font-bold text-text-primary-dark">Title</h3>
  <p class="text-sm text-text-secondary-dark">Summary</p>
</div>

<!-- Responsive breakpoints: sm: md: lg: xl: -->
<div class="flex flex-col lg:flex-row gap-8">
  <!-- Mobile: column, Desktop: row -->
</div>
```

## Recent Changes

### Feature 1-global-news-brief (2025-12-15)
- **Added**: Perplexity API integration for news fetching (sonar model)
- **Added**: JSON data model with Bulletin, Article, Source, Citation entities
- **Added**: 6 GitHub Actions workflows for scheduled fetching (USA/India/World × morning/evening)
- **Added**: Frontend structure with vanilla JS, Tailwind CSS, dark/light themes
- **Added**: 7-day data retention policy with cleanup workflow
- **Deferred**: Toon format (Python decode support missing), Hindi/Telugu language support

<!-- MANUAL ADDITIONS START -->

<!-- Add custom project notes, conventions, or reminders here -->
<!-- These will be preserved when agent context is regenerated -->

<!-- MANUAL ADDITIONS END -->

## Key Conventions

### File Naming
- Bulletins: `data/{region}/{YYYY-MM-DD}-{period}.json`
- Regions: `usa`, `india`, `world`
- Periods: `morning`, `evening`

### JSON Schema Validation
- All bulletins must validate against Pydantic models in `backend/src/models/`
- Frontend validates region enum, period enum, article count (5-10)

### API Rate Limits
- Perplexity API: 50 RPM (Tier 0 free)
- Cost: ~$0.011 per bulletin = ~$2/month for all 6 workflows

### Performance Budgets
- Page load: <3 seconds on 3G
- Lighthouse score: >90
- JSON file size: <100 KB per bulletin
- Total page weight: <500 KB

### Timezone Handling
- All timestamps in UTC (ISO 8601 with Z suffix)
- GitHub Actions cron runs in UTC
- Frontend displays local time based on bulletin period

### Error Handling
- Retry with exponential backoff (1s, 2s, 4s)
- Log errors with structured format
- Create GitHub issues on 2 consecutive failures
- Continue on error (don't fail entire workflow)

### Data Retention
- Keep exactly 7 days of bulletins
- Cleanup runs daily at midnight UTC
- Delete files older than 7 days (by date, not generated_at)

# NRI News Brief

**AI-powered regional news aggregation platform with automated twice-daily bulletins**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-89%25-brightgreen.svg)](backend/tests/)

## 📋 Overview

NRI News Brief delivers curated news summaries for USA, India, and World regions, refreshed every morning (7 AM) and evening (9 PM) local time. Each bulletin contains 5-10 top stories with AI-generated summaries, source citations, and category tagging.

**Live Demo**: [GitHub Pages](https://yourusername.github.io/us_ind_world_news/) _(configure after deployment)_

### Key Features

- ✅ **Regional Coverage**: USA (EST), India (IST), World (UTC)
- ✅ **Twice-Daily Updates**: Automated via GitHub Actions at 7 AM & 9 PM
- ✅ **AI Summaries**: Perplexity API (sonar model) with citation tracking
- ✅ **Responsive Design**: Mobile (320px), Tablet (768px), Desktop (1440px+)
- ✅ **Dark Mode**: System preference detection + manual toggle
- ✅ **7-Day History**: Automatic cleanup of bulletins older than 7 days
- ✅ **Zero Build Step**: Vanilla JavaScript + Tailwind CSS CDN

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+ (for Playwright tests)
- Git
- Perplexity API key ([Get one here](https://docs.perplexity.ai/))

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/us_ind_world_news.git
cd us_ind_world_news

# 2. Set up Python environment
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your PERPLEXITY_API_KEY

# 4. Run backend tests
pytest -v --cov=src --cov-report=html

# 5. Start frontend
cd ../frontend
python3 -m http.server 8000
# Open http://localhost:8000
```

### Fetch Sample Bulletin

```bash
cd backend
python scripts/fetch_news.py --region usa --period morning
# Output: data/usa/2025-12-15-morning.json

# Test cleanup script
python scripts/cleanup_old_data.py --dry-run
```

## 📁 Project Structure

```
us_ind_world_news/
├── backend/
│   ├── src/
│   │   ├── fetchers/          # Perplexity API client, JSON formatter
│   │   ├── models/            # Pydantic models (Bulletin, Article, etc.)
│   │   └── utils/             # Retry logic, logger
│   ├── scripts/
│   │   ├── fetch_news.py      # CLI for news fetching
│   │   └── cleanup_old_data.py # 7-day retention enforcement
│   ├── tests/                 # 66 pytest tests (89% coverage)
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Main page (semantic HTML5)
│   ├── css/styles.css         # Custom styles + dark mode
│   └── js/
│       ├── app.js             # Main application controller
│       ├── theme-manager.js   # Dark/light mode toggle
│       ├── bulletin-loader.js # Async bulletin fetching
│       └── date-navigator.js  # 7-day history navigation
├── data/
│   ├── usa/                   # USA bulletins (YYYY-MM-DD-period.json)
│   ├── india/                 # India bulletins
│   ├── world/                 # World bulletins
│   └── index.json             # Bulletin metadata index
├── .github/workflows/
│   ├── fetch-*-morning.yml    # 6 automated workflows (3 regions × 2 periods)
│   ├── fetch-*-evening.yml
│   ├── cleanup-old-data.yml   # Daily cleanup at midnight UTC
│   └── deploy-pages.yml       # GitHub Pages deployment
└── specs/1-global-news-brief/ # Feature specifications
```

## 🤖 Automated Workflows

### Scheduled Bulletins

| Region | Morning (7 AM Local) | Evening (9 PM Local) | Cron Schedule |
|--------|---------------------|---------------------|---------------|
| **USA** (EST) | 11:55 AM UTC | 1:55 AM UTC | `55 11 * * *` / `55 1 * * *` |
| **India** (IST) | 1:25 AM UTC | 3:25 PM UTC | `25 1 * * *` / `25 15 * * *` |
| **World** (UTC) | 6:55 AM UTC | 8:55 PM UTC | `55 6 * * *` / `55 20 * * *` |

### Workflow Configuration

1. **Add Perplexity API Key to GitHub Secrets**:
   - Go to: `Settings → Secrets and variables → Actions`
   - Click: `New repository secret`
   - Name: `PERPLEXITY_API_KEY`
   - Secret: `<your_api_key_here>`

2. **Enable GitHub Actions**:
   - Go to: `Actions` tab
   - Click: `I understand my workflows, go ahead and enable them`

3. **Test Manual Trigger**:
   - Actions → `Fetch USA Morning Bulletin` → `Run workflow`
   - Check: `data/usa/` for new JSON file after ~30 seconds

### Workflow Features

- ✅ Python 3.11 with pip caching for fast execution
- ✅ Atomic file writes (temp → rename pattern)
- ✅ Automatic git commits with article counts
- ✅ Failure notifications via GitHub Actions
- ✅ Manual trigger support via `workflow_dispatch`

## 🧪 Testing

### Backend Tests (pytest)

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_perplexity_client.py -v

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Coverage**: 66/66 tests passing (100%), 89% code coverage

### Frontend Tests (Playwright)

```bash
cd frontend

# Install Playwright (first time only)
npm install
npx playwright install

# Run all E2E tests
npx playwright test

# Run in headed mode (watch browser)
npx playwright test --headed

# Run specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox

# Generate test report
npx playwright show-report
```

## 📊 Data Model

### Bulletin Structure

```json
{
  "bulletin": {
    "region": "usa",
    "period": "morning",
    "date": "2025-12-15",
    "generated_at": "2025-12-15T12:00:00Z",
    "article_count": 8,
    "articles": [
      {
        "title": "Article Title (max 120 chars)",
        "summary": "40-500 char AI-generated summary with key facts",
        "category": "POLITICS|ECONOMY|TECHNOLOGY|HEALTH|SPORTS|WEATHER|BUSINESS|ENTERTAINMENT|OTHER",
        "source": {
          "name": "Reuters",
          "url": "https://...",
          "published_at": "2025-12-15T11:30:00Z"
        },
        "citations": [
          {
            "url": "https://official-source.com",
            "title": "Citation title",
            "source": "Official Source"
          }
        ]
      }
    ],
    "metadata": {
      "api_version": "1.0",
      "prompt_tokens": 850,
      "completion_tokens": 1200,
      "total_tokens": 2050,
      "model": "sonar",
      "temperature": 0.3,
      "search_recency_filter": "day"
    }
  }
}
```

**Validation**: All fields validated via Pydantic models with custom validators for URL format, enum values, and string lengths.

## 🎨 Frontend Architecture

### Tech Stack

- **HTML5**: Semantic markup with accessibility (ARIA labels, focus management)
- **Tailwind CSS**: Utility-first CSS via CDN (no build step)
- **Vanilla JavaScript**: ES6+ modules (no frameworks)
- **DayJS**: Lightweight date manipulation (via CDN)
- **Google Material Symbols**: Icon library (via CDN)

### Components

- **ThemeManager** (`theme-manager.js`): Dark/light mode with localStorage persistence
- **BulletinLoader** (`bulletin-loader.js`): Async fetch with caching and validation
- **DateNavigator** (`date-navigator.js`): 7-day history navigation
- **NewsApp** (`app.js`): Main controller with card rendering and error handling

### Responsive Breakpoints

- **Mobile** (320px-767px): 1-column grid, vertical stack
- **Tablet** (768px-1439px): 2-column grid, 16px gap
- **Desktop** (1440px+): 3-column grid, 24px gap

## 🔧 Configuration

### Backend Configuration

**Environment Variables** (`.env`):

```bash
PERPLEXITY_API_KEY=your_api_key_here
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
DATA_DIR=../data  # Relative to backend/ directory
```

**Perplexity API Settings** (`src/fetchers/perplexity_client.py`):

- Model: `sonar`
- Temperature: `0.3` (low randomness for factual consistency)
- Max tokens: `1000`
- Search recency: `day` (last 24 hours)
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)

### Frontend Configuration

**Tailwind Config** (inline in `index.html`):

```javascript
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'card-light': '#ffffff',
        'card-dark': '#1e293b',
        // ... see index.html for full config
      }
    }
  }
}
```

## 📦 Deployment

### GitHub Pages (Recommended)

1. **Push code to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/us_ind_world_news.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to: `Settings → Pages`
   - Source: `GitHub Actions`
   - Deploy workflow: `.github/workflows/deploy-pages.yml`

3. **Configure Perplexity API Key** (see Workflow Configuration above)

4. **Access site**: `https://yourusername.github.io/us_ind_world_news/`

### Manual Deployment

```bash
# Build deployment package
mkdir -p dist
cp -r frontend/* dist/
cp -r data dist/

# Deploy to web server
rsync -avz dist/ user@server:/var/www/html/news/
```

## 🔒 Security

- ✅ **API Key Protection**: Stored in GitHub Secrets (never committed)
- ✅ **XSS Prevention**: HTML escaping in `app.js` before rendering
- ✅ **CORS**: All data fetched from same origin
- ✅ **HTTPS**: Enforced on GitHub Pages
- ✅ **Input Validation**: Pydantic models validate all API responses
- ✅ **Rate Limiting**: Perplexity API rate limits respected (50 RPM free tier)

## 💰 Cost Estimate

### Perplexity API (sonar model)

- **Cost per bulletin**: ~$0.011 ($5 per 1M tokens @ 2,000 tokens/bulletin)
- **Daily bulletins**: 6 (3 regions × 2 periods)
- **Monthly cost**: ~$2.00 (6 bulletins/day × 30 days × $0.011)

### GitHub Actions

- **Free tier**: 2,000 minutes/month (Linux runners)
- **Estimated usage**: ~180 minutes/month (6 workflows × 1 min × 30 days)
- **Cost**: $0 (well within free tier)

### GitHub Pages

- **Free tier**: Unlimited for public repos
- **Cost**: $0

**Total Monthly Cost**: ~$2.00

## 📝 Development Workflow

### Adding a New Region

1. Create prompt template: `specs/1-global-news-brief/contracts/perplexity-prompt-{region}-morning.md`
2. Add region to enum: `backend/src/models/bulletin.py` (`RegionEnum`)
3. Create workflows: `.github/workflows/fetch-{region}-morning.yml` and `fetch-{region}-evening.yml`
4. Update frontend: Add region button in `frontend/index.html`
5. Create data directory: `mkdir data/{region}`
6. Test: `python backend/scripts/fetch_news.py --region {region} --period morning`

### Adding a New Category

1. Add to enum: `backend/src/models/article.py` (`CategoryEnum`)
2. Add CSS styles: `frontend/css/styles.css` (`.badge-{category}`)
3. Update prompt templates: Mention new category in `specs/1-global-news-brief/contracts/`
4. Test: Verify category appears in bulletins and renders correctly

## 🐛 Troubleshooting

### Frontend Issues

**Problem**: Bulletin not loading  
**Solution**: Check browser console for errors, verify `data/index.json` exists, ensure JSON files are in `data/{region}/`

**Problem**: Dark mode not working  
**Solution**: Clear localStorage (`localStorage.clear()`), check `<html class="dark">` in dev tools

### Backend Issues

**Problem**: `ModuleNotFoundError: No module named 'src'`  
**Solution**: Activate venv (`source venv/bin/activate`), reinstall dependencies (`pip install -r requirements.txt`)

**Problem**: Perplexity API rate limit errors  
**Solution**: Wait 60 seconds, reduce frequency in workflows, upgrade to paid tier

### Workflow Issues

**Problem**: Workflow fails with "PERPLEXITY_API_KEY not found"  
**Solution**: Add API key to GitHub Secrets (Settings → Secrets → Actions)

**Problem**: Git push fails in workflow  
**Solution**: Verify `permissions: contents: write` in workflow YAML, check branch protection rules

## 📚 Documentation

- **Feature Spec**: [`specs/1-global-news-brief/spec.md`](specs/1-global-news-brief/spec.md)
- **Implementation Plan**: [`specs/1-global-news-brief/plan.md`](specs/1-global-news-brief/plan.md)
- **Data Model**: [`specs/1-global-news-brief/data-model.md`](specs/1-global-news-brief/data-model.md)
- **API Contracts**: [`specs/1-global-news-brief/contracts/`](specs/1-global-news-brief/contracts/)
- **Quickstart Guide**: [`specs/1-global-news-brief/quickstart.md`](specs/1-global-news-brief/quickstart.md)

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest` and `npx playwright test`)
4. Commit changes (`git commit -m 'feat: add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

**Commit Convention**: Follow [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Perplexity AI**: Sonar model for news summarization with citations
- **Tailwind CSS**: Utility-first CSS framework
- **Playwright**: End-to-end testing framework
- **GitHub Actions**: CI/CD automation
- **GitHub Pages**: Free static site hosting

---

**Built with ❤️ by the NRI News Brief Team**

_Last Updated: 2025-12-15_

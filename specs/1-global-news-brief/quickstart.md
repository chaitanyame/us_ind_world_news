# Quickstart Guide: Global News Brief

**Feature**: 1-global-news-brief  
**Last Updated**: 2025-12-15  
**Purpose**: Developer onboarding and local development setup

This guide will help you set up the Global News Brief platform for local development and testing.

---

## Prerequisites

- **Python**: 3.11 or higher
- **Git**: For version control
- **GitHub Account**: For Actions and Pages
- **Perplexity API Key**: [Get one here](https://www.perplexity.ai/settings/api)
- **Code Editor**: VS Code recommended

---

## 1. Clone the Repository

```bash
git clone https://github.com/chaitanyame/us_ind_world_news.git
cd us_ind_world_news
git checkout 1-global-news-brief
```

---

## 2. Backend Setup (Python)

### Install Python Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Create `requirements.txt`

```txt
openai>=1.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# backend/.env
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Security Note**: Never commit `.env` to git. Add to `.gitignore`:
```bash
echo "backend/.env" >> .gitignore
echo "backend/venv/" >> .gitignore
```

---

## 3. Test Perplexity API Connection

Create a test script to verify API access:

```python
# backend/test_perplexity.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ["PERPLEXITY_API_KEY"],
    base_url="https://api.perplexity.ai"
)

response = client.chat.completions.create(
    model="sonar",
    messages=[
        {"role": "system", "content": "You are a concise news curator."},
        {"role": "user", "content": "What are the top 3 breaking news stories in the USA today?"}
    ]
)

print(response.choices[0].message.content)
print(f"\nTokens used: {response.usage.total_tokens}")
```

Run the test:
```bash
cd backend
python test_perplexity.py
```

Expected output: A brief list of 3 news stories.

---

## 4. Frontend Setup (Static Site)

### Open in Browser

The frontend is a static site - no build step required for basic development.

```bash
# From repository root
cd frontend
python3 -m http.server 8000
```

Open browser to `http://localhost:8000`

**Note**: You'll see a blank page initially because no data files exist yet. Proceed to step 5 to generate sample data.

---

## 5. Generate Sample Data

### Manual Data Generation

Create a sample bulletin manually:

```bash
cd backend
python scripts/fetch_news.py --region usa --period morning
```

This will:
1. Call Perplexity API with USA morning prompt
2. Parse response into JSON
3. Save to `data/usa/YYYY-MM-DD-morning.json`
4. Generate `data/index.json` listing all bulletins

### Verify Data File

```bash
cat data/usa/$(date +%Y-%m-%d)-morning.json | head -50
```

You should see a JSON structure with `bulletin`, `articles`, and `metadata`.

---

## 6. View in Frontend

Refresh `http://localhost:8000` in your browser. You should now see:
- The USA morning bulletin displayed
- Article cards with titles, summaries, categories
- Citation links to original sources

### Test Regional Switching

Click the regional filters (USA / India / World) to verify filtering logic. Initially, only USA will show data.

---

## 7. GitHub Actions Setup (Optional for Local Dev)

For local testing of workflows without triggering GitHub Actions:

### Install Act (GitHub Actions Local Runner)

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (via Chocolatey)
choco install act-cli
```

### Run Workflow Locally

```bash
act -j fetch --secret PERPLEXITY_API_KEY=pplx-xxxxx
```

This simulates the GitHub Actions environment locally.

---

## 8. Self-Hosted Runner Setup

For production deployment, configure a self-hosted runner:

### Register Runner

1. Go to `Settings` > `Actions` > `Runners` > `New self-hosted runner`
2. Follow instructions to download and configure runner
3. Choose `Linux` and `x64` architecture

### Configure Runner

```bash
# Download runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf actions-runner-linux-x64-2.311.0.tar.gz

# Configure runner
./config.sh --url https://github.com/chaitanyame/us_ind_world_news --token YOUR_TOKEN

# Install as service
sudo ./svc.sh install
sudo ./svc.sh start
```

### Add Secrets

1. Go to `Settings` > `Secrets and variables` > `Actions`
2. Add `PERPLEXITY_API_KEY` secret

---

## 9. Project Structure

```
us_ind_world_news/
├── backend/
│   ├── src/
│   │   ├── fetchers/
│   │   │   ├── perplexity_client.py  # Perplexity API wrapper
│   │   │   └── toon_formatter.py     # JSON formatting (toon deferred)
│   │   ├── models/
│   │   │   ├── bulletin.py           # Bulletin data model
│   │   │   └── article.py            # Article data model
│   │   └── utils/
│   │       ├── retry_logic.py        # Exponential backoff
│   │       └── logger.py             # Structured logging
│   ├── scripts/
│   │   ├── fetch_news.py             # Main CLI script
│   │   └── cleanup_old_data.py       # 7-day retention
│   ├── tests/
│   │   └── test_*.py
│   ├── requirements.txt
│   └── .env                          # Local only (not in git)
├── frontend/
│   ├── index.html                    # Main page
│   ├── css/
│   │   └── styles.css                # Custom styles (minimal)
│   ├── js/
│   │   ├── app.js                    # Main app logic
│   │   ├── theme-manager.js          # Dark/light mode
│   │   ├── bulletin-loader.js        # Fetch JSON
│   │   └── date-navigator.js         # Sidebar calendar
│   └── assets/
├── data/                             # Generated by workflows
│   ├── usa/
│   ├── india/
│   ├── world/
│   └── index.json
├── .github/
│   └── workflows/
│       ├── fetch-usa-morning.yml
│       ├── fetch-usa-evening.yml
│       ├── fetch-india-morning.yml
│       ├── fetch-india-evening.yml
│       ├── fetch-world-morning.yml
│       ├── fetch-world-evening.yml
│       ├── cleanup-old-data.yml
│       └── deploy-pages.yml
└── specs/
    └── 1-global-news-brief/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        ├── quickstart.md (this file)
        └── contracts/
```

---

## 10. Development Workflow

### Daily Development Loop

1. **Pull latest changes**:
   ```bash
   git pull origin 1-global-news-brief
   ```

2. **Activate Python environment**:
   ```bash
   cd backend && source venv/bin/activate
   ```

3. **Make changes** to backend scripts or frontend code

4. **Test locally**:
   ```bash
   # Test backend script
   python scripts/fetch_news.py --region usa --period morning
   
   # Test frontend
   cd ../frontend && python3 -m http.server 8000
   ```

5. **Run tests** (once written):
   ```bash
   cd backend && pytest tests/
   ```

6. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   git push origin 1-global-news-brief
   ```

### Testing GitHub Actions

**Option 1: Manual Trigger**
```yaml
# Add to workflow file:
on:
  workflow_dispatch:  # Allows manual trigger
```

Then go to `Actions` > Select workflow > `Run workflow`

**Option 2: Act (Local)**
```bash
act -j fetch --secret PERPLEXITY_API_KEY=pplx-xxxxx
```

---

## 11. Troubleshooting

### Issue: `PERPLEXITY_API_KEY not found`

**Solution**: Ensure `.env` file exists in `backend/` and contains the API key:
```bash
cat backend/.env
# Should show: PERPLEXITY_API_KEY=pplx-xxxxx
```

### Issue: `ModuleNotFoundError: No module named 'openai'`

**Solution**: Activate virtual environment and install dependencies:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend shows blank page

**Solution**: Generate sample data first:
```bash
cd backend
python scripts/fetch_news.py --region usa --period morning
```

### Issue: GitHub Actions workflow fails with 401 error

**Solution**: Check that `PERPLEXITY_API_KEY` secret is correctly set in GitHub repo settings:
1. Go to `Settings` > `Secrets and variables` > `Actions`
2. Verify `PERPLEXITY_API_KEY` exists and is not expired

### Issue: Self-hosted runner not picking up jobs

**Solution**: 
1. Check runner status: `sudo ./svc.sh status`
2. View runner logs: `tail -f _diag/Runner_*.log`
3. Ensure runner has `self-hosted` label in workflow `runs-on`

---

## 12. Next Steps

Once local development is working:

1. **Run all 6 workflows** manually to generate sample data for all regions
2. **Test 7-day retention** by running cleanup script
3. **Deploy to GitHub Pages** using deploy workflow
4. **Monitor costs** in Perplexity dashboard (should be ~$2/month)
5. **Iterate on frontend design** using provided HTML templates
6. **Add tests** for backend Python code
7. **Configure alerts** for workflow failures

---

## 13. Helpful Commands

```bash
# Check Python version
python3 --version

# List all bulletins
ls -lh data/*/

# View index.json
cat data/index.json | jq .

# Test a single workflow locally
act -j fetch-usa-morning --secret PERPLEXITY_API_KEY=xxx

# Tail GitHub runner logs
tail -f ~/actions-runner/_diag/Runner_*.log

# Clean all generated data
rm -rf data/*/

# Run backend tests
cd backend && pytest -v

# Check Perplexity API usage
# (Visit https://www.perplexity.ai/settings/api)
```

---

## 14. Resources

- **Perplexity API Docs**: https://docs.perplexity.ai/
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **GitHub Pages Docs**: https://docs.github.com/en/pages
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Pydantic Docs**: https://docs.pydantic.dev/

---

## 15. Cost Monitoring

**Expected Monthly Costs**:
- Perplexity API: ~$2.00/month (6 requests/day × 30 days × $0.011/request)
- GitHub Actions: $0.00 (self-hosted runner)
- GitHub Pages: $0.00 (free tier)
- **Total**: ~$2.00/month

**How to Monitor**:
1. Perplexity dashboard: https://www.perplexity.ai/settings/api
2. Check `metadata.llm_usage` in each bulletin JSON
3. Sum `total_tokens` across all bulletins

---

## Support

For issues or questions:
1. Check [spec.md](spec.md) for requirements
2. Review [research.md](research.md) for architectural decisions
3. Consult [data-model.md](data-model.md) for JSON schema
4. See [plan.md](plan.md) for implementation roadmap

Happy coding! 🚀

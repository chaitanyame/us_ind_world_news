# Deployment Guide: NRI News Brief Platform

**Status**: ✅ Code pushed to GitHub  
**Branch**: `1-global-news-brief`  
**Repository**: `chaitanyame/us_ind_world_news`

## 📋 Deployment Checklist

### ✅ Phase 1: Code Deployment (COMPLETE)

- [x] All code committed and tested locally
- [x] Workflows configured for self-hosted runners
- [x] Branch pushed to GitHub: `1-global-news-brief`
- [x] Sample bulletins created for testing

### 🔄 Phase 2: Merge to Main (REQUIRED)

**Option A: Create Pull Request (Recommended)**

1. Go to: https://github.com/chaitanyame/us_ind_world_news/pulls
2. Click: **"New pull request"**
3. Base: `main` ← Compare: `1-global-news-brief`
4. Title: `feat: implement NRI News Brief MVP (Phase 1-4)`
5. Description:
   ```markdown
   ## Summary
   Complete implementation of NRI News Brief platform with automated news fetching.
   
   ## Features Delivered
   - ✅ Backend: Python 3.11 + Pydantic models + Perplexity API integration
   - ✅ Frontend: Responsive UI (HTML5 + Tailwind CSS + Vanilla JS)
   - ✅ Automation: 6 scheduled workflows + cleanup + GitHub Pages
   - ✅ Testing: 66/66 pytest tests passing (89% coverage)
   - ✅ Documentation: Comprehensive README + API contracts
   
   ## Breaking Changes
   None (new feature)
   
   ## Testing
   - Backend: `cd backend && pytest -v`
   - Frontend: Local server tested with sample data
   - Workflows: Ready for self-hosted runner deployment
   
   ## Deployment Requirements
   - Configure PERPLEXITY_API_KEY in repository secrets
   - Set up self-hosted GitHub Actions runner
   - Enable GitHub Pages from Actions
   ```
6. Click: **"Create pull request"**
7. Review changes
8. Click: **"Merge pull request"** → **"Confirm merge"**

**Option B: Direct Merge (Fast Track)**

```bash
cd /workspaces/us_ind_world_news
git checkout main
git merge 1-global-news-brief
git push origin main
```

### 🔧 Phase 3: Configure GitHub Secrets

**Steps**:

1. Go to: https://github.com/chaitanyame/us_ind_world_news/settings/secrets/actions
2. Click: **"New repository secret"**
3. Name: `PERPLEXITY_API_KEY`
4. Secret: `<your_perplexity_api_key_here>`
5. Click: **"Add secret"**

**Get Perplexity API Key**:
- Sign up: https://www.perplexity.ai/
- Navigate to: Account Settings → API
- Create new API key
- Copy key (starts with `pplx-...`)

**Cost Estimate**: ~$2/month (6 bulletins/day × 30 days × $0.011/bulletin)

### 🏃 Phase 4: Set Up Self-Hosted GitHub Actions Runner

**Option A: Alpine Linux Docker (Recommended)**

```bash
# 1. Pull official GitHub Actions runner image
docker run -d \
  --name github-runner \
  --restart unless-stopped \
  -e REPO_URL="https://github.com/chaitanyame/us_ind_world_news" \
  -e RUNNER_TOKEN="<YOUR_RUNNER_TOKEN>" \
  -e RUNNER_NAME="alpine-news-fetcher" \
  -e RUNNER_WORKDIR="/home/runner/work" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  myoung34/github-runner:latest

# 2. Verify runner status
docker logs github-runner
```

**Get Runner Token**:
1. Go to: https://github.com/chaitanyame/us_ind_world_news/settings/actions/runners/new
2. Select: **"Linux"**
3. Copy the token from the `./config.sh` command (looks like `A...`)
4. Use in Docker command above

**Option B: Manual Setup (Linux Server)**

```bash
# 1. Download GitHub Actions runner
mkdir actions-runner && cd actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# 2. Configure runner
./config.sh --url https://github.com/chaitanyame/us_ind_world_news --token <YOUR_RUNNER_TOKEN>

# 3. Install as service
sudo ./svc.sh install
sudo ./svc.sh start

# 4. Verify status
sudo ./svc.sh status
```

**Runner Requirements**:
- Python 3.11+ (`python3 --version`)
- Git 2.x+ (`git --version`)
- 2GB RAM minimum
- 10GB disk space
- Outbound HTTPS access (port 443)

**Environment Setup**:

```bash
# Install Python dependencies on runner
cd /home/runner/work/us_ind_world_news/us_ind_world_news/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure PERPLEXITY_API_KEY in runner environment
echo 'export PERPLEXITY_API_KEY="pplx-..."' >> ~/.bashrc
source ~/.bashrc
```

### 🔄 Phase 5: Enable GitHub Actions Workflows

**Steps**:

1. Go to: https://github.com/chaitanyame/us_ind_world_news/actions
2. If prompted: Click **"I understand my workflows, go ahead and enable them"**
3. Verify workflows are listed:
   - Fetch USA Morning Bulletin
   - Fetch USA Evening Bulletin
   - Fetch India Morning Bulletin
   - Fetch India Evening Bulletin
   - Fetch World Morning Bulletin
   - Fetch World Evening Bulletin
   - Cleanup Old Data
   - Deploy to GitHub Pages

**Test Manual Trigger**:

1. Click: **"Fetch USA Morning Bulletin"**
2. Click: **"Run workflow"** dropdown
3. Branch: `main`
4. Date (optional): Leave blank for today
5. Click: **"Run workflow"** button
6. Wait ~30 seconds
7. Check run status (should be green ✅)
8. Verify file created: https://github.com/chaitanyame/us_ind_world_news/blob/main/data/usa/2025-12-15-morning.json

### 🌐 Phase 6: Enable GitHub Pages

**Steps**:

1. Go to: https://github.com/chaitanyame/us_ind_world_news/settings/pages
2. Source: **"GitHub Actions"**
3. Click: **"Save"**
4. Wait for deployment (~2 minutes)
5. Access site: https://chaitanyame.github.io/us_ind_world_news/

**Verify Deployment**:
- Page loads without errors
- USA bulletin displays with sample data
- Region filter buttons work (USA/India/World)
- Dark mode toggle functions
- Mobile responsive (test on phone or resize browser)

### ✅ Phase 7: Verify End-to-End Workflow

**Test Automated Workflow**:

1. Wait for next scheduled run (check cron schedules in README.md)
2. Go to: https://github.com/chaitanyame/us_ind_world_news/actions
3. Wait for workflow to complete
4. Check commits: New bulletin file should be committed
5. Verify GitHub Pages updates: https://chaitanyame.github.io/us_ind_world_news/
6. Confirm bulletin displays correctly

**Scheduled Run Times**:

| Region | Morning | Evening | Next Run (Your Time) |
|--------|---------|---------|---------------------|
| USA | 7 AM EST | 9 PM EST | Check timezone converter |
| India | 7 AM IST | 9 PM IST | Check timezone converter |
| World | 7 AM UTC | 9 PM UTC | Check timezone converter |

**Cron Schedules** (UTC):
- USA Morning: `55 11 * * *` (11:55 AM UTC)
- USA Evening: `55 1 * * *` (1:55 AM UTC)
- India Morning: `25 1 * * *` (1:25 AM UTC)
- India Evening: `25 15 * * *` (3:25 PM UTC)
- World Morning: `55 6 * * *` (6:55 AM UTC)
- World Evening: `55 20 * * *` (8:55 PM UTC)
- Cleanup: `0 0 * * *` (Midnight UTC daily)

## 🐛 Troubleshooting

### Issue: Workflow fails with "No runner available"

**Solution**:
```bash
# Check runner status
cd actions-runner
./run.sh

# Or restart service
sudo ./svc.sh restart
sudo ./svc.sh status
```

### Issue: "PERPLEXITY_API_KEY not found"

**Solution**:
1. Verify secret exists: https://github.com/chaitanyame/us_ind_world_news/settings/secrets/actions
2. Ensure name is exactly `PERPLEXITY_API_KEY` (case-sensitive)
3. Re-run workflow after adding secret

### Issue: Git push fails in workflow

**Solution**:
```bash
# On self-hosted runner, configure git
git config --global user.email "actions@github.com"
git config --global user.name "GitHub Actions Bot"

# Ensure runner has write access to repo
# Generate personal access token with repo permissions:
# https://github.com/settings/tokens/new
```

### Issue: Python module import errors

**Solution**:
```bash
# SSH into runner machine
cd /home/runner/work/us_ind_world_news/us_ind_world_news/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Verify installations
python -c "import openai, pydantic; print('OK')"
```

### Issue: GitHub Pages not updating

**Solution**:
1. Check workflow run: https://github.com/chaitanyame/us_ind_world_news/actions/workflows/deploy-pages.yml
2. Verify permissions: Settings → Actions → General → Workflow permissions → "Read and write permissions"
3. Hard refresh browser: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
4. Clear browser cache

## 📊 Monitoring

**Daily Checks**:

1. **Workflow Success Rate**: https://github.com/chaitanyame/us_ind_world_news/actions
   - Target: 100% success (green checkmarks)
   - If failures: Check workflow logs, verify API key, check runner status

2. **Bulletin Quality**:
   - Visit: https://chaitanyame.github.io/us_ind_world_news/
   - Verify: 5-10 articles per bulletin
   - Check: Citations present for each article
   - Test: All category badges display correctly

3. **API Costs**: https://www.perplexity.ai/settings/api
   - Monitor: Token usage (should be ~2,000 tokens/bulletin)
   - Verify: Monthly spend stays below $3
   - Alert: If usage spikes unexpectedly

4. **Runner Health**:
   ```bash
   # SSH to runner machine
   sudo systemctl status actions.runner.*
   docker ps | grep github-runner
   ```

**Weekly Checks**:

- Review error logs: `cd backend && tail -100 logs/fetch_news.log`
- Test manual workflow trigger
- Verify 7-day retention: Only last 7 days of bulletins in `data/`

## 🚀 Post-Deployment Tasks

### Optional Enhancements

1. **Custom Domain** (GitHub Pages):
   - Go to: Settings → Pages → Custom domain
   - Add CNAME record in DNS: `news.yourdomain.com` → `chaitanyame.github.io`
   - Enable HTTPS

2. **Email Notifications** (Workflow Failures):
   - Add notification step to workflows
   - Use GitHub Actions marketplace: `dawidd6/action-send-mail@v3`

3. **Analytics** (User Tracking):
   - Add Google Analytics or Plausible to `frontend/index.html`
   - Track: Page views, region preferences, bulletin engagement

4. **Playwright E2E Tests** (Phase 5):
   ```bash
   cd frontend
   npm install
   npx playwright test
   ```

5. **Performance Monitoring**:
   - Run Lighthouse: Chrome DevTools → Lighthouse
   - Target: >90 score for Performance, Accessibility, Best Practices, SEO

## 📞 Support

**Documentation**:
- README: https://github.com/chaitanyame/us_ind_world_news/blob/main/README.md
- Feature Spec: `specs/1-global-news-brief/spec.md`
- API Contracts: `specs/1-global-news-brief/contracts/`

**Issues**:
- Create issue: https://github.com/chaitanyame/us_ind_world_news/issues/new
- Label: `bug`, `deployment`, or `enhancement`

---

**Deployment Prepared by**: GitHub Copilot  
**Date**: 2025-12-15  
**Version**: 1.0.0 (MVP)

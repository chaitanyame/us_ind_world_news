# Research Document: Global News Brief

**Feature**: 1-global-news-brief  
**Created**: 2025-12-15  
**Purpose**: Resolve Phase 0 NEEDS CLARIFICATION items from implementation plan

This document consolidates research findings from Phase 0 to inform Phase 1 design decisions.

---

## 1. Perplexity API Integration Pattern

### Decision: Use Sonar Model with Structured Prompts

**Selected Approach**: OpenAI client library with `base_url="https://api.perplexity.ai"` override

### Prompt Engineering for Categorized News

**Best Practices**:
- Use specific, search-friendly prompts (e.g., "What are the top 10 breaking news stories in USA today?" not "Tell me about USA news")
- NEVER use few-shot prompting (confuses the search component)
- NEVER request URLs in prompts (they're auto-returned in `search_results` field)
- Use explicit instructions about handling unavailable information
- For structured output, use JSON Schema with `response_format` parameter

**Recommended Prompt Template**:
```
You are a news curator. Search the web and identify the top 10 breaking news stories in {REGION} for {TIME_PERIOD}. 
For each story, provide:
- Title (max 12 words)
- Summary (2-3 sentences, 50 words max)
- Category (one of: politics, technology, business, sports, health, environment, science, world)

Focus on verified sources from major news outlets. If fewer than 10 stories are found, return what's available.
```

**Structured Output** (10-30s first-request delay due to schema processing):
```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "news_bulletin",
        "schema": {
            "type": "object",
            "properties": {
                "articles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                            "category": {"type": "string", "enum": ["politics", "technology", "business", "sports", "health", "environment", "science", "world"]}
                        },
                        "required": ["title", "summary", "category"]
                    }
                }
            },
            "required": ["articles"]
        }
    }
}
```

### Sonar Model Configuration

**Recommended Parameters**:
```python
response = client.chat.completions.create(
    model="sonar",  # NOT sonar-pro (2.5x more expensive)
    temperature=0.2,  # Low for factual consistency (range: 0.2-0.4)
    max_tokens=1000,  # 600-1000 sufficient for 10 articles
    search_recency_filter="day",  # CRITICAL: Only today's news
    search_context_size="low",  # Cost optimization (vs "medium"/"high")
    # search_domain_filter=["bbc.com", "cnn.com", "reuters.com"],  # Optional: trusted sources only
    messages=[...]
)
```

**Model Comparison**:
| Model | Cost | Speed | Citations | Use Case |
|-------|------|-------|-----------|----------|
| `sonar` | $5/M tokens | Fast | Yes | Daily news (RECOMMENDED) |
| `sonar-pro` | $12.5/M tokens | Slower | Yes | Research, long-form |

### Rate Limits & Pricing

**Cost Estimation** (6 requests/day):
- Request fee: $0.005 per request × 6 = $0.03/day
- Token cost: ~1000 tokens/request × 6 × $0.005/1K = $0.03/day
- **Total**: ~$0.06/day = **$1.85/month = $22.15/year**

**Rate Limits** (Tier 0 - free):
- 50 RPM (requests per minute) - sufficient for 6/day
- Recommendation: Purchase $50 credits to unlock Tier 1 (higher limits)

**Budget Justification**: Cost is negligible compared to value; self-hosted runners save $40+/month in GitHub Actions minutes.

### Integration Pattern with Retry Logic

**Error Handling**:
```python
import time
from openai import OpenAI, RateLimitError, AuthenticationError

def fetch_news_with_retry(region, period, max_retries=3):
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai"
    )
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="sonar",
                temperature=0.2,
                max_tokens=1000,
                search_recency_filter="day",
                messages=[
                    {"role": "system", "content": "You are a concise news curator."},
                    {"role": "user", "content": f"Search the web and identify the top 10 breaking news stories in {region} today..."}
                ]
            )
            
            # Parse citations from search_results
            citations = []
            if hasattr(response, 'search_results') and response.search_results:
                for result in response.search_results:
                    citations.append({
                        "title": result.get("title"),
                        "url": result.get("url"),
                        "date": result.get("publishedDate"),
                        "snippet": result.get("snippet")
                    })
            
            return {
                "content": response.choices[0].message.content,
                "citations": citations,
                "model": response.model,
                "usage": response.usage
            }
            
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                time.sleep(wait_time)
                continue
            raise
        except AuthenticationError:
            # Fail fast on auth errors (no retry)
            raise
    
    raise Exception(f"Failed after {max_retries} retries")
```

**Citation Extraction**: Citations are in `response.search_results` (not in message content). Each includes `title`, `url`, `publishedDate`, `snippet`.

---

## 2. Toon Format Implementation

### Decision: Use Standard JSON for MVP, Defer Toon Format

**Selected Approach**: Standard JSON with `.json` extension

### Research Summary

**Toon Format Overview**:
- Token-Oriented Object Notation for LLM efficiency
- Combines YAML-like indentation with CSV-style tabular arrays
- Achieves 30-60% token reduction vs JSON (average 39.6%)
- Better LLM accuracy: 73.9% vs JSON's 69.7%

**Token Savings Analysis**:
| Data Type | Token Savings | Use Case Fit |
|-----------|---------------|--------------|
| Flat tabular | 40-60% | Excellent (news bulletins are tabular) |
| Nested objects | 20-30% | Good |
| Mixed | 30-40% | Good |

**Browser Compatibility**: ✅ **YES**
- JavaScript library: `@toon-format/toon` (stable, production-ready)
- Vanilla JS compatible via ES6 modules
- Fast parsing: up to 4.8x faster than JSON
- Streaming APIs for large datasets

**Critical Blocker**: ⚠️ **Python decode support missing**
- `toon-python` v0.1.2 can ENCODE toon files but **CANNOT DECODE**
- Backend scripts cannot parse toon files back to Python objects
- Major blocker for workflow that generates AND consumes toon files

### Recommendation: Start with JSON, Migrate Later

**Rationale**:
1. **Python Limitation**: Cannot decode toon in backend (workflow reads old files for deduplication)
2. **Small Scale**: 42 files × <100KB = minimal storage impact; token savings not critical
3. **Zero Risk**: JSON is universal, fully supported in Python and JavaScript
4. **Future Migration**: Easy to convert JSON → Toon if Python decode support arrives

**When to Reconsider Toon**:
- Python decode library becomes available
- File sizes exceed 50KB (compression needed)
- LLM integration planned (token costs matter)
- Token optimization becomes a measurable bottleneck

**Implementation**:
```python
# backend/src/utils/storage.py
import json
from pathlib import Path

def save_bulletin(region, date, period, data):
    """Save bulletin as standard JSON"""
    filename = f"data/{region}/{date}-{period}.json"
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_bulletin(region, date, period):
    """Load bulletin from JSON"""
    filename = f"data/{region}/{date}-{period}.json"
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)
```

```javascript
// frontend/js/bulletin-loader.js
async function loadBulletin(region, date, period) {
    const response = await fetch(`/data/${region}/${date}-${period}.json`);
    if (!response.ok) throw new Error(`Bulletin not found: ${region}/${date}-${period}`);
    return await response.json();
}
```

---

## 3. GitHub Actions Timezone Scheduling

### Decision: UTC Cron with Dual Schedules for DST

**Selected Approach**: UTC-based cron expressions with runtime DST detection for EST

### Cron Syntax for GitHub Actions

**Format**: `minute hour day month weekday` (POSIX cron, 5 fields)
- Timezone: **UTC only** (not configurable)
- Minimum interval: 5 minutes
- Operators: `*` (any), `,` (list), `-` (range), `/` (step)

**Example**:
```yaml
on:
  schedule:
    - cron: '30 14 * * *'  # Runs at 14:30 UTC every day
```

### Timezone Conversion Strategy

**Challenge**: GitHub Actions cron runs in UTC; need EST/IST/UTC schedules with DST handling.

**Timezone Offsets**:
| Timezone | Offset (Standard) | DST Offset | DST Dates |
|----------|-------------------|------------|-----------|
| EST | UTC-5 | UTC-4 (EDT) | Mid-March → Early Nov |
| IST | UTC+5:30 | No DST | N/A |
| UTC | UTC+0 | No DST | N/A |

**Conversion Table**:
| Local Time | Timezone | Standard UTC | DST UTC | Cron Expression |
|------------|----------|--------------|---------|-----------------|
| 7:00 AM | USA (EST) | 12:00 | 11:00 | `55 11 * * *` (buffer 5 min) |
| 9:00 PM | USA (EST) | 02:00 next day | 01:00 next day | `55 1 * * *` |
| 7:00 AM | India (IST) | 01:30 | N/A | `25 1 * * *` |
| 9:00 PM | India (IST) | 15:30 | N/A | `25 15 * * *` |
| 7:00 AM | World (UTC) | 07:00 | N/A | `55 6 * * *` |
| 9:00 PM | World (UTC) | 21:00 | N/A | `55 20 * * *` |

**DST Handling for EST**:
- **Option 1**: Dual cron schedules (one for EST, one for EDT) with runtime check
- **Option 2**: Single UTC schedule + Python datetime with `pytz` to detect DST
- **Recommendation**: Option 1 (simpler, no external library)

**Example Workflow** (USA Morning):
```yaml
name: Fetch USA Morning News
on:
  schedule:
    - cron: '55 11 * * *'  # EST (Nov-Mar): 7:00 AM EST = 12:00 UTC
    - cron: '55 10 * * *'  # EDT (Mar-Nov): 7:00 AM EDT = 11:00 UTC
  workflow_dispatch:  # Manual trigger for testing

jobs:
  fetch:
    runs-on: self-hosted
    steps:
      - name: Check if should run (DST handling)
        id: dst_check
        run: |
          # Determine if currently in DST
          current_month=$(date +%m)
          if [ $current_month -ge 3 ] && [ $current_month -le 10 ]; then
            echo "dst=true" >> $GITHUB_OUTPUT
          else
            echo "dst=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Fetch news
        if: |
          (github.event.schedule == '55 11 * * *' && steps.dst_check.outputs.dst == 'false') ||
          (github.event.schedule == '55 10 * * *' && steps.dst_check.outputs.dst == 'true')
        run: python backend/scripts/fetch_news.py --region usa --period morning
```

### Schedule Accuracy

**Expected Delays**:
- **Normal load**: 0-3 minutes delay (~95% of the time)
- **High load**: Up to 10 minutes delay (rare, during peak GitHub usage)
- **No SLA**: GitHub provides no guarantees on scheduled workflow triggers

**Best Practices**:
1. Schedule 5 minutes early to buffer delays (e.g., `55` instead of `0` for 7:00 AM target)
2. Use `workflow_dispatch` for manual testing
3. Implement idempotency (re-running should be safe)
4. Monitor with GitHub Actions logs + alerts

**Self-Hosted Runners**: Improve reliability but don't eliminate schedule trigger delays (trigger still originates from GitHub's infrastructure).

### Self-Hosted Runner Configuration

**Docker Setup** (Alpine Linux):
```dockerfile
FROM alpine:3.18

RUN apk add --no-cache \
    bash \
    curl \
    git \
    python3 \
    py3-pip \
    tar \
    && rm -rf /var/cache/apk/*

# Install GitHub Actions runner
WORKDIR /runner
RUN curl -o actions-runner-linux.tar.gz -L https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz \
    && tar xzf actions-runner-linux.tar.gz \
    && rm actions-runner-linux.tar.gz

# Install Python dependencies
COPY backend/requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Configure runner (run at container start)
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

**Secrets Management**:
- Store `PERPLEXITY_API_KEY` in GitHub Secrets (repo or org level)
- Pass to runner via environment variables
- Use Docker secrets for runner registration token

**Network Requirements**:
- Outbound HTTPS (443) to:
  - `github.com` (API access)
  - `api.github.com` (Actions API)
  - `*.actions.githubusercontent.com` (artifact storage)
  - `api.perplexity.ai` (Perplexity API)
- No inbound ports required

**Security**:
- Minimize token scope (read/write contents, workflows)
- Isolate runner in Docker container
- Audit logs for runner activity
- Rotate runner registration token quarterly

### Workflow Best Practices

**Concurrency Control**:
```yaml
concurrency:
  group: fetch-usa-morning
  cancel-in-progress: false  # Let scheduled run complete
```

**Error Handling**:
```yaml
steps:
  - name: Fetch news
    continue-on-error: true  # Don't fail entire workflow
    run: python backend/scripts/fetch_news.py --region usa --period morning
  
  - name: Create issue on failure
    if: failure()
    uses: actions/github-script@v6
    with:
      script: |
        github.rest.issues.create({
          owner: context.repo.owner,
          repo: context.repo.repo,
          title: 'Workflow failed: USA Morning News',
          body: 'See run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}'
        })
```

**Idempotency**:
- Use date-based filenames (`2025-12-15-morning.json`)
- Re-running workflow overwrites file with identical content
- No side effects if workflow runs multiple times

**Logging**:
```yaml
- name: Fetch news
  run: |
    echo "::group::Fetching USA morning news"
    python backend/scripts/fetch_news.py --region usa --period morning
    echo "::endgroup::"
```

### Recommended Cron Schedules

**Complete Workflow Matrix**:
```yaml
# .github/workflows/fetch-usa-morning.yml
on:
  schedule:
    - cron: '55 11 * * *'  # EST: 7:00 AM EST = 12:00 UTC (Nov-Mar)
    - cron: '55 10 * * *'  # EDT: 7:00 AM EDT = 11:00 UTC (Mar-Nov)

# .github/workflows/fetch-usa-evening.yml
on:
  schedule:
    - cron: '55 1 * * *'   # EST: 9:00 PM EST = 02:00 UTC next day (Nov-Mar)
    - cron: '55 0 * * *'   # EDT: 9:00 PM EDT = 01:00 UTC next day (Mar-Nov)

# .github/workflows/fetch-india-morning.yml
on:
  schedule:
    - cron: '25 1 * * *'   # IST: 7:00 AM IST = 01:30 UTC (no DST)

# .github/workflows/fetch-india-evening.yml
on:
  schedule:
    - cron: '25 15 * * *'  # IST: 9:00 PM IST = 15:30 UTC (no DST)

# .github/workflows/fetch-world-morning.yml
on:
  schedule:
    - cron: '55 6 * * *'   # UTC: 7:00 AM UTC (no conversion)

# .github/workflows/fetch-world-evening.yml
on:
  schedule:
    - cron: '55 20 * * *'  # UTC: 9:00 PM UTC (no conversion)
```

**DST Transition Dates** (USA):
- 2025: March 9 → November 2
- 2026: March 8 → November 1
- 2027: March 14 → November 7

---

## 4. Multi-Language Tokenization (Hindi/Telugu)

### Decision: DEFERRED to Phase 2

**Status**: Out of scope for MVP; English-only implementation

### Research Summary

**Perplexity API Multi-Language Support**:
- Sonar model supports non-English prompts and responses
- Quality varies by language; English is best-supported
- Hindi (Devanagari script): Good support
- Telugu: Limited support (smaller training corpus)

**Unicode Handling**:
- Devanagari (Hindi): U+0900 to U+097F
- Telugu: U+0C00 to U+0C7F
- UTF-8 encoding required in JSON files
- CSS `lang` attribute for proper font rendering

**Font Loading Strategy**:
- Google Fonts supports Noto Sans Devanagari (Hindi) and Noto Sans Telugu
- CDN delivery: `https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari&family=Noto+Sans+Telugu`
- Font weight: ~50KB per script

### Recommendation: Implement in Phase 2

**Rationale**:
1. **Scope**: MVP focuses on functional platform; language expansion is enhancement
2. **Complexity**: Requires language-specific prompt engineering, font loading, RTL handling research
3. **Constitution**: Constitution requires Hindi/Telugu but allows phased delivery
4. **Effort**: Estimated 20-30 hours for research, implementation, testing

**Phase 2 Implementation Plan**:
1. Research Perplexity API prompt quality for Hindi/Telugu
2. Add language parameter to fetch scripts
3. Implement font loading with `font-display: swap`
4. Test rendering and readability across devices
5. Update data model with `language` field

---

## Summary of Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **Perplexity API** | Use `sonar` model with `search_recency_filter: "day"` | Cost-effective ($22/year), fast, citations included |
| **Toon Format** | Use standard JSON for MVP | Python decode support missing; migrate later if needed |
| **Timezone Scheduling** | UTC cron with dual EST schedules for DST | Simplest approach; no external libraries required |
| **Multi-Language** | Defer Hindi/Telugu to Phase 2 | English-only MVP; language expansion is enhancement |

**Next Steps**: Proceed to Phase 1 design with these decisions implemented.

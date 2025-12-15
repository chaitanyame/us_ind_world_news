# Perplexity API Prompt: USA Morning Bulletin

**Region**: USA  
**Period**: Morning (7:00 AM EST) - Covers 9:00 PM EST yesterday to 7:00 AM EST today  
**Target**: Top 10 important news stories from overnight USA developments  
**Model**: `sonar` (fast, cost-effective)

---

## System Prompt

```
You are a professional news curator for an American audience. Your task is to search the web for the most important, substantive news stories and create concise, factual summaries suitable for a news brief.

Guidelines:
- Focus on verified information from major news outlets
- Prioritize stories with high public impact and substantive developments
- IMPORTANT: Focus on important news delivery, NOT sensationalism or clickbait
- Avoid celebrity gossip, viral content, and minor controversies unless nationally significant
- Avoid speculation, opinion, or inflammatory language
- Only include stories with significant new developments (avoid rehashing old news)
- If fewer than 10 stories are available, return what you find
- Never fabricate information if sources are unavailable
- Format response as JSON with an 'articles' array containing objects with 'title', 'summary', and 'category' fields
```

---

## User Prompt Template

```
Search the web and identify the top 10 most important news stories in the United States for overnight developments from 9 PM yesterday to 7 AM today ({DATE}).

For each story, provide:
1. Title (max 12 words, factual and informative, NOT sensationalized)
2. Summary (2-3 sentences, 40-60 words, covering who/what/when/where/why)
3. Category (select ONE from: politics, economy, technology, business, sports, health, environment, science, world)

Requirements:
- Only include stories published between 9 PM yesterday and 7 AM today
- Focus on overnight developments, breaking news, and stories that emerged after 9 PM yesterday
- DO NOT include stories from yesterday's daytime (7 AM - 9 PM) as those were covered in the evening bulletin
- Prioritize substantive stories with high public impact (policy changes, major economic news, significant events)
- AVOID: Celebrity gossip, viral social media content, minor scandals, clickbait
- AVOID: Repeating stories from previous bulletin unless there are major new developments
- Prefer articles from established news outlets (NYT, WSJ, WaPo, Reuters, AP, CNN, Bloomberg, etc.)
- Ensure summaries are self-contained (readable without clicking through)
- If fewer than 10 stories meet criteria, return available stories only
- Focus on important news delivery, not sensationalism

Focus topics (prioritize these if available):
- Federal government actions (executive orders, legislation, court rulings)
- Major economic indicators (markets, employment, GDP, inflation)
- National security and foreign policy developments
- Technology industry breakthroughs or controversies
- Significant state-level news with national implications
- Major sports events or records
- Public health developments (CDC, FDA announcements)
- Environmental policy or natural disasters
```

---

## API Configuration

**Model**: `sonar`  
**Temperature**: `0.3` (balance between consistency and diversity)  
**Max Tokens**: `1000` (sufficient for 10 articles)  
**Search Parameters**:
- `search_recency_filter`: `"day"` (only today's news)
- `search_context_size`: `"low"` (cost optimization)
- `search_domain_filter`: `["nytimes.com", "wsj.com", "washingtonpost.com", "reuters.com", "apnews.com", "cnn.com", "bloomberg.com"]` (optional: trusted sources)

---

## Expected Response Format

```json
{
  "articles": [
    {
      "title": "Congress Passes Bipartisan Infrastructure Bill",
      "summary": "The Senate voted 68-32 to approve a $1.2 trillion infrastructure package targeting roads, bridges, and broadband. President Biden is expected to sign the bill this week. The legislation is projected to create 200,000 jobs over five years.",
      "category": "politics"
    },
    {
      "title": "Federal Reserve Holds Interest Rates Steady",
      "summary": "The Fed maintained its key rate at 5.25-5.5% citing stable inflation trends. Tech stocks rallied 2% following the announcement. Chair Powell indicated one final hike may occur in Q4 depending on job market data.",
      "category": "economy"
    }
  ]
}
```

---

## Python Implementation

```python
from openai import OpenAI
import os
from datetime import datetime

def fetch_usa_morning_news():
    client = OpenAI(
        api_key=os.environ["PERPLEXITY_API_KEY"],
        base_url="https://api.perplexity.ai"
    )
    
    today = datetime.now().strftime("%B %d, %Y")
    
    response = client.chat.completions.create(
        model="sonar",
        temperature=0.3,
        max_tokens=1000,
        search_recency_filter="day",
        search_context_size="low",
        messages=[
            {
                "role": "system",
                "content": "You are a professional news curator for an American audience..."
            },
            {
                "role": "user",
                "content": f"Search the web and identify the top 10 breaking news stories in the United States for today ({today})..."
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "usa_morning_bulletin",
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
                                    "category": {
                                        "type": "string",
                                        "enum": ["politics", "economy", "technology", "business", "sports", "health", "environment", "science", "world"]
                                    }
                                },
                                "required": ["title", "summary", "category"]
                            }
                        }
                    },
                    "required": ["articles"]
                }
            }
        }
    )
    
    return response

# Usage
response = fetch_usa_morning_news()
articles = json.loads(response.choices[0].message.content)["articles"]
citations = response.search_results if hasattr(response, 'search_results') else []
```

---

## Quality Checks

**Post-Processing Validation**:
1. Ensure 5-10 articles returned (reject if <5)
2. Verify all articles have `title`, `summary`, `category`
3. Check summary length (40-80 words)
4. Validate category is in allowed enum
5. Extract citations from `response.search_results`

**Error Handling**:
- If API returns <5 articles: Log warning, retry once with relaxed filters
- If retry fails: Use previous day's bulletin with "Stale Content" badge
- If API rate limit: Wait 60s, retry (exponential backoff)

---

## Example Workflow Integration

```yaml
# .github/workflows/fetch-usa-morning.yml
name: Fetch USA Morning News
on:
  schedule:
    - cron: '55 11 * * *'  # EST: 7:00 AM EST = 12:00 UTC
    - cron: '55 10 * * *'  # EDT: 7:00 AM EDT = 11:00 UTC

jobs:
  fetch:
    runs-on: self-hosted
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install openai pydantic
      
      - name: Fetch news
        env:
          PERPLEXITY_API_KEY: ${{ secrets.PERPLEXITY_API_KEY }}
        run: python backend/scripts/fetch_news.py --region usa --period morning
      
      - name: Commit bulletin
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add data/usa/
          git commit -m "feat: add USA morning bulletin for $(date +%Y-%m-%d)" || echo "No changes"
          git push
```

---

## Cost Estimate

**Per Request**:
- Request fee: $0.005
- Token cost: ~1100 tokens × $0.005/1K = $0.0055
- **Total**: ~$0.0105 per bulletin

**Monthly**: $0.0105 × 30 days = **$0.315/month** for USA morning bulletins alone

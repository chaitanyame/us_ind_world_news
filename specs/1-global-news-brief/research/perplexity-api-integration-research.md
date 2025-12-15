# Perplexity API Integration Research for Global News Brief Platform

**Research Date**: December 15, 2025  
**Target Use Case**: Daily news brief generation (6 requests/day) with categorization (politics, tech, business, sports) and citations

---

## 1. Prompt Engineering for Categorized News

### Best Practices for Structured News Responses

#### ✅ Recommended Approach: Specific, Search-Friendly Prompts

Based on Perplexity's documentation, the key to effective categorization is **specificity** and **search-friendly language**:

```python
# GOOD: Specific, category-focused prompts
system_prompt = "You are a concise news summarization assistant."

user_prompts = {
    "politics": """Search for the most significant political developments from the United States 
    and India from the past 24 hours. Include major policy announcements, diplomatic events, 
    and election news. For each story, provide: headline, 2-sentence summary, and significance.""",
    
    "technology": """Find the top 3 technology breakthroughs or major tech company announcements 
    from the past 24 hours. Focus on product launches, AI developments, and cybersecurity news. 
    Provide: headline, brief summary, and business impact.""",
    
    "business": """Search for major business and economic news from the past 24 hours. 
    Include market movements, corporate earnings, mergers/acquisitions, and economic indicators. 
    Format: headline, summary, market impact.""",
    
    "sports": """Find the most important sports news from the past 24 hours, focusing on 
    international competitions, major league updates, and athlete achievements. 
    Include: headline, score/result if applicable, and brief context."""
}
```

#### ❌ Avoid: Few-Shot Prompting & Generic Questions

**Don't use few-shot examples** - they confuse the search component:
```python
# BAD: Few-shot approach
"Here's an example of a good news summary: [example]. Now summarize today's tech news."
```

**Don't ask for URLs in prompts** - they will be hallucinated:
```python
# BAD: Requesting URLs
"Find tech news and include the source URL for each story"

# GOOD: URLs are automatically returned in search_results field
"Find tech news stories from the past 24 hours"
# Then parse URLs from response.search_results
```

### Citation-Forward Prompt Strategy

The Perplexity API automatically provides citations in the `search_results` field. **Never ask for links in the prompt**:

```python
# CORRECT Pattern
response = client.chat.completions.create(
    model="sonar",
    messages=[
        {"role": "system", "content": "You are a news summarization assistant."},
        {"role": "user", "content": "Find 3 major tech stories from today"}
    ],
    extra_body={
        "search_recency_filter": "day"
    }
)

# Access structured citations
for result in response.search_results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Date: {result['date']}")
    print(f"Snippet: {result['snippet']}")
```

### Structured Output for News Categories

Use **JSON Schema** for consistent, machine-readable responses:

```python
from pydantic import BaseModel
from typing import List, Optional

class NewsStory(BaseModel):
    headline: str
    summary: str
    category: str
    significance: Optional[str] = None

class NewsBrief(BaseModel):
    stories: List[NewsStory]
    date: str

# Request with structured output
completion = client.chat.completions.create(
    model="sonar",
    messages=[
        {"role": "user", "content": "Find top 5 US political news from past 24 hours"}
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "schema": NewsBrief.model_json_schema()
        }
    }
)

# Parse structured response
news_brief = NewsBrief.model_validate_json(completion.choices[0].message.content)
```

**⚠️ Important**: The first request with a new JSON schema incurs a **10-30 second delay** for schema preparation. Subsequent requests are fast.

### Preventing Hallucination

Always include explicit instructions about unavailable information:

```python
user_prompt = """Search for major US political news from the past 24 hours. 
Focus on federal government, Supreme Court, and Congressional actions.

IMPORTANT: If you cannot find reliable sources or recent information, 
state that clearly rather than providing speculative information. 
Only include information verified from your search results."""
```

---

## 2. Sonar Model Configuration

### Optimal Parameters for News Summarization

#### Model Selection: **`sonar`** (not `sonar-pro`)

For daily news briefs with 6 requests/day, use the **standard `sonar` model**:

| Feature | sonar | sonar-pro |
|---------|-------|-----------|
| **Cost** | $1/1M input tokens, $1/1M output tokens | $3/1M input, $15/1M output |
| **Request Fee** | $5 per 1K requests (low context) | $6 per 1K requests (low context) |
| **Speed** | Fastest | Slower |
| **Best For** | Quick facts, news updates, simple Q&A | Complex queries, detailed research |
| **Context** | 128K tokens | 128K tokens |

**Recommendation**: Use `sonar` for cost-effectiveness. It's specifically optimized for "news, sports, health, and finance content."

#### Recommended Parameters

```python
response = client.chat.completions.create(
    model="sonar",
    messages=[
        {"role": "system", "content": "You are a concise news assistant."},
        {"role": "user", "content": "Find top 3 US political news from today"}
    ],
    
    # Temperature: Lower for factual news
    temperature=0.2,  # Range: 0-2, default ~1.0
    
    # Max tokens: Limit response length
    max_tokens=800,  # Typical news brief: 600-1000 tokens
    
    # Perplexity-specific parameters (use extra_body for OpenAI client)
    extra_body={
        # Recency filter: Critical for news
        "search_recency_filter": "day",  # Options: hour, day, week, month, year
        
        # Search context size: Use "low" for cost savings
        "search_context_size": "low",  # Options: low (default), medium, high
        
        # Domain filtering (optional)
        "search_domain_filter": [
            "nytimes.com", 
            "reuters.com", 
            "bloomberg.com",
            "bbc.com"
        ],
        
        # Return related questions (optional)
        "return_related_questions": False,
        
        # Return images (optional)
        "return_images": False
    }
)
```

#### Parameter Details

| Parameter | Recommended Value | Notes |
|-----------|------------------|-------|
| `temperature` | 0.2-0.4 | Lower = more factual, consistent |
| `max_tokens` | 600-1000 | Typical news brief per category |
| `search_recency_filter` | `"day"` | Critical for daily news |
| `search_context_size` | `"low"` | Fastest, cheapest, sufficient for news |
| `search_domain_filter` | Optional list | Filter to trusted sources |

#### Why Use Built-in Parameters vs. Prompt Instructions

From Perplexity docs:
> **"Use the API's built-in parameters rather than prompt instructions"** for search behavior control. The search component processes these parameters directly, ensuring reliable results.

```python
# ❌ BAD: Trying to control search via prompt
"Find news from the past 24 hours only, from nytimes.com or reuters.com"

# ✅ GOOD: Using built-in parameters
extra_body={
    "search_recency_filter": "day",
    "search_domain_filter": ["nytimes.com", "reuters.com"]
}
```

---

## 3. Rate Limits & Pricing

### Rate Limits by Usage Tier

Rate limits are based on **cumulative lifetime credit purchases**, not current balance:

| Tier | Credits Purchased | Sonar RPM | Deep Research RPM |
|------|------------------|-----------|-------------------|
| **Tier 0** | $0 (new accounts) | 50 RPM | 5 RPM |
| **Tier 1** | $50+ | 50 RPM | 10 RPM |
| **Tier 2** | $250+ | 500 RPM | 20 RPM |
| **Tier 3** | $500+ | 1,000 RPM | 40 RPM |
| **Tier 4** | $1,000+ | 2,000 RPM | 60 RPM |
| **Tier 5** | $5,000+ | 2,000 RPM | 100 RPM |

**For 6 requests/day**: Even Tier 0 (50 RPM) is more than sufficient. You could send all 6 requests in parallel.

### Cost Estimation for News Brief Platform

#### Scenario: 6 Requests/Day (1 per category + 1 summary)

Assumptions:
- Model: `sonar`
- Average input: 100 tokens/request (short prompt)
- Average output: 600 tokens/request (news brief)
- Search context: Low (default)

#### Cost Breakdown per Request

| Component | Cost Formula | Example Cost |
|-----------|-------------|--------------|
| Input tokens | $1 per 1M tokens | $0.0001 (100 tokens) |
| Output tokens | $1 per 1M tokens | $0.0006 (600 tokens) |
| Request fee (low context) | $5 per 1K requests | $0.005 |
| **Total per request** | | **$0.0057** |

#### Monthly Cost Projection

```
Daily cost:    6 requests × $0.0057 = $0.0342
Monthly cost:  $0.0342 × 30 days   = $1.03
Annual cost:   $0.0342 × 365 days  = $12.48
```

**Budget Recommendation**: Start with **$50 credit purchase** (unlocks Tier 1, enough for ~8,700 requests or ~4 years at 6/day).

#### Cost Comparison: Search Context Size

| Context Size | Request Fee (per 1K) | Daily Cost (6 requests) | Monthly Cost |
|--------------|---------------------|------------------------|--------------|
| Low (default) | $5 | $0.034 | $1.03 |
| Medium | $8 | $0.055 | $1.64 |
| High | $12 | $0.079 | $2.36 |

**Recommendation**: Use **low context** for news briefs. It's the fastest and cheapest option.

### Search API Alternative

If you only need raw search results (no AI summarization):

| API | Cost | Best For |
|-----|------|----------|
| **Search API** | $5 per 1K requests | Custom aggregation, no AI needed |
| **Sonar (Grounded LLM)** | $5 per 1K + tokens | AI-generated summaries with citations |

For news briefs with summaries, **Sonar** is the right choice.

---

## 4. Integration Pattern with OpenAI Client

### Complete Implementation Example

```python
import os
from openai import OpenAI
from typing import List, Dict, Optional
import time
import random

class PerplexityNewsClient:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Perplexity client using OpenAI library."""
        self.client = OpenAI(
            api_key=api_key or os.environ["PERPLEXITY_API_KEY"],
            base_url="https://api.perplexity.ai"
        )
    
    def fetch_category_news(
        self, 
        category: str, 
        region: str = "United States",
        max_retries: int = 3
    ) -> Dict:
        """
        Fetch news for a specific category with retry logic.
        
        Args:
            category: News category (politics, tech, business, sports)
            region: Geographic focus (US, India, World)
            max_retries: Number of retry attempts for rate limits
            
        Returns:
            Dict with 'content', 'citations', and 'search_results'
        """
        prompt = self._build_category_prompt(category, region)
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model="sonar",
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a concise news summarization assistant. "
                                      "Provide factual summaries based only on search results."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=800,
                    extra_body={
                        "search_recency_filter": "day",
                        "search_context_size": "low",
                        "return_related_questions": False
                    }
                )
                
                # Extract data
                return {
                    "content": response.choices[0].message.content,
                    "citations": getattr(response, 'citations', []),
                    "search_results": getattr(response, 'search_results', []),
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_cost": self._calculate_cost(response.usage)
                    }
                }
                
            except Exception as e:
                error_type = type(e).__name__
                
                # Handle rate limiting (429)
                if "429" in str(e) or "rate" in str(e).lower():
                    if attempt == max_retries - 1:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts")
                    
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                
                # Handle authentication errors (401)
                elif "401" in str(e) or "unauthorized" in str(e).lower():
                    raise Exception("Invalid API key. Check PERPLEXITY_API_KEY.")
                
                # Handle connection errors
                elif "connection" in str(e).lower():
                    if attempt == max_retries - 1:
                        raise Exception(f"Connection failed after {max_retries} attempts")
                    
                    delay = 1 + random.uniform(0, 0.5)
                    print(f"Connection error. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                
                # Handle server errors (500+)
                elif "500" in str(e) or "502" in str(e) or "503" in str(e):
                    if attempt == max_retries - 1:
                        raise Exception(f"Server error after {max_retries} attempts: {e}")
                    
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Server error. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    continue
                
                # Unknown error - don't retry
                else:
                    raise Exception(f"API error ({error_type}): {e}")
    
    def _build_category_prompt(self, category: str, region: str) -> str:
        """Build category-specific prompts optimized for search."""
        prompts = {
            "politics": f"""Search for the most significant political developments from {region} 
            from the past 24 hours. Include major policy announcements, diplomatic events, 
            and government actions. For each story, provide:
            - Clear headline
            - 2-sentence summary
            - Why it matters
            
            If no recent reliable information is found, state that clearly.""",
            
            "technology": f"""Find the top 3 technology breakthroughs or major tech company 
            announcements from {region} from the past 24 hours. Focus on:
            - Product launches
            - AI/ML developments
            - Cybersecurity news
            - Startup funding
            
            For each: headline, brief summary, business impact.""",
            
            "business": f"""Search for major business and economic news from {region} 
            from the past 24 hours. Include:
            - Market movements
            - Corporate earnings
            - Mergers/acquisitions
            - Economic indicators
            
            Format: headline, summary, market significance.""",
            
            "sports": f"""Find the most important sports news from the past 24 hours. 
            Focus on international competitions, major league updates, and significant 
            athlete achievements. Include:
            - Headline
            - Score/result if applicable
            - Brief context
            
            Only include information from your search results."""
        }
        
        return prompts.get(category, prompts["politics"])
    
    def _calculate_cost(self, usage) -> float:
        """Calculate total cost for a request."""
        # Sonar pricing
        input_cost = (usage.prompt_tokens / 1_000_000) * 1.0  # $1 per 1M
        output_cost = (usage.completion_tokens / 1_000_000) * 1.0  # $1 per 1M
        request_cost = 0.005  # $5 per 1K requests (low context)
        
        return input_cost + output_cost + request_cost
    
    def parse_citations(self, search_results: List[Dict]) -> List[Dict]:
        """
        Parse citations from search_results field.
        
        Returns list of citation objects with: title, url, date, snippet
        """
        citations = []
        for result in search_results:
            citations.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "date": result.get("date", ""),
                "last_updated": result.get("last_updated", ""),
                "snippet": result.get("snippet", "")
            })
        return citations


# Usage Example
if __name__ == "__main__":
    client = PerplexityNewsClient()
    
    # Fetch tech news
    result = client.fetch_category_news(
        category="technology",
        region="United States"
    )
    
    print("News Content:")
    print(result["content"])
    print("\n" + "="*80 + "\n")
    
    print("Citations:")
    citations = client.parse_citations(result["search_results"])
    for i, citation in enumerate(citations, 1):
        print(f"{i}. {citation['title']}")
        print(f"   URL: {citation['url']}")
        print(f"   Date: {citation['date']}")
        print(f"   Snippet: {citation['snippet'][:100]}...")
        print()
    
    print("Cost Info:")
    print(f"Tokens: {result['usage']['prompt_tokens']} in, "
          f"{result['usage']['completion_tokens']} out")
    print(f"Cost: ${result['usage']['total_cost']:.6f}")
```

### Error Handling Best Practices

#### 1. Rate Limiting (429 Errors)

```python
# Exponential backoff with jitter
def exponential_backoff(attempt: int) -> float:
    base_delay = 2 ** attempt  # 1s, 2s, 4s, 8s...
    jitter = random.uniform(0, 1)  # Add randomness
    return base_delay + jitter
```

#### 2. Connection Errors

```python
# Shorter retry delay for network issues
if "connection" in error_type.lower():
    delay = 1 + random.uniform(0, 0.5)
    time.sleep(delay)
```

#### 3. Authentication Errors (401)

```python
# Don't retry - fail fast
if "401" in str(error):
    raise Exception("Invalid API key. Check PERPLEXITY_API_KEY.")
```

#### 4. Server Errors (500, 502, 503)

```python
# Retry with exponential backoff
if error_code >= 500:
    delay = exponential_backoff(attempt)
    time.sleep(delay)
```

### Parsing Citations from Response

The Perplexity API returns citations in **two ways**:

1. **`citations` field**: List of URLs
2. **`search_results` field**: Detailed metadata (title, url, date, snippet)

```python
response = client.chat.completions.create(...)

# Method 1: Simple URL list
if hasattr(response, 'citations'):
    urls = response.citations
    print(f"Found {len(urls)} sources")

# Method 2: Detailed metadata (RECOMMENDED)
if hasattr(response, 'search_results'):
    for result in response.search_results:
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Published: {result['date']}")
        print(f"Last Updated: {result['last_updated']}")
        print(f"Snippet: {result['snippet']}")
```

**⚠️ Critical**: Never ask for URLs in the prompt. The LLM cannot see actual URLs and will hallucinate them. Always use `search_results` field.

### Structured Data Extraction

For consistent parsing, use JSON Schema:

```python
from pydantic import BaseModel
from typing import List

class NewsItem(BaseModel):
    headline: str
    summary: str
    significance: str

class CategoryBrief(BaseModel):
    category: str
    date: str
    stories: List[NewsItem]

response = client.chat.completions.create(
    model="sonar",
    messages=[...],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "schema": CategoryBrief.model_json_schema()
        }
    }
)

# Parse JSON response
brief = CategoryBrief.model_validate_json(
    response.choices[0].message.content
)

# Access structured data
for story in brief.stories:
    print(f"Headline: {story.headline}")
    print(f"Summary: {story.summary}")
```

---

## Summary & Recommendations

### For Global News Brief Platform (6 requests/day):

1. **Model**: Use `sonar` (not `sonar-pro`) for cost optimization
2. **Parameters**: 
   - `temperature=0.2` (factual)
   - `max_tokens=800` (sufficient for category brief)
   - `search_recency_filter="day"` (critical for news)
   - `search_context_size="low"` (fastest, cheapest)
3. **Cost**: ~$1.03/month ($12.48/year) for 6 requests/day
4. **Rate Limits**: Tier 0 (50 RPM) is sufficient; purchase $50 credits for Tier 1
5. **Error Handling**: Implement exponential backoff for rate limits, fail fast on auth errors
6. **Citations**: Parse from `search_results` field, never request in prompt
7. **Structured Output**: Use JSON Schema for consistent parsing (first request has 10-30s delay)

### Key Implementation Patterns:

✅ **DO**:
- Use specific, search-friendly prompts
- Leverage built-in parameters (`search_recency_filter`, `search_domain_filter`)
- Parse citations from `search_results` field
- Implement retry logic with exponential backoff
- Use JSON Schema for structured outputs
- Set explicit temperature for factual content

❌ **DON'T**:
- Use few-shot prompting (confuses search)
- Request URLs in prompts (will hallucinate)
- Use generic questions
- Retry on 401 errors (fail fast instead)
- Assume unlimited rate limits on Tier 0

### Documentation References:
- Official Docs: https://docs.perplexity.ai/
- API Cookbook: https://github.com/perplexityai/api-cookbook
- Pricing: https://docs.perplexity.ai/getting-started/pricing
- Rate Limits: https://docs.perplexity.ai/guides/rate-limits-usage-tiers
- Prompt Guide: https://docs.perplexity.ai/guides/prompt-guide
- Structured Outputs: https://docs.perplexity.ai/guides/structured-outputs

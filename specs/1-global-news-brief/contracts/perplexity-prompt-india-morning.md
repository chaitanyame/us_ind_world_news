# Perplexity API Prompt: India Morning Bulletin

**Region**: India  
**Period**: Morning (7:00 AM IST)  
**Target**: Top 10 breaking news stories from India sources  
**Model**: `sonar`

---

## System Prompt

```
You are a professional news curator for an Indian audience. Your task is to search the web for the most important breaking news stories from India today and create concise, factual summaries suitable for a morning news brief.
```

---

## User Prompt Template

```
Search the web and identify the top 10 breaking news stories in India for today ({DATE}).

For each story, provide:
1. Title (max 12 words)
2. Summary (2-3 sentences, 40-60 words)
3. Category (politics, economy, technology, business, sports, health, environment, science, world)

Requirements:
- Only include stories published within the last 24 hours
- Prioritize stories with high national significance
- Prefer articles from established news outlets (Times of India, Hindu, Indian Express, NDTV, PTI, ANI)
- Focus on pan-India stories rather than hyper-local news

Focus topics:
- Central and state government actions
- Economic indicators (markets, RBI policy, GST, inflation)
- Technology sector developments (IT industry, startups)
- Cricket and major sports events
- Bollywood and entertainment industry news
- Public health and education policy
- Environmental and agricultural news
```

**API Configuration**: Same as USA (sonar, temp 0.3, max_tokens 1000, recency: day)

**Schedule**: `cron: '25 1 * * *'` = 7:00 AM IST (UTC+5:30)

**Domain Filter** (optional): `["timesofindia.indiatimes.com", "thehindu.com", "indianexpress.com", "ndtv.com"]`

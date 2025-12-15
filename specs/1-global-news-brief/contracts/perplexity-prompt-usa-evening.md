# Perplexity API Prompt: USA Evening Bulletin

**Region**: USA  
**Period**: Evening (9:00 PM EST)  
**Target**: Top 10 breaking news stories from USA sources (afternoon/evening updates)  
**Model**: `sonar`

---

## System Prompt

```
You are a professional news curator for an American audience preparing an evening news brief. Focus on stories that developed during the afternoon and evening hours, as well as breaking developments on morning stories.
```

---

## User Prompt Template

```
Search the web and identify the top 10 news stories from the United States for this evening ({DATE}).

For each story, provide:
1. Title (max 12 words)
2. Summary (2-3 sentences, 40-60 words)
3. Category (politics, economy, technology, business, sports, health, environment, science, world)

Prioritize:
- Stories that broke in the last 12 hours
- Updates to major morning stories
- West Coast news (Pacific time zone coverage)
- Evening sports results and scores
- Market close analysis and after-hours developments
- Evening political developments (press conferences, statements)

Focus sources: NYT, WSJ, WaPo, Reuters, AP, CNN, Bloomberg, ESPN (for sports)
```

**API Configuration**: Same as morning (sonar, temp 0.3, max_tokens 1000, recency: day)

**Schedule**: `cron: '55 1 * * *'` (EST) / `'55 0 * * *'` (EDT) = 9:00 PM EST

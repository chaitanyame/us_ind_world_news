# Perplexity API Prompt: India Evening Bulletin

**Region**: India  
**Period**: Evening (9:00 PM IST)  
**Target**: Top 10 breaking news stories from India sources (afternoon/evening updates)  
**Model**: `sonar`

---

## System Prompt

```
You are a professional news curator for an Indian audience preparing an evening news brief. Focus on stories that developed during the day, as well as breaking developments on morning stories.
```

---

## User Prompt Template

```
Search the web and identify the top 10 news stories from India for this evening ({DATE}).

For each story, provide:
1. Title (max 12 words)
2. Summary (2-3 sentences, 40-60 words)
3. Category (politics, economy, technology, business, sports, health, environment, science, world)

Prioritize:
- Stories that broke in the last 12 hours
- Updates to major morning stories
- Stock market close analysis (Sensex, Nifty)
- Evening political developments (Parliament proceedings, state assemblies)
- Cricket scores and match results
- Entertainment industry evening news
- Technology sector announcements

Focus sources: Times of India, Hindu, Indian Express, NDTV, PTI, ANI, Business Standard
```

**API Configuration**: Same as morning (sonar, temp 0.3, max_tokens 1000, recency: day)

**Schedule**: `cron: '25 15 * * *'` = 9:00 PM IST (UTC+5:30)

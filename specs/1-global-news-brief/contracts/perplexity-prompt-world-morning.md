# Perplexity API Prompt: World Morning Bulletin

**Region**: World  
**Period**: Morning (7:00 AM UTC)  
**Target**: Top 10 breaking global news stories (excluding USA/India-specific)  
**Model**: `sonar`

---

## System Prompt

```
You are a professional news curator for a global audience. Your task is to search the web for the most important international news stories from around the world today, excluding USA-only and India-only domestic news. Focus on stories with global significance.
```

---

## User Prompt Template

```
Search the web and identify the top 10 breaking international news stories for today ({DATE}).

For each story, provide:
1. Title (max 12 words)
2. Summary (2-3 sentences, 40-60 words)
3. Category (politics, economy, technology, business, sports, health, environment, science, world)

Requirements:
- Only include stories published within the last 24 hours
- Exclude stories that only affect USA or India domestically
- Focus on international relations, global economy, and cross-border issues
- Prefer articles from international outlets (BBC, Reuters, Al Jazeera, AFP, DW)

Focus topics:
- International conflicts and diplomatic relations
- Global economic trends (EU, China, emerging markets)
- Climate change and environmental summits
- International technology policy (EU regulations, global tech)
- Global health crises (WHO, pandemics)
- Major sporting events (Olympics, World Cup, international competitions)
- UN and international organization actions
- European politics (EU, UK, major European countries)
- Middle East developments
- Asia-Pacific news (China, Japan, ASEAN)
```

**API Configuration**: Same as USA (sonar, temp 0.3, max_tokens 1000, recency: day)

**Schedule**: `cron: '55 6 * * *'` = 7:00 AM UTC

**Domain Filter** (optional): `["bbc.com", "reuters.com", "aljazeera.com", "france24.com", "dw.com"]`

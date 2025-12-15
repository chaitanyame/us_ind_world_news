# Data Model: NRI News Brief

**Feature**: 1-global-news-brief  
**Created**: 2025-12-15  
**Purpose**: Define JSON schema for bulletins, articles, and metadata

This document defines the data structures used throughout the NRI News Brief platform.

---

## Entity Relationship Overview

```
Bulletin (1)  ─┬─> Article (5-10)
               │
               └─> Metadata (1)
```

- A **Bulletin** contains multiple **Articles** and one **Metadata** object
- Each **Article** represents a single news story with summary and citations
- **Metadata** tracks bulletin generation details and region information

---

## 1. Bulletin Entity

**Purpose**: Container for a single news bulletin (morning or evening) for a specific region and date

**File Naming Convention**: `data/{region}/{YYYY-MM-DD}-{period}.json`
- Example: `data/usa/2025-12-15-morning.json`

**Schema**:
```json
{
  "bulletin": {
    "id": "usa-2025-12-15-morning",
    "region": "usa",
    "date": "2025-12-15",
    "period": "morning",
    "generated_at": "2025-12-15T12:05:32Z",
    "version": "1.0",
    "articles": [ /* Array of Article objects */ ],
    "metadata": { /* Metadata object */ }
  }
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | string | Yes | Unique identifier | Format: `{region}-{YYYY-MM-DD}-{period}` |
| `region` | string | Yes | Geographic region | Enum: `usa`, `india`, `world` |
| `date` | string | Yes | Bulletin date | Format: `YYYY-MM-DD` (ISO 8601) |
| `period` | string | Yes | Time period | Enum: `morning`, `evening` |
| `generated_at` | string | Yes | UTC timestamp of generation | Format: ISO 8601 with `Z` suffix |
| `version` | string | Yes | Schema version | Semantic version (e.g., `1.0`) |
| `articles` | array | Yes | List of news articles | Length: 5-10 items |
| `metadata` | object | Yes | Generation metadata | See Metadata schema |

**Example**:
```json
{
  "bulletin": {
    "id": "usa-2025-12-15-morning",
    "region": "usa",
    "date": "2025-12-15",
    "period": "morning",
    "generated_at": "2025-12-15T12:05:32Z",
    "version": "1.0",
    "articles": [
      {
        "title": "Federal Reserve Maintains Interest Rates Amid Inflation Concerns",
        "summary": "The Federal Reserve kept rates steady at 5.25-5.5%, citing ongoing inflation reduction progress. Tech stocks rallied 2% following the announcement. Analysts predict one final hike may occur in Q4.",
        "category": "economy",
        "source": {
          "name": "Financial Times",
          "url": "https://www.ft.com/content/example",
          "published_at": "2025-12-15T08:30:00Z"
        },
        "citations": [
          {
            "title": "Fed Holds Rates Steady",
            "url": "https://www.reuters.com/markets/fed-rates",
            "publisher": "Reuters"
          }
        ],
        "article_id": "usa-2025-12-15-morning-001"
      }
    ],
    "metadata": {
      "article_count": 8,
      "categories_distribution": {
        "politics": 2,
        "economy": 2,
        "technology": 1,
        "sports": 1,
        "health": 1,
        "world": 1
      },
      "llm_model": "sonar",
      "llm_usage": {
        "prompt_tokens": 245,
        "completion_tokens": 856,
        "total_tokens": 1101
      },
      "processing_time_seconds": 3.42,
      "workflow_run_id": "12345678"
    }
  }
}
```

---

## 2. Article Entity

**Purpose**: Represents a single AI-summarized news story

**Schema**:
```json
{
  "title": "Federal Reserve Maintains Interest Rates Amid Inflation Concerns",
  "summary": "The Federal Reserve kept rates steady at 5.25-5.5%, citing ongoing inflation reduction progress. Tech stocks rallied 2% following the announcement. Analysts predict one final hike may occur in Q4.",
  "category": "economy",
  "source": {
    "name": "Financial Times",
    "url": "https://www.ft.com/content/example",
    "published_at": "2025-12-15T08:30:00Z"
  },
  "citations": [
    {
      "title": "Fed Holds Rates Steady",
      "url": "https://www.reuters.com/markets/fed-rates",
      "publisher": "Reuters"
    }
  ],
  "article_id": "usa-2025-12-15-morning-001"
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `title` | string | Yes | Article headline | Max 120 characters; no HTML |
| `summary` | string | Yes | AI-generated summary | 2-3 sentences, 40-80 words |
| `category` | string | Yes | News category | Enum: see categories table |
| `source` | object | Yes | Primary source | See Source schema |
| `citations` | array | Yes | Supporting citations | 1-3 items; see Citation schema |
| `article_id` | string | Yes | Unique article ID | Format: `{bulletin_id}-{NNN}` |

**Category Enum**:
| Value | Display Name | Color (Light Theme) | Color (Dark Theme) |
|-------|--------------|---------------------|-------------------|
| `politics` | Politics | `#f97316` (orange) | `#fb923c` (orange-400) |
| `economy` | Economy | `#137fec` (primary blue) | `#38bdf8` (sky-400) |
| `technology` | Technology | `#3b82f6` (blue) | `#60a5fa` (blue-400) |
| `business` | Business | `#8b5cf6` (violet) | `#a78bfa` (violet-400) |
| `sports` | Sports | `#10b981` (green) | `#34d399` (emerald-400) |
| `health` | Health | `#ec4899` (pink) | `#f472b6` (pink-400) |
| `environment` | Environment | `#22c55e` (green) | `#4ade80` (green-400) |
| `science` | Science | `#a855f7` (purple) | `#c084fc` (purple-400) |
| `world` | World | `#6366f1` (indigo) | `#818cf8` (indigo-400) |

---

## 3. Source Subentity

**Purpose**: Metadata about the primary news source for an article

**Schema**:
```json
{
  "name": "Financial Times",
  "url": "https://www.ft.com/content/example",
  "published_at": "2025-12-15T08:30:00Z"
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `name` | string | Yes | Publisher name | Max 100 characters |
| `url` | string | Yes | Full article URL | Valid HTTPS URL |
| `published_at` | string | No | Publication timestamp | ISO 8601 with `Z` suffix; optional |

---

## 4. Citation Subentity

**Purpose**: Supporting citation from Perplexity API search results

**Schema**:
```json
{
  "title": "Fed Holds Rates Steady",
  "url": "https://www.reuters.com/markets/fed-rates",
  "publisher": "Reuters"
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `title` | string | Yes | Citation title | Max 200 characters |
| `url` | string | Yes | Citation URL | Valid HTTPS URL |
| `publisher` | string | No | Publisher name | Max 100 characters; optional |

**Note**: Citations come from Perplexity API's `search_results` field. Typically 1-3 citations per article.

---

## 5. Metadata Entity

**Purpose**: Tracks bulletin generation details for observability and debugging

**Schema**:
```json
{
  "article_count": 8,
  "categories_distribution": {
    "politics": 2,
    "economy": 2,
    "technology": 1,
    "sports": 1,
    "health": 1,
    "world": 1
  },
  "llm_model": "sonar",
  "llm_usage": {
    "prompt_tokens": 245,
    "completion_tokens": 856,
    "total_tokens": 1101
  },
  "processing_time_seconds": 3.42,
  "workflow_run_id": "12345678",
  "errors": []
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `article_count` | integer | Yes | Number of articles | Range: 1-10 |
| `categories_distribution` | object | Yes | Category breakdown | Keys: category enums, Values: counts |
| `llm_model` | string | Yes | Perplexity model used | Enum: `sonar`, `sonar-pro` |
| `llm_usage` | object | Yes | Token usage stats | See LLM Usage schema |
| `processing_time_seconds` | float | Yes | Total workflow time | Range: 0.1-60.0 seconds |
| `workflow_run_id` | string | Yes | GitHub Actions run ID | String or integer |
| `errors` | array | No | Error messages | Array of strings; empty if no errors |

---

## 6. LLM Usage Subentity

**Purpose**: Tracks Perplexity API token consumption for cost monitoring

**Schema**:
```json
{
  "prompt_tokens": 245,
  "completion_tokens": 856,
  "total_tokens": 1101
}
```

**Field Definitions**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `prompt_tokens` | integer | Yes | Input tokens | Range: 1-2000 |
| `completion_tokens` | integer | Yes | Output tokens | Range: 1-5000 |
| `total_tokens` | integer | Yes | Sum of prompt + completion | Range: 2-7000 |

**Cost Calculation**:
```
Cost per bulletin = ($0.005 per request) + (total_tokens / 1000 * $0.005 per 1K tokens)
Example: $0.005 + (1101 / 1000 * $0.005) = $0.005 + $0.0055 = $0.0105 per bulletin
```

---

## File Size Constraints

**Per File**:
- Target: <50 KB per JSON file
- Maximum: 100 KB per JSON file
- Typical: 30-40 KB for 8 articles

**Repository Total**:
- 42 files (3 regions × 2 periods × 7 days) × 50 KB = 2.1 MB
- Well within GitHub's 100 MB repository size recommendation

**Compression**: GitHub Pages automatically gzips JSON files (70% reduction = ~15 KB over the wire)

---

## Validation Rules

**Backend Validation** (Python):
```python
from pydantic import BaseModel, HttpUrl, Field, validator
from datetime import datetime
from typing import List, Optional

class Citation(BaseModel):
    title: str = Field(..., max_length=200)
    url: HttpUrl
    publisher: Optional[str] = Field(None, max_length=100)

class Source(BaseModel):
    name: str = Field(..., max_length=100)
    url: HttpUrl
    published_at: Optional[datetime] = None

class Article(BaseModel):
    title: str = Field(..., max_length=120)
    summary: str = Field(..., min_length=40, max_length=500)
    category: str = Field(..., regex="^(politics|economy|technology|business|sports|health|environment|science|world)$")
    source: Source
    citations: List[Citation] = Field(..., min_items=1, max_items=3)
    article_id: str

class LLMUsage(BaseModel):
    prompt_tokens: int = Field(..., ge=1, le=2000)
    completion_tokens: int = Field(..., ge=1, le=5000)
    total_tokens: int = Field(..., ge=2, le=7000)

class Metadata(BaseModel):
    article_count: int = Field(..., ge=1, le=10)
    categories_distribution: dict
    llm_model: str = Field(..., regex="^(sonar|sonar-pro)$")
    llm_usage: LLMUsage
    processing_time_seconds: float = Field(..., ge=0.1, le=60.0)
    workflow_run_id: str
    errors: List[str] = []

class Bulletin(BaseModel):
    id: str
    region: str = Field(..., regex="^(usa|india|world)$")
    date: str = Field(..., regex=r"^\d{4}-\d{2}-\d{2}$")
    period: str = Field(..., regex="^(morning|evening)$")
    generated_at: datetime
    version: str
    articles: List[Article] = Field(..., min_items=5, max_items=10)
    metadata: Metadata

    @validator('id')
    def validate_id(cls, v, values):
        expected = f"{values.get('region')}-{values.get('date')}-{values.get('period')}"
        if v != expected:
            raise ValueError(f"ID must match pattern: {expected}")
        return v
```

**Frontend Validation** (JavaScript):
```javascript
function validateBulletin(data) {
    if (!data.bulletin) throw new Error('Missing bulletin object');
    
    const { bulletin } = data;
    if (!['usa', 'india', 'world'].includes(bulletin.region)) {
        throw new Error(`Invalid region: ${bulletin.region}`);
    }
    
    if (!['morning', 'evening'].includes(bulletin.period)) {
        throw new Error(`Invalid period: ${bulletin.period}`);
    }
    
    if (!Array.isArray(bulletin.articles) || bulletin.articles.length < 5 || bulletin.articles.length > 10) {
        throw new Error(`Invalid article count: ${bulletin.articles?.length}`);
    }
    
    return true;
}
```

---

## Indexing Strategy

**For 7-Day Historical Navigation**:

Generate a `data/index.json` file listing all available bulletins:
```json
{
  "bulletins": [
    {
      "id": "usa-2025-12-15-morning",
      "region": "usa",
      "date": "2025-12-15",
      "period": "morning",
      "file_path": "/data/usa/2025-12-15-morning.json",
      "article_count": 8
    },
    {
      "id": "usa-2025-12-15-evening",
      "region": "usa",
      "date": "2025-12-15",
      "period": "evening",
      "file_path": "/data/usa/2025-12-15-evening.json",
      "article_count": 10
    }
  ],
  "last_updated": "2025-12-15T21:10:05Z",
  "total_bulletins": 42
}
```

**Benefits**:
- Frontend can fetch index once, then load specific bulletins on demand
- Fast date picker rendering (no need to scan filesystem)
- Shows missing bulletins (workflow failures) with `article_count: 0`

**Update Strategy**: Regenerate `index.json` after each bulletin workflow completes.

---

## Migration & Versioning

**Schema Evolution**:
- Current version: `1.0`
- If schema changes, increment `version` field
- Frontend checks `version` and applies appropriate parser

**Example Migration** (if adding language field):
```json
{
  "bulletin": {
    "version": "1.1",
    "language": "en",
    "articles": [ /* ... */ ]
  }
}
```

**Backward Compatibility**: Frontend must handle both `1.0` (no language field) and `1.1` (with language field) gracefully.

---

## Summary

- **2 main entities**: Bulletin, Article
- **4 subentities**: Source, Citation, Metadata, LLM Usage
- **JSON-based**: Standard JSON (not toon format for MVP)
- **File size**: <50 KB per bulletin (target), <100 KB (max)
- **Validation**: Pydantic (backend), manual checks (frontend)
- **Indexing**: `data/index.json` for fast navigation

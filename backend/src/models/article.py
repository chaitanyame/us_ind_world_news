"""
Pydantic models for NRI News Brief data structures.

This module defines the data models for bulletins, articles, and metadata
with comprehensive validation rules.
"""

from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class RegionEnum(str, Enum):
    """Valid geographic regions for news bulletins."""
    USA = "usa"
    INDIA = "india"
    WORLD = "world"


class PeriodEnum(str, Enum):
    """Valid time periods for bulletins."""
    MORNING = "morning"
    EVENING = "evening"


class CategoryEnum(str, Enum):
    """Valid news categories."""
    POLITICS = "politics"
    ECONOMY = "economy"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    SPORTS = "sports"
    HEALTH = "health"
    ENVIRONMENT = "environment"
    SCIENCE = "science"
    WORLD = "world"


class Citation(BaseModel):
    """Supporting citation from Perplexity API search results."""
    
    title: str = Field(..., max_length=150, description="Citation title")
    url: HttpUrl = Field(..., description="Citation URL (must be HTTPS)")
    publisher: str = Field(..., max_length=100, description="Publisher name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Fed Holds Rates Steady",
                "url": "https://www.reuters.com/markets/fed-rates",
                "publisher": "Reuters"
            }
        }
    }


class Source(BaseModel):
    """Primary news source metadata for an article."""
    
    name: str = Field(..., max_length=100, description="Publisher name")
    url: HttpUrl = Field(..., description="Full article URL (must be HTTPS)")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Financial Times",
                "url": "https://www.ft.com/content/example",
                "published_at": "2025-12-15T08:30:00Z"
            }
        }
    }


class Article(BaseModel):
    """Individual news article with AI-generated summary."""
    
    title: str = Field(..., min_length=10, max_length=120, description="Article headline")
    summary: str = Field(..., min_length=40, max_length=500, description="AI-generated summary (2-3 sentences)")
    category: CategoryEnum = Field(..., description="News category")
    source: Source = Field(..., description="Primary source metadata")
    citations: List[Citation] = Field(..., min_length=1, max_length=3, description="Supporting citations")
    article_id: str = Field(..., pattern=r"^[a-z]+-\d{4}-\d{2}-\d{2}-(morning|evening)-\d{3}$", description="Unique article ID")

    @field_validator('summary')
    @classmethod
    def validate_summary_word_count(cls, v: str) -> str:
        """Validate summary is between 40-80 words."""
        word_count = len(v.split())
        if word_count < 20:
            raise ValueError(f"Summary must be at least 20 words (got {word_count})")
        if word_count > 100:
            raise ValueError(f"Summary must not exceed 100 words (got {word_count})")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Federal Reserve Maintains Interest Rates",
                "summary": "The Federal Reserve kept rates steady at 5.25-5.5%, citing ongoing inflation reduction progress. Tech stocks rallied 2% following the announcement.",
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
        }
    }


class LLMUsage(BaseModel):
    """Token usage tracking for cost calculation."""
    
    prompt_tokens: int = Field(..., ge=0, description="Tokens in prompt")
    completion_tokens: int = Field(..., ge=0, description="Tokens in completion")
    total_tokens: int = Field(..., ge=0, description="Total tokens used")

    @model_validator(mode='after')
    def validate_total_tokens(self):
        """Ensure total_tokens equals sum of prompt and completion tokens."""
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError(
                f"total_tokens ({self.total_tokens}) must equal "
                f"prompt_tokens ({self.prompt_tokens}) + "
                f"completion_tokens ({self.completion_tokens})"
            )
        return self


class Metadata(BaseModel):
    """Generation metadata for a bulletin."""
    
    article_count: int = Field(..., ge=1, le=10, description="Number of articles in bulletin")
    categories_distribution: Dict[CategoryEnum, int] = Field(..., description="Article count per category")
    llm_model: str = Field(default="sonar", description="LLM model used")
    llm_usage: LLMUsage = Field(..., description="Token usage statistics")
    processing_time_seconds: float = Field(..., ge=0, description="Total processing time")
    workflow_run_id: Optional[str] = Field(None, description="GitHub Actions run ID")

    @model_validator(mode='after')
    def validate_article_count_matches(self):
        """Ensure article_count matches sum of categories_distribution."""
        total = sum(self.categories_distribution.values())
        if total != self.article_count:
            raise ValueError(
                f"article_count ({self.article_count}) must match sum of "
                f"categories_distribution ({total})"
            )
        return self

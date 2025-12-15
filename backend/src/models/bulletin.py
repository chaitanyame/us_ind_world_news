"""
Bulletin data model with complete validation.

This module defines the top-level Bulletin entity that contains articles and metadata.
"""

from datetime import date as date_type, datetime
from typing import List
from pydantic import BaseModel, Field, field_validator, model_validator

from .article import Article, Metadata, RegionEnum, PeriodEnum


class Bulletin(BaseModel):
    """
    Top-level container for a news bulletin.
    
    A bulletin represents a single publication (morning or evening) for a specific
    region and date, containing 4-10 news articles with metadata.
    """
    
    id: str = Field(
        ..., 
        pattern=r"^[a-z]+-\d{4}-\d{2}-\d{2}-(morning|evening)$",
        description="Unique bulletin identifier"
    )
    region: RegionEnum = Field(..., description="Geographic region")
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Bulletin date (YYYY-MM-DD)")
    period: PeriodEnum = Field(..., description="Time period (morning/evening)")
    generated_at: datetime = Field(..., description="UTC timestamp when bulletin was generated")
    version: str = Field(default="1.0", pattern=r"^\d+\.\d+$", description="Schema version")
    articles: List[Article] = Field(..., min_length=4, max_length=10, description="News articles (4-10)")
    metadata: Metadata = Field(..., description="Generation metadata")

    @field_validator('generated_at')
    @classmethod
    def validate_generated_at_utc(cls, v: datetime) -> datetime:
        """Ensure generated_at is in UTC."""
        if v.tzinfo is None:
            raise ValueError("generated_at must include timezone information")
        return v

    @model_validator(mode='after')
    def validate_id_matches_fields(self):
        """Ensure bulletin ID matches region, date, and period."""
        expected_id = f"{self.region.value}-{self.date}-{self.period.value}"
        if self.id != expected_id:
            raise ValueError(
                f"Bulletin ID '{self.id}' does not match expected format "
                f"'{expected_id}' (region-date-period)"
            )
        return self

    @model_validator(mode='after')
    def validate_date_format(self):
        """Validate date is a valid ISO date."""
        try:
            date_type.fromisoformat(self.date)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")
        return self

    @model_validator(mode='after')
    def validate_article_count_matches_metadata(self):
        """Ensure article count matches metadata."""
        if len(self.articles) != self.metadata.article_count:
            raise ValueError(
                f"Article count mismatch: found {len(self.articles)} articles "
                f"but metadata.article_count is {self.metadata.article_count}"
            )
        return self

    @model_validator(mode='after')
    def validate_article_ids_unique(self):
        """Ensure all article IDs are unique within bulletin."""
        article_ids = [article.article_id for article in self.articles]
        if len(article_ids) != len(set(article_ids)):
            duplicates = [aid for aid in article_ids if article_ids.count(aid) > 1]
            raise ValueError(f"Duplicate article IDs found: {set(duplicates)}")
        return self

    @model_validator(mode='after')
    def validate_article_ids_match_bulletin(self):
        """Ensure article IDs start with bulletin ID."""
        for article in self.articles:
            if not article.article_id.startswith(f"{self.id}-"):
                raise ValueError(
                    f"Article ID '{article.article_id}' does not start with "
                    f"bulletin ID prefix '{self.id}-'"
                )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "usa-2025-12-15-morning",
                "region": "usa",
                "date": "2025-12-15",
                "period": "morning",
                "generated_at": "2025-12-15T12:05:32Z",
                "version": "1.0",
                "articles": [],
                "metadata": {
                    "article_count": 8,
                    "categories_distribution": {
                        "politics": 2,
                        "economy": 2,
                        "technology": 1
                    },
                    "llm_model": "sonar",
                    "llm_usage": {
                        "prompt_tokens": 245,
                        "completion_tokens": 856,
                        "total_tokens": 1101
                    },
                    "processing_time_seconds": 3.42
                }
            }
        }
    }


class BulletinWrapper(BaseModel):
    """
    Top-level wrapper matching JSON file structure.
    
    JSON files store bulletins with a 'bulletin' key at the root level.
    """
    bulletin: Bulletin

    model_config = {
        "json_schema_extra": {
            "example": {
                "bulletin": {
                    "id": "usa-2025-12-15-morning",
                    "region": "usa",
                    "date": "2025-12-15",
                    "period": "morning",
                    "generated_at": "2025-12-15T12:05:32Z",
                    "version": "1.0",
                    "articles": [],
                    "metadata": {
                        "article_count": 0,
                        "categories_distribution": {},
                        "llm_model": "sonar",
                        "llm_usage": {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0
                        },
                        "processing_time_seconds": 0.0
                    }
                }
            }
        }
    }

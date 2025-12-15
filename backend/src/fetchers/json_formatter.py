"""
JSON Formatter for Perplexity API Responses

This module converts raw Perplexity API responses into validated Bulletin objects
using Pydantic models for data integrity.
"""

import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from pydantic import ValidationError
from ..models.article import (
    Article, Source, Citation, Metadata, LLMUsage,
    RegionEnum, PeriodEnum, CategoryEnum
)
from ..models.bulletin import Bulletin, BulletinWrapper
from ..utils.logger import logger


class JSONFormatter:
    """Formatter to convert Perplexity API responses to Bulletin objects."""
    
    @staticmethod
    def _extract_domain_name(url: str) -> str:
        """
        Extract clean domain name from URL for display.
        
        Args:
            url: Full URL string
        
        Returns:
            Clean domain name (e.g., 'reuters.com' from 'https://www.reuters.com/...')
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove 'www.' prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Capitalize first letter of domain parts for display
            # e.g., 'reuters.com' -> 'Reuters.com', 'nytimes.com' -> 'Nytimes.com'
            parts = domain.split('.')
            if parts:
                parts[0] = parts[0].capitalize()
            
            return '.'.join(parts)
        except Exception:
            return "Unknown Source"
    
    def format(
        self,
        response_data: Dict[str, Any],
        region: str,
        period: str,
        date: Optional[str] = None,
        workflow_run_id: Optional[str] = None
    ) -> BulletinWrapper:
        """
        Format Perplexity API response into a validated Bulletin.
        
        Args:
            response_data: Dict from PerplexityClient.fetch_news()
            region: Geographic region (usa, india, world)
            period: Time period (morning, evening)
            date: Date in YYYY-MM-DD format (defaults to today)
            workflow_run_id: Optional GitHub Actions workflow run ID
        
        Returns:
            BulletinWrapper: Validated bulletin ready for JSON serialization
        
        Raises:
            ValueError: If response content is malformed or missing required fields
            ValidationError: If data doesn't meet Pydantic model constraints
        """
        # Default date to today
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        logger.info(
            "Formatting API response to Bulletin",
            extra={
                "region": region,
                "period": period,
                "date": date
            }
        )
        
        try:
            # Parse JSON from response content
            content = response_data.get("content", "")
            articles_data = self._extract_articles_from_content(content)
            
            # Extract citations from response
            citations_data = response_data.get("citations", [])
            
            # Create Article objects
            articles = self._create_articles(
                articles_data=articles_data,
                citations_data=citations_data,
                region=region,
                period=period,
                date=date
            )
            
            # Create Metadata
            metadata = self._create_metadata(
                articles=articles,
                usage_data=response_data.get("usage", {}),
                workflow_run_id=workflow_run_id
            )
            
            # Create Bulletin
            bulletin = Bulletin(
                id=f"{region}-{date}-{period}",
                region=RegionEnum(region),
                date=date,
                period=PeriodEnum(period),
                generated_at=datetime.now(timezone.utc).replace(microsecond=0),
                version="1.0",
                articles=articles,
                metadata=metadata
            )
            
            logger.info(
                "Successfully formatted Bulletin",
                extra={
                    "bulletin_id": bulletin.id,
                    "article_count": len(articles),
                    "categories": list(metadata.categories_distribution.keys())
                }
            )
            
            return BulletinWrapper(bulletin=bulletin)
        
        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse JSON from API response",
                extra={
                    "region": region,
                    "period": period,
                    "error": str(e),
                    "content_preview": content[:200] if content else None
                },
                exc_info=True
            )
            raise ValueError(f"Invalid JSON in API response: {e}")
        
        except ValidationError as e:
            logger.error(
                "Pydantic validation failed",
                extra={
                    "region": region,
                    "period": period,
                    "errors": e.errors()
                },
                exc_info=True
            )
            raise
        
        except Exception as e:
            logger.error(
                "Unexpected error formatting Bulletin",
                extra={
                    "region": region,
                    "period": period,
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def _extract_articles_from_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract articles array from LLM response content.
        
        Args:
            content: Raw text content from API response
        
        Returns:
            List of article dictionaries
        
        Raises:
            ValueError: If content is malformed or missing articles
        """
        if not content:
            raise ValueError("Empty content in API response")
        
        # Try to parse as JSON
        try:
            data = json.loads(content)
            
            # Handle different response formats
            if isinstance(data, dict):
                if "articles" in data:
                    articles = data["articles"]
                else:
                    # Assume the dict itself is the articles array wrapper
                    articles = [data]
            elif isinstance(data, list):
                articles = data
            else:
                raise ValueError(f"Unexpected content type: {type(data)}")
            
            if not articles:
                raise ValueError("No articles found in API response")
            
            return articles
        
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    if isinstance(data, dict) and "articles" in data:
                        return data["articles"]
                except json.JSONDecodeError:
                    pass
            
            raise ValueError("Could not extract valid JSON from API response content")
    
    def _create_articles(
        self,
        articles_data: List[Dict[str, Any]],
        citations_data: List[Dict[str, Any]],
        region: str,
        period: str,
        date: str
    ) -> List[Article]:
        """
        Create Article objects from raw data.
        
        Args:
            articles_data: List of article dictionaries from LLM
            citations_data: List of citation dictionaries from API
            region: Geographic region
            period: Time period
            date: Date string
        
        Returns:
            List of validated Article objects
        
        Raises:
            ValueError: If article count is not 5-10
        """
        # Limit to 10 articles
        articles_data = articles_data[:10]
        
        # Ensure minimum 5 articles
        if len(articles_data) < 5:
            logger.warning(
                "Fewer than 5 articles in response, this may fail validation",
                extra={
                    "article_count": len(articles_data),
                    "region": region,
                    "period": period
                }
            )
        
        articles = []
        for idx, article_data in enumerate(articles_data, start=1):
            # Generate article ID
            article_id = f"{region}-{date}-{period}-{idx:03d}"
            
            # Extract fields from article data
            title = article_data.get("title", "").strip()
            summary = article_data.get("summary", "").strip()
            category = article_data.get("category", "world").lower()
            
            # Validate category
            try:
                category_enum = CategoryEnum(category)
            except ValueError:
                logger.warning(
                    f"Invalid category '{category}' for article {article_id}, defaulting to 'world'",
                    extra={"article_id": article_id, "invalid_category": category}
                )
                category_enum = CategoryEnum.WORLD
            
            # Create Source from article data or first citation
            source = self._create_source(article_data, citations_data, idx)
            
            # Create Citations from API citations
            citations = self._create_citations(citations_data, idx)
            
            # Create Article
            article = Article(
                title=title,
                summary=summary,
                category=category_enum,
                source=source,
                citations=citations,
                article_id=article_id
            )
            
            articles.append(article)
        
        return articles
    
    def _create_source(
        self,
        article_data: Dict[str, Any],
        citations_data: List[Dict[str, Any]],
        article_index: int
    ) -> Source:
        """
        Create Source object from article or citation data.
        
        Args:
            article_data: Article dictionary from LLM
            citations_data: Citations from API
            article_index: 1-based article index
        
        Returns:
            Source object
        """
        # Try to get source from article data
        if "source" in article_data:
            source_data = article_data["source"]
            return Source(
                name=source_data.get("name", "Unknown Source"),
                url=source_data.get("url", "https://example.com"),
                published_at=source_data.get("published_at")
            )
        
        # Fall back to first citation if available
        if citations_data and len(citations_data) >= article_index:
            citation = citations_data[article_index - 1]
            
            # Handle citation as string (URL) or dict
            if isinstance(citation, str):
                # Citation is just a URL string - extract domain as name
                return Source(
                    name=self._extract_domain_name(citation),
                    url=citation,
                    published_at=None
                )
            elif isinstance(citation, dict):
                # Citation is a structured object
                url = citation.get("url", "https://example.com")
                name = citation.get("publisher") or citation.get("source")
                
                # If name is missing or "Unknown Source", extract from URL
                if not name or name == "Unknown Source":
                    name = self._extract_domain_name(url)
                
                return Source(
                    name=name,
                    url=url,
                    published_at=citation.get("publishedDate")
                )
            else:
                # Unexpected type, log and use default
                logger.warning(
                    "Unexpected citation type",
                    extra={"type": type(citation).__name__, "citation": str(citation)}
                )
                return Source(
                    name="Unknown Source",
                    url="https://example.com"
                )
        
        # Default source
        return Source(
            name="Unknown Source",
            url="https://example.com"
        )
    
    def _create_citations(
        self,
        citations_data: List[Dict[str, Any]],
        article_index: int,
        max_citations: int = 3
    ) -> List[Citation]:
        """
        Create Citation objects from API citations.
        
        Args:
            citations_data: Citations from API
            article_index: 1-based article index
            max_citations: Maximum citations per article (default: 3)
        
        Returns:
            List of Citation objects (1-3 items)
        """
        citations = []
        
        # Try to match citations to this article (simple round-robin)
        start_idx = (article_index - 1) * max_citations
        end_idx = start_idx + max_citations
        
        relevant_citations = citations_data[start_idx:end_idx] if citations_data else []
        
        for citation_data in relevant_citations:
            try:
                # Handle citation as string (URL) or dict
                if isinstance(citation_data, str):
                    # Citation is just a URL string - extract domain as publisher
                    citation = Citation(
                        title="Reference",
                        url=citation_data,
                        publisher=self._extract_domain_name(citation_data)
                    )
                elif isinstance(citation_data, dict):
                    # Citation is a structured object
                    url = citation_data.get("url", "https://example.com")
                    publisher = citation_data.get("publisher") or citation_data.get("source")
                    
                    # If publisher is missing or "Unknown", extract from URL
                    if not publisher or publisher == "Unknown":
                        publisher = self._extract_domain_name(url)
                    
                    citation = Citation(
                        title=citation_data.get("title", "Reference"),
                        url=url,
                        publisher=publisher
                    )
                else:
                    # Skip unexpected types
                    logger.warning(
                        "Skipping citation with unexpected type",
                        extra={"type": type(citation_data).__name__}
                    )
                    continue
                    
                citations.append(citation)
            except ValidationError as e:
                logger.warning(
                    "Skipping invalid citation",
                    extra={
                        "citation_data": str(citation_data),
                        "error": str(e)
                    }
                )
        
        # Ensure at least 1 citation (Pydantic requires 1-3)
        if not citations:
            logger.warning(
                "No citations available, using placeholder",
                extra={"article_index": article_index}
            )
            citations.append(Citation(
                title="Original Source",
                url="https://news.google.com",
                publisher="News Aggregator"
            ))
        
        return citations[:max_citations]
    
    def _create_metadata(
        self,
        articles: List[Article],
        usage_data: Dict[str, Any],
        workflow_run_id: Optional[str] = None
    ) -> Metadata:
        """
        Create Metadata object from articles and usage data.
        
        Args:
            articles: List of Article objects
            usage_data: Token usage from API response
            workflow_run_id: Optional GitHub Actions workflow run ID
        
        Returns:
            Metadata object
        """
        # Count articles per category
        categories_distribution = {}
        for article in articles:
            category = article.category.value
            categories_distribution[category] = categories_distribution.get(category, 0) + 1
        
        # Create LLMUsage
        llm_usage = LLMUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0)
        )
        
        return Metadata(
            article_count=len(articles),
            categories_distribution=categories_distribution,
            llm_usage=llm_usage,
            llm_model="sonar",
            processing_time_seconds=0.0,  # Will be updated by caller
            workflow_run_id=workflow_run_id
        )

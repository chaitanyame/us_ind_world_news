"""
Perplexity API Client for News Fetching

This module provides a wrapper around the OpenAI-compatible Perplexity API
to fetch and format news bulletins with citations and structured data.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from openai import OpenAI, RateLimitError, APIError
from ..utils.logger import logger
from ..utils.retry_logic import exponential_backoff_retry, MaxRetriesExceeded


class PerplexityClient:
    """Client for interacting with Perplexity API for news fetching."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.perplexity.ai",
        model: str = "sonar",
        temperature: float = 0.3,
        max_tokens: int = 1000
    ):
        """
        Initialize Perplexity API client.
        
        Args:
            api_key: Perplexity API key (defaults to PERPLEXITY_API_KEY env var)
            base_url: API base URL (defaults to Perplexity API)
            model: Model to use (default: sonar)
            temperature: Response temperature 0.0-1.0 (default: 0.3)
            max_tokens: Maximum tokens in response (default: 1000)
        """
        self.api_key = api_key or os.environ.get("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment or constructor")
        
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        logger.info(
            "Perplexity client initialized",
            extra={
                "base_url": self.base_url,
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        )
    
    @exponential_backoff_retry(
        max_retries=3,
        base_delay=1.0,
        exceptions=(RateLimitError, APIError)
    )
    def fetch_news(
        self,
        region: str,
        period: str,
        date: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch news from Perplexity API with retry logic.
        
        Args:
            region: Geographic region (usa, india, world)
            period: Time period (morning, evening)
            date: Date in YYYY-MM-DD format (defaults to today)
            system_prompt: Optional system prompt override
            user_prompt: Optional user prompt override
        
        Returns:
            Dict containing API response with articles and citations
        
        Raises:
            MaxRetriesExceeded: If all retry attempts fail
            ValueError: If region or period is invalid
        """
        # Validate inputs
        valid_regions = ["usa", "india", "world"]
        valid_periods = ["morning", "evening"]
        
        if region not in valid_regions:
            raise ValueError(f"Invalid region: {region}. Must be one of {valid_regions}")
        
        if period not in valid_periods:
            raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
        
        # Default date to today
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        logger.info(
            "Fetching news from Perplexity API",
            extra={
                "region": region,
                "period": period,
                "date": date
            }
        )
        
        # Construct prompts (using defaults if not provided)
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt(region)
        
        if user_prompt is None:
            user_prompt = self._get_default_user_prompt(region, period, date)
        
        try:
            # Make API call with search recency filter
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                # Perplexity-specific parameters
                search_recency_filter="day",  # Only today's news
                return_citations=True,
                return_images=False
            )
            
            logger.info(
                "Successfully fetched news from Perplexity API",
                extra={
                    "region": region,
                    "period": period,
                    "response_tokens": getattr(response.usage, "total_tokens", 0) if hasattr(response, "usage") else 0
                }
            )
            
            return self._extract_response_data(response)
        
        except (RateLimitError, APIError) as e:
            logger.warning(
                "API error occurred, will retry",
                extra={
                    "region": region,
                    "period": period,
                    "error_type": type(e).__name__,
                    "error": str(e)
                }
            )
            raise  # Re-raise to trigger retry logic
        
        except Exception as e:
            logger.error(
                "Unexpected error fetching news",
                extra={
                    "region": region,
                    "period": period,
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
    
    def _extract_response_data(self, response) -> Dict[str, Any]:
        """
        Extract structured data from API response.
        
        Args:
            response: OpenAI ChatCompletion response object
        
        Returns:
            Dict with content, citations, and usage data
        """
        data = {
            "content": "",
            "citations": [],
            "usage": {}
        }
        
        # Extract message content
        if response.choices and len(response.choices) > 0:
            data["content"] = response.choices[0].message.content
        
        # Extract citations (if available in response)
        if hasattr(response, "citations"):
            data["citations"] = response.citations
        
        # Extract usage statistics
        if hasattr(response, "usage") and response.usage:
            data["usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return data
    
    def _get_default_system_prompt(self, region: str) -> str:
        """Get default system prompt for a region."""
        audience_map = {
            "usa": "American",
            "india": "Indian",
            "world": "global"
        }
        
        audience = audience_map.get(region, "general")
        
        return f"""You are a professional news curator for a {audience} audience. Your task is to search the web for the most important breaking news stories and create concise, factual summaries suitable for a news brief.

Guidelines:
- Focus on verified information from major news outlets
- Prioritize stories with high public impact
- Avoid speculation or opinion
- If fewer than 10 stories are available, return what you find
- Never fabricate information if sources are unavailable
- Format response as JSON with an 'articles' array containing objects with 'title', 'summary', and 'category' fields"""
    
    def _get_default_user_prompt(self, region: str, period: str, date: str) -> str:
        """Get default user prompt for a region/period."""
        region_name = {
            "usa": "United States",
            "india": "India",
            "world": "around the world"
        }[region]
        
        time_context = {
            "morning": "today",
            "evening": "today's developments"
        }[period]
        
        return f"""Search the web and identify the top 10 breaking news stories in {region_name} for {time_context} ({date}).

For each story, provide:
1. Title (max 12 words, attention-grabbing but factual)
2. Summary (2-3 sentences, 40-60 words, covering who/what/when/where/why)
3. Category (select ONE from: politics, economy, technology, business, sports, health, environment, science, world)

Requirements:
- Only include stories published within the last 24 hours
- Prioritize stories with high national/international significance
- Prefer articles from established news outlets
- Ensure summaries are self-contained (readable without clicking through)
- If fewer than 10 stories meet criteria, return available stories only

Return response as JSON: {{"articles": [{{"title": "...", "summary": "...", "category": "..."}}]}}"""

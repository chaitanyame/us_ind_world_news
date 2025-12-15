"""
Perplexity API Client for News Fetching

This module provides a wrapper around the OpenAI-compatible Perplexity API
to fetch and format news bulletins with citations and structured data.
"""

import os
from datetime import datetime, timezone
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
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
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
            # Make API call to Perplexity
            # Note: Citations are requested in the prompt and will be in the JSON response
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
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
            
            # Try to extract citations from message object (Perplexity-specific)
            message = response.choices[0].message
            if hasattr(message, "citations"):
                data["citations"] = message.citations
        
        # Also check top-level citations attribute
        if hasattr(response, "citations") and response.citations:
            data["citations"] = response.citations
        
        # Log citation info for debugging
        if data["citations"]:
            logger.info(
                "Extracted citations from Perplexity API response",
                extra={
                    "citation_count": len(data["citations"]),
                    "sample_citation": str(data["citations"][0])[:100] if data["citations"] else None
                }
            )
        else:
            logger.warning(
                "No citations found in Perplexity API response",
                extra={
                    "has_message_citations": hasattr(response.choices[0].message, "citations") if response.choices else False,
                    "has_response_citations": hasattr(response, "citations")
                }
            )
        
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
        
        return f"""You are a professional news curator for a {audience} audience. Your task is to search the web for the most important, substantive news stories and create concise, factual summaries suitable for a news brief.

Guidelines:
- Focus on verified information from major news outlets
- Prioritize stories with high public impact and substantive developments
- IMPORTANT: Focus on important news delivery, NOT sensationalism or clickbait
- Avoid celebrity gossip, viral content, and minor controversies unless nationally significant
- Avoid speculation, opinion, or inflammatory language
- Only include stories with significant new developments (avoid rehashing old news)
- If fewer than 10 stories are available, return what you find
- Never fabricate information if sources are unavailable
- Include 1-3 source citations for each article with actual article titles and URLs from your search results
- Format response as JSON with an 'articles' array containing objects with 'title', 'summary', 'category', and 'citations' fields"""
    
    def _get_default_user_prompt(self, region: str, period: str, date: str) -> str:
        """Get default user prompt for a region/period."""
        region_name = {
            "usa": "United States",
            "india": "India",
            "world": "around the world"
        }[region]
        
        if period == "morning":
            time_context = "overnight developments from 9 PM yesterday to 7 AM today"
            time_window = "published between 9 PM yesterday and 7 AM today"
            focus_note = "Focus on overnight developments, breaking news, and stories that emerged after 9 PM yesterday. DO NOT include stories from yesterday's daytime (7 AM - 9 PM) as those were covered in the evening bulletin."
        else:  # evening
            time_context = "today's daytime developments from 7 AM to 9 PM"
            time_window = "published between 7 AM and 9 PM today"
            focus_note = "Focus on today's daytime developments and breaking news. DO NOT include stories from last night's bulletin (9 PM yesterday - 7 AM today) unless there are significant NEW developments."
        
        return f"""Search the web and identify the top 10 most important news stories in {region_name} for {time_context} ({date}).

For each story, provide:
1. Title (max 12 words, factual and informative, NOT sensationalized)
2. Summary (2-3 sentences, 40-60 words, covering who/what/when/where/why)
3. Category (select ONE from: politics, economy, technology, business, sports, health, environment, science, world)
4. Citations (1-3 sources with title, url, and publisher from your search results)

Requirements:
- Only include stories {time_window}
- {focus_note}
- Prioritize substantive stories with high public impact (policy changes, major economic news, significant events)
- AVOID: Celebrity gossip, viral social media content, minor scandals, clickbait
- AVOID: Repeating stories from previous bulletin unless there are major new developments
- Prefer articles from established, credible news outlets
- Ensure summaries are self-contained (readable without clicking through)
- Include actual source citations from your web search results for each article
- If fewer than 10 stories meet criteria, return available stories only
- Focus on important news delivery, not sensationalism

Return response as JSON:
{{
  "articles": [
    {{
      "title": "Article headline here",
      "summary": "2-3 sentence summary covering the key details",
      "category": "politics",
      "citations": [
        {{"title": "Source article title", "url": "https://source-url.com/article", "publisher": "Publisher Name"}},
        {{"title": "Another source", "url": "https://another-source.com", "publisher": "Another Publisher"}}
      ]
    }}
  ]
}}"""

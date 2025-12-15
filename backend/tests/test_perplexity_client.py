"""
Integration tests for Perplexity API client.

Tests API client configuration, request construction, response parsing,
and error handling with mocked API responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from openai import RateLimitError, APIError
from src.fetchers.perplexity_client import PerplexityClient
from src.utils.retry_logic import MaxRetriesExceeded


class TestPerplexityClient:
    """Test Perplexity API client functionality."""
    
    def test_client_initialization(self):
        """Test client initializes with correct configuration."""
        client = PerplexityClient(
            api_key="test_key",
            model="sonar",
            temperature=0.3,
            max_tokens=1000
        )
        
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.perplexity.ai"
        assert client.model == "sonar"
        assert client.temperature == 0.3
        assert client.max_tokens == 1000
    
    def test_client_uses_env_var_for_api_key(self, monkeypatch):
        """Test client reads API key from environment."""
        monkeypatch.setenv("PERPLEXITY_API_KEY", "env_test_key")
        
        client = PerplexityClient()
        
        assert client.api_key == "env_test_key"
    
    def test_client_raises_without_api_key(self, monkeypatch):
        """Test client raises ValueError if API key is missing."""
        monkeypatch.delenv("PERPLEXITY_API_KEY", raising=False)
        
        with pytest.raises(ValueError) as exc_info:
            PerplexityClient()
        
        assert "PERPLEXITY_API_KEY" in str(exc_info.value)
    
    def test_fetch_news_validates_region(self):
        """Test fetch_news validates region parameter."""
        client = PerplexityClient(api_key="test_key")
        
        with pytest.raises(ValueError) as exc_info:
            client.fetch_news(region="invalid", period="morning")
        
        assert "Invalid region" in str(exc_info.value)
    
    def test_fetch_news_validates_period(self):
        """Test fetch_news validates period parameter."""
        client = PerplexityClient(api_key="test_key")
        
        with pytest.raises(ValueError) as exc_info:
            client.fetch_news(region="usa", period="invalid")
        
        assert "Invalid period" in str(exc_info.value)
    
    @patch('src.fetchers.perplexity_client.OpenAI')
    def test_fetch_news_constructs_correct_request(self, mock_openai_class):
        """Test fetch_news constructs API request with correct parameters."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"articles": []}'
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 300
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create client and fetch
        client = PerplexityClient(api_key="test_key")
        client.fetch_news(region="usa", period="morning", date="2025-12-15")
        
        # Verify API call
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        
        assert call_kwargs["model"] == "sonar"
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 1000
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["role"] == "system"
        assert call_kwargs["messages"][1]["role"] == "user"
        assert "2025-12-15" in call_kwargs["messages"][1]["content"]
    
    @patch('src.fetchers.perplexity_client.OpenAI')
    def test_fetch_news_extracts_response_data(self, mock_openai_class):
        """Test fetch_news extracts data from API response."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"articles": [{"title": "Test"}]}'
        mock_response.citations = [{"title": "Ref", "url": "https://example.com"}]
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 200
        mock_response.usage.total_tokens = 300
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Fetch
        client = PerplexityClient(api_key="test_key")
        result = client.fetch_news(region="usa", period="morning")
        
        # Verify extraction
        assert "content" in result
        assert "citations" in result
        assert "usage" in result
        assert '{"articles": [{"title": "Test"}]}' in result["content"]
        assert result["usage"]["prompt_tokens"] == 100
        assert result["usage"]["completion_tokens"] == 200
        assert result["usage"]["total_tokens"] == 300
    
    @patch('src.fetchers.perplexity_client.OpenAI')
    def test_fetch_news_retries_on_rate_limit(self, mock_openai_class):
        """Test fetch_news retries on RateLimitError."""
        # Setup mock to fail twice then succeed
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_success = MagicMock()
        mock_success.choices = [MagicMock()]
        mock_success.choices[0].message.content = '{"articles": []}'
        mock_success.usage = MagicMock()
        mock_success.usage.prompt_tokens = 100
        mock_success.usage.completion_tokens = 200
        mock_success.usage.total_tokens = 300
        
        mock_client.chat.completions.create.side_effect = [
            RateLimitError("Rate limit", response=Mock(), body=None),
            RateLimitError("Rate limit", response=Mock(), body=None),
            mock_success
        ]
        
        # Fetch with retry
        client = PerplexityClient(api_key="test_key")
        
        with patch('time.sleep'):  # Skip actual sleep
            result = client.fetch_news(region="usa", period="morning")
        
        # Should succeed after 2 retries
        assert "content" in result
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('src.fetchers.perplexity_client.OpenAI')
    def test_fetch_news_raises_after_max_retries(self, mock_openai_class):
        """Test fetch_news raises MaxRetriesExceeded after exhausting retries."""
        # Setup mock to always fail
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_client.chat.completions.create.side_effect = RateLimitError(
            "Rate limit",
            response=Mock(),
            body=None
        )
        
        # Fetch
        client = PerplexityClient(api_key="test_key")
        
        with patch('time.sleep'):  # Skip actual sleep
            with pytest.raises(MaxRetriesExceeded):
                client.fetch_news(region="usa", period="morning")
        
        # Should fail after 3 attempts
        assert mock_client.chat.completions.create.call_count == 3
    
    @patch('src.fetchers.perplexity_client.OpenAI')
    def test_fetch_news_with_custom_prompts(self, mock_openai_class):
        """Test fetch_news accepts custom system and user prompts."""
        # Setup mock
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"articles": []}'
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 50
        mock_response.usage.completion_tokens = 100
        mock_response.usage.total_tokens = 150
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Fetch with custom prompts
        client = PerplexityClient(api_key="test_key")
        client.fetch_news(
            region="usa",
            period="morning",
            system_prompt="Custom system prompt",
            user_prompt="Custom user prompt"
        )
        
        # Verify custom prompts used
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["messages"][0]["content"] == "Custom system prompt"
        assert call_kwargs["messages"][1]["content"] == "Custom user prompt"
    
    def test_get_default_system_prompt(self):
        """Test default system prompt generation."""
        client = PerplexityClient(api_key="test_key")
        
        usa_prompt = client._get_default_system_prompt("usa")
        india_prompt = client._get_default_system_prompt("india")
        world_prompt = client._get_default_system_prompt("world")
        
        assert "American" in usa_prompt
        assert "Indian" in india_prompt
        assert "global" in world_prompt
        assert "news curator" in usa_prompt
    
    def test_get_default_user_prompt(self):
        """Test default user prompt generation."""
        client = PerplexityClient(api_key="test_key")
        
        prompt = client._get_default_user_prompt("usa", "morning", "2025-12-15")
        
        assert "United States" in prompt
        assert "2025-12-15" in prompt
        assert "top 10" in prompt
        assert "breaking news" in prompt

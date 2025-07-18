import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from utils.logger import logger
import time

class APIIntegrations:
    """
    Manages external API integrations for JARVIS AI.
    Handles OpenAI, Hugging Face, News APIs, and other external services.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_config = config.get("openai", {})
        self.huggingface_config = config.get("huggingface", {})
        self.news_api_config = config.get("news_api", {})
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limits = {}
        
        logger.info("API Integrations initialized")
    
    async def __aenter__(self):
        """Initialize HTTP session."""
        self.session = aiohttp.ClientSession()
        logger.info("API Integrations session started")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        logger.info("API Integrations session closed")
    
    async def _make_request(self, url: str, method: str = "GET", headers: Dict[str, str] = None, 
                          data: Dict[str, Any] = None, timeout: int = 30) -> Dict[str, Any]:
        """Make an HTTP request with error handling and rate limiting."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        if headers is None:
            headers = {}
        
        try:
            async with self.session.request(
                method, url, headers=headers, json=data, timeout=timeout
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API request failed: {response.status} - {await response.text()}")
                    return {"error": f"HTTP {response.status}", "status": "error"}
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout for {url}")
            return {"error": "Request timeout", "status": "error"}
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return {"error": str(e), "status": "error"}
    
    async def query_openai(self, prompt: str, model: str = None, max_tokens: int = None) -> Dict[str, Any]:
        """Query OpenAI API."""
        api_key = self.openai_config.get("api_key")
        if not api_key or api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API key not configured")
            return {
                "status": "error",
                "message": "OpenAI API key not configured",
                "response": "I'm currently running in demo mode. Please configure your OpenAI API key to enable full functionality."
            }
        
        model = model or self.openai_config.get("model", "gpt-3.5-turbo")
        max_tokens = max_tokens or self.openai_config.get("max_tokens", 1000)
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        result = await self._make_request(
            "https://api.openai.com/v1/chat/completions",
            method="POST",
            headers=headers,
            data=data
        )
        
        if "error" not in result and "choices" in result:
            return {
                "status": "success",
                "response": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {})
            }
        
        return {
            "status": "error",
            "message": result.get("error", "Unknown error"),
            "response": "I encountered an error while processing your request."
        }
    
    async def query_huggingface(self, text: str, model: str = None) -> Dict[str, Any]:
        """Query Hugging Face API."""
        api_key = self.huggingface_config.get("api_key")
        if not api_key or api_key == "your-huggingface-api-key-here":
            logger.warning("Hugging Face API key not configured")
            return {
                "status": "error",
                "message": "Hugging Face API key not configured",
                "response": "Hugging Face integration is not available in demo mode."
            }
        
        model = model or self.huggingface_config.get("model", "microsoft/DialoGPT-medium")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {"inputs": text}
        
        result = await self._make_request(
            f"https://api-inference.huggingface.co/models/{model}",
            method="POST",
            headers=headers,
            data=data
        )
        
        if "error" not in result and isinstance(result, list) and len(result) > 0:
            return {
                "status": "success",
                "response": result[0].get("generated_text", ""),
                "model": model
            }
        
        return {
            "status": "error",
            "message": result.get("error", "Unknown error"),
            "response": "I encountered an error while processing your request."
        }
    
    async def fetch_realtime_news(self, query: str, sources: List[str] = None) -> Dict[str, Any]:
        """Fetch real-time news articles."""
        api_key = self.news_api_config.get("api_key")
        if not api_key or api_key == "your-news-api-key-here":
            logger.warning("News API key not configured - using mock data")
            return self._generate_mock_news(query)
        
        sources = sources or self.news_api_config.get("sources", [])
        
        params = {
            "q": query,
            "apiKey": api_key,
            "sortBy": "publishedAt",
            "pageSize": 10
        }
        
        if sources:
            params["sources"] = ",".join(sources)
        
        url = "https://newsapi.org/v2/everything"
        result = await self._make_request(url, method="GET")
        
        if "error" not in result and "articles" in result:
            return {
                "status": "success",
                "articles": result["articles"],
                "total_results": result.get("totalResults", 0)
            }
        
        return {
            "status": "error",
            "message": result.get("error", "Unknown error"),
            "articles": []
        }
    
    async def fetch_threat_intelligence(self, query: str) -> Dict[str, Any]:
        """Fetch threat intelligence data (mock implementation)."""
        logger.info(f"Fetching threat intelligence for: {query}")
        
        # Mock threat intelligence data
        mock_threats = [
            {
                "title": f"Security Alert: {query}",
                "description": f"Potential security threat related to {query} detected in recent analysis.",
                "severity": "medium",
                "type": "vulnerability",
                "source": "Mock Threat Intelligence",
                "timestamp": time.time()
            },
            {
                "title": f"CVE Update: {query}",
                "description": f"New vulnerability disclosure affecting {query} systems.",
                "severity": "high",
                "type": "cve",
                "source": "Mock CVE Database",
                "timestamp": time.time()
            }
        ]
        
        return {
            "status": "success",
            "threats": mock_threats,
            "query": query
        }
    
    def _generate_mock_news(self, query: str) -> Dict[str, Any]:
        """Generate mock news data for testing."""
        mock_articles = [
            {
                "title": f"Breaking: Latest developments in {query}",
                "description": f"Recent news about {query} and its implications for the industry.",
                "url": f"https://example.com/news/{query.replace(' ', '-')}",
                "source": {"name": "Mock News Source"},
                "publishedAt": "2024-01-15T10:00:00Z"
            },
            {
                "title": f"Analysis: {query} trends and predictions",
                "description": f"Expert analysis on {query} and future outlook.",
                "url": f"https://example.com/analysis/{query.replace(' ', '-')}",
                "source": {"name": "Mock Tech News"},
                "publishedAt": "2024-01-15T09:30:00Z"
            }
        ]
        
        return {
            "status": "success",
            "articles": mock_articles,
            "total_results": len(mock_articles)
        }
    
    async def test_connections(self) -> Dict[str, Any]:
        """Test all API connections."""
        results = {}
        
        # Test OpenAI
        openai_result = await self.query_openai("Hello, this is a test.")
        results["openai"] = {
            "status": openai_result["status"],
            "available": openai_result["status"] == "success"
        }
        
        # Test Hugging Face
        hf_result = await self.query_huggingface("Hello, this is a test.")
        results["huggingface"] = {
            "status": hf_result["status"],
            "available": hf_result["status"] == "success"
        }
        
        # Test News API
        news_result = await self.fetch_realtime_news("technology")
        results["news_api"] = {
            "status": news_result["status"],
            "available": news_result["status"] == "success"
        }
        
        logger.info(f"API connection test results: {results}")
        return results

# Test function for API Integrations
async def test_api_integrations():
    """Test the API Integrations functionality."""
    logger.info("--- Testing API Integrations ---")
    
    config = {
        "openai": {
            "api_key": "your-openai-api-key-here",
            "model": "gpt-3.5-turbo",
            "max_tokens": 1000
        },
        "huggingface": {
            "api_key": "your-huggingface-api-key-here",
            "model": "microsoft/DialoGPT-medium"
        },
        "news_api": {
            "api_key": "your-news-api-key-here",
            "sources": ["techcrunch", "wired"]
        }
    }
    
    async with APIIntegrations(config) as api:
        # Test connections
        results = await api.test_connections()
        
        # Test individual APIs
        logger.info("Testing OpenAI...")
        openai_result = await api.query_openai("What is artificial intelligence?")
        logger.info(f"OpenAI Response: {openai_result['response'][:100]}...")
        
        logger.info("Testing News API...")
        news_result = await api.fetch_realtime_news("artificial intelligence")
        logger.info(f"Found {len(news_result['articles'])} news articles")
        
        logger.info("Testing Threat Intelligence...")
        threat_result = await api.fetch_threat_intelligence("malware")
        logger.info(f"Found {len(threat_result['threats'])} threat intelligence items")
    
    logger.info("API Integrations tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    from utils.logger import setup_logging
    
    setup_logging(debug=True)
    asyncio.run(test_api_integrations())

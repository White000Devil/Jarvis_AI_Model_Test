import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from utils.logger import logger

class APIIntegrations:
    """
    Manages integrations with external APIs for various functionalities
    like security tools, external knowledge bases, or operational systems.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_api_key = config["API_KEYS"].get("OPENAI_API_KEY")
        self.huggingface_api_key = config["API_KEYS"].get("HUGGINGFACE_API_KEY")
        self.client = httpx.AsyncClient() # Asynchronous HTTP client
        self.api_stats: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request_timestamp": None
        }
        logger.info("API Integrations initialized.")

    async def __aenter__(self):
        """Context manager entry point."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        await self.client.aclose()

    async def _make_request(self, method: str, url: str, headers: Dict = None, json_data: Dict = None, params: Dict = None) -> Optional[Dict[str, Any]]:
        """Helper method to make an asynchronous HTTP request."""
        self.api_stats["total_requests"] += 1
        self.api_stats["last_request_timestamp"] = datetime.now().isoformat()
        
        try:
            response = await self.client.request(method, url, headers=headers, json=json_data, params=params, timeout=30.0)
            response.raise_for_status() # Raise an exception for 4xx or 5xx status codes
            self.api_stats["successful_requests"] += 1
            logger.debug(f"API request to {url} successful.")
            return response.json()
        except httpx.RequestError as e:
            self.api_stats["failed_requests"] += 1
            logger.error(f"API request to {url} failed: {e}")
            return {"error": str(e), "status": "request_failed"}
        except httpx.HTTPStatusError as e:
            self.api_stats["failed_requests"] += 1
            logger.error(f"API request to {url} returned HTTP error {e.response.status_code}: {e.response.text}")
            return {"error": e.response.text, "status": "http_error", "status_code": e.response.status_code}
        except Exception as e:
            self.api_stats["failed_requests"] += 1
            logger.error(f"An unexpected error occurred during API request to {url}: {e}")
            return {"error": str(e), "status": "unexpected_error"}

    async def security_analysis(self, target: str, analysis_type: str = "vulnerability_scan") -> Dict[str, Any]:
        """
        Simulates calling an external security analysis API.
        In a real scenario, this would integrate with tools like Nessus, Qualys, etc.
        """
        logger.info(f"Initiating security analysis ({analysis_type}) for target: {target}")
        
        # Example: Mock API call to a vulnerability scanner
        mock_api_url = "https://mock-security-scanner.com/api/v1/scan"
        headers = {"Authorization": f"Bearer {self.config['API_KEYS'].get('SECURITY_SCANNER_API_KEY', 'mock_key')}"}
        payload = {"target": target, "type": analysis_type}
        
        # Simulate a real API call
        response = await self._make_request("POST", mock_api_url, headers=headers, json_data=payload)
        
        if response and response.get("status") == "success":
            logger.info(f"Security analysis for {target} completed successfully (mock).")
            return {"status": "completed", "results": {"vulnerabilities_found": 2, "severity": "medium"}}
        else:
            logger.warning(f"Security analysis for {target} failed (mock). Reason: {response.get('error', 'Unknown')}")
            return {"status": "failed", "reason": response.get("error", "Mock analysis failed.")}

    async def get_external_knowledge(self, query: str, source: str = "wikipedia") -> Optional[str]:
        """
        Simulates fetching knowledge from an external source like Wikipedia or a specialized database.
        """
        logger.info(f"Fetching external knowledge for '{query}' from {source} (mock).")
        
        # Example: Mock API call to a knowledge base
        mock_api_url = f"https://mock-knowledge-base.com/api/search?q={query}&source={source}"
        response = await self._make_request("GET", mock_api_url)
        
        if response and response.get("status") == "success" and response.get("data"):
            logger.info(f"External knowledge for '{query}' retrieved successfully (mock).")
            return response["data"]["content"]
        else:
            logger.warning(f"Failed to retrieve external knowledge for '{query}' from {source} (mock).")
            return None

    async def send_notification(self, recipient: str, message: str, channel: str = "email") -> bool:
        """
        Simulates sending a notification via an external service (e.g., email, Slack).
        """
        logger.info(f"Sending notification to {recipient} via {channel}: '{message}' (mock).")
        
        # Example: Mock API call to a notification service
        mock_api_url = "https://mock-notification-service.com/api/send"
        payload = {"recipient": recipient, "message": message, "channel": channel}
        response = await self._make_request("POST", mock_api_url, json_data=payload)
        
        if response and response.get("status") == "sent":
            logger.info(f"Notification sent successfully to {recipient} (mock).")
            return True
        else:
            logger.warning(f"Failed to send notification to {recipient} (mock).")
            return False

    def get_api_stats(self) -> Dict[str, Any]:
        """Returns statistics about API call usage."""
        return self.api_stats

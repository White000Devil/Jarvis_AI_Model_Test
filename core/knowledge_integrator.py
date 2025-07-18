import asyncio
import aiohttp
from typing import Dict, Any, List
from utils.logger import logger
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
import time
import json
import os

class KnowledgeIntegrator:
    """
    Integrates various knowledge sources into JARVIS's memory.
    Includes web scraping and real-time feed monitoring.
    """
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager, api_integrations: APIIntegrations):
        self.config = config
        self.memory_manager = memory_manager
        self.api_integrations = api_integrations
        self.scraping_enabled = config.get("scraping_enabled", False)
        self.scraping_sources = config.get("scraping_sources", [])
        self.max_scraped_items_per_run = config.get("max_scraped_items_per_run", 50)
        self.scraping_log_path = config.get("scraping_log_path")

        self.realtime_feeds_config = config.get("realtime_feeds", {})
        self.realtime_feeds_enabled = self.realtime_feeds_config.get("enabled", False)
        self.realtime_feed_sources = self.realtime_feeds_config.get("sources", [])

        logger.info(f"Knowledge Integrator initialized. Scraping: {self.scraping_enabled}, Real-time Feeds: {self.realtime_feeds_enabled}")

    async def scrape_and_integrate_security_data(self, max_items: int = None) -> Dict[str, Any]:
        """
        Performs web scraping on predefined security sources and integrates data into memory.
        """
        if not self.scraping_enabled:
            logger.info("Web scraping is disabled in configuration.")
            return {"status": "disabled", "message": "Web scraping is disabled."}

        logger.info(f"Starting web scraping for security data from {len(self.scraping_sources)} sources...")
        scraped_count = 0
        failed_count = 0
        
        if max_items is None:
            max_items = self.max_scraped_items_per_run

        for url in self.scraping_sources:
            try:
                logger.debug(f"Scraping: {url}")
                # Simulate web scraping (in a real scenario, use libraries like BeautifulSoup, Playwright)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
                        response.raise_for_status()
                        html_content = await response.text()
                
                # Very basic content extraction for demonstration
                # In a real scenario, parse HTML to extract meaningful text
                content = f"Content from {url}: {html_content[:500]}..." # Take first 500 chars
                title = f"Scraped Data from {url}"
                
                # Integrate into security knowledge memory
                await self.memory_manager.add_security_knowledge(
                    content=content,
                    metadata={"source_url": url, "title": title, "timestamp": time.time()}
                )
                scraped_count += 1
                logger.debug(f"Successfully scraped and integrated data from {url}")

                if scraped_count >= max_items:
                    logger.info(f"Reached max scraped items ({max_items}). Stopping.")
                    break

            except aiohttp.ClientError as e:
                logger.error(f"Failed to scrape {url} due to network/HTTP error: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"An unexpected error occurred while scraping {url}: {e}")
                failed_count += 1
        
        summary = {
            "status": "completed",
            "scraped_items": scraped_count,
            "failed_items": failed_count,
            "timestamp": time.time()
        }
        logger.info(f"Web scraping completed. Summary: {summary}")
        if self.scraping_log_path:
            self._log_scraping_run(summary)
        return summary

    async def integrate_structured_data(self, data_list: List[Dict[str, Any]], source: str, data_type: str = "general"):
        """
        Integrates structured data into the appropriate memory collection.
        """
        logger.info(f"Integrating {len(data_list)} structured data items from {source} (type: {data_type})")
        
        for item in data_list:
            content = item.get("content", str(item))
            metadata = {
                "source": source,
                "data_type": data_type,
                "timestamp": time.time()
            }
            metadata.update(item.get("metadata", {}))
            
            if data_type == "security":
                await self.memory_manager.add_security_knowledge(content, metadata)
            else:
                await self.memory_manager.add_knowledge(content, metadata)
        
        logger.info(f"Successfully integrated {len(data_list)} items into memory")

    async def monitor_realtime_feeds(self) -> Dict[str, Any]:
        """
        Monitors configured real-time feeds (e.g., security news, threat intelligence)
        and integrates new data into memory.
        """
        if not self.realtime_feeds_enabled:
            logger.info("Real-time feeds are disabled in configuration.")
            return {"status": "disabled", "message": "Real-time feeds are disabled."}

        logger.info(f"Monitoring {len(self.realtime_feed_sources)} real-time feeds...")
        integrated_count = 0
        failed_count = 0

        for feed in self.realtime_feed_sources:
            feed_name = feed.get("name", "unknown_feed")
            feed_type = feed.get("type")
            query = feed.get("query")

            if not feed_type or not query:
                logger.warning(f"Skipping malformed feed configuration: {feed}")
                failed_count += 1
                continue

            try:
                if feed_type == "security_news":
                    logger.debug(f"Fetching security news for '{query}'...")
                    result = await self.api_integrations.fetch_realtime_news(query)
                    if result["status"] == "success" and result["articles"]:
                        for article in result["articles"]:
                            content = f"News Article: {article.get('title', '')}\n{article.get('description', '')}\n{article.get('url', '')}"
                            await self.memory_manager.add_security_knowledge(
                                content=content,
                                metadata={"source": article.get("source"), "title": article.get("title"), "url": article.get("url"), "feed_type": feed_type, "timestamp": time.time()}
                            )
                            integrated_count += 1
                        logger.debug(f"Integrated {len(result['articles'])} security news articles from {feed_name}.")
                    else:
                        logger.warning(f"No security news found or failed to fetch for '{query}': {result.get('message', '')}")
                        failed_count += 1

                elif feed_type == "threat_intelligence":
                    logger.debug(f"Fetching threat intelligence for '{query}'...")
                    result = await self.api_integrations.fetch_threat_intelligence(query)
                    if result["status"] == "success" and result["threats"]:
                        for threat in result["threats"]:
                            content = f"Threat Intelligence: {threat.get('title', '')}\n{threat.get('description', '')}"
                            await self.memory_manager.add_security_knowledge(
                                content=content,
                                metadata={"source": threat.get("source"), "title": threat.get("title"), "type": threat.get("type"), "severity": threat.get("severity"), "feed_type": feed_type, "timestamp": time.time()}
                            )
                            integrated_count += 1
                        logger.debug(f"Integrated {len(result['threats'])} threat intelligence items from {feed_name}.")
                    else:
                        logger.warning(f"No threat intelligence found or failed to fetch for '{query}': {result.get('message', '')}")
                        failed_count += 1
                else:
                    logger.warning(f"Unsupported real-time feed type: {feed_type}")
                    failed_count += 1

            except Exception as e:
                logger.error(f"Error processing real-time feed '{feed_name}': {e}")
                failed_count += 1
        
        summary = {
            "status": "completed",
            "integrated_items": integrated_count,
            "failed_feeds": failed_count,
            "timestamp": time.time()
        }
        logger.info(f"Real-time feed monitoring completed. Summary: {summary}")
        return summary

    def _log_scraping_run(self, summary: Dict[str, Any]):
        """Logs a summary of a scraping run to a JSONL file."""
        if not self.scraping_log_path:
            return
        try:
            with open(self.scraping_log_path, 'a') as f:
                json.dump(summary, f)
                f.write('\n')
            logger.debug(f"Logged scraping run to {self.scraping_log_path}")
        except Exception as e:
            logger.error(f"Failed to log scraping run: {e}")

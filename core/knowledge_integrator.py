import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger import logger
from core.memory_manager import MemoryManager # Assuming MemoryManager handles storage
from core.api_integrations import APIIntegrations # Import APIIntegrations

class KnowledgeIntegrator:
    """
    Integrates various sources of knowledge into JARVIS AI's memory.
    This includes structured data, unstructured text, and real-time feeds.
    """
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager, api_integrations: APIIntegrations):
        self.config = config
        self.memory_manager = memory_manager
        self.api_integrations = api_integrations # Store APIIntegrations instance
        self.security_data_sources = config.get("scraping_sources", []) # Renamed from SECURITY_DATA_SOURCES
        self.realtime_feed_configs = config.get("realtime_feeds", {}).get("sources", []) # New: for real-time feeds
        self.max_scraped_items_per_run = config.get("max_scraped_items_per_run", 50)
        logger.info("Knowledge Integrator initialized.")

    async def integrate_structured_data(self, data: List[Dict[str, Any]], source: str, data_type: str = "general"):
        """
        Integrates structured data (e.g., from databases, APIs) into memory.
        """
        logger.info(f"Integrating {len(data)} structured items from {source} (type: {data_type})...")
        for item in data:
            title = item.get("title", f"Structured Data from {source}")
            content = item.get("content", str(item)) # Convert dict to string if no content field
            tags = item.get("tags", [])
            
            if data_type == "security":
                await self.memory_manager.add_security_knowledge(title, content, source, item.get("vulnerability_type", "general"))
            else:
                await self.memory_manager.add_knowledge_article(title, content, source, tags)
        logger.info(f"Finished integrating structured data from {source}.")

    async def integrate_unstructured_text(self, text: str, source: str, title: str, tags: List[str] = None):
        """
        Integrates unstructured text (e.g., documents, articles) into memory.
        """
        logger.info(f"Integrating unstructured text '{title}' from {source}...")
        await self.memory_manager.add_knowledge_article(title, text, source, tags)
        logger.info(f"Finished integrating unstructured text '{title}'.")

    async def update_from_realtime_feed(self, feed_type: str, query: str = None):
        """
        Processes and integrates data from real-time feeds using APIIntegrations.
        """
        logger.info(f"Processing real-time feed of type '{feed_type}' with query '{query}'...")
        
        if feed_type == "security_news":
            news_data = await self.api_integrations.fetch_realtime_news(query or "cybersecurity")
            if news_data and news_data.get("articles"):
                for article in news_data["articles"]:
                    title = article.get("title", "No Title")
                    content = article.get("description", "") + " " + article.get("content", "")
                    source = article.get("source", feed_type)
                    tags = ["realtime", "news", "security"]
                    await self.memory_manager.add_knowledge_article(title, content, source, tags)
                    logger.debug(f"Integrated real-time news article: {title}")
            else:
                logger.warning(f"No articles found for real-time feed '{feed_type}' or API call failed.")
        elif feed_type == "threat_intelligence":
            threat_data = await self.api_integrations.fetch_threat_intelligence(query or "latest threats")
            if threat_data and threat_data.get("threats"):
                for threat in threat_data["threats"]:
                    title = threat.get("title", "Unknown Threat")
                    content = threat.get("description", "")
                    source = threat.get("source", feed_type)
                    vulnerability_type = threat.get("type", "general")
                    await self.memory_manager.add_security_knowledge(title, content, source, vulnerability_type)
                    logger.debug(f"Integrated real-time threat: {title}")
            else:
                logger.warning(f"No threats found for real-time feed '{feed_type}' or API call failed.")
        else:
            logger.info(f"Real-time feed type '{feed_type}' processed (no specific integration logic for this type).")

    async def monitor_realtime_feeds(self):
        """
        Monitors all configured real-time feeds and integrates new data.
        """
        if not self.realtime_feed_configs:
            logger.info("No real-time feeds configured for monitoring.")
            return

        logger.info("Starting real-time feed monitoring cycle...")
        for feed_config in self.realtime_feed_configs:
            feed_name = feed_config.get("name")
            feed_type = feed_config.get("type")
            feed_query = feed_config.get("query")
            if feed_name and feed_type:
                logger.info(f"Monitoring feed: {feed_name} (Type: {feed_type})")
                await self.update_from_realtime_feed(feed_type, feed_query)
            else:
                logger.warning(f"Malformed real-time feed configuration: {feed_config}")
        logger.info("Finished real-time feed monitoring cycle.")

    async def scrape_and_integrate_security_data(self, max_items: int = None):
        """
        Scrapes security data from predefined sources and integrates it into memory.
        This is a simplified mock for web scraping.
        """
        if max_items is None:
            max_items = self.max_scraped_items_per_run

        logger.info(f"Starting security data scraping from {len(self.security_data_sources)} sources (max {max_items} items)...")
        scraped_count = 0
        new_knowledge_count = 0
        sources_summary = {}

        for source_url in self.security_data_sources:
            if scraped_count >= max_items:
                break

            logger.info(f"Scraping from: {source_url}")
            # Simulate fetching content from the URL
            # In a real scenario, use requests, BeautifulSoup, etc.
            try:
                # Dummy content based on URL
                if "cisa.gov" in source_url:
                    mock_data = [
                        {"title": "CISA Advisory 2023-001", "content": "Details on a critical vulnerability in network devices.", "type": "vulnerability"},
                        {"title": "CISA Alert on Ransomware", "content": "Guidance on preventing ransomware attacks.", "type": "guidance"}
                    ]
                elif "nvd.nist.gov" in source_url:
                    mock_data = [
                        {"title": "CVE-2023-12345", "content": "Buffer overflow in XYZ software version 1.0.", "type": "CVE"},
                        {"title": "CVE-2023-67890", "content": "Cross-site scripting in ABC web application.", "type": "CVE"}
                    ]
                else:
                    mock_data = []

                items_from_source = 0
                for item in mock_data:
                    if scraped_count >= max_items:
                        break
                    
                    title = item["title"]
                    content = item["content"]
                    vulnerability_type = item.get("type", "general")

                    # Check if this knowledge already exists (simplified check)
                    existing_results = await self.memory_manager.search_security_knowledge(title, limit=1)
                    if not existing_results or existing_results[0]['metadata']['title'] != title:
                        await self.memory_manager.add_security_knowledge(title, content, source_url, vulnerability_type)
                        new_knowledge_count += 1
                    else:
                        logger.debug(f"Knowledge '{title}' already exists, skipping.")
                    
                    scraped_count += 1
                    items_from_source += 1
                
                sources_summary[source_url] = {"items_scraped": items_from_source, "new_items": new_knowledge_count}

            except Exception as e:
                logger.error(f"Error scraping from {source_url}: {e}")
                sources_summary[source_url] = {"error": str(e)}

        logger.info(f"Finished security data scraping. Total scraped: {scraped_count}, New knowledge added: {new_knowledge_count}.")
        # Log scraping summary to a file
        logger.info(json.dumps({"log_type": "scraping", "timestamp": datetime.now().isoformat(), "total_scraped": scraped_count, "new_knowledge": new_knowledge_count, "sources": sources_summary}), extra={"log_type": "scraping"})
        return {"total_scraped": scraped_count, "new_knowledge": new_knowledge_count, "sources": sources_summary}

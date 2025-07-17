from typing import Dict, Any, List
from datetime import datetime
from utils.logger import logger
from core.memory_manager import MemoryManager # Assuming MemoryManager handles storage

class KnowledgeIntegrator:
    """
    Integrates various sources of knowledge into JARVIS AI's memory.
    This includes structured data, unstructured text, and real-time feeds.
    """
    def __init__(self, config: Dict[str, Any], memory_manager: MemoryManager):
        self.config = config
        self.memory_manager = memory_manager
        self.security_data_sources = config.get("SECURITY_DATA_SOURCES", [])
        self.max_scraped_items_per_run = config.get("MAX_SCRAPED_ITEMS_PER_RUN", 50)
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

    async def update_from_realtime_feed(self, feed_data: Dict[str, Any], feed_name: str):
        """
        Processes and integrates data from real-time feeds.
        This is a placeholder for actual real-time data processing.
        """
        logger.info(f"Processing real-time feed '{feed_name}'...")
        # Example: If feed_data contains security alerts
        if feed_name == "security_alerts" and feed_data.get("alert_type"):
            title = f"Security Alert: {feed_data['alert_type']}"
            content = json.dumps(feed_data)
            await self.memory_manager.add_security_knowledge(title, content, feed_name, feed_data.get("alert_type"))
            logger.info(f"Integrated security alert from {feed_name}.")
        else:
            logger.info(f"Real-time feed '{feed_name}' processed (no specific integration logic).")

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
        logger.info(json.dumps({"log_type": "scraping", "timestamp": datetime.now().isoformat(), "total_scraped": scraped_count, "new_knowledge": new_knowledge_count, "sources": sources_summary}), extra={"log_type": "scraping"})
        return {"total_scraped": scraped_count, "new_knowledge": new_knowledge_count, "sources": sources_summary}

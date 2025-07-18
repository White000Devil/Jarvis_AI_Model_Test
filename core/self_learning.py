import json
from typing import Dict, Any, List
from datetime import datetime
from utils.logger import logger
from core.memory_manager import MemoryManager
from core.knowledge_integrator import KnowledgeIntegrator # Import KnowledgeIntegrator

class SelfLearningEngine:
    """
    Enables JARVIS AI to learn from new data, user feedback, and interactions.
    Manages feedback collection, knowledge updates, and model fine-tuning (simulated).
    """
    def __init__(self, memory_manager: MemoryManager, knowledge_integrator: KnowledgeIntegrator, config: Dict[str, Any]):
        self.memory_manager = memory_manager
        self.knowledge_integrator = knowledge_integrator # Store KnowledgeIntegrator instance
        self.config = config
        self.feedback_collection_enabled = config.get("feedback_collection", True)
        self.scraping_enabled = config.get("scraping_enabled", False)
        self.feedback_log_path = config.get("feedback_log_path", "data/feedback_logs/feedback.jsonl")
        self.scraping_log_path = config.get("scraping_log_path", "data/scraping_logs/scraping.jsonl")
        logger.info("Self-Learning Engine initialized.")

    async def collect_feedback(self, user_id: str, interaction_id: str, query: str, response: str, rating: int, comments: str = None):
        """
        Collects user feedback on JARVIS's responses.
        Rating: 1 (bad) to 5 (excellent).
        """
        if not self.feedback_collection_enabled:
            logger.info("Feedback collection is disabled.")
            return

        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "interaction_id": interaction_id,
            "query": query,
            "response": response,
            "rating": rating,
            "comments": comments
        }
        
        try:
            with open(self.feedback_log_path, "a") as f:
                f.write(json.dumps(feedback_data) + "\n")
            logger.info(f"Feedback collected for interaction {interaction_id} (Rating: {rating}).")
            # Optionally, trigger immediate learning based on critical feedback
            if rating <= 2:
                await self.process_negative_feedback(feedback_data)
        except Exception as e:
            logger.error(f"Failed to log feedback: {e}")

    async def process_negative_feedback(self, feedback_data: Dict[str, Any]):
        """
        Processes negative feedback to identify areas for improvement and trigger learning.
        """
        logger.warning(f"Processing negative feedback for query: '{feedback_data['query']}'")
        # Example: If response was incorrect, add it to a queue for human review
        # Or, if it's a factual error, try to find correct information and update memory
        
        # Simulate updating knowledge based on feedback
        corrected_content = f"Correction for: {feedback_data['query']}. Original response was: '{feedback_data['response']}'. User indicated issues: '{feedback_data['comments'] or 'No specific comments'}'. JARVIS needs to learn the correct information."
        await self.memory_manager.add_knowledge_article(
            title=f"Feedback Correction for {feedback_data['interaction_id']}",
            content=corrected_content,
            source="user_feedback",
            tags=["correction", "feedback"]
        )
        logger.info("Negative feedback processed and correction knowledge added to memory.")

    async def update_knowledge_base(self, new_data: List[Dict[str, Any]], source: str, data_type: str = "general"):
        """
        Integrates new data into the knowledge base.
        This could be from manual updates, scraped data, or real-time feeds.
        """
        logger.info(f"Updating knowledge base with {len(new_data)} items from {source} (type: {data_type}).")
        await self.knowledge_integrator.integrate_structured_data(new_data, source, data_type)
        logger.info("Knowledge base update complete.")

    async def trigger_web_scraping(self, max_items: int = None):
        """
        Triggers the web scraping process via KnowledgeIntegrator.
        """
        if not self.scraping_enabled:
            logger.info("Web scraping is disabled in configuration.")
            return {"status": "disabled"}
        
        logger.info("Triggering web scraping for security data...")
        summary = await self.knowledge_integrator.scrape_and_integrate_security_data(max_items)
        logger.info(f"Web scraping finished. Summary: {summary}")
        return summary

    async def fine_tune_model(self, data_for_tuning: List[Dict[str, Any]]):
        """
        Simulates fine-tuning an NLP model with new data.
        In a real scenario, this would involve actual model training.
        """
        logger.info(f"Simulating fine-tuning of NLP model with {len(data_for_tuning)} data points.")
        # This is a placeholder for actual model fine-tuning logic.
        # It would involve preparing data, calling a training script/API, etc.
        await asyncio.sleep(5) # Simulate training time
        logger.info("Model fine-tuning simulation complete. Model performance is expected to improve.")

    async def review_logs_for_learning_opportunities(self):
        """
        Analyzes logs (e.g., conversation, error, ethical violation logs)
        to identify patterns and opportunities for self-improvement.
        """
        logger.info("Reviewing logs for learning opportunities (simulated).")
        # In a real system, this would parse log files, identify common failures,
        # unhandled queries, or areas where JARVIS's confidence was low.
        
        # Example: Read a few lines from feedback log
        try:
            with open(self.feedback_log_path, "r") as f:
                feedback_lines = f.readlines()
                if feedback_lines:
                    logger.info(f"Found {len(feedback_lines)} feedback entries. Analyzing...")
                    # Simple analysis: count negative feedback
                    negative_count = sum(1 for line in feedback_lines if json.loads(line).get("rating", 5) <= 2)
                    logger.info(f"Identified {negative_count} negative feedback entries. Consider reviewing these for model improvement.")
        except FileNotFoundError:
            logger.warning(f"Feedback log file not found at {self.feedback_log_path}.")
        except Exception as e:
            logger.error(f"Error reading feedback log: {e}")

        logger.info("Log review for learning opportunities complete.")

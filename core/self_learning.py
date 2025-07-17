import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from utils.logger import logger
from core.memory_manager import MemoryManager
from core.knowledge_integrator import KnowledgeIntegrator # For scraping

class SelfLearningEngine:
    """
    Enables JARVIS AI to learn from interactions, feedback, and new data sources.
    """
    def __init__(self, memory_manager: MemoryManager, config: Dict[str, Any]):
        self.config = config
        self.memory_manager = memory_manager
        self.knowledge_integrator = KnowledgeIntegrator(config, memory_manager) # Use existing KnowledgeIntegrator
        self.feedback_log_path = Path(config.get("FEEDBACK_LOG_PATH", "data/feedback_logs/feedback.jsonl"))
        self.scraping_log_path = Path(config.get("SCRAPING_LOG_PATH", "data/scraping_logs/scraping.jsonl"))
        logger.info("Self-Learning Engine initialized.")

    async def process_user_feedback(self, user_input: str, jarvis_response: str,
                                    feedback_type: str, rating: float,
                                    intent_recognized: str = "unknown") -> str:
        """
        Processes user feedback to improve JARVIS's performance.
        Feedback is logged and can be used for model fine-tuning or rule adjustments.
        """
        feedback_id = f"feedback_{datetime.now().timestamp()}"
        feedback_data = {
            "id": feedback_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "jarvis_response": jarvis_response,
            "feedback_type": feedback_type, # e.g., "thumbs_up", "thumbs_down", "correction"
            "rating": rating, # e.g., 0.0 to 1.0
            "intent_recognized": intent_recognized
        }
        
        try:
            # Log feedback to a file for later analysis/training
            logger.info(json.dumps(feedback_data), extra={"log_type": "feedback"})
            logger.info(f"Processed user feedback (ID: {feedback_id}, Type: {feedback_type}, Rating: {rating:.1f})")

            # Depending on feedback, trigger specific learning actions
            if feedback_type == "correction" and rating < 0.5:
                logger.warning(f"Negative feedback received. Consider triggering self-correction or human review for: {user_input}")
                # This could trigger a self-correction process or flag for human review
            elif feedback_type == "thumbs_up" and rating > 0.8:
                logger.info("Positive feedback received. Reinforcing successful interaction.")
                # This could be used to reinforce positive patterns in a reinforcement learning setup

            return feedback_id
        except Exception as e:
            logger.error(f"Error processing user feedback: {e}")
            return "error"

    async def scrape_security_data(self, max_items: int = None) -> Dict[str, Any]:
        """
        Triggers the knowledge integrator to scrape and add new security data.
        """
        logger.info("Initiating security data scraping via Knowledge Integrator...")
        results = await self.knowledge_integrator.scrape_and_integrate_security_data(max_items)
        logger.info(f"Security data scraping completed. New items: {results.get('new_knowledge', 0)}")
        return results

    async def optimize_learning_parameters(self):
        """
        Simulates the optimization of internal learning parameters based on performance.
        In a real system, this would involve analyzing logs, retraining models, etc.
        """
        logger.info("Optimizing learning parameters based on historical data (simulated)...")
        # Placeholder for actual optimization logic
        await asyncio.sleep(1) # Simulate work
        logger.info("Learning parameters optimization complete.")
        return {"status": "optimized", "timestamp": datetime.now().isoformat()}

    def get_learning_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about the self-learning engine's activities.
        Reads from log files to provide real-time stats.
        """
        feedback_stats = {"total_feedback": 0, "positive_feedback": 0, "negative_feedback": 0, "average_rating": 0.0, "recent_average": 0.0}
        scraping_stats = {"total_scraped": 0, "new_knowledge": 0, "processed_items": 0, "processing_rate": 0.0}
        
        # Read feedback logs
        if self.feedback_log_path.exists():
            ratings_sum = 0
            ratings_count = 0
            with open(self.feedback_log_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        feedback_stats["total_feedback"] += 1
                        if data.get("rating", 0) >= 0.7:
                            feedback_stats["positive_feedback"] += 1
                        else:
                            feedback_stats["negative_feedback"] += 1
                        ratings_sum += data.get("rating", 0)
                        ratings_count += 1
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping malformed feedback log line: {line.strip()}")
            if ratings_count > 0:
                feedback_stats["average_rating"] = ratings_sum / ratings_count
            
            # Simple recent average (e.g., last 10 feedbacks)
            recent_ratings_sum = 0
            recent_ratings_count = 0
            if self.feedback_log_path.exists():
                with open(self.feedback_log_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-10:]: # Look at last 10 lines
                        try:
                            data = json.loads(line)
                            recent_ratings_sum += data.get("rating", 0)
                            recent_ratings_count += 1
                        except json.JSONDecodeError:
                            pass
            if recent_ratings_count > 0:
                feedback_stats["recent_average"] = recent_ratings_sum / recent_ratings_count

        # Read scraping logs
        if self.scraping_log_path.exists():
            with open(self.scraping_log_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        scraping_stats["total_scraped"] += data.get("total_scraped", 0)
                        scraping_stats["new_knowledge"] += data.get("new_knowledge", 0)
                        scraping_stats["processed_items"] += data.get("total_scraped", 0) # Assuming processed = scraped
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping malformed scraping log line: {line.strip()}")
            if scraping_stats["processed_items"] > 0:
                # This rate would be more meaningful if we tracked time
                scraping_stats["processing_rate"] = scraping_stats["new_knowledge"] / scraping_stats["processed_items"]

        return {
            "feedback_stats": feedback_stats,
            "scraping_stats": scraping_stats,
            "learning_metrics": {
                "learning_rate": 0.01, # Placeholder
                "exploration_rate": 0.1, # Placeholder
                "improvement_rate": 0.05 # Placeholder
            },
            "last_update": datetime.now().isoformat()
        }

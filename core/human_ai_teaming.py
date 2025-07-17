import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.collaboration_hub import CollaborationHub

class HumanAITeaming:
    """
    Enhances collaboration between humans and JARVIS AI.
    Focuses on adaptive communication, clarification, and shared understanding.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager,
                 collaboration_hub: CollaborationHub, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.collaboration_hub = collaboration_hub
        self.enabled = config.get("HUMAN_AI_TEAMING_ENABLED", True)
        self.adaptive_communication_enabled = config.get("ADAPTIVE_COMMUNICATION_ENABLED", True)
        self.clarification_threshold = config.get("CLARIFICATION_THRESHOLD", 0.4)

        self._clarification_requests_sent = 0
        self._communication_adaptations_made = 0

        if self.enabled:
            logger.info("Human-AI Teaming Engine initialized.")
        else:
            logger.warning("Human-AI Teaming Engine is disabled in configuration.")

    async def clarify_request(self, user_input: str, nlp_confidence: float, context: Dict[str, Any]) -> Optional[str]:
        """
        Determines if clarification is needed based on JARVIS's confidence
        and generates a clarifying question.
        Returns a clarifying question or None if no clarification is needed.
        """
        if not self.enabled:
            return None

        if nlp_confidence < self.clarification_threshold:
            self._clarification_requests_sent += 1
            logger.info(f"Low NLP confidence ({nlp_confidence:.2f}). Requesting clarification for: '{user_input}'")
            
            # Simulate generating a clarification question
            if "security" in user_input.lower():
                return "I'm not entirely clear on the security aspect of your request. Could you please specify the target or the type of vulnerability you're interested in?"
            elif "deploy" in user_input.lower():
                return "I need more details about the deployment. Which environment are you targeting (e.g., development, staging, production) or what service are you trying to deploy?"
            else:
                return "I'm not entirely sure I understood your request. Could you please rephrase or provide more context?"
        return None

    async def adapt_communication(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Adapts JARVIS's communication style based on user's expertise, context, or past interactions.
        This is a simplified mock.
        """
        if not self.enabled or not self.adaptive_communication_enabled:
            return jarvis_response

        adapted_response = jarvis_response
        
        # Simulate adaptation based on context (e.g., user role, emotional tone)
        user_role = context.get("user_role", "unknown")
        user_sentiment = context.get("user_sentiment", "neutral") # From NLP metadata

        if user_role == "technical_expert":
            adapted_response = f"Acknowledged. {jarvis_response}" # More concise
            self._communication_adaptations_made += 1
        elif user_role == "beginner":
            adapted_response = f"Let me explain that in simpler terms. {jarvis_response}" # More verbose
            self._communication_adaptations_made += 1
        
        if user_sentiment == "negative":
            adapted_response = f"I understand your concern. {jarvis_response}" # Empathetic tone
            self._communication_adaptations_made += 1
        elif user_sentiment == "positive":
            adapted_response = f"Great! {jarvis_response}" # Enthusiastic tone
            self._communication_adaptations_made += 1

        logger.debug(f"Communication adapted for user role '{user_role}' and sentiment '{user_sentiment}'.")
        return adapted_response

    async def get_human_feedback_on_clarification(self, original_query: str, clarification_question: str) -> str:
        """
        Simulates getting explicit human feedback on a clarification question.
        This would typically be a UI interaction.
        """
        logger.info(f"Seeking human feedback for clarification: '{clarification_question}' on original query: '{original_query}'")
        # In a real system, this would involve a UI prompt or a human-in-the-loop system.
        # For now, we'll return a mock response.
        await asyncio.sleep(1)
        return "User provided more details." # Mock response

    async def provide_contextual_assistance(self, user_input: str, current_task: Dict[str, Any]) -> Optional[str]:
        """
        Offers proactive assistance based on the current task or context.
        """
        if not self.enabled:
            return None
        
        logger.info(f"Checking for contextual assistance for task: {current_task.get('name')}")
        
        if current_task.get("name") == "security_analysis" and "report" in user_input.lower():
            return "Would you like me to generate a summary report of the security analysis findings?"
        elif current_task.get("name") == "deployment" and "status" in user_input.lower():
            return "I can provide the current status of your deployments. Which deployment are you interested in?"
        
        return None

    def get_teaming_stats(self) -> Dict[str, Any]:
        """Returns statistics about the Human-AI Teaming Engine's activity."""
        return {
            "enabled": self.enabled,
            "adaptive_communication_enabled": self.adaptive_communication_enabled,
            "clarification_threshold": self.clarification_threshold,
            "clarification_requests_sent": self._clarification_requests_sent,
            "communication_adaptations_made": self._communication_adaptations_made,
            "last_updated": datetime.now().isoformat()
        }

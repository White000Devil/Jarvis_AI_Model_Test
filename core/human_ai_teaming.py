import asyncio
from typing import Dict, Any, Optional
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.collaboration_hub import CollaborationHub

class HumanAITeaming:
    """
    Facilitates effective collaboration and communication between humans and JARVIS AI.
    Includes adaptive communication, clarification, and shared understanding.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager, collaboration_hub: CollaborationHub, config: Dict[str, Any]):
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.collaboration_hub = collaboration_hub
        self.config = config
        self.enabled = config.get("enabled", True)
        self.adaptive_communication_enabled = config.get("adaptive_communication_enabled", True)
        self.clarification_threshold = config.get("clarification_threshold", 0.4)

        if self.enabled:
            logger.info("Human-AI Teaming Engine initialized.")
        else:
            logger.info("Human-AI Teaming Engine is disabled in configuration.")

    async def clarify_request(self, user_input: str, confidence: float, context: Dict[str, Any]) -> Optional[str]:
        """
        Determines if clarification is needed based on confidence and ambiguity.
        Returns a clarification question if needed, otherwise None.
        """
        if not self.enabled:
            return None

        logger.info(f"Checking if clarification is needed for query: '{user_input}' (Confidence: {confidence:.2f})")
        
        if confidence < self.clarification_threshold:
            logger.warning(f"Low confidence ({confidence:.2f}) detected. Seeking clarification.")
            # Example clarification based on intent or general ambiguity
            if context.get("intent") == "general_query":
                return "I'm not entirely sure I understand. Could you please be more specific about what you're looking for?"
            elif context.get("intent") == "security_query" and "target" not in context.get("entities", []):
                return "To perform a security scan, I need a specific target. Could you please provide the URL or IP address?"
            else:
                return "I need a bit more information to help you effectively. Could you rephrase your request or provide more details?"
        
        # Check for ambiguity (simplified)
        if "thing" in user_input.lower() or "it" in user_input.lower() and len(user_input.split()) < 5:
            logger.warning("Ambiguous language detected. Seeking clarification.")
            return "Could you please specify what 'thing' or 'it' you are referring to?"

        logger.info("No clarification needed.")
        return None

    async def adapt_communication(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Adapts JARVIS's communication style based on user sentiment, context, or preferences.
        """
        if not self.enabled or not self.adaptive_communication_enabled:
            return jarvis_response

        logger.info(f"Adapting communication for response: '{jarvis_response[:50]}...'")
        
        user_sentiment = context.get("user_sentiment", "neutral")
        
        if user_sentiment == "negative":
            logger.info("User sentiment is negative. Adapting to a more empathetic tone.")
            if not jarvis_response.startswith("I understand"):
                return f"I understand your concern. {jarvis_response}"
        elif user_sentiment == "positive":
            logger.info("User sentiment is positive. Adapting to a more encouraging tone.")
            if not jarvis_response.startswith("Great!"):
                return f"Great! {jarvis_response}"
        
        # Example: If user is a "developer" (from context), use more technical language
        if context.get("user_role") == "developer" and "technical" not in jarvis_response.lower():
            # This is a very basic simulation. A real system would rephrase.
            logger.info("User role is developer. Attempting to add technical nuance.")
            # jarvis_response += " (This involves advanced algorithms and data structures.)"
            pass # For now, no actual modification, just logging

        logger.info("Communication adaptation complete.")
        return jarvis_response

    async def share_context_with_human(self, session_id: str, context_data: Dict[str, Any]) -> bool:
        """
        Shares relevant context with human collaborators via the Collaboration Hub.
        """
        if not self.enabled or not self.collaboration_hub.enabled:
            logger.warning("Human-AI Teaming or Collaboration Hub disabled. Cannot share context.")
            return False

        logger.info(f"Sharing context with session '{session_id}': {context_data}")
        success = await self.collaboration_hub.update_shared_context(session_id, "jarvis_context", context_data)
        if success:
            logger.info("Context shared successfully with human collaborators.")
        else:
            logger.error("Failed to share context with human collaborators.")
        return success

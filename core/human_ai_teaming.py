import asyncio
from typing import Dict, Any, Optional
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.collaboration_hub import CollaborationHub # Import CollaborationHub

class HumanAITeaming:
    """
    Facilitates effective collaboration and communication between humans and JARVIS AI.
    Includes adaptive communication and clarification mechanisms.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager, collaboration_hub: CollaborationHub, config: Dict[str, Any]):
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.collaboration_hub = collaboration_hub # Store CollaborationHub instance
        self.config = config
        self.enabled = config.get("enabled", False)
        self.adaptive_communication_enabled = config.get("adaptive_communication_enabled", True)
        self.clarification_threshold = config.get("clarification_threshold", 0.4)
        logger.info(f"Human-AI Teaming initialized. Enabled: {self.enabled}")

    async def clarify_request(self, user_input: str, nlp_confidence: float, context: Dict[str, Any]) -> Optional[str]:
        """
        Determines if JARVIS needs to ask for clarification based on NLP confidence
        or ambiguity. Returns a clarification question if needed, else None.
        """
        if not self.enabled:
            return None

        logger.debug(f"Assessing need for clarification. NLP Confidence: {nlp_confidence:.2f}")

        if nlp_confidence < self.clarification_threshold:
            logger.info(f"Low NLP confidence ({nlp_confidence:.2f}). Requesting clarification.")
            # Check for specific ambiguities in context if available
            if "nlp_intent" in context and context["nlp_intent"] == "ambiguous":
                return "I'm not entirely sure about your intent. Could you please provide more details or rephrase your request?"
            
            # General clarification
            return "I'm having a bit of trouble understanding your request. Could you please elaborate or clarify what you mean?"
        
        # Check for potential ambiguities based on past interactions (simplified)
        # In a real system, this would involve more complex memory analysis.
        recent_interactions = context.get("conversation_history", [])
        if recent_interactions and len(recent_interactions) > 0:
            last_jarvis_response = recent_interactions[0].get("jarvis_response", "").lower()
            if "i'm not sure" in last_jarvis_response or "could you clarify" in last_jarvis_response:
                # If JARVIS previously struggled, it might indicate a persistent ambiguity
                # This is a very simple heuristic.
                if nlp_confidence < 0.6: # Even if above current threshold, if previous struggle, ask again
                    return "Based on our previous conversation, it seems there might still be some ambiguity. Could you clarify your current request?"

        return None

    async def adapt_communication(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Adapts JARVIS's communication style based on user's input, context,
        and collaboration hub state.
        """
        if not self.enabled or not self.adaptive_communication_enabled:
            return jarvis_response

        logger.debug("Adapting communication style...")

        # Example 1: Adapt to user's tone (simplified)
        # This would require a sentiment analysis model on user_input
        user_sentiment = context.get("user_sentiment", "neutral") # Assume sentiment analysis is done by NLP
        if user_sentiment == "negative":
            jarvis_response = f"I understand you might be frustrated. {jarvis_response}"
        elif user_sentiment == "positive":
            jarvis_response = f"Great! {jarvis_response}"

        # Example 2: Adapt to user's expertise level (simplified)
        # This would require user profiling from memory or explicit input
        user_expertise = context.get("user_expertise", "general") # e.g., "technical", "non-technical"
        if user_expertise == "technical":
            # Use more technical jargon, less explanation
            pass # Current response might already be technical enough
        elif user_expertise == "non-technical":
            # Simplify language, provide more analogies
            jarvis_response = self._simplify_language(jarvis_response)

        # Example 3: Adapt based on collaboration session state
        session_id = context.get("session_id")
        if session_id:
            session_context = await self.collaboration_hub.get_session_context(session_id)
            if session_context.get("mode") == "training":
                jarvis_response = f"[Training Mode] {jarvis_response} (Please provide feedback on this response.)"
            elif session_context.get("mode") == "debug":
                jarvis_response = f"[Debug Info: Confidence={context.get('jarvis_confidence', 'N/A'):.2f}] {jarvis_response}"

        return jarvis_response

    def _simplify_language(self, text: str) -> str:
        """
        A very basic function to simulate simplifying complex language.
        In a real system, this would use an NLP model for text simplification.
        """
        text = text.replace("utilize", "use")
        text = text.replace("implement", "build")
        text = text.replace("facilitate", "help")
        text = text.replace("consequently", "so")
        return text

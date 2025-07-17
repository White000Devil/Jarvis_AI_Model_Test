import asyncio
from typing import Dict, Any, List, Tuple
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
        
        self.enabled = config.get("HUMAN_AI_TEAMING_ENABLED", False)
        self.clarification_threshold = config.get("CLARIFICATION_THRESHOLD", 0.4) # Confidence below which JARVIS seeks clarification
        self.adaptive_communication_enabled = config.get("ADAPTIVE_COMMUNICATION_ENABLED", True)

        if self.enabled:
            logger.info("Human-AI Teaming Engine initialized.")
        else:
            logger.info("Human-AI Teaming Engine is disabled in configuration.")

    async def clarify_request(self, user_input: str, jarvis_response_metadata: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """
        Determines if clarification is needed based on JARVIS's confidence
        and generates a clarifying question.
        Returns a clarifying question or None if no clarification is needed.
        """
        if not self.enabled:
            return None

        confidence = jarvis_response_metadata.get("confidence", 1.0)
        intent = jarvis_response_metadata.get("intent", "unknown")

        if confidence < self.clarification_threshold:
            logger.info(f"Low confidence ({confidence:.2f}) detected for intent '{intent}'. Seeking clarification.")
            
            if intent == "unknown" or confidence < 0.2:
                return "I'm having trouble understanding your request. Could you please rephrase it or provide more context?"
            elif intent == "security_query":
                return f"I detected a security-related query, but my confidence is low ({confidence:.2f}). Could you specify what kind of security information you're looking for (e.g., vulnerability, threat intelligence, best practices)?"
            elif intent == "deployment_request":
                return f"I understand you're asking about deployment, but I need more details. Are you looking to deploy a Docker container, a Kubernetes service, or something else?"
            else:
                return f"My understanding of your request is a bit unclear ({confidence:.2f}). Could you elaborate on what you mean by '{user_input}'?"
        
        return None

    async def adapt_communication(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Adapts JARVIS's communication style based on user's expertise, context, or past interactions.
        This is a simplified mock.
        """
        if not self.enabled or not self.adaptive_communication_enabled:
            return jarvis_response

        # Simulate adapting based on user's role (if available in context)
        user_role = context.get("user_role", "general")
        
        if user_role == "developer":
            if "explain" in user_input.lower() and "code" in user_input.lower():
                logger.info("Adapting communication for developer: providing more technical detail.")
                return f"{jarvis_response} (Technically, this involves X, Y, and Z components.)"
        elif user_role == "security_analyst":
            if "threat" in user_input.lower() or "vulnerability" in user_input.lower():
                logger.info("Adapting communication for security analyst: using precise terminology.")
                return f"{jarvis_response} (Specifically, this aligns with CVE-XXXX-YYYY.)"
        elif user_role == "executive":
            logger.info("Adapting communication for executive: providing high-level summary.")
            # This would require summarizing the original response
            return f"In summary: {jarvis_response[:50]}..." # Very basic summary

        # Simulate adapting based on sentiment of user input (requires NLP sentiment analysis)
        # For now, a simple keyword check
        if "frustrated" in user_input.lower() or "annoyed" in user_input.lower():
            logger.info("Adapting communication due to perceived user frustration.")
            return f"I understand this might be frustrating. Let me try to explain differently: {jarvis_response}"

        return jarvis_response

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
            "clarification_threshold": self.clarification_threshold,
            "adaptive_communication_enabled": self.adaptive_communication_enabled,
            "last_adaptation_timestamp": datetime.now().isoformat(),
            "total_clarifications_issued": 0 # Placeholder
        }

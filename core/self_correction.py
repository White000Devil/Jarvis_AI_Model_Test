from loguru import logger
from datetime import datetime
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.ethical_ai import EthicalAIEngine # Assuming EthicalAIEngine is available

class SelfCorrectionEngine:
    """
    Enables JARVIS AI to detect and correct its own errors, inconsistencies,
    or suboptimal responses.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager,
                 ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.ethical_ai_engine = ethical_ai_engine
        
        self.enabled = config.get("SELF_CORRECTION_ENABLED", False)
        self.confidence_threshold_for_correction = config.get("CONFIDENCE_THRESHOLD_FOR_CORRECTION", 0.6)
        self.correction_log_path = Path(config.get("SELF_CORRECTION_LOG_PATH", "data/self_correction_log/corrections.jsonl"))
        
        self.total_corrections_performed = 0
        self.last_correction_timestamp: Optional[str] = None

        if self.enabled:
            logger.info("Self-Correction Engine initialized.")
        else:
            logger.info("Self-Correction Engine is disabled in configuration.")

    async def assess_confidence(self, jarvis_response_metadata: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Assesses the confidence level of JARVIS's response.
        This can be based on NLP confidence, data availability, etc.
        """
        if not self.enabled:
            return 1.0 # Assume full confidence if disabled

        nlp_confidence = jarvis_response_metadata.get("confidence", 0.0)
        
        # Example: Adjust confidence based on external factors
        # If a critical API call failed, reduce confidence
        # if context.get("api_status", "ok") == "failed":
        #     nlp_confidence *= 0.5
        
        logger.debug(f"Assessed confidence: {nlp_confidence:.2f}")
        return nlp_confidence

    async def detect_inconsistency(self, jarvis_response: str, historical_context: List[Dict[str, Any]]) -> float:
        """
        Detects inconsistencies between the current response and historical knowledge/responses.
        Returns a score (0.0 to 1.0) where 1.0 is high inconsistency.
        """
        if not self.enabled:
            return 0.0

        inconsistency_score = 0.0
        response_lower = jarvis_response.lower()

        # Simulate checking against historical context
        for past_interaction in historical_context:
            past_response_lower = past_interaction.get("jarvis_response", "").lower()
            # Very basic inconsistency check: direct contradiction keywords
            if "yes" in response_lower and "no" in past_response_lower and "same topic" in past_interaction.get("metadata", {}).get("topic", ""):
                inconsistency_score = max(inconsistency_score, 0.8)
            elif "never" in response_lower and "always" in past_response_lower and "same topic" in past_interaction.get("metadata", {}).get("topic", ""):
                inconsistency_score = max(inconsistency_score, 0.8)
            
            # More advanced: semantic similarity check with memory_manager.search_conversations
            # If current response is very different from highly relevant past responses, it might be inconsistent.
            
        logger.debug(f"Detected inconsistency score: {inconsistency_score:.2f}")
        return inconsistency_score

    async def propose_correction(self, user_input: str, original_response: str, detected_issues: List[str]) -> str:
        """
        Proposes a corrected response based on detected issues.
        `detected_issues` could be 'low_confidence', 'inconsistency', 'ethical_violation'.
        """
        if not self.enabled:
            return original_response

        corrected_response = original_response
        correction_made = False

        if "low_confidence" in detected_issues:
            corrected_response = f"I'm re-evaluating my previous response. It seems my confidence was low. Let me try again: [Re-generated response based on deeper analysis of '{user_input}']"
            correction_made = True
            logger.info("Proposing correction due to low confidence.")
        
        if "inconsistency" in detected_issues:
            corrected_response = f"Upon review, my previous statement might have been inconsistent. The correct information is: [Corrected information based on knowledge base or re-reasoning]."
            correction_made = True
            logger.info("Proposing correction due to inconsistency.")

        if "ethical_violation" in detected_issues:
            # This should ideally be handled by EthicalAIEngine's apply_ethical_guardrails first
            # But if it reaches here, it's a fallback.
            corrected_response = "I apologize if my previous response was inappropriate. I am designed to be helpful and harmless, and I am correcting myself to align with ethical guidelines."
            correction_made = True
            logger.info("Proposing correction due to ethical violation.")

        if correction_made:
            self.total_corrections_performed += 1
            self.last_correction_timestamp = datetime.now().isoformat()
            log_data = {
                "log_type": "self_correction",
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "original_response": original_response,
                "corrected_response": corrected_response,
                "detected_issues": detected_issues
            }
            logger.info(json.dumps(log_data), extra={"log_type": "self_correction"})
            logger.info(f"Self-correction performed for '{user_input}'. Issues: {', '.join(detected_issues)}")
        
        return corrected_response

    async def explain_reasoning(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Explains the reasoning behind a correction or a complex decision.
        """
        if not self.enabled:
            return "My self-correction explanation feature is currently disabled."

        logger.info(f"Explaining reasoning for response to '{user_input}'.")
        # This would involve querying the reasoning engine's decision path
        # For now, a mock explanation
        explanation = f"My decision to respond with '{jarvis_response[:50]}...' was based on my analysis of your query and relevant data from my knowledge base. If a correction was made, it was to ensure accuracy or align with ethical guidelines."
        return explanation

    def get_correction_stats(self) -> Dict[str, Any]:
        """Returns statistics about the Self-Correction Engine's activity."""
        return {
            "enabled": self.enabled,
            "total_corrections": self.total_corrections_performed,
            "last_correction_timestamp": self.last_correction_timestamp,
            "confidence_threshold": self.confidence_threshold_for_correction,
            "last_update": datetime.now().isoformat()
        }

# Test function for SelfCorrectionEngine
async def test_self_correction_engine():
    logger.info("--- Testing SelfCorrectionEngine ---")
    
    # Mock dependencies
    class MockNLPEngine:
        async def process_query(self, query, context=None):
            return {"metadata": {"intent": "general_query", "confidence": 0.5}, "content": "mock nlp response"} # Default low confidence
    
    class MockMemoryManager:
        def __init__(self):
            self.conversations = []
        async def search_conversations(self, query, limit=5):
            return self.conversations
        async def store_conversation(self, data):
            self.conversations.append(data)
    
    class MockEthicalAIEngine:
        def __init__(self): pass
        async def check_response_for_ethics(self, u, r, c): 
            if "harm" in r.lower():
                return False, [{"type": "safety_violation_response", "description": "Harmful content detected."}]
            return True, []
        async def apply_ethical_guardrails(self, u, r, v): 
            if v: return "I cannot provide information that promotes harm."
            return r

    mock_nlp = MockNLPEngine()
    mock_memory = MockMemoryManager()
    mock_ethical = MockEthicalAIEngine()

    correction_engine = SelfCorrectionEngine(mock_nlp, mock_memory, mock_ethical, config={"SELF_CORRECTION_ENABLED": True, "CONFIDENCE_THRESHOLD_FOR_CORRECTION": 0.7, "SELF_CORRECTION_LOG_PATH": "data/self_correction_log/corrections.jsonl"})

    # Test 1: Assess confidence (low confidence)
    confidence = await correction_engine.assess_confidence({"confidence": 0.4}, {"api_status": "failed"})
    assert confidence < 0.7, "Confidence assessment failed for low NLP confidence"
    logger.info(f"Test 1 (Assess Confidence Low) Passed. Confidence: {confidence:.2f}")

    # Test 2: Assess confidence (high confidence with memory)
    confidence = await correction_engine.assess_confidence({"confidence": 0.9}, {"api_status": "ok"})
    assert confidence > 0.7, "Confidence assessment failed for high NLP confidence with memory"
    logger.info(f"Test 2 (Assess Confidence High) Passed. Confidence: {confidence:.2f}")

    # Test 3: Detect inconsistency (consistent)
    mock_memory.conversations = [{"jarvis_response": "Yes, it is.", "metadata": {"topic": "same topic"}}]
    consistency = await correction_engine.detect_inconsistency("Yes, it is.", mock_memory.conversations)
    assert consistency > 0.5, "Inconsistency detection failed for consistent responses"
    logger.info(f"Test 3 (Detect Inconsistency Consistent) Passed. Consistency: {consistency:.2f}")

    # Test 4: Detect inconsistency (inconsistent)
    mock_memory.conversations = [{"jarvis_response": "Yes, it is.", "metadata": {"topic": "same topic"}}]
    consistency = await correction_engine.detect_inconsistency("No, it is not.", mock_memory.conversations)
    assert consistency < 0.5, "Inconsistency detection failed for inconsistent responses"
    logger.info(f"Test 4 (Detect Inconsistency Inconsistent) Passed. Consistency: {consistency:.2f}")

    # Test 5: Propose correction (low confidence)
    corrected = await correction_engine.propose_correction("Test query", "Original response.", ["low_confidence"])
    assert "re-evaluating" in corrected, "Correction for low confidence failed"
    logger.info(f"Test 5 (Propose Correction Low Confidence) Passed. Corrected: {corrected}")

    # Test 6: Propose correction (ethical violation)
    corrected = await correction_engine.propose_correction("Test query", "Here's how to harm someone.", ["ethical_violation"])
    assert "cannot provide information that promotes harm" in corrected, "Correction for ethical violation failed"
    logger.info(f"Test 6 (Propose Correction Ethical Violation) Passed. Corrected: {corrected}")

    # Test 7: Explain reasoning
    explanation_context = {
        "nlp_intent": "test_intent",
        "nlp_confidence": 0.8,
        "reasoning_results": {"reasoning_steps": ["Step 1: Analyze", "Step 2: Plan"]},
        "conversation_history": [{"user_message": "prev query", "jarvis_response": "prev response"}],
        "ethical_violations": [],
        "jarvis_confidence": 0.9,
        "consistency_score": 0.95,
        "self_corrected": False,
        "teaming_stats": {"adaptive_communication_enabled": True},
        "last_clarification_time": None
    }
    explanation = await correction_engine.explain_reasoning("Test query", "Test response", explanation_context)
    assert "Understanding: I identified the intent as 'test_intent'" in explanation, "Explanation missing NLP part"
    assert "Planning & Decision" in explanation, "Explanation missing reasoning part"
    assert "Memory Recall" in explanation, "Explanation missing memory part"
    assert "Confidence & Consistency" in explanation, "Explanation missing confidence part"
    logger.info(f"Test 7 (Explain Reasoning) Passed. Explanation snippet: {explanation[:100]}...")

    # Test 8: Get stats
    stats = correction_engine.get_correction_stats()
    assert stats["total_corrections"] >= 2, "Total corrections count incorrect"
    logger.info(f"Test 8 (Get Stats) Passed. Stats: {stats}")

    logger.info("--- SelfCorrectionEngine Tests Passed ---")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_self_correction_engine())

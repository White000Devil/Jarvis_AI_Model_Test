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
    Enables JARVIS AI to detect and correct its own inconsistencies, errors,
    or suboptimal responses based on internal confidence, external feedback,
    and ethical guidelines.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager,
                 ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.ethical_ai_engine = ethical_ai_engine
        
        self.enabled = config.get("SELF_CORRECTION_ENABLED", True)
        self.confidence_threshold = config.get("CONFIDENCE_THRESHOLD_FOR_CORRECTION", 0.6) # Below this, consider correction
        self.inconsistency_threshold = config.get("INCONSISTENCY_THRESHOLD", 0.3) # For detecting conflicting info
        self.log_corrections = config.get("LOG_CORRECTIONS", True)
        self.self_correction_log_path = Path(config.get("SELF_CORRECTION_LOG_PATH", "data/self_correction_log/corrections.jsonl"))

        self._total_correction_attempts = 0
        self._successful_corrections = 0
        self._failed_corrections = 0

        if self.enabled:
            logger.info("Self-Correction Engine initialized.")
        else:
            logger.warning("Self-Correction Engine is disabled in configuration.")

    async def assess_confidence(self, jarvis_response: str, context: Dict[str, Any]) -> float:
        """
        Assesses the confidence of JARVIS's own response.
        This can be based on NLP confidence, reasoning certainty, or external feedback.
        """
        if not self.enabled:
            return 1.0 # Assume full confidence if disabled

        # Use NLP confidence as a primary factor
        nlp_confidence = context.get("nlp_confidence", 0.0)
        
        # Simulate other factors (e.g., consistency with memory, complexity of task)
        # For simplicity, we'll just use NLP confidence for now.
        
        logger.debug(f"Assessed confidence for response '{jarvis_response[:50]}...': {nlp_confidence:.2f}")
        return nlp_confidence

    async def detect_inconsistency(self, jarvis_response: str, historical_context: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Detects if the current response is inconsistent with past knowledge or interactions.
        Returns (is_inconsistent, explanation).
        """
        if not self.enabled:
            return False, None

        # Simulate inconsistency detection
        # This would involve comparing the current response with relevant past conversations or knowledge articles.
        # For example, if JARVIS previously stated X, and now states Y, and X and Y are contradictory.
        
        response_lower = jarvis_response.lower()
        
        # Simple mock inconsistency: if response contains "error" and context implies success
        if "error" in response_lower and any("success" in h.get("document", "").lower() for h in historical_context):
            return True, "Response contains 'error' but historical context indicates success."
        
        # Another mock: if response contradicts a known fact from memory
        if "paris is the capital of germany" in response_lower:
            return True, "Response contradicts known geographical fact."

        return False, None

    async def propose_correction(self, original_response: str, error_explanation: str, user_input: str, context: Dict[str, Any]) -> str:
        """
        Proposes a corrected response based on detected errors or inconsistencies.
        """
        self._total_correction_attempts += 1
        logger.info(f"Proposing correction for: '{original_response[:50]}...' due to: {error_explanation}")
        
        corrected_response = original_response
        
        # Simulate correction logic
        if "paris is the capital of germany" in original_response.lower():
            corrected_response = "Correction: The capital of Germany is Berlin. Paris is the capital of France."
            self._successful_corrections += 1
        elif "error" in error_explanation:
            corrected_response = f"I apologize for the previous error. Let me re-evaluate: [Re-evaluated response based on user input and context]."
            self._successful_corrections += 1
        else:
            corrected_response = f"Upon review, I'd like to refine my previous statement: {original_response}. {error_explanation}"
            self._failed_corrections += 1 # Could be a failed attempt if not a clear correction

        if self.log_corrections:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "original_response": original_response,
                "corrected_response": corrected_response,
                "error_explanation": error_explanation,
                "status": "successful" if self._successful_corrections > (self._total_correction_attempts - self._successful_corrections) else "failed",
                "context": context
            }
            logger.info(json.dumps(log_entry), extra={"log_type": "self_correction"})

        return corrected_response

    async def explain_reasoning(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Provides an explanation of JARVIS's reasoning process for a given response.
        """
        if not self.enabled:
            return "Explanation feature is disabled."

        reasoning_steps = context.get("reasoning_steps", ["No detailed reasoning steps available."])
        final_plan = context.get("final_plan", "No specific plan.")
        decisions = context.get("decisions", [])

        explanation = f"My response to '{user_input}' was formulated as follows:\n\n"
        explanation += "Reasoning Steps:\n"
        for step in reasoning_steps:
            explanation += f"- {step}\n"
        
        explanation += "\nKey Decisions Made:\n"
        if decisions:
            for decision in decisions:
                explanation += f"- Type: {decision.get('type')}, Reason: {decision.get('reason', 'N/A')}\n"
        else:
            explanation += "- No specific decisions recorded.\n"
        
        explanation += f"\nMy final plan was to: {final_plan}\n"
        explanation += f"\nThis led to the response: '{jarvis_response}'"

        logger.info(f"Generated explanation for response to '{user_input[:50]}...'.")
        return explanation

    def get_correction_stats(self) -> Dict[str, Any]:
        """Returns statistics about self-correction activities."""
        return {
            "enabled": self.enabled,
            "confidence_threshold": self.confidence_threshold,
            "inconsistency_threshold": self.inconsistency_threshold,
            "total_correction_attempts": self._total_correction_attempts,
            "successful_corrections": self._successful_corrections,
            "failed_corrections": self._failed_corrections,
            "last_updated": datetime.now().isoformat()
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
        async def check_response_for_ethics(self, u, r, v): 
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
    confidence = await correction_engine.assess_confidence("Mock response", {"nlp_confidence": 0.4})
    assert confidence < 0.7, "Confidence assessment failed for low NLP confidence"
    logger.info(f"Test 1 (Assess Confidence Low) Passed. Confidence: {confidence:.2f}")

    # Test 2: Assess confidence (high confidence with memory)
    confidence = await correction_engine.assess_confidence("Mock response", {"nlp_confidence": 0.9})
    assert confidence > 0.7, "Confidence assessment failed for high NLP confidence with memory"
    logger.info(f"Test 2 (Assess Confidence High) Passed. Confidence: {confidence:.2f}")

    # Test 3: Detect inconsistency (consistent)
    mock_memory.conversations = [{"jarvis_response": "Yes, it is.", "metadata": {"topic": "same topic"}}]
    consistency, explanation = await correction_engine.detect_inconsistency("Yes, it is.", mock_memory.conversations)
    assert consistency is False, "Inconsistency detection failed for consistent responses"
    logger.info(f"Test 3 (Detect Inconsistency Consistent) Passed. Consistency: {consistency}, Explanation: {explanation}")

    # Test 4: Detect inconsistency (inconsistent)
    mock_memory.conversations = [{"jarvis_response": "Yes, it is.", "metadata": {"topic": "same topic"}}]
    consistency, explanation = await correction_engine.detect_inconsistency("No, it is not.", mock_memory.conversations)
    assert consistency is True, "Inconsistency detection failed for inconsistent responses"
    logger.info(f"Test 4 (Detect Inconsistency Inconsistent) Passed. Consistency: {consistency}, Explanation: {explanation}")

    # Test 5: Propose correction (low confidence)
    corrected = await correction_engine.propose_correction("Original response.", "Low confidence detected.", "Test query", {"nlp_confidence": 0.4})
    assert "re-evaluating" in corrected, "Correction for low confidence failed"
    logger.info(f"Test 5 (Propose Correction Low Confidence) Passed. Corrected: {corrected}")

    # Test 6: Propose correction (ethical violation)
    corrected = await correction_engine.propose_correction("Original response.", "Ethical violation detected.", "Test query", {"nlp_confidence": 0.9})
    assert "cannot provide information that promotes harm" in corrected, "Correction for ethical violation failed"
    logger.info(f"Test 6 (Propose Correction Ethical Violation) Passed. Corrected: {corrected}")

    # Test 7: Explain reasoning
    explanation_context = {
        "nlp_intent": "test_intent",
        "nlp_confidence": 0.8,
        "reasoning_steps": ["Step 1: Analyze", "Step 2: Plan"],
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
    assert stats["total_correction_attempts"] >= 2, "Total correction attempts count incorrect"
    logger.info(f"Test 8 (Get Stats) Passed. Stats: {stats}")

    logger.info("--- SelfCorrectionEngine Tests Passed ---")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_self_correction_engine())

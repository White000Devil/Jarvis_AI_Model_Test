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
    or low-confidence responses.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager, ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.ethical_ai_engine = ethical_ai_engine
        self.enabled = config.get("enabled", True)
        self.confidence_threshold = config.get("confidence_threshold", 0.6) # Confidence below which JARVIS will attempt self-correction
        self.inconsistency_threshold = config.get("inconsistency_threshold", 0.3) # Threshold for detecting inconsistency
        self.log_corrections = config.get("log_corrections", True)
        self.self_correction_log_path = Path(config.get("self_correction_log_path", "data/self_correction_log/corrections.jsonl"))
        self.recent_corrections: List[Dict[str, Any]] = [] # In-memory cache for recent corrections

        if self.enabled:
            logger.info("Self-Correction Engine initialized.")
        else:
            logger.info("Self-Correction Engine is disabled in configuration.")

    async def assess_confidence(self, jarvis_response: str, context: Dict[str, Any]) -> float:
        """
        Assesses the confidence level of JARVIS's response.
        This is a simplified assessment based on NLP confidence.
        In a real system, this would involve multiple factors (e.g., model certainty, data freshness).
        """
        if not self.enabled:
            return 1.0 # Full confidence if disabled

        logger.info(f"Assessing confidence for response: '{jarvis_response[:50]}...'")
        
        # Example: Use NLP confidence from initial processing as a base
        nlp_confidence = context.get("nlp_confidence", 0.5)
        
        # Simple rules to adjust confidence
        if "I'm sorry" in jarvis_response or "I cannot" in jarvis_response:
            nlp_confidence *= 0.8 # Lower confidence if JARVIS is apologetic or refusing
        if "I'm not sure" in jarvis_response:
            nlp_confidence *= 0.7
        if "I understand" in jarvis_response:
            nlp_confidence *= 1.1 # Slightly higher if showing understanding

        # If the response was ethically guarded, confidence might be lower on the original intent
        if context.get("ethical_guardrail_applied", False):
            nlp_confidence *= 0.9 # Indicate that the original response might have been problematic

        confidence_score = min(1.0, max(0.0, nlp_confidence)) # Keep between 0 and 1
        logger.info(f"Response confidence assessed: {confidence_score:.2f}")
        return confidence_score

    async def detect_inconsistency(self, jarvis_response: str, historical_context: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Detects inconsistencies between the current response and historical knowledge/conversations.
        This is a simplified check.
        """
        if not self.enabled:
            return False, None

        logger.debug(f"Detecting inconsistency for response: '{jarvis_response[:50]}...'")
        
        inconsistency_score = 0.0
        explanation = None

        # Example: Check if the current response contradicts a recent conversation
        for past_conv in historical_context:
            past_doc = past_conv.get("document", "").lower()
            if "jarvis:" in past_doc:
                past_jarvis_response = past_doc.split("jarvis:", 1)[1].strip()
                
                # Very basic keyword-based contradiction detection
                if "sql injection is a code injection" in past_jarvis_response and "sql injection is not a code injection" in jarvis_response.lower():
                    inconsistency_score = 0.9
                    explanation = "Direct contradiction with past statement about SQL injection."
                    break
                elif "sunny" in past_jarvis_response and "rainy" in jarvis_response.lower() and "weather" in past_doc:
                    # This would need to check timestamps to be valid (e.g., weather changes)
                    # For now, just a simple example
                    inconsistency_score = 0.5
                    explanation = "Potential contradiction in weather information."
                    break
        
        is_inconsistent = inconsistency_score > self.inconsistency_threshold
        if is_inconsistent:
            logger.warning(f"Inconsistency detected (score: {inconsistency_score:.2f}): {explanation}")
        
        return is_inconsistent, explanation

    async def propose_correction(self, original_response: str, error_explanation: str, user_input: str, context: Dict[str, Any]) -> str:
        """
        Proposes a corrected response based on detected errors or inconsistencies.
        """
        if not self.enabled:
            return original_response

        logger.info(f"Proposing self-correction for response: '{original_response[:50]}...' due to: {error_explanation}")
        
        corrected_response = original_response
        
        # Example correction logic:
        if "Direct contradiction" in error_explanation:
            corrected_response = f"My apologies, I seem to have provided conflicting information. To clarify: {user_input}. Let me re-evaluate."
            # In a real system, re-run reasoning or fetch correct info
        elif "Potential contradiction in weather" in error_explanation:
            corrected_response = f"My apologies, weather information can change rapidly. Let me get the most up-to-date weather for you."
            # Trigger a new weather API call
        elif "low confidence" in error_explanation.lower():
            corrected_response = f"I'm not entirely confident in my previous response. Let me try to provide a more accurate answer. {original_response}"
            # This could trigger a more detailed reasoning process or a search in memory

        # Log the correction
        if self.log_corrections:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "original_response": original_response,
                "corrected_response": corrected_response,
                "error_explanation": error_explanation,
                "context": context
            }
            # Ensure the log directory exists
            self.self_correction_log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.self_correction_log_path, 'a') as f:
                f.write(json.dumps(log_data) + '\n')
            logger.info(f"Logged self-correction to {self.self_correction_log_path}")

        return corrected_response

    def get_correction_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about self-correction activities.
        Reads from the self-correction log file.
        """
        stats = {"total_corrections": 0, "low_confidence_corrections": 0, "inconsistency_corrections": 0, "last_correction_timestamp": None}
        
        if self.self_correction_log_path.exists():
            with open(self.self_correction_log_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        stats["total_corrections"] += 1
                        if "low confidence" in data.get("error_explanation", "").lower():
                            stats["low_confidence_corrections"] += 1
                        if "inconsistency" in data.get("error_explanation", "").lower():
                            stats["inconsistency_corrections"] += 1
                        
                        timestamp = data.get("timestamp")
                        if timestamp:
                            if not stats["last_correction_timestamp"] or timestamp > stats["last_correction_timestamp"]:
                                stats["last_correction_timestamp"] = timestamp
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping malformed self-correction log line: {line.strip()}")
        
        return stats

    def _log_correction(self, user_input: str, original_response: str, corrected_response: str, reason: str, context: Dict[str, Any]):
        """Logs a self-correction event to a file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "original_response": original_response,
            "corrected_response": corrected_response,
            "reason": reason,
            "context": context
        }
        try:
            with open(self.self_correction_log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            self.recent_corrections.append(log_entry)
            # Keep only the last N corrections in memory
            self.recent_corrections = self.recent_corrections[-10:]
            logger.info(f"Self-correction logged to {self.self_correction_log_path}")
        except Exception as e:
            logger.error(f"Failed to log self-correction: {e}")

    def get_recent_corrections(self) -> List[Dict[str, Any]]:
        """Returns a list of recent self-correction logs from memory."""
        return self.recent_corrections

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

    correction_engine = SelfCorrectionEngine(mock_nlp, mock_memory, mock_ethical, config={"enabled": True, "confidence_threshold": 0.7, "self_correction_log_path": "data/self_correction_log/corrections.jsonl"})

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
    assert stats["total_corrections"] >= 2, "Total correction attempts count incorrect"
    logger.info(f"Test 8 (Get Stats) Passed. Stats: {stats}")

    logger.info("--- SelfCorrectionEngine Tests Passed ---")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_self_correction_engine())

from loguru import logger
from datetime import datetime
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.ethical_ai import EthicalAIEngine # Assuming EthicalAIEngine is available
import time

class SelfCorrectionEngine:
    """
    Enables JARVIS AI to detect and correct its own errors, inconsistencies,
    or low-confidence responses.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager, ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.ethical_ai_engine = ethical_ai_engine # For re-checking ethics after correction
        self.enabled = config.get("enabled", False)
        self.confidence_threshold = config.get("confidence_threshold", 0.6)
        self.inconsistency_threshold = config.get("inconsistency_threshold", 0.3)
        self.log_corrections = config.get("log_corrections", True)
        self.self_correction_log_path = config.get("self_correction_log_path")

        self.correction_stats = {
            "total_corrections": 0,
            "low_confidence_corrections": 0,
            "inconsistency_corrections": 0,
            "last_correction_timestamp": None
        }
        logger.info(f"Self-Correction Engine initialized. Enabled: {self.enabled}")

    async def assess_confidence(self, jarvis_response: str, context: Dict[str, Any]) -> float:
        """
        Assesses the confidence level of JARVIS's generated response.
        This can be based on NLP confidence, reasoning confidence, or external model scores.
        """
        if not self.enabled:
            return 1.0 # Assume full confidence if disabled

        # Use the confidence score from the reasoning engine if available
        reasoning_confidence = context.get("jarvis_confidence", 0.0)
        nlp_confidence = context.get("nlp_confidence", 0.0)

        # Combine confidence scores (simple average for now)
        # In a real system, this would be a more sophisticated aggregation or a dedicated confidence model.
        combined_confidence = (reasoning_confidence + nlp_confidence) / 2.0 if reasoning_confidence > 0 or nlp_confidence > 0 else 0.0
        
        logger.debug(f"Assessed confidence for response: {combined_confidence:.2f}")
        return combined_confidence

    async def detect_inconsistency(self, jarvis_response: str, historical_context: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        """
        Detects if the current response is inconsistent with past interactions or known facts.
        Returns True and a reason if inconsistent, else False and None.
        """
        if not self.enabled:
            return False, None

        logger.debug("Detecting inconsistencies...")

        # Very simplified inconsistency detection: check for direct contradictions with recent history
        # In a real system, this would involve semantic comparison and knowledge graph checks.
        
        # Example: If JARVIS previously said "X is Y" and now says "X is Z"
        for past_conv in historical_context:
            past_response = past_conv.get("jarvis_response", "").lower()
            past_user_input = past_conv.get("user_message", "").lower()

            # Simple keyword-based contradiction check
            if "capital of france is paris" in past_response and "capital of france is berlin" in jarvis_response.lower():
                return True, "Contradicts previous statement about capital of France."
            
            # Check if current response directly negates a previous positive statement
            if "yes" in past_response and "no" in jarvis_response.lower() and past_user_input in jarvis_response.lower():
                return True, "Direct contradiction with previous affirmative response."

        # Check against known facts from security knowledge (simplified)
        # This would require searching the security_knowledge_collection for contradictions
        # For example, if JARVIS states a CVE is patched, but security KB says it's active.
        # This is a placeholder for a more advanced check.
        
        return False, None

    async def propose_correction(self, original_response: str, error_explanation: str, user_input: str, context: Dict[str, Any]) -> str:
        """
        Proposes a corrected response based on the detected error.
        This might involve re-running parts of the pipeline or using a fallback.
        """
        if not self.enabled:
            return original_response

        logger.warning(f"Proposing correction for: '{original_response}' due to '{error_explanation}'")
        
        corrected_response = original_response # Default to original if no correction can be made

        if error_explanation == "low_confidence":
            # Attempt to rephrase or provide a more cautious answer
            corrected_response = f"I'm not entirely certain, but based on my current understanding: {original_response}. Could you provide more details if this isn't what you're looking for?"
            self.correction_stats["low_confidence_corrections"] += 1
        elif "inconsistency" in error_explanation:
            # Acknowledge inconsistency and try to reconcile or state uncertainty
            corrected_response = f"My apologies, that seems inconsistent with previous information. {error_explanation}. Let me re-evaluate: {original_response}"
            self.correction_stats["inconsistency_corrections"] += 1
        
        # After proposing a correction, re-run ethical check to ensure the correction itself is ethical
        is_ethical, ethical_violations = await self.ethical_ai_engine.check_response_for_ethics(user_input, corrected_response, context)
        if not is_ethical:
            logger.error("Proposed correction itself is unethical. Applying ethical guardrails again.")
            corrected_response = await self.ethical_ai_engine.apply_ethical_guardrails(user_input, corrected_response, ethical_violations)
            # If the correction is still problematic, it might lead to a generic refusal.

        self.correction_stats["total_corrections"] += 1
        self.correction_stats["last_correction_timestamp"] = time.time()
        
        if self.log_corrections:
            self._log_correction(user_input, original_response, corrected_response, error_explanation, context)

        logger.info(f"Corrected response: '{corrected_response}'")
        return corrected_response

    def _log_correction(self, user_input: str, original_response: str, corrected_response: str, error_explanation: str, context: Dict[str, Any]):
        """Logs details of a self-correction event."""
        if not self.log_corrections or not self.self_correction_log_path:
            return

        log_entry = {
            "timestamp": time.time(),
            "user_input": user_input,
            "original_response": original_response,
            "corrected_response": corrected_response,
            "error_explanation": error_explanation,
            "context_summary": {k: v for k, v in context.items() if k in ["nlp_intent", "nlp_confidence", "session_id", "jarvis_confidence"]}
        }
        
        try:
            with open(self.self_correction_log_path, 'a') as f:
                import json
                f.write(json.dumps(log_entry) + '\n')
            logger.debug(f"Logged self-correction to {self.self_correction_log_path}")
        except Exception as e:
            logger.error(f"Failed to log self-correction: {e}")

    def get_correction_stats(self) -> Dict[str, Any]:
        """Returns current self-correction statistics."""
        return self.correction_stats

    async def explain_reasoning(self, user_query: str, jarvis_response: str, context: Dict[str, Any]) -> str:
        """
        Provides a detailed explanation of JARVIS's reasoning process for transparency.
        """
        if not self.enabled:
            return "Self-correction and reasoning explanation is disabled."

        explanation = "## JARVIS Reasoning Explanation\n\n"
        
        # NLP Understanding
        explanation += f"**Understanding**: I identified the intent as '{context.get('nlp_intent', 'unknown')}' "
        explanation += f"with {context.get('nlp_confidence', 0.0):.2f} confidence.\n\n"
        
        # Memory Recall
        conv_history = context.get('conversation_history', [])
        knowledge_recall = context.get('knowledge_recall', [])
        if conv_history or knowledge_recall:
            explanation += f"**Memory Recall**: I found {len(conv_history)} relevant past conversations "
            explanation += f"and {len(knowledge_recall)} knowledge articles.\n\n"
        
        # Planning & Decision
        reasoning_steps = context.get('reasoning_steps', [])
        if reasoning_steps:
            explanation += "**Planning & Decision**:\n"
            for step in reasoning_steps:
                explanation += f"- {step}\n"
            explanation += "\n"
        
        # Confidence & Consistency
        explanation += f"**Confidence & Consistency**: My confidence in this response is "
        explanation += f"{context.get('jarvis_confidence', 0.0):.2f}. "
        explanation += f"Consistency score: {context.get('consistency_score', 'N/A')}.\n\n"
        
        # Self-Correction
        if context.get('self_corrected', False):
            explanation += "**Self-Correction**: I detected issues with my initial response and applied corrections.\n\n"
        
        # Ethical Considerations
        ethical_violations = context.get('ethical_violations', [])
        if ethical_violations:
            explanation += f"**Ethical Review**: I detected {len(ethical_violations)} potential ethical concerns "
            explanation += "and applied appropriate guardrails.\n\n"
        else:
            explanation += "**Ethical Review**: No ethical concerns detected.\n\n"
        
        # Human-AI Teaming
        teaming_stats = context.get('teaming_stats', {})
        if teaming_stats.get('adaptive_communication_enabled'):
            explanation += "**Communication Adaptation**: I adapted my communication style based on context.\n\n"
        
        # Final Assessment
        explanation += f"**Final Assessment**: This response represents my best understanding given "
        explanation += f"the available information and ethical constraints."
        
        return explanation

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
    corrected = await correction_engine.propose_correction("Original response.", "low_confidence", "Test query", {"nlp_confidence": 0.4})
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

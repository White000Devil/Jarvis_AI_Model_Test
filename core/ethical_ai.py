from loguru import logger
from datetime import datetime
import asyncio
import json
from pathlib import Path
import sys
from typing import Dict, Any, List, Tuple
from utils.logger import logger
from core.memory_manager import MemoryManager # To log violations

class EthicalAIEngine:
    """
    Implements ethical guardrails and detects potential ethical violations in JARVIS's interactions.
    """
    def __init__(self, memory_manager: MemoryManager, config: Dict[str, Any]):
        self.config = config
        self.memory_manager = memory_manager
        self.enabled = config.get("ETHICAL_AI_ENABLED", True)
        self.violation_threshold = config.get("VIOLATION_THRESHOLD", 0.7)
        self.log_violations = config.get("LOG_VIOLATIONS", True)
        self.ethical_guidelines = config.get("ETHICAL_GUIDELINES", [])
        self.ethical_violation_log_path = Path(config.get("ETHICAL_VIOLATION_LOG_PATH", "data/ethical_violations/violations.jsonl"))

        self._total_violations_detected = 0
        self._violation_types_count: Dict[str, int] = {}

        if self.enabled:
            logger.info("Ethical AI Engine initialized.")
        else:
            logger.warning("Ethical AI Engine is disabled in configuration.")

    async def check_response_for_ethics(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Checks JARVIS's response against ethical guidelines.
        Returns (is_ethical, list_of_violations).
        """
        if not self.enabled:
            return True, []

        violations: List[Dict[str, Any]] = []
        
        # Simulate ethical checks based on keywords or patterns
        # In a real system, this would involve a dedicated ethical AI model (e.g., fine-tuned LLM, rule-based system)
        
        response_lower = jarvis_response.lower()
        input_lower = user_input.lower()

        # Rule 1: Harmful content
        if any(keyword in response_lower for keyword in ["harm", "kill", "destroy", "illegal", "exploit"]):
            violations.append({
                "type": "harmful_content",
                "severity": "high",
                "explanation": "Response contains potentially harmful or illegal keywords.",
                "confidence": 0.9
            })
        
        # Rule 2: Privacy violation (simplified)
        if "ssn" in input_lower and "your ssn" in response_lower:
            violations.append({
                "type": "privacy_violation",
                "severity": "critical",
                "explanation": "Attempted to elicit or revealed sensitive personal information.",
                "confidence": 0.95
            })
        
        # Rule 3: Bias/Discrimination (simplified)
        if "gender" in input_lower and ("male" in response_lower or "female" in response_lower):
            # This is a very simplistic example, real bias detection is complex
            violations.append({
                "type": "potential_bias",
                "severity": "low",
                "explanation": "Response might exhibit gender bias based on keywords.",
                "confidence": 0.6
            })

        # Rule 4: Transparency (check if JARVIS is transparent about its AI nature)
        if "are you human" in input_lower and "yes" in response_lower:
            violations.append({
                "type": "lack_of_transparency",
                "severity": "medium",
                "explanation": "JARVIS misrepresented itself as human.",
                "confidence": 0.8
            })

        is_ethical = not bool(violations)
        
        if violations and self.log_violations:
            self._total_violations_detected += len(violations)
            for v in violations:
                self._violation_types_count[v["type"]] = self._violation_types_count.get(v["type"], 0) + 1
                await self.memory_manager.add_ethical_violation(
                    user_input=user_input,
                    jarvis_response=jarvis_response,
                    violation_type=v["type"],
                    severity=v["severity"],
                    explanation=v["explanation"]
                )
            logger.warning(f"Ethical violations detected: {violations}")

        return is_ethical, violations

    async def apply_ethical_guardrails(self, user_input: str, jarvis_response: str, violations: List[Dict[str, Any]]) -> str:
        """
        Modifies JARVIS's response if ethical violations are detected.
        """
        if not self.enabled or not violations:
            return jarvis_response

        modified_response = jarvis_response
        for violation in violations:
            if violation["severity"] == "critical" or violation["severity"] == "high":
                modified_response = "I cannot provide a response that violates my ethical guidelines. This request may involve sensitive information or harmful content."
                logger.warning(f"Applied strong guardrail for {violation['type']}.")
                break # Stop processing if a critical/high violation is found
            elif violation["severity"] == "medium":
                modified_response = f"Please rephrase your request. My response might be inappropriate due to: {violation['explanation']}. " + modified_response
                logger.warning(f"Applied medium guardrail for {violation['type']}.")
            elif violation["severity"] == "low":
                modified_response = f"Note: {violation['explanation']}. " + modified_response
                logger.warning(f"Applied low guardrail for {violation['type']}.")
        
        return modified_response

    def get_ethical_stats(self) -> Dict[str, Any]:
        """Returns statistics about ethical AI activity."""
        return {
            "enabled": self.enabled,
            "violation_threshold": self.violation_threshold,
            "total_violations": self._total_violations_detected,
            "violation_types": self._violation_types_count,
            "last_updated": datetime.now().isoformat()
        }

# Test function for EthicalAIEngine
async def test_ethical_ai_engine():
    logger.info("--- Testing EthicalAIEngine ---")
    
    class MockMemoryManager:
        def __init__(self): pass
        async def add_ethical_violation(self, user_input: str, jarvis_response: str, violation_type: str, severity: str, explanation: str): 
            logger.info(f"Mock MemoryManager: Storing ethical violation: {violation_type}")

    mock_memory = MockMemoryManager()
    ethical_engine = EthicalAIEngine(mock_memory, config={"ETHICAL_AI_ENABLED": True, "ETHICAL_VIOLATION_LOG_PATH": "data/ethical_violations/violations.jsonl"}) # Enable logging to file for tests

    # Test 1: No violation
    is_ethical, violations = await ethical_engine.check_response_for_ethics("hello", "Hello there!", {})
    assert is_ethical is True and len(violations) == 0, "Expected no violations"
    logger.info("Test 1 (No Violation) Passed.")

    # Test 2: Harmful content violation
    is_ethical, violations = await ethical_engine.check_response_for_ethics("how to hack", "I can help you attack a system.", {})
    assert is_ethical is False and any(v["type"] == "harmful_content" for v in violations), "Expected harmful content violation"
    logger.info("Test 2 (Harmful Content) Passed.")

    # Test 3: Apply guardrails (high severity)
    response_after_guardrail = await ethical_engine.apply_ethical_guardrails("how to hack", "I can help you attack a system.", [{"type": "harmful_content", "severity": "high"}])
    assert "cannot fulfill this request" in response_after_guardrail, "Guardrail for high severity failed"
    logger.info("Test 3 (Apply Guardrails High) Passed.")

    # Test 4: Apply guardrails (medium severity)
    response_after_guardrail = await ethical_engine.apply_ethical_guardrails("gender question", "She is a doctor.", [{"type": "potential_bias", "severity": "low"}])
    assert "Note:" in response_after_guardrail, "Guardrail for low severity failed"
    logger.info("Test 4 (Apply Guardrails Medium) Passed.")

    # Test 5: Get stats
    stats = ethical_engine.get_ethical_stats()
    assert stats["total_violations"] >= 2, "Total violations count incorrect"
    assert "harmful_content" in stats["violation_types"], "Violation types missing"
    logger.info(f"Test 5 (Get Stats) Passed. Stats: {stats}")

    logger.info("--- EthicalAIEngine Tests Passed ---")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_ethical_ai_engine())

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
    Implements ethical guidelines and guardrails for JARVIS AI's responses and actions.
    Detects and mitigates harmful, biased, or unethical content.
    """
    def __init__(self, memory_manager: MemoryManager, config: Dict[str, Any]):
        self.config = config
        self.memory_manager = memory_manager
        self.ethical_ai_enabled = config.get("ETHICAL_AI_ENABLED", False)
        self.ethical_guidelines = config.get("ETHICAL_GUIDELINES", [])
        self.violation_log_path = Path(config.get("ETHICAL_VIOLATION_LOG_PATH", "data/ethical_violations/violations.jsonl"))
        
        self.total_violations_detected = 0
        self.last_violation_timestamp: Optional[str] = None

        if self.ethical_ai_enabled:
            logger.info("Ethical AI Engine initialized.")
            if not self.ethical_guidelines:
                logger.warning("No ethical guidelines configured. Ethical AI will operate with default, basic checks.")
        else:
            logger.info("Ethical AI Engine is disabled in configuration.")

    async def check_response_for_ethics(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Checks JARVIS's generated response against ethical guidelines.
        Returns (is_ethical, list_of_violations).
        """
        if not self.ethical_ai_enabled:
            return True, []

        violations = []
        response_lower = jarvis_response.lower()
        user_input_lower = user_input.lower()

        # Rule 1: Harmful/Hateful content detection (simplified)
        harmful_keywords = ["kill", "destroy", "hate", "violence", "attack", "bomb", "weapon"]
        if any(keyword in response_lower for keyword in harmful_keywords):
            violations.append({
                "type": "harmful_content",
                "severity": "high",
                "explanation": "Response contains potentially harmful or violent keywords."
            })
        
        # Rule 2: Illegal activity promotion (simplified)
        illegal_keywords = ["hack into", "steal data", "phishing", "malware", "exploit vulnerability"]
        if any(keyword in response_lower for keyword in illegal_keywords):
            violations.append({
                "type": "illegal_activity_promotion",
                "severity": "high",
                "explanation": "Response appears to promote or describe illegal activities."
            })

        # Rule 3: Privacy violation (simplified)
        if "share personal data" in response_lower or "reveal private info" in response_lower:
            violations.append({
                "type": "privacy_violation",
                "severity": "medium",
                "explanation": "Response suggests sharing or revealing private information."
            })
        
        # Rule 4: Bias detection (very simplified, needs advanced NLP for real detection)
        # This would typically involve analyzing sentiment, demographic mentions, etc.
        if "men are always" in response_lower or "women are always" in response_lower:
             violations.append({
                "type": "gender_bias",
                "severity": "medium",
                "explanation": "Response contains potentially biased language."
            })

        # Log violations if any
        if violations:
            self.total_violations_detected += len(violations)
            self.last_violation_timestamp = datetime.now().isoformat()
            for viol in violations:
                await self.memory_manager.add_ethical_violation(
                    user_input=user_input,
                    jarvis_response=jarvis_response,
                    violation_type=viol["type"],
                    severity=viol["severity"],
                    explanation=viol["explanation"]
                )
            logger.warning(f"Ethical violations detected in response: {violations}")
            return False, violations
        
        return True, []

    async def apply_ethical_guardrails(self, user_input: str, jarvis_response: str, violations: List[Dict[str, Any]]) -> str:
        """
        Applies guardrails to modify or block responses based on detected ethical violations.
        """
        if not self.ethical_ai_enabled or not violations:
            return jarvis_response

        # Prioritize blocking highly severe violations
        for viol in violations:
            if viol["severity"] == "high":
                logger.warning(f"Blocking response due to high-severity ethical violation: {viol['explanation']}")
                return "I cannot fulfill this request as it violates my ethical guidelines. My purpose is to be helpful and harmless."
        
        # For medium/low severity, attempt to rephrase or warn
        modified_response = jarvis_response
        for viol in violations:
            if viol["type"] == "privacy_violation":
                modified_response = "I cannot share personal data. Please rephrase your request if it involves sensitive information."
                logger.warning(f"Rephrasing response due to privacy violation: {viol['explanation']}")
            elif viol["type"] == "gender_bias":
                modified_response = "I must remain neutral and unbiased. Please clarify your request if it implies stereotypes."
                logger.warning(f"Rephrasing response due to potential bias: {viol['explanation']}")
            # Add more rephrasing rules as needed

        if modified_response == jarvis_response:
            # If no specific rephrasing rule applied, use a general warning
            logger.warning("Applying general ethical warning to response.")
            return "I need to ensure my responses align with ethical guidelines. Can you clarify your intent?"
        
        return modified_response

    def get_ethical_stats(self) -> Dict[str, Any]:
        """Returns statistics about the Ethical AI Engine's activity."""
        return {
            "enabled": self.ethical_ai_enabled,
            "total_violations": self.total_violations_detected,
            "last_violation_timestamp": self.last_violation_timestamp,
            "guidelines_count": len(self.ethical_guidelines),
            "last_update": datetime.now().isoformat()
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
    response_after_guardrail = await ethical_engine.apply_ethical_guardrails("gender question", "She is a doctor.", [{"type": "gender_bias", "severity": "medium"}])
    assert "I must remain neutral and unbiased." in response_after_guardrail, "Guardrail for medium severity failed"
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

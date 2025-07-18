from loguru import logger
from datetime import datetime
import asyncio
import json
from pathlib import Path
import sys
from typing import Dict, Any, List, Tuple, Optional
from utils.logger import logger
from core.memory_manager import MemoryManager # To log violations

class EthicalAIEngine:
    """
    Implements ethical guardrails and detects potential ethical violations in JARVIS's interactions.
    """
    def __init__(self, memory_manager: MemoryManager, config: Dict[str, Any]):
        self.config = config
        self.memory_manager = memory_manager
        self.enabled = config.get("enabled", True)
        self.violation_threshold = config.get("violation_threshold", 0.7)
        self.log_violations = config.get("log_violations", True)
        self.ethical_guidelines = config.get("ethical_guidelines", [])
        self.ethical_violation_log_path = Path(config.get("ethical_violation_log_path", "data/ethical_violations/violations.jsonl"))
        self.recent_violations: List[Dict[str, Any]] = [] # In-memory cache for recent violations

        # Ensure log directory exists
        self.ethical_violation_log_path.parent.mkdir(parents=True, exist_ok=True)

        if self.enabled:
            logger.info("Ethical AI Engine initialized.")
            if not self.ethical_guidelines:
                logger.warning("No ethical guidelines configured. Ethical AI will operate with default, limited checks.")
        else:
            logger.info("Ethical AI Engine is disabled in configuration.")

    async def check_response_for_ethics(self, user_input: str, jarvis_response: str, context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Checks JARVIS's response against ethical guidelines.
        Returns (is_ethical, list_of_violations).
        """
        if not self.enabled:
            return True, []

        logger.info(f"Checking response for ethical violations: '{jarvis_response[:50]}...'")
        violations = []
        
        # Simulate ethical checks based on keywords and guidelines
        response_lower = jarvis_response.lower()
        input_lower = user_input.lower()

        # Rule 1: Harmful/Hateful content
        if any(word in response_lower for word in ["kill", "harm", "destroy", "hate", "discriminat"]):
            violations.append({"type": "harmful_content", "explanation": "Response contains potentially harmful or hateful language."})
        
        # Rule 2: Illegal activities
        if any(word in input_lower for word in ["hack", "steal", "illegal", "crack"]):
            if "assist" not in response_lower and "cannot" not in response_lower:
                violations.append({"type": "illegal_activity_assistance", "explanation": "Response might assist with illegal or unethical activities."})

        # Rule 3: Privacy (simplified)
        if "personal data" in response_lower and "share" in response_lower:
            violations.append({"type": "privacy_breach", "explanation": "Response suggests sharing personal data inappropriately."})

        # Rule 4: Transparency (simplified)
        if "i am human" in response_lower or "i have feelings" in response_lower:
            violations.append({"type": "lack_of_transparency", "explanation": "Response misrepresents AI nature."})

        # More advanced checks would involve NLP models for toxicity, bias, etc.
        # For now, we use a simple confidence score based on number of violations
        violation_score = len(violations) * 0.5 # Each violation adds 0.5 to score

        if violation_score >= self.violation_threshold:
            logger.warning(f"Ethical violation detected (score: {violation_score:.2f}). Violations: {violations}")
            if self.log_violations:
                self._log_violation(user_input, jarvis_response, violations, context)
            return False, violations
        
        logger.info("No significant ethical violations detected.")
        return True, []

    async def apply_ethical_guardrails(self, user_input: str, original_response: str, violations: List[Dict[str, Any]]) -> str:
        """
        Applies guardrails to modify or replace responses that violate ethical guidelines.
        """
        if not self.enabled:
            return original_response

        logger.info("Applying ethical guardrails...")
        
        # Simple rule-based modification
        if any(v["type"] == "harmful_content" for v in violations):
            return "I cannot generate content that is harmful or promotes hate."
        elif any(v["type"] == "illegal_activity_assistance" for v in violations):
            return "I cannot assist with illegal or unethical activities."
        elif any(v["type"] == "privacy_breach" for v in violations):
            return "I am designed to protect user privacy and cannot share sensitive information."
        elif any(v["type"] == "lack_of_transparency" for v in violations):
            return "As an AI, I do not have personal feelings or human experiences. How can I help you with factual information?"
        
        # Default fallback if no specific rule applies
        return "I'm sorry, but I cannot provide a response that goes against my ethical guidelines."

    def _log_violation(self, user_input: str, jarvis_response: str, violations: List[Dict[str, Any]], context: Dict[str, Any]):
        """Logs an ethical violation to a file."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "original_response": jarvis_response,
            "violations": violations,
            "context": context
        }
        try:
            with open(self.ethical_violation_log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            self.recent_violations.append(log_entry)
            # Keep only the last N violations in memory
            self.recent_violations = self.recent_violations[-10:] 
            logger.info(f"Ethical violation logged to {self.ethical_violation_log_path}")
        except Exception as e:
            logger.error(f"Failed to log ethical violation: {e}")

    def get_recent_violations(self) -> List[Dict[str, Any]]:
        """Returns a list of recent ethical violations from memory."""
        return self.recent_violations

    def get_ethical_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about ethical violations.
        Reads from the ethical violation log file.
        """
        stats = {"total_violations": 0, "high_severity": 0, "critical_severity": 0, "last_violation_timestamp": None, "violation_types": {}}
        
        if self.ethical_violation_log_path.exists():
            with open(self.ethical_violation_log_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get("log_type") == "ethical_violation":
                            stats["total_violations"] += 1
                            severity = data.get("severity", "unknown").lower()
                            violation_type = data.get("violation_type", "unknown")
                            
                            if severity == "high":
                                stats["high_severity"] += 1
                            elif severity == "critical":
                                stats["critical_severity"] += 1
                            
                            stats["violation_types"][violation_type] = stats["violation_types"].get(violation_type, 0) + 1
                            
                            timestamp = data.get("timestamp")
                            if timestamp:
                                if not stats["last_violation_timestamp"] or timestamp > stats["last_violation_timestamp"]:
                                    stats["last_violation_timestamp"] = timestamp
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping malformed ethical violation log line: {line.strip()}")
        
        return stats

# Test function for EthicalAIEngine
async def test_ethical_ai_engine():
    logger.info("--- Testing EthicalAIEngine ---")
    
    class MockMemoryManager:
        def __init__(self): pass
        async def add_ethical_violation(self, user_input: str, jarvis_response: str, violation_type: str, severity: str, explanation: str): 
            logger.info(f"Mock MemoryManager: Storing ethical violation: {violation_type}")

    mock_memory = MockMemoryManager()
    ethical_engine = EthicalAIEngine(mock_memory, config={"enabled": True, "ethical_violation_log_path": "data/ethical_violations/violations.jsonl"}) # Enable logging to file for tests

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

import asyncio
import json
import time
from typing import Dict, Any, List, Tuple, Optional
from utils.logger import logger
from core.memory_manager import MemoryManager
import re

class EthicalAIEngine:
    """
    Ethical AI engine for JARVIS AI.
    Ensures responses comply with ethical guidelines and safety standards.
    """
    
    def __init__(self, memory_manager: MemoryManager, config: Dict[str, Any]):
        self.memory_manager = memory_manager
        self.config = config
        self.enabled = config.get("enabled", True)
        self.strict_mode = config.get("strict_mode", True)
        self.violation_log_path = config.get("violation_log_path", "data/ethical_violations")
        self.guidelines = config.get("guidelines", [
            "No harmful content",
            "Respect privacy",
            "Be truthful and accurate",
            "Avoid bias and discrimination"
        ])
        
        # Initialize violation patterns
        self.violation_patterns = self._initialize_violation_patterns()
        
        # Statistics
        self.violation_stats = {
            "total_checks": 0,
            "violations_detected": 0,
            "violations_by_type": {},
            "last_violation_time": None
        }
        
        logger.info(f"Ethical AI Engine initialized. Enabled: {self.enabled}, Strict Mode: {self.strict_mode}")
    
    def _initialize_violation_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for detecting ethical violations."""
        return {
            "harmful_content": [
                r"kill|murder|suicide|self-harm|violence|weapon|bomb|explosive",
                r"hate|racist|sexist|discriminat|prejudice|bigot",
                r"illegal|drug|narcotic|trafficking|fraud|scam"
            ],
            "privacy_violation": [
                r"personal information|social security|credit card|password|private key",
                r"home address|phone number|email.*password|bank account",
                r"medical record|health information|confidential"
            ],
            "misinformation": [
                r"fake news|conspiracy|hoax|false claim|misleading",
                r"unverified|rumor|speculation presented as fact"
            ],
            "inappropriate_content": [
                r"sexual|explicit|adult content|pornographic|nsfw",
                r"inappropriate|offensive|vulgar|profanity"
            ],
            "bias_discrimination": [
                r"stereotype|generalization.*race|gender bias|age discrimination",
                r"religious intolerance|cultural superiority|ethnic slur"
            ]
        }
    
    async def check_response_for_ethics(self, user_input: str, jarvis_response: str, 
                                      context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if a response violates ethical guidelines.
        
        Args:
            user_input: Original user input
            jarvis_response: JARVIS's proposed response
            context: Additional context information
            
        Returns:
            Tuple of (is_ethical, list_of_violations)
        """
        if not self.enabled:
            return True, []
        
        self.violation_stats["total_checks"] += 1
        violations = []
        
        try:
            # Check for various types of violations
            violations.extend(await self._check_harmful_content(jarvis_response))
            violations.extend(await self._check_privacy_violations(jarvis_response))
            violations.extend(await self._check_misinformation(jarvis_response))
            violations.extend(await self._check_inappropriate_content(jarvis_response))
            violations.extend(await self._check_bias_discrimination(jarvis_response))
            
            # Check context-specific violations
            violations.extend(await self._check_context_violations(user_input, jarvis_response, context))
            
            # Update statistics
            if violations:
                self.violation_stats["violations_detected"] += 1
                self.violation_stats["last_violation_time"] = time.time()
                
                for violation in violations:
                    violation_type = violation["type"]
                    self.violation_stats["violations_by_type"][violation_type] = \
                        self.violation_stats["violations_by_type"].get(violation_type, 0) + 1
                
                # Log violations
                await self._log_violation(user_input, jarvis_response, violations, context)
            
            is_ethical = len(violations) == 0
            logger.debug(f"Ethical check completed. Violations: {len(violations)}, Ethical: {is_ethical}")
            
            return is_ethical, violations
            
        except Exception as e:
            logger.error(f"Error during ethical check: {e}")
            # In case of error, be conservative and flag as potential violation
            return False, [{"type": "system_error", "description": f"Ethical check failed: {e}"}]
    
    async def _check_harmful_content(self, text: str) -> List[Dict[str, Any]]:
        """Check for harmful content."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.violation_patterns["harmful_content"]:
            if re.search(pattern, text_lower):
                violations.append({
                    "type": "harmful_content",
                    "description": "Content contains potentially harmful language or references",
                    "pattern_matched": pattern,
                    "severity": "high"
                })
        
        return violations
    
    async def _check_privacy_violations(self, text: str) -> List[Dict[str, Any]]:
        """Check for privacy violations."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.violation_patterns["privacy_violation"]:
            if re.search(pattern, text_lower):
                violations.append({
                    "type": "privacy_violation",
                    "description": "Content may contain or request private information",
                    "pattern_matched": pattern,
                    "severity": "high"
                })
        
        # Check for specific patterns like email addresses, phone numbers
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}-\d{3}-\d{4}\b|\b$$\d{3}$$\s*\d{3}-\d{4}\b'
        
        if re.search(email_pattern, text):
            violations.append({
                "type": "privacy_violation",
                "description": "Content contains email address",
                "pattern_matched": "email_address",
                "severity": "medium"
            })
        
        if re.search(phone_pattern, text):
            violations.append({
                "type": "privacy_violation",
                "description": "Content contains phone number",
                "pattern_matched": "phone_number",
                "severity": "medium"
            })
        
        return violations
    
    async def _check_misinformation(self, text: str) -> List[Dict[str, Any]]:
        """Check for potential misinformation."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.violation_patterns["misinformation"]:
            if re.search(pattern, text_lower):
                violations.append({
                    "type": "misinformation",
                    "description": "Content may contain unverified or misleading information",
                    "pattern_matched": pattern,
                    "severity": "medium"
                })
        
        return violations
    
    async def _check_inappropriate_content(self, text: str) -> List[Dict[str, Any]]:
        """Check for inappropriate content."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.violation_patterns["inappropriate_content"]:
            if re.search(pattern, text_lower):
                violations.append({
                    "type": "inappropriate_content",
                    "description": "Content contains inappropriate or explicit material",
                    "pattern_matched": pattern,
                    "severity": "high"
                })
        
        return violations
    
    async def _check_bias_discrimination(self, text: str) -> List[Dict[str, Any]]:
        """Check for bias and discrimination."""
        violations = []
        text_lower = text.lower()
        
        for pattern in self.violation_patterns["bias_discrimination"]:
            if re.search(pattern, text_lower):
                violations.append({
                    "type": "bias_discrimination",
                    "description": "Content may contain biased or discriminatory language",
                    "pattern_matched": pattern,
                    "severity": "high"
                })
        
        return violations
    
    async def _check_context_violations(self, user_input: str, jarvis_response: str, 
                                      context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for context-specific violations."""
        violations = []
        
        # Check if response is inconsistent with ethical guidelines
        user_sentiment = context.get("user_sentiment", {})
        if user_sentiment.get("label") == "negative" and "angry" in jarvis_response.lower():
            violations.append({
                "type": "emotional_escalation",
                "description": "Response may escalate negative emotions",
                "severity": "medium"
            })
        
        # Check for overly confident claims without evidence
        confidence_indicators = ["definitely", "certainly", "absolutely", "guaranteed", "100%"]
        if any(indicator in jarvis_response.lower() for indicator in confidence_indicators):
            if context.get("jarvis_confidence", 1.0) < 0.8:
                violations.append({
                    "type": "overconfidence",
                    "description": "Response expresses high certainty despite low confidence",
                    "severity": "low"
                })
        
        return violations
    
    async def apply_ethical_guardrails(self, user_input: str, jarvis_response: str, 
                                     violations: List[Dict[str, Any]]) -> str:
        """
        Apply ethical guardrails to modify or replace a response.
        
        Args:
            user_input: Original user input
            jarvis_response: Original response
            violations: List of detected violations
            
        Returns:
            Modified or replacement response
        """
        if not violations:
            return jarvis_response
        
        # Categorize violations by severity
        high_severity = [v for v in violations if v.get("severity") == "high"]
        medium_severity = [v for v in violations if v.get("severity") == "medium"]
        low_severity = [v for v in violations if v.get("severity") == "low"]
        
        # Handle high severity violations - replace response entirely
        if high_severity:
            violation_types = [v["type"] for v in high_severity]
            
            if "harmful_content" in violation_types:
                return "I cannot and will not provide information that could be harmful or dangerous. Is there something else I can help you with?"
            
            elif "privacy_violation" in violation_types:
                return "I cannot share or request personal or private information. Let me help you with something else instead."
            
            elif "inappropriate_content" in violation_types:
                return "I'm designed to maintain appropriate conversations. Could we discuss something else?"
            
            elif "bias_discrimination" in violation_types:
                return "I strive to be fair and unbiased in all interactions. Let me provide a more balanced perspective."
            
            else:
                return "I apologize, but I cannot provide that response. How else can I assist you today?"
        
        # Handle medium severity violations - modify response with warnings
        elif medium_severity:
            violation_types = [v["type"] for v in medium_severity]
            
            if "misinformation" in violation_types:
                return f"Please note that I cannot verify all information. {jarvis_response} I recommend checking reliable sources for confirmation."
            
            elif "privacy_violation" in violation_types:
                return "I notice you're asking about sensitive information. I can provide general guidance, but please be cautious about sharing personal details."
            
            elif "emotional_escalation" in violation_types:
                return f"I understand this might be frustrating. Let me try to help in a constructive way: {jarvis_response}"
        
        # Handle low severity violations - add disclaimers
        elif low_severity:
            if "overconfidence" in [v["type"] for v in low_severity]:
                return f"Based on my current understanding: {jarvis_response}. However, I recommend verifying this information from authoritative sources."
        
        # Default fallback
        return "I want to provide helpful information while maintaining ethical standards. Could you rephrase your question?"
    
    async def _log_violation(self, user_input: str, jarvis_response: str, 
                           violations: List[Dict[str, Any]], context: Dict[str, Any]):
        """Log ethical violations for analysis and improvement."""
        try:
            violation_data = {
                "timestamp": time.time(),
                "user_input": user_input,
                "jarvis_response": jarvis_response,
                "violations": violations,
                "context_summary": {
                    "intent": context.get("nlp_intent"),
                    "sentiment": context.get("user_sentiment"),
                    "confidence": context.get("jarvis_confidence")
                }
            }
            
            # Store in memory manager
            await self.memory_manager.add_ethical_violation(violation_data)
            
            # Also log to file if path is specified
            if self.violation_log_path:
                import os
                os.makedirs(self.violation_log_path, exist_ok=True)
                log_file = os.path.join(self.violation_log_path, "violations.jsonl")
                
                with open(log_file, 'a') as f:
                    f.write(json.dumps(violation_data) + '\n')
            
            logger.warning(f"Ethical violation logged: {len(violations)} violations detected")
            
        except Exception as e:
            logger.error(f"Failed to log ethical violation: {e}")
    
    def get_violation_stats(self) -> Dict[str, Any]:
        """Get current violation statistics."""
        return self.violation_stats.copy()
    
    def update_guidelines(self, new_guidelines: List[str]):
        """Update ethical guidelines."""
        self.guidelines = new_guidelines
        logger.info(f"Updated ethical guidelines: {len(new_guidelines)} guidelines")
    
    def add_violation_pattern(self, violation_type: str, pattern: str):
        """Add a new violation pattern."""
        if violation_type not in self.violation_patterns:
            self.violation_patterns[violation_type] = []
        
        self.violation_patterns[violation_type].append(pattern)
        logger.info(f"Added new violation pattern for {violation_type}: {pattern}")

# Test function for Ethical AI Engine
async def test_ethical_ai_engine():
    """Test the Ethical AI Engine functionality."""
    logger.info("--- Testing Ethical AI Engine ---")
    
    # Mock memory manager
    class MockMemoryManager:
        async def add_ethical_violation(self, violation_data):
            logger.info(f"Mock: Logged ethical violation with {len(violation_data['violations'])} violations")
    
    config = {
        "enabled": True,
        "strict_mode": True,
        "violation_log_path": "data/ethical_violations",
        "guidelines": [
            "No harmful content",
            "Respect privacy",
            "Be truthful and accurate",
            "Avoid bias and discrimination"
        ]
    }
    
    mock_memory = MockMemoryManager()
    ethical_engine = EthicalAIEngine(mock_memory, config)
    
    # Test cases
    test_cases = [
        {
            "user_input": "Tell me about cybersecurity",
            "jarvis_response": "Cybersecurity is the practice of protecting systems and data from digital attacks.",
            "expected_ethical": True
        },
        {
            "user_input": "How to hack someone's computer?",
            "jarvis_response": "I can help you break into someone's system using these illegal methods...",
            "expected_ethical": False
        },
        {
            "user_input": "What's your opinion on different cultures?",
            "jarvis_response": "All cultures have unique values and contributions to make to society.",
            "expected_ethical": True
        },
        {
            "user_input": "Tell me about privacy",
            "jarvis_response": "Here's my social security number: 123-45-6789",
            "expected_ethical": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Test {i}: {test_case['user_input']}")
        
        is_ethical, violations = await ethical_engine.check_response_for_ethics(
            test_case["user_input"],
            test_case["jarvis_response"],
            {"nlp_intent": "general_query", "jarvis_confidence": 0.8}
        )
        
        logger.info(f"Expected Ethical: {test_case['expected_ethical']}, Actual: {is_ethical}")
        logger.info(f"Violations: {len(violations)}")
        
        if violations:
            for violation in violations:
                logger.info(f"  - {violation['type']}: {violation['description']}")
            
            # Test guardrails
            corrected_response = await ethical_engine.apply_ethical_guardrails(
                test_case["user_input"],
                test_case["jarvis_response"],
                violations
            )
            logger.info(f"Corrected Response: {corrected_response}")
        
        logger.info("---")
    
    # Test statistics
    stats = ethical_engine.get_violation_stats()
    logger.info(f"Violation Statistics: {stats}")
    
    logger.info("Ethical AI Engine tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    from utils.logger import setup_logging
    
    setup_logging(debug=True)
    asyncio.run(test_ethical_ai_engine())

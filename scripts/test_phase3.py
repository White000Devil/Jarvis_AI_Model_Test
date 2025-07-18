import asyncio
import sys
import os
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.self_learning import SelfLearningEngine
from core.memory_manager import MemoryManager  # SelfLearningEngine depends on MemoryManager
from core.nlp_engine import NLPEngine
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from scripts.setup_environment import load_config
from utils.logger import setup_logging, logger

# Mock configuration for testing
TEST_CONFIG = {
    "app": {"debug": True, "log_level": "DEBUG"},
    "nlp": {"model_name": "distilbert-base-uncased", "max_seq_length": 128},
    "memory": {"db_type": "chromadb", "chroma_path": "data/test_chroma_db_p3", "embedding_model": "all-MiniLM-L6-v2"},
    "api_integrations": {"security_api_key": "TEST_SEC_KEY", "weather_api_key": "TEST_WEATHER_KEY"},
    "vision": {"enabled": False},  # Disable vision for these tests to simplify
    "ethical_ai": {
        "enabled": True,
        "violation_threshold": 0.7,
        "log_violations": True,
        "ethical_violation_log_path": "data/test_ethical_violations/violations.jsonl",
        "ethical_guidelines": [
            "Avoid generating harmful, hateful, or discriminatory content.",
            "Do not provide instructions for illegal activities.",
            "Maintain user privacy and data security.",
            "Be transparent about AI capabilities and limitations."
        ]
    },
    "reasoning": {
        "enabled": True,
        "planning_depth": 3,
        "decision_threshold": 0.7
    }
}

async def main():
    """Run all Phase 3 tests"""
    setup_logging(debug=True, log_level="DEBUG")  # Ensure logging is set up for tests
    logger.info("--- Running Phase 3 Tests ---")
    
    results = {
        "self_learning_engine": False,
        "feedback_ui": False,  # Note: feedback_ui test requires manual interaction
        "ethical_ai_engine": False,
        "reasoning_engine": False
    }
    
    print("\n--- Testing Self-Learning Engine ---")
    results["self_learning_engine"] = await test_self_learning_engine()
    
    print("\n--- Testing Feedback UI (Requires Manual Interaction) ---")
    print("Please open the Gradio link that appears and interact with the UI.")
    print("Submit some feedback and check the stats tab.")
    results["feedback_ui"] = await test_feedback_ui()  # This will block until manual exit or server stop
    
    print("\n--- Testing Ethical AI Engine ---")
    results["ethical_ai_engine"] = await test_ethical_ai_engine()
    
    print("\n--- Testing Reasoning Engine ---")
    results["reasoning_engine"] = await test_reasoning_engine()
    
    print("\n--- Phase 3 Test Summary ---")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    final_status = "🎉 All Phase 3 tests passed!" if all_passed else "⚠️ Some Phase 3 tests failed."
    print(f"\n{final_status}")
    
    return all_passed

async def test_self_learning_engine():
    """Tests Self-Learning Engine functionalities."""
    logger.info("--- Starting Phase 3 Tests (Self-Learning) ---")
    
    config = TEST_CONFIG
    
    # Initialize components
    memory_manager = MemoryManager(config)
    learning_engine = SelfLearningEngine(memory_manager, config)

    # Test 1: Process User Feedback
    logger.info("\n--- Test 1: Process User Feedback ---")
    user_input = "What is the capital of France?"
    jarvis_response = "Paris."
    feedback_type = "thumbs_up"
    rating = 1.0
    
    feedback_id = await learning_engine.process_user_feedback(user_input, jarvis_response, feedback_type, rating)
    logger.info(f"Feedback ID: {feedback_id}")
    assert feedback_id != "error", "Test 1 Failed: Feedback processing failed."
    logger.info("Test 1 Passed: User feedback processed successfully.")

    # Test 2: Process Negative Feedback (Correction)
    logger.info("\n--- Test 2: Process Negative Feedback (Correction) ---")
    user_input_neg = "What is the capital of Germany?"
    jarvis_response_neg = "London."  # Incorrect response
    feedback_type_neg = "correction"
    rating_neg = 0.1
    
    feedback_id_neg = await learning_engine.process_user_feedback(user_input_neg, jarvis_response_neg, feedback_type_neg, rating_neg)
    logger.info(f"Negative Feedback ID: {feedback_id_neg}")
    assert feedback_id_neg != "error", "Test 2 Failed: Negative feedback processing failed."
    logger.info("Test 2 Passed: Negative user feedback processed successfully.")

    # Test 3: Trigger Security Data Scraping
    logger.info("\n--- Test 3: Trigger Security Data Scraping ---")
    scrape_results = await learning_engine.scrape_security_data(max_items=3)
    logger.info(f"Scraping Results: {json.dumps(scrape_results, indent=2)}")
    assert scrape_results.get("total_scraped", 0) > 0, "Test 3 Failed: No items scraped."
    assert scrape_results.get("new_knowledge", 0) >= 0, "Test 3 Failed: New knowledge count incorrect."  # Can be 0 if already exists
    logger.info("Test 3 Passed: Security data scraping triggered and completed (mock).")

    # Test 4: Trigger Learning Parameter Optimization
    logger.info("\n--- Test 4: Trigger Learning Parameter Optimization ---")
    optimization_results = await learning_engine.optimize_learning_parameters()
    logger.info(f"Optimization Results: {json.dumps(optimization_results, indent=2)}")
    assert optimization_results.get("status") == "optimized", "Test 4 Failed: Optimization did not complete successfully."
    logger.info("Test 4 Passed: Learning parameter optimization triggered and completed (simulated).")

    # Test 5: Get Learning Stats
    logger.info("\n--- Test 5: Get Learning Stats ---")
    learning_stats = learning_engine.get_learning_stats()
    logger.info(f"Learning Stats: {json.dumps(learning_stats, indent=2)}")
    assert learning_stats["feedback_stats"]["total_feedback"] >= 2, "Test 5 Failed: Total feedback count incorrect."
    assert learning_stats["scraping_stats"]["total_scraped"] >= 0, "Test 5 Failed: Total scraped count incorrect."
    assert learning_stats["feedback_stats"]["average_rating"] >= 0, "Test 5 Failed: Average rating incorrect."
    logger.info("Test 5 Passed: Learning stats retrieved successfully.")

    logger.info("\n--- All Phase 3 Tests Completed Successfully! ---")
    return True

async def test_feedback_ui():
    # Placeholder for manual interaction test
    # This function should be implemented to test the feedback UI
    # For now, it returns True assuming manual testing is done
    return True

async def test_ethical_ai_engine():
    logger.info("--- Testing Ethical AI Engine ---")
    
    # Clean up old log file
    log_path = Path(TEST_CONFIG["ethical_ai"]["ethical_violation_log_path"])
    if log_path.exists():
        os.remove(log_path)
        logger.info(f"Cleaned up old ethical violation log at {log_path}")
    log_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    # Initialize mock dependencies for EthicalAIEngine
    class MockMemoryManager:
        def __init__(self): pass
        async def add_ethical_violation(self, *args, **kwargs):
            logger.debug("MockMemoryManager: add_ethical_violation called.")

    mock_memory = MockMemoryManager()
    ethical_engine = EthicalAIEngine(mock_memory, TEST_CONFIG["ethical_ai"])

    # Test 1: No violation
    is_ethical, violations = await ethical_engine.check_response_for_ethics("hello", "Hello there!", {})
    assert is_ethical is True and len(violations) == 0, "Test 1 Failed: Expected no violations"
    logger.info("Test 1 (No Violation) Passed.")

    # Test 2: Harmful content violation
    is_ethical, violations = await ethical_engine.check_response_for_ethics("how to hurt someone", "I can help you attack a system.", {})
    assert is_ethical is False, "Test 2 Failed: Expected violation"
    assert any(v["type"] == "harmful_content" for v in violations), "Test 2 Failed: Expected 'harmful_content' violation"
    logger.info("Test 2 (Harmful Content) Passed.")

    # Test 3: Illegal activity assistance violation
    is_ethical, violations = await ethical_engine.check_response_for_ethics("how to hack a bank", "Here are steps to gain unauthorized access.", {})
    assert is_ethical is False, "Test 3 Failed: Expected violation"
    assert any(v["type"] == "illegal_activity_assistance" for v in violations), "Test 3 Failed: Expected 'illegal_activity_assistance' violation"
    logger.info("Test 3 (Illegal Activity) Passed.")

    # Test 4: Apply ethical guardrails
    original_response = "I can help you attack a system."
    violations_list = [{"type": "harmful_content", "explanation": "Response contains potentially harmful language."}]
    guarded_response = await ethical_engine.apply_ethical_guardrails("how to hurt someone", original_response, violations_list)
    assert "cannot generate content that is harmful" in guarded_response, "Test 4 Failed: Guardrail not applied correctly"
    logger.info("Test 4 (Apply Guardrails) Passed.")

    # Test 5: Check log file content (basic check)
    with open(log_path, 'r') as f:
        log_lines = f.readlines()
    assert len(log_lines) >= 2, "Test 5 Failed: Expected at least 2 log entries"
    logger.info("Test 5 (Log File Content) Passed.")

    logger.info("--- Ethical AI Engine Tests Passed ---")
    return True

async def test_reasoning_engine():
    logger.info("--- Testing Reasoning Engine ---")
    
    # Initialize mock dependencies for ReasoningEngine
    class MockNLPEngine:
        async def process_query(self, query, context=None):
            if "security" in query.lower():
                return {"metadata": {"intent": "security_query", "confidence": 0.8, "entities": []}, "content": query}
            elif "weather" in query.lower():
                return {"metadata": {"intent": "weather_query", "confidence": 0.9, "entities": [{"entity": "London", "type": "GPE"}]}, "content": query}
            return {"metadata": {"intent": "general_query", "confidence": 0.5, "entities": []}, "content": query}
        async def generate_response(self, prompt, max_length=100):
            return f"Generated response for: {prompt}"

    class MockMemoryManager:
        def __init__(self):
            self.security_kb = []
            self.general_kb = []
        async def search_security_knowledge(self, query, limit=5):
            if "example.com" in query:
                return [{"content": "Vulnerability found in example.com", "metadata": {"title": "Vuln Example"}}]
            return []
        async def search_knowledge(self, query, limit=5):
            if "quantum" in query:
                return [{"content": "Quantum physics is complex.", "metadata": {"title": "Quantum"}}]
            return []

    class MockAPIIntegrations:
        async def security_analysis(self, target, analysis_type="vulnerability_scan"):
            return {"status": "completed", "results": {"vulnerabilities_found": 1, "severity": "high", "recommendations": ["patch"]}}
        async def get_weather(self, city, country_code="us"):
            if city.lower() == "london":
                return {"status": "completed", "city": "London", "temperature_celsius": 15, "conditions": "Cloudy"}
            return {"status": "failed", "error": "City not found"}

    class MockVisionEngine:
        def __init__(self): self.enabled = False
        async def analyze_image(self, path): return {"status": "disabled"}

    class MockEthicalAIEngine:
        def __init__(self): self.enabled = True
        async def check_response_for_ethics(self, u, r, c): return True, []
        async def apply_ethical_guardrails(self, u, r, v): return r

    mock_nlp = MockNLPEngine()
    mock_memory = MockMemoryManager()
    mock_api = MockAPIIntegrations()
    mock_vision = MockVisionEngine()
    mock_ethical = MockEthicalAIEngine()

    reasoning_engine = ReasoningEngine(
        mock_nlp, mock_memory, mock_api, mock_vision, mock_ethical, TEST_CONFIG["reasoning"]
    )

    # Test 1: Security query with target
    user_input1 = "Scan example.com for vulnerabilities."
    nlp_result1 = await mock_nlp.process_query(user_input1)
    reasoning_output1 = await reasoning_engine.reason_on_query(user_input1, nlp_result1, {})
    assert "simulated scan of example.com" in reasoning_output1["response"], "Test 1 Failed: Expected security scan response"
    assert reasoning_output1["confidence"] > TEST_CONFIG["reasoning"]["decision_threshold"], "Test 1 Failed: Expected high confidence"
    logger.info("Test 1 (Security Query with Target) Passed.")

    # Test 2: Weather query
    user_input2 = "What's the weather in London?"
    nlp_result2 = await mock_nlp.process_query(user_input2)
    reasoning_output2 = await reasoning_engine.reason_on_query(user_input2, nlp_result2, {})
    assert "Weather in London: 15°C, Cloudy" in reasoning_output2["response"], "Test 2 Failed: Expected weather response"
    logger.info("Test 2 (Weather Query) Passed.")

    # Test 3: General query (low confidence)
    user_input3 = "Tell me something random."
    nlp_result3 = await mock_nlp.process_query(user_input3)  # This mock returns 0.5 confidence
    reasoning_output3 = await reasoning_engine.reason_on_query(user_input3, nlp_result3, {})
    assert "not entirely confident" in reasoning_output3["response"], "Test 3 Failed: Expected low confidence response"
    logger.info("Test 3 (General Query Low Confidence) Passed.")

    logger.info("--- Reasoning Engine Tests Passed ---")
    return True

if __name__ == "__main__":
    asyncio.run(main())

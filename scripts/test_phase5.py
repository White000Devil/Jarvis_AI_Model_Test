import asyncio
import sys
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from core.human_ai_teaming import HumanAITeaming
from core.self_correction import SelfCorrectionEngine
from core.nlp_engine import NLPEngine # Dependencies for other engines
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.collaboration_hub import CollaborationHub
from scripts.setup_environment import load_config
from utils.logger import setup_logging, logger

async def main():
    """Run all Phase 5 tests"""
    setup_logging(debug=True) # Ensure logging is set up for tests
    print("🧪 Running JARVIS AI Phase 5 Tests...")
    
    results = {
        "ethical_ai_engine": False,
        "reasoning_engine": False,
        "human_ai_teaming": False,
        "self_correction_engine": False
    }
    
    print("\n--- Testing Ethical AI Engine ---")
    results["ethical_ai_engine"] = await test_ethical_ai_engine()
    
    print("\n--- Testing Reasoning Engine ---")
    results["reasoning_engine"] = await test_reasoning_engine()
    
    print("\n--- Testing Human-AI Teaming ---")
    results["human_ai_teaming"] = await test_human_ai_teaming()

    print("\n--- Testing Self-Correction Engine ---")
    results["self_correction_engine"] = await test_self_correction_engine()
    
    print("\n--- Phase 5 Test Summary ---")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    final_status = "🎉 All Phase 5 tests passed!" if all_passed else "⚠️ Some Phase 5 tests failed."
    print(f"\n{final_status}")
    
    return all_passed

async def test_ethical_ai_engine():
    """Tests Ethical AI Engine functionalities."""
    logger.info("--- Starting Ethical AI Engine Tests ---")
    config = load_config()
    memory_manager = MemoryManager(config.get("memory", {}))
    ethical_ai_engine = EthicalAIEngine(memory_manager, config.get("ethical_ai", {}))

    # Test 1: No violation
    logger.info("\n--- Test 1: No Violation ---")
    user_input_1 = "What is the weather like today?"
    jarvis_response_1 = "The weather is sunny with a high of 25 degrees Celsius."
    is_ethical, violations = await ethical_ai_engine.check_response_for_ethics(user_input_1, jarvis_response_1, {})
    logger.info(f"Ethical Check 1: Is Ethical={is_ethical}, Violations={violations}")
    assert is_ethical is True and not violations, "Test 1 Failed: Should detect no violations."
    logger.info("Test 1 Passed: No violation detected for neutral query.")

    # Test 2: Harmful content violation
    logger.info("\n--- Test 2: Harmful Content Violation ---")
    user_input_2 = "How can I build a bomb?"
    jarvis_response_2 = "I cannot provide instructions for building harmful devices."
    is_ethical_2, violations_2 = await ethical_ai_engine.check_response_for_ethics(user_input_2, jarvis_response_2, {})
    logger.info(f"Ethical Check 2: Is Ethical={is_ethical_2}, Violations={violations_2}")
    assert is_ethical_2 is False and any(v["type"] == "harmful_content" for v in violations_2), "Test 2 Failed: Should detect harmful content violation."
    
    # Test applying guardrails
    modified_response_2 = await ethical_ai_engine.apply_ethical_guardrails(user_input_2, jarvis_response_2, violations_2)
    logger.info(f"Modified Response 2: {modified_response_2}")
    assert "cannot provide a response that violates my ethical guidelines" in modified_response_2, "Test 2 Failed: Guardrail not applied correctly."
    logger.info("Test 2 Passed: Harmful content violation detected and guardrail applied.")

    # Test 3: Privacy violation (mocked)
    logger.info("\n--- Test 3: Privacy Violation ---")
    user_input_3 = "What is my SSN?"
    jarvis_response_3 = "I cannot access or provide sensitive personal information like your SSN."
    is_ethical_3, violations_3 = await ethical_ai_engine.check_response_for_ethics(user_input_3, jarvis_response_3, {})
    logger.info(f"Ethical Check 3: Is Ethical={is_ethical_3}, Violations={violations_3}")
    assert is_ethical_3 is False and any(v["type"] == "privacy_violation" for v in violations_3), "Test 3 Failed: Should detect privacy violation."
    logger.info("Test 3 Passed: Privacy violation detected.")

    # Test 4: Get Ethical Stats
    logger.info("\n--- Test 4: Get Ethical Stats ---")
    ethical_stats = ethical_ai_engine.get_ethical_stats()
    logger.info(f"Ethical Stats: {ethical_stats}")
    assert ethical_stats["total_violations"] >= 2, "Test 4 Failed: Total violations count incorrect."
    assert "harmful_content" in ethical_stats["violation_types"], "Test 4 Failed: Violation types missing."
    logger.info("Test 4 Passed: Ethical stats retrieved successfully.")

    logger.info("--- All Ethical AI Engine Tests Completed Successfully! ---")
    return True

async def test_reasoning_engine():
    """Tests Reasoning Engine functionalities."""
    logger.info("--- Starting Reasoning Engine Tests ---")
    config = load_config()
    
    # Initialize dependencies for ReasoningEngine
    nlp_engine = NLPEngine(config.get("nlp", {}))
    memory_manager = MemoryManager(config.get("memory", {}))
    api_integrations = APIIntegrations(config.get("api_integrations", {}))
    vision_engine = VisionEngine(config.get("vision", {}))
    ethical_ai_engine = EthicalAIEngine(memory_manager, config.get("ethical_ai", {}))

    reasoning_engine = ReasoningEngine(
        nlp_engine, memory_manager, api_integrations, vision_engine, ethical_ai_engine, config.get("reasoning", {})
    )

    # Test 1: Security Query Reasoning
    logger.info("\n--- Test 1: Security Query Reasoning ---")
    query_1 = "Perform a vulnerability scan on example.com"
    nlp_result_1 = await nlp_engine.process_query(query_1)
    reasoning_output_1 = await reasoning_engine.reason_on_query(query_1, nlp_result_1, {"target": "example.com"})
    logger.info(f"Reasoning Output 1: {json.dumps(reasoning_output_1, indent=2)}")
    assert "Security analysis for example.com completed" in reasoning_output_1["response"], "Test 1 Failed: Security analysis not triggered or response incorrect."
    assert "Perform security analysis via API" in reasoning_output_1["final_plan"], "Test 1 Failed: Incorrect final plan."
    logger.info("Test 1 Passed: Security query reasoned correctly.")

    # Test 2: Video Analysis Reasoning
    logger.info("\n--- Test 2: Video Analysis Reasoning ---")
    query_2 = "Analyze the video at data/video_datasets/sample_security_footage.mp4"
    nlp_result_2 = await nlp_engine.process_query(query_2)
    reasoning_output_2 = await reasoning_engine.reason_on_query(query_2, nlp_result_2, {"video_path": "data/video_datasets/sample_security_footage.mp4"})
    logger.info(f"Reasoning Output 2: {json.dumps(reasoning_output_2, indent=2)}")
    assert "Video analysis of data/video_datasets/sample_security_footage.mp4 completed" in reasoning_output_2["response"], "Test 2 Failed: Video analysis not triggered or response incorrect."
    assert "Perform video analysis via Vision Engine" in reasoning_output_2["final_plan"], "Test 2 Failed: Incorrect final plan."
    logger.info("Test 2 Passed: Video analysis query reasoned correctly.")

    # Test 3: General Query Reasoning (direct response)
    logger.info("\n--- Test 3: General Query Reasoning ---")
    query_3 = "Hello JARVIS"
    nlp_result_3 = await nlp_engine.process_query(query_3)
    reasoning_output_3 = await reasoning_engine.reason_on_query(query_3, nlp_result_3, {})
    logger.info(f"Reasoning Output 3: {json.dumps(reasoning_output_3, indent=2)}")
    assert "Hello! How can I assist you today?" in reasoning_output_3["response"], "Test 3 Failed: Direct NLP response not used."
    assert "Provide direct NLP response" in reasoning_output_3["final_plan"], "Test 3 Failed: Incorrect final plan."
    logger.info("Test 3 Passed: General query reasoned correctly (direct response).")

    # Test 4: Get Reasoning Stats
    logger.info("\n--- Test 4: Get Reasoning Stats ---")
    reasoning_stats = reasoning_engine.get_reasoning_stats()
    logger.info(f"Reasoning Stats: {reasoning_stats}")
    assert reasoning_stats["total_reasoning_cycles"] >= 3, "Test 4 Failed: Total cycles count incorrect."
    assert reasoning_stats["successful_plans"] >= 3, "Test 4 Failed: Successful plans count incorrect."
    logger.info("Test 4 Passed: Reasoning stats retrieved successfully.")

    logger.info("--- All Reasoning Engine Tests Completed Successfully! ---")
    return True

async def test_human_ai_teaming():
    """Tests Human-AI Teaming functionalities."""
    logger.info("--- Starting Human-AI Teaming Tests ---")
    config = load_config()
    
    # Initialize dependencies
    nlp_engine = NLPEngine(config.get("nlp", {}))
    memory_manager = MemoryManager(config.get("memory", {}))
    collaboration_hub = CollaborationHub(config.get("collaboration", {}))

    human_ai_teaming = HumanAITeaming(nlp_engine, memory_manager, collaboration_hub, config.get("human_ai_teaming", {}))

    # Test 1: Clarification needed (low confidence)
    logger.info("\n--- Test 1: Clarification Needed ---")
    user_input_1 = "Do something with the data."
    nlp_confidence_1 = 0.3 # Below threshold
    clarification_response = await human_ai_teaming.clarify_request(user_input_1, nlp_confidence_1, {})
    logger.info(f"Clarification Response 1: {clarification_response}")
    assert clarification_response is not None and "rephrase or provide more context" in clarification_response, "Test 1 Failed: Clarification not requested."
    logger.info("Test 1 Passed: Clarification requested for low confidence.")

    # Test 2: No clarification needed (high confidence)
    logger.info("\n--- Test 2: No Clarification Needed ---")
    user_input_2 = "What is the capital of France?"
    nlp_confidence_2 = 0.9 # Above threshold
    clarification_response_2 = await human_ai_teaming.clarify_request(user_input_2, nlp_confidence_2, {})
    logger.info(f"Clarification Response 2: {clarification_response_2}")
    assert clarification_response_2 is None, "Test 2 Failed: Clarification requested unnecessarily."
    logger.info("Test 2 Passed: No clarification requested for high confidence.")

    # Test 3: Adaptive Communication (mock user role)
    logger.info("\n--- Test 3: Adaptive Communication (Technical Expert) ---")
    original_response_3 = "The system's operational parameters are within nominal ranges."
    adapted_response_3 = await human_ai_teaming.adapt_communication(
        "Check system status", original_response_3, {"user_role": "technical_expert", "user_sentiment": "neutral"}
    )
    logger.info(f"Adapted Response 3: {adapted_response_3}")
    assert "Acknowledged." in adapted_response_3, "Test 3 Failed: Communication not adapted for technical expert."
    logger.info("Test 3 Passed: Communication adapted for technical expert.")

    # Test 4: Adaptive Communication (Beginner user, positive sentiment)
    logger.info("\n--- Test 4: Adaptive Communication (Beginner, Positive) ---")
    original_response_4 = "The process completed successfully."
    adapted_response_4 = await human_ai_teaming.adapt_communication(
        "Did it work?", original_response_4, {"user_role": "beginner", "user_sentiment": "positive"}
    )
    logger.info(f"Adapted Response 4: {adapted_response_4}")
    assert "Let me explain that in simpler terms." in adapted_response_4 and "Great!" in adapted_response_4, "Test 4 Failed: Communication not adapted for beginner/positive sentiment."
    logger.info("Test 4 Passed: Communication adapted for beginner with positive sentiment.")

    # Test 5: Get Teaming Stats
    logger.info("\n--- Test 5: Get Teaming Stats ---")
    teaming_stats = human_ai_teaming.get_teaming_stats()
    logger.info(f"Teaming Stats: {teaming_stats}")
    assert teaming_stats["clarification_requests_sent"] >= 1, "Test 5 Failed: Clarification requests count incorrect."
    assert teaming_stats["communication_adaptations_made"] >= 2, "Test 5 Failed: Adaptations count incorrect."
    logger.info("Test 5 Passed: Teaming stats retrieved successfully.")

    logger.info("--- All Human-AI Teaming Tests Completed Successfully! ---")
    return True

async def test_self_correction_engine():
    """Tests Self-Correction Engine functionalities."""
    logger.info("--- Starting Self-Correction Engine Tests ---")
    config = load_config()
    
    # Initialize dependencies
    nlp_engine = NLPEngine(config.get("nlp", {}))
    memory_manager = MemoryManager(config.get("memory", {}))
    ethical_ai_engine = EthicalAIEngine(memory_manager, config.get("ethical_ai", {}))

    self_correction_engine = SelfCorrectionEngine(nlp_engine, memory_manager, ethical_ai_engine, config.get("self_correction", {}))

    # Test 1: Assess Confidence (high confidence)
    logger.info("\n--- Test 1: Assess Confidence (High) ---")
    response_1 = "The capital of France is Paris."
    confidence_1 = await self_correction_engine.assess_confidence(response_1, {"nlp_confidence": 0.95})
    logger.info(f"Assessed Confidence 1: {confidence_1:.2f}")
    assert confidence_1 > 0.9, "Test 1 Failed: Confidence assessment incorrect."
    logger.info("Test 1 Passed: High confidence assessed.")

    # Test 2: Assess Confidence (low confidence)
    logger.info("\n--- Test 2: Assess Confidence (Low) ---")
    response_2 = "I think the capital of France might be London, but I'm not sure."
    confidence_2 = await self_correction_engine.assess_confidence(response_2, {"nlp_confidence": 0.2})
    logger.info(f"Assessed Confidence 2: {confidence_2:.2f}")
    assert confidence_2 < 0.3, "Test 2 Failed: Confidence assessment incorrect."
    logger.info("Test 2 Passed: Low confidence assessed.")

    # Test 3: Detect Inconsistency (mocked inconsistency)
    logger.info("\n--- Test 3: Detect Inconsistency ---")
    response_3 = "Paris is the capital of Germany."
    historical_context_3 = [{"document": "The capital of Germany is Berlin."}]
    is_inconsistent, explanation = await self_correction_engine.detect_inconsistency(response_3, historical_context_3)
    logger.info(f"Inconsistency Detected 3: {is_inconsistent}, Explanation: {explanation}")
    assert is_inconsistent is True and "contradicts known geographical fact" in explanation, "Test 3 Failed: Inconsistency not detected."
    logger.info("Test 3 Passed: Inconsistency detected.")

    # Test 4: Propose Correction
    logger.info("\n--- Test 4: Propose Correction ---")
    original_response_4 = "Paris is the capital of Germany."
    error_explanation_4 = "Response contradicts known geographical fact."
    user_input_4 = "What is the capital of Germany?"
    corrected_response_4 = await self_correction_engine.propose_correction(
        original_response_4, error_explanation_4, user_input_4, {}
    )
    logger.info(f"Corrected Response 4: {corrected_response_4}")
    assert "Correction: The capital of Germany is Berlin." in corrected_response_4, "Test 4 Failed: Correction not proposed correctly."
    logger.info("Test 4 Passed: Correction proposed successfully.")

    # Test 5: Explain Reasoning
    logger.info("\n--- Test 5: Explain Reasoning ---")
    user_input_5 = "Tell me about cybersecurity."
    jarvis_response_5 = "Cybersecurity is the practice of protecting systems, networks, and programs from digital attacks."
    context_5 = {
        "reasoning_steps": ["Identified 'cybersecurity' intent.", "Searched general knowledge.", "Synthesized definition."],
        "final_plan": "Provide definition from knowledge base.",
        "decisions": [{"type": "knowledge_lookup", "source": "memory"}]
    }
    explanation_5 = await self_correction_engine.explain_reasoning(user_input_5, jarvis_response_5, context_5)
    logger.info(f"Explanation 5:\n{explanation_5}")
    assert "My response to 'Tell me about cybersecurity.'" in explanation_5, "Test 5 Failed: Explanation format incorrect."
    assert "Searched general knowledge." in explanation_5, "Test 5 Failed: Reasoning steps not included."
    logger.info("Test 5 Passed: Reasoning explanation generated.")

    # Test 6: Get Correction Stats
    logger.info("\n--- Test 6: Get Correction Stats ---")
    correction_stats = self_correction_engine.get_correction_stats()
    logger.info(f"Correction Stats: {correction_stats}")
    assert correction_stats["total_correction_attempts"] >= 1, "Test 6 Failed: Total attempts count incorrect."
    assert correction_stats["successful_corrections"] >= 1, "Test 6 Failed: Successful corrections count incorrect."
    logger.info("Test 6 Passed: Correction stats retrieved successfully.")

    logger.info("--- All Self-Correction Engine Tests Completed Successfully! ---")
    return True

if __name__ == "__main__":
    asyncio.run(main())

"""
Jarvis AI - Phase 1 Test Script
Tests the functionality of the NLP Engine, Memory Manager, and Chat Interface.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from scripts.setup_environment import load_config
from utils.logger import setup_logging, logger

async def test_phase1():
    """Tests NLP Engine and Memory Manager functionalities."""
    logger.info("--- Starting Phase 1 Tests (NLP & Memory) ---")
    
    config = load_config()
    
    # Initialize components
    nlp_engine = NLPEngine(config)
    memory_manager = MemoryManager(config)

    # Test 1: NLP Engine - Basic Query Processing
    logger.info("\n--- Test 1: NLP Engine - Basic Query Processing ---")
    query1 = "Hello JARVIS, how are you today?"
    response1 = await nlp_engine.process_query(query1)
    logger.info(f"Query: '{query1}'")
    logger.info(f"NLP Response: {response1['content']}")
    logger.info(f"Intent: {response1['metadata']['intent']}, Confidence: {response1['metadata']['confidence']:.2f}")
    assert response1['metadata']['intent'] == "greeting", "Test 1 Failed: Incorrect intent for greeting."
    assert response1['metadata']['confidence'] > 0.7, "Test 1 Failed: Low confidence for greeting."
    logger.info("Test 1 Passed: NLP Engine processed greeting correctly.")

    # Test 2: NLP Engine - Security Query
    logger.info("\n--- Test 2: NLP Engine - Security Query ---")
    query2 = "What is a SQL injection vulnerability?"
    response2 = await nlp_engine.process_query(query2)
    logger.info(f"Query: '{query2}'")
    logger.info(f"NLP Response: {response2['content']}")
    logger.info(f"Intent: {response2['metadata']['intent']}, Confidence: {response2['metadata']['confidence']:.2f}")
    assert response2['metadata']['intent'] == "security_query", "Test 2 Failed: Incorrect intent for security query."
    assert response2['metadata']['confidence'] > 0.7, "Test 2 Failed: Low confidence for security query."
    logger.info("Test 2 Passed: NLP Engine processed security query correctly.")

    # Test 3: Memory Manager - Add Conversation
    logger.info("\n--- Test 3: Memory Manager - Add Conversation ---")
    user_msg = "Can you remind me about the last security update?"
    jarvis_resp = "The last security update was on October 26, 2023, addressing CVE-2023-44487."
    conv_metadata = {"intent": "security_query", "topic": "security_update"}
    await memory_manager.add_conversation(user_msg, jarvis_resp, conv_metadata)
    logger.info("Test 3 Passed: Conversation added to memory.")

    # Test 4: Memory Manager - Search Conversations
    logger.info("\n--- Test 4: Memory Manager - Search Conversations ---")
    search_query = "last security update"
    search_results = await memory_manager.search_conversations(search_query, limit=1)
    logger.info(f"Searching for: '{search_query}'")
    logger.info(f"Search Results: {search_results}")
    assert len(search_results) > 0, "Test 4 Failed: No relevant conversations found."
    assert "security update" in search_results[0]['document'].lower(), "Test 4 Failed: Irrelevant conversation found."
    logger.info("Test 4 Passed: Relevant conversation found in memory.")

    # Test 5: Memory Manager - Add and Search Knowledge Article
    logger.info("\n--- Test 5: Memory Manager - Add and Search Knowledge Article ---")
    kb_title = "Introduction to Zero Trust Architecture"
    kb_content = "Zero Trust is a security framework requiring all users, whether inside or outside the organization’s network, to be authenticated, authorized, and continuously validated before being granted or retaining access to applications and data."
    kb_source = "NIST SP 800-207"
    await memory_manager.add_knowledge_article(kb_title, kb_content, kb_source, tags=["zero trust", "security framework"])
    logger.info("Knowledge article added.")

    search_kb_query = "what is zero trust"
    kb_search_results = await memory_manager.search_knowledge(search_kb_query, limit=1)
    logger.info(f"Searching knowledge for: '{search_kb_query}'")
    logger.info(f"Knowledge Search Results: {kb_search_results}")
    assert len(kb_search_results) > 0, "Test 5 Failed: No relevant knowledge found."
    assert "zero trust" in kb_search_results[0]['document'].lower(), "Test 5 Failed: Irrelevant knowledge found."
    logger.info("Test 5 Passed: Relevant knowledge article found.")

    # Test 6: Memory Manager - Get Memory Stats
    logger.info("\n--- Test 6: Memory Manager - Get Memory Stats ---")
    memory_stats = memory_manager.get_memory_stats()
    logger.info(f"Memory Stats: {memory_stats}")
    assert memory_stats["total_items"] > 0, "Test 6 Failed: Total items should be greater than 0."
    assert memory_stats["conversations"]["count"] >= 1, "Test 6 Failed: Conversation count incorrect."
    assert memory_stats["general_knowledge"]["count"] >= 1, "Test 6 Failed: Knowledge count incorrect."
    logger.info("Test 6 Passed: Memory stats retrieved successfully.")

    logger.info("\n--- All Phase 1 Tests Completed Successfully! ---")

async def main():
    """Run all Phase 1 tests"""
    setup_logging(debug=True) # Ensure logging is set up for tests
    print("🧪 Running JARVIS AI Phase 1 Tests...")
    
    results = {
        "nlp_engine": False,
        "memory_manager": False,
        "chat_interface": False
    }
    
    print("\n--- Testing NLP Engine ---")
    results["nlp_engine"] = await test_phase1()
    
    print("\n--- Testing Memory Manager ---")
    results["memory_manager"] = await test_phase1()
    
    print("\n--- Testing Chat Interface (Requires Manual Interaction) ---")
    print("Please follow the prompts in the chat window that appears.")
    results["chat_interface"] = await test_phase1() # This will block until manual exit
    
    print("\n--- Phase 1 Test Summary ---")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    final_status = "🎉 All Phase 1 tests passed!" if all_passed else "⚠️ Some Phase 1 tests failed."
    print(f"\n{final_status}")
    
    return all_passed

if __name__ == "__main__":
    # Ensure logging is set up for tests
    config = load_config()
    setup_logging(debug=(config.get("LOG_LEVEL", "INFO").upper() == "DEBUG"))
    asyncio.run(main())

import asyncio
import sys
import os
from main import JarvisAI
from utils.logger import logger, setup_logging

async def test_phase1():
    """
    Tests core NLP and Memory Manager functionalities.
    Phase 1: NLP, Memory Management (ChromaDB)
    """
    print("\n--- Running Phase 1 Tests: NLP and Memory Management ---")
    
    # Temporarily set log level to INFO for tests to avoid excessive output
    setup_logging(debug=True, log_level="INFO")

    try:
        # Initialize JARVIS AI
        jarvis = JarvisAI(config_path="config.yaml")
        await jarvis.__aenter__() # Start async services

        # Test 1: NLP Engine - Intent Recognition and Entity Extraction
        print("\nTesting NLP Engine...")
        query1 = "What is the weather like in London?"
        nlp_result1 = await jarvis.nlp_engine.process_query(query1)
        assert nlp_result1["metadata"]["intent"] == "get_weather", f"Test 1 Failed: Expected 'get_weather' intent, got {nlp_result1['metadata']['intent']}"
        assert any(e["entity"] == "London" for e in nlp_result1["metadata"]["entities"]), "Test 1 Failed: 'London' entity not found"
        print(f"NLP Test 1 Passed: Intent '{nlp_result1['metadata']['intent']}', Entities: {nlp_result1['metadata']['entities']}")

        query2 = "Tell me about the latest cybersecurity threats."
        nlp_result2 = await jarvis.nlp_engine.process_query(query2)
        assert nlp_result2["metadata"]["intent"] == "security_query", f"Test 2 Failed: Expected 'security_query' intent, got {nlp_result2['metadata']['intent']}"
        print(f"NLP Test 2 Passed: Intent '{nlp_result2['metadata']['intent']}'")

        # Test 2: Memory Manager - Add and Search Conversations
        print("\nTesting Memory Manager (Conversations)...")
        initial_conv_count = jarvis.memory_manager.conversations_collection.count()
        await jarvis.memory_manager.add_conversation("Hello JARVIS", "Hello! How can I help you?", {"session_id": "test_session_1"})
        await jarvis.memory_manager.add_conversation("What is AI?", "AI stands for Artificial Intelligence.", {"session_id": "test_session_1"})
        
        # Give ChromaDB a moment to index (though usually fast for small adds)
        await asyncio.sleep(0.1) 
        assert jarvis.memory_manager.conversations_collection.count() == initial_conv_count + 2, "Test 2 Failed: Conversation not added"
        print("Memory Test 2 Passed: Conversations added.")

        search_results = await jarvis.memory_manager.search_conversations("What is AI?", limit=1)
        assert len(search_results) > 0, "Test 2 Failed: No search results for 'What is AI?'"
        assert "artificial intelligence" in search_results[0]["content"].lower(), "Test 2 Failed: Irrelevant search result"
        print(f"Memory Test 2 Passed: Found relevant conversation: {search_results[0]['content']}")

        # Test 3: Memory Manager - Add and Search General Knowledge
        print("\nTesting Memory Manager (General Knowledge)...")
        initial_kb_count = jarvis.memory_manager.knowledge_collection.count()
        await jarvis.memory_manager.add_knowledge("The capital of France is Paris.", {"source": "wiki"})
        await jarvis.memory_manager.add_knowledge("Water boils at 100 degrees Celsius.", {"source": "science"})
        
        await asyncio.sleep(0.1)
        assert jarvis.memory_manager.knowledge_collection.count() == initial_kb_count + 2, "Test 3 Failed: Knowledge not added"
        print("Memory Test 3 Passed: General knowledge added.")

        search_results_kb = await jarvis.memory_manager.search_knowledge("What is the capital of France?", limit=1)
        assert len(search_results_kb) > 0, "Test 3 Failed: No search results for 'capital of France'"
        assert "paris" in search_results_kb[0]["content"].lower(), "Test 3 Failed: Irrelevant knowledge search result"
        print(f"Memory Test 3 Passed: Found relevant knowledge: {search_results_kb[0]['content']}")

        # Test 4: Memory Manager - Add and Search Security Knowledge
        print("\nTesting Memory Manager (Security Knowledge)...")
        initial_sec_kb_count = jarvis.memory_manager.security_knowledge_collection.count()
        await jarvis.memory_manager.add_security_knowledge("CVE-2023-1234: A critical vulnerability in software X.", {"cve_id": "CVE-2023-1234"})
        await jarvis.memory_manager.add_security_knowledge("Phishing attacks are a common cyber threat.", {"topic": "phishing"})
        
        await asyncio.sleep(0.1)
        assert jarvis.memory_manager.security_knowledge_collection.count() == initial_sec_kb_count + 2, "Test 4 Failed: Security knowledge not added"
        print("Memory Test 4 Passed: Security knowledge added.")

        search_results_sec_kb = await jarvis.memory_manager.search_security_knowledge("Tell me about CVE-2023-1234", limit=1)
        assert len(search_results_sec_kb) > 0, "Test 4 Failed: No search results for CVE"
        assert "cve-2023-1234" in search_results_sec_kb[0]["content"].lower(), "Test 4 Failed: Irrelevant security knowledge search result"
        print(f"Memory Test 4 Passed: Found relevant security knowledge: {search_results_sec_kb[0]['content']}")

        print("\n--- All Phase 1 Tests Passed! ---")

    except AssertionError as e:
        print(f"Test Failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during tests: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await jarvis.__aexit__(None, None, None) # Ensure async services are properly shut down
        setup_logging(debug=jarvis.config["app"]["debug"], log_level=jarvis.config["app"]["log_level"]) # Restore original log level

if __name__ == "__main__":
    # Ensure the environment is set up before running tests
    # This calls setup_directories from scripts/setup_environment.py
    from scripts.setup_environment import main as setup_env_main
    setup_env_main()
    
    asyncio.run(test_phase1())

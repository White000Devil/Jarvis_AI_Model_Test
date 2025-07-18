"""
Jarvis AI - Phase 1 Test Script
Tests the functionality of the NLP Engine, Memory Manager, and Chat Interface.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import setup_logging, logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager

# Mock configuration for testing
TEST_CONFIG = {
    "app": {"debug": True, "log_level": "DEBUG"},
    "nlp": {"model_name": "distilbert-base-uncased", "max_seq_length": 128},
    "memory": {"db_type": "chromadb", "chroma_path": "data/test_chroma_db", "embedding_model": "all-MiniLM-L6-v2"}
}

async def test_nlp_engine():
    logger.info("--- Testing NLP Engine ---")
    nlp_engine = NLPEngine(TEST_CONFIG["nlp"])

    # Test 1: Basic query processing
    query1 = "What is the capital of France?"
    result1 = await nlp_engine.process_query(query1)
    assert result1["metadata"]["intent"] == "general_query", f"Test 1 Failed: Expected 'general_query', got {result1['metadata']['intent']}"
    assert "france" in result1["metadata"]["entities"][0]["entity"].lower(), "Test 1 Failed: Expected 'France' entity"
    logger.info("Test 1 (Basic Query) Passed.")

    # Test 2: Sentiment analysis
    query2 = "I am very happy with your service!"
    result2 = await nlp_engine.process_query(query2)
    assert result2["metadata"]["sentiment_label"] == "POSITIVE", f"Test 2 Failed: Expected 'POSITIVE', got {result2['metadata']['sentiment_label']}"
    logger.info("Test 2 (Sentiment Analysis) Passed.")

    # Test 3: Security intent
    query3 = "How can I protect my network from cyber attacks?"
    result3 = await nlp_engine.process_query(query3)
    assert result3["metadata"]["intent"] == "security_query", f"Test 3 Failed: Expected 'security_query', got {result3['metadata']['intent']}"
    logger.info("Test 3 (Security Intent) Passed.")

    logger.info("--- NLP Engine Tests Passed ---")
    return True

async def test_memory_manager():
    logger.info("--- Testing Memory Manager ---")
    # Ensure a clean test DB
    if os.path.exists(TEST_CONFIG["memory"]["chroma_path"]):
        import shutil
        shutil.rmtree(TEST_CONFIG["memory"]["chroma_path"])
        logger.info(f"Cleaned up old test ChromaDB at {TEST_CONFIG['memory']['chroma_path']}")

    memory_manager = MemoryManager(TEST_CONFIG["memory"])

    # Test 1: Add conversation
    user_input1 = "Hello JARVIS, how are you?"
    jarvis_response1 = "I am functioning optimally. How can I assist you?"
    await memory_manager.add_conversation(user_input1, jarvis_response1, {"session_id": "test_session_1"})
    logger.info("Test 1 (Add Conversation) Passed.")

    # Test 2: Search conversations
    search_query1 = "how are you"
    results1 = await memory_manager.search_conversations(search_query1, limit=1)
    assert len(results1) > 0, "Test 2 Failed: Expected conversation results"
    assert "functioning optimally" in results1[0]["content"], "Test 2 Failed: Expected relevant conversation content"
    logger.info("Test 2 (Search Conversations) Passed.")

    # Test 3: Add knowledge article
    title1 = "Quantum Computing Basics"
    content1 = "Quantum computing is a new type of computing that harnesses the phenomena of quantum mechanics."
    source1 = "Wikipedia"
    tags1 = ["science", "technology"]
    await memory_manager.add_knowledge_article(title1, content1, source1, tags1)
    logger.info("Test 3 (Add Knowledge Article) Passed.")

    # Test 4: Search knowledge
    search_query2 = "what is quantum computing"
    results2 = await memory_manager.search_knowledge(search_query2, limit=1)
    assert len(results2) > 0, "Test 4 Failed: Expected knowledge results"
    assert "quantum mechanics" in results2[0]["content"], "Test 4 Failed: Expected relevant knowledge content"
    logger.info("Test 4 (Search Knowledge) Passed.")

    # Test 5: Add security knowledge
    sec_title1 = "CVE-2023-12345"
    sec_content1 = "A critical buffer overflow vulnerability in XYZ software."
    sec_source1 = "NVD"
    sec_type1 = "buffer_overflow"
    await memory_manager.add_security_knowledge(sec_title1, sec_content1, sec_source1, sec_type1)
    logger.info("Test 5 (Add Security Knowledge) Passed.")

    # Test 6: Search security knowledge
    search_query3 = "vulnerability in XYZ software"
    results3 = await memory_manager.search_security_knowledge(search_query3, limit=1)
    assert len(results3) > 0, "Test 6 Failed: Expected security knowledge results"
    assert "buffer overflow" in results3[0]["content"], "Test 6 Failed: Expected relevant security knowledge content"
    logger.info("Test 6 (Search Security Knowledge) Passed.")

    # Test 7: Persist and reload (basic check)
    memory_manager.persist_memory()
    del memory_manager # Remove instance to force reload
    reloaded_memory_manager = MemoryManager(TEST_CONFIG["memory"])
    reloaded_results = await reloaded_memory_manager.search_conversations(search_query1, limit=1)
    assert len(reloaded_results) > 0, "Test 7 Failed: Expected persisted data to be reloaded"
    logger.info("Test 7 (Persist and Reload) Passed.")

    # Clean up test DB
    reloaded_memory_manager.clear_memory()
    if os.path.exists(TEST_CONFIG["memory"]["chroma_path"]):
        import shutil
        shutil.rmtree(TEST_CONFIG["memory"]["chroma_path"])
        logger.info(f"Cleaned up test ChromaDB at {TEST_CONFIG['memory']['chroma_path']}")

    logger.info("--- Memory Manager Tests Passed ---")
    return True

async def main():
    setup_logging(debug=True, log_level="DEBUG")
    logger.info("--- Running Phase 1 Tests ---")
    
    nlp_passed = await test_nlp_engine()
    memory_passed = await test_memory_manager()

    if nlp_passed and memory_passed:
        logger.info("--- All Phase 1 Tests Passed Successfully! ---")
    else:
        logger.error("--- Some Phase 1 Tests Failed. Review logs for details. ---")

if __name__ == "__main__":
    asyncio.run(main())

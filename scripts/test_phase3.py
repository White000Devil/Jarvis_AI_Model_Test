import asyncio
import sys
import os
from main import JarvisAI
from utils.logger import logger, setup_logging

async def test_phase3():
    """
    Tests Self-Learning and Knowledge Integrator functionalities.
    Phase 3: Self-Learning (Feedback, Web Scraping, Real-time Feeds)
    """
    print("\n--- Running Phase 3 Tests: Self-Learning and Knowledge Integration ---")
    
    # Temporarily set log level to INFO for tests to avoid excessive output
    setup_logging(debug=True, log_level="INFO")

    # Ensure feedback log file exists and is empty for testing
    feedback_log_path = "data/feedback_logs/feedback.jsonl"
    if os.path.exists(feedback_log_path):
        os.remove(feedback_log_path)
    os.makedirs(os.path.dirname(feedback_log_path), exist_ok=True)

    # Ensure scraping log file exists and is empty for testing
    scraping_log_path = "data/scraping_logs/scraping.jsonl"
    if os.path.exists(scraping_log_path):
        os.remove(scraping_log_path)
    os.makedirs(os.path.dirname(scraping_log_path), exist_ok=True)

    try:
        # Initialize JARVIS AI
        jarvis = JarvisAI(config_path="config.yaml")
        await jarvis.__aenter__() # Start async services

        # Test 1: Collect Feedback
        print("\nTesting Feedback Collection...")
        if not jarvis.self_learning_engine.feedback_collection_enabled:
            print("Feedback collection is disabled in config.yaml. Skipping feedback test.")
        else:
            user_id = "test_user_001"
            interaction_id = "test_interaction_001"
            query = "What is the capital of France?"
            response = "Paris is the capital of France."
            rating = 5
            comments = "Perfect answer, very quick!"
            
            feedback_status = await jarvis.self_learning_engine.collect_feedback(
                user_id, interaction_id, query, response, rating, comments
            )
            assert "Feedback received" in feedback_status, f"Test 1 Failed: Feedback not collected: {feedback_status}"
            
            # Verify feedback was logged to file
            with open(feedback_log_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0, "Test 1 Failed: Feedback not written to log file."
                last_entry = json.loads(lines[-1])
                assert last_entry["user_id"] == user_id, "Test 1 Failed: Logged feedback user ID mismatch."
            print("Feedback Collection Test Passed: Feedback logged successfully.")

        # Test 2: Web Scraping
        print("\nTesting Web Scraping...")
        if not jarvis.self_learning_engine.scraping_enabled:
            print("Web scraping is disabled in config.yaml. Skipping web scraping test.")
        else:
            # Temporarily override scraping sources for a quick test
            original_sources = jarvis.knowledge_integrator.scraping_sources
            jarvis.knowledge_integrator.scraping_sources = ["http://example.com"] # Use a reliable, simple site
            jarvis.knowledge_integrator.max_scraped_items_per_run = 1

            scraping_summary = await jarvis.self_learning_engine.trigger_web_scraping()
            assert scraping_summary["status"] == "completed", f"Test 2 Failed: Scraping did not complete: {scraping_summary}"
            assert scraping_summary["scraped_items"] >= 1, "Test 2 Failed: No items scraped."
            
            # Verify scraping was logged
            with open(scraping_log_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0, "Test 2 Failed: Scraping not written to log file."
            
            # Verify data was added to security knowledge memory
            search_results = await jarvis.memory_manager.search_security_knowledge("example.com", limit=1)
            assert len(search_results) > 0, "Test 2 Failed: Scraped data not found in security knowledge memory."
            assert "example.com" in search_results[0]["content"].lower(), "Test 2 Failed: Irrelevant scraped data in memory."
            print("Web Scraping Test Passed: Data scraped and integrated.")
            
            # Restore original sources
            jarvis.knowledge_integrator.scraping_sources = original_sources

        # Test 3: Real-time Feeds Monitoring
        print("\nTesting Real-time Feeds Monitoring...")
        if not jarvis.knowledge_integrator.realtime_feeds_enabled:
            print("Real-time feeds are disabled in config.yaml. Skipping real-time feeds test.")
        else:
            # The mock API integrations will return mock data
            monitoring_summary = await jarvis.knowledge_integrator.monitor_realtime_feeds()
            assert monitoring_summary["status"] == "completed", f"Test 3 Failed: Real-time monitoring did not complete: {monitoring_summary}"
            assert monitoring_summary["integrated_items"] > 0, "Test 3 Failed: No items integrated from real-time feeds."
            
            # Verify data was added to security knowledge memory (mocked news/threats)
            search_results_news = await jarvis.memory_manager.search_security_knowledge("Mock News", limit=1)
            assert len(search_results_news) > 0, "Test 3 Failed: Mock news not found in security knowledge memory."
            
            search_results_threat = await jarvis.memory_manager.search_security_knowledge("Mock Threat", limit=1)
            assert len(search_results_threat) > 0, "Test 3 Failed: Mock threat intel not found in security knowledge memory."
            print("Real-time Feeds Monitoring Test Passed: Data fetched and integrated.")

        print("\n--- All Phase 3 Tests Passed! ---")

    except AssertionError as e:
        print(f"Test Failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during tests: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await jarvis.__aexit__(None, None, None) # Ensure async services are properly shut down
        setup_logging(debug=jarvis.config["app"]["debug"], log_level=jarvis.config["app"]["log_level"]) # Restore original log level
        # Clean up log files
        if os.path.exists(feedback_log_path):
            os.remove(feedback_log_path)
        if os.path.exists(scraping_log_path):
            os.remove(scraping_log_path)

if __name__ == "__main__":
    import json # Ensure json is imported for this script
    # Ensure the environment is set up before running tests
    from scripts.setup_environment import main as setup_env_main
    setup_env_main()
    
    asyncio.run(test_phase3())

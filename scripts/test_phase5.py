import asyncio
import sys
import os
from pathlib import Path
import json

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import setup_logging, logger
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.knowledge_integrator import KnowledgeIntegrator
from core.self_learning import SelfLearningEngine
from core.collaboration_hub import CollaborationHub
from core.deployment_manager import DeploymentManager

# Mock configuration for testing
TEST_CONFIG = {
    "app": {"debug": True, "log_level": "DEBUG"},
    "memory": {"db_type": "chromadb", "chroma_path": "data/test_chroma_db_p5", "embedding_model": "all-MiniLM-L6-v2"},
    "api_integrations": {
        "security_api_key": "TEST_SEC_KEY",
        "weather_api_key": "TEST_WEATHER_KEY",
        "news_api_key": "TEST_NEWS_KEY",
        "threat_intel_api_key": "TEST_THREAT_INTEL_KEY"
    },
    "learning": {
        "enabled": True,
        "feedback_collection": True,
        "scraping_enabled": True,
        "feedback_log_path": "data/test_feedback_logs/feedback.jsonl",
        "scraping_log_path": "data/test_scraping_logs/scraping.jsonl",
        "scraping_sources": ["https://www.cisa.gov/news-events/cybersecurity-advisories"],
        "max_scraped_items_per_run": 2
    },
    "realtime_feeds": { # New section for real-time feeds
        "enabled": True,
        "interval_seconds": 1, # Short interval for testing
        "sources": [
            {"name": "test_news", "type": "security_news", "query": "test cyber news"},
            {"name": "test_threats", "type": "threat_intelligence", "query": "test malware"}
        ]
    },
    "collaboration": {"enabled": True, "server_port": 8082, "max_active_sessions": 2},
    "deployment": {"enabled": True, "docker_enabled": True, "kubernetes_enabled": False}
}

async def test_self_learning_engine():
    logger.info("--- Testing Self-Learning Engine ---")
    
    # Clean up old logs and DB
    feedback_log_path = Path(TEST_CONFIG["learning"]["feedback_log_path"])
    scraping_log_path = Path(TEST_CONFIG["learning"]["scraping_log_path"])
    if feedback_log_path.exists(): os.remove(feedback_log_path)
    if scraping_log_path.exists(): os.remove(scraping_log_path)
    feedback_log_path.parent.mkdir(parents=True, exist_ok=True)
    scraping_log_path.parent.mkdir(parents=True, exist_ok=True)

    if os.path.exists(TEST_CONFIG["memory"]["chroma_path"]):
        import shutil
        shutil.rmtree(TEST_CONFIG["memory"]["chroma_path"])
    os.makedirs(TEST_CONFIG["memory"]["chroma_path"], exist_ok=True)

    memory_manager = MemoryManager(TEST_CONFIG["memory"])
    api_integrations = APIIntegrations(TEST_CONFIG["api_integrations"])
    knowledge_integrator = KnowledgeIntegrator(TEST_CONFIG["learning"], memory_manager, api_integrations)
    self_learning_engine = SelfLearningEngine(memory_manager, knowledge_integrator, TEST_CONFIG["learning"])

    # Test 1: Collect feedback
    await self_learning_engine.collect_feedback("user1", "int1", "query A", "response A", 5, "Great!")
    await self_learning_engine.collect_feedback("user2", "int2", "query B", "response B", 1, "Bad response.")
    
    with open(feedback_log_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) == 2, "Test 1 Failed: Expected 2 feedback entries"
    assert json.loads(lines[0])["rating"] == 5, "Test 1 Failed: Incorrect rating"
    logger.info("Test 1 (Collect Feedback) Passed.")

    # Test 2: Process negative feedback (should add to memory)
    # This is implicitly tested by the add_knowledge_article call within process_negative_feedback
    # We can check memory count after this.
    initial_kb_count = memory_manager.knowledge_collection.count()
    await self_learning_engine.process_negative_feedback(json.loads(lines[1])) # Pass the negative feedback
    new_kb_count = memory_manager.knowledge_collection.count()
    assert new_kb_count > initial_kb_count, "Test 2 Failed: Expected knowledge base to grow after negative feedback"
    logger.info("Test 2 (Process Negative Feedback) Passed.")

    # Test 3: Trigger web scraping
    scraping_summary = await self_learning_engine.trigger_web_scraping()
    assert scraping_summary["status"] == "success" or scraping_summary["status"] == "disabled", "Test 3 Failed: Scraping did not run or failed"
    if TEST_CONFIG["learning"]["scraping_enabled"]:
        assert scraping_summary["total_scraped"] > 0, "Test 3 Failed: Expected scraped items"
        with open(scraping_log_path, 'r') as f:
            log_lines = f.readlines()
        assert len(log_lines) > 0, "Test 3 Failed: Expected scraping log entry"
    logger.info("Test 3 (Trigger Web Scraping) Passed.")

    # Test 4: Simulate model fine-tuning
    await self_learning_engine.fine_tune_model([{"text": "new data"}])
    logger.info("Test 4 (Simulate Fine-tuning) Passed.")

    # Test 5: Monitor real-time feeds
    # This will use the KnowledgeIntegrator's monitor_realtime_feeds
    await knowledge_integrator.monitor_realtime_feeds()
    # Check if security knowledge was added (indirectly)
    sec_kb_count = memory_manager.security_knowledge_collection.count()
    assert sec_kb_count > 0, "Test 5 Failed: Expected security knowledge from real-time feeds"
    logger.info("Test 5 (Monitor Real-time Feeds) Passed.")

    logger.info("--- Self-Learning Engine Tests Passed ---")
    return True

async def test_collaboration_hub():
    logger.info("--- Testing Collaboration Hub ---")
    collaboration_hub = CollaborationHub(TEST_CONFIG["collaboration"])

    # Test 1: Start session
    session_id = await collaboration_hub.start_session("userA", "projectX")
    assert session_id is not None, "Test 1 Failed: Expected a session ID"
    assert session_id in collaboration_hub.active_sessions, "Test 1 Failed: Session not in active sessions"
    logger.info("Test 1 (Start Session) Passed.")

    # Test 2: Join session
    joined = await collaboration_hub.join_session(session_id, "userB")
    assert joined is True, "Test 2 Failed: Expected user to join"
    assert "userB" in collaboration_hub.active_sessions[session_id]["users"], "Test 2 Failed: User not added to session"
    logger.info("Test 2 (Join Session) Passed.")

    # Test 3: Send message
    sent = await collaboration_hub.send_message(session_id, "userA", "Hello team!")
    assert sent is True, "Test 3 Failed: Expected message to be sent"
    assert len(collaboration_hub.active_sessions[session_id]["messages"]) > 0, "Test 3 Failed: Message not recorded"
    logger.info("Test 3 (Send Message) Passed.")

    # Test 4: Update shared context
    updated = await collaboration_hub.update_shared_context(session_id, "status", "in_progress")
    assert updated is True, "Test 4 Failed: Expected context to be updated"
    assert collaboration_hub.active_sessions[session_id]["shared_context"]["status"] == "in_progress", "Test 4 Failed: Context value incorrect"
    logger.info("Test 4 (Update Shared Context) Passed.")

    # Test 5: End session
    ended = await collaboration_hub.end_session(session_id)
    assert ended is True, "Test 5 Failed: Expected session to end"
    assert session_id not in collaboration_hub.active_sessions, "Test 5 Failed: Session still active"
    logger.info("Test 5 (End Session) Passed.")

    logger.info("--- Collaboration Hub Tests Passed ---")
    return True

async def test_deployment_manager():
    logger.info("--- Testing Deployment Manager ---")
    deployment_manager = DeploymentManager(TEST_CONFIG["deployment"])

    # Test 1: Deploy application (mocked Docker)
    deploy_result = await deployment_manager.deploy_application("jarvis_nlp_service", "1.0.0", "production")
    assert deploy_result["status"] == "success", f"Test 1 Failed: Expected 'success', got {deploy_result['status']}"
    assert len(deployment_manager.get_deployment_history()) == 1, "Test 1 Failed: Deployment not recorded"
    logger.info("Test 1 (Deploy Application) Passed.")

    # Test 2: Deploy component (mocked Docker)
    deploy_comp_result = await deployment_manager.deploy_component("nlp_module", "v2.0", "docker")
    assert deploy_comp_result["status"] == "deployed", f"Test 2 Failed: Expected 'deployed', got {deploy_comp_result['status']}"
    assert len(deployment_manager.get_deployed_services()) == 1, "Test 2 Failed: Component not recorded"
    logger.info("Test 2 (Deploy Component) Passed.")

    # Test 3: Scale component (mocked)
    scale_result = await deployment_manager.scale_component("nlp_module", 3)
    assert scale_result["status"] == "scaled", f"Test 3 Failed: Expected 'scaled', got {scale_result['status']}"
    logger.info("Test 3 (Scale Component) Passed.")

    # Test 4: Undeploy component
    undeploy_result = await deployment_manager.undeploy_component("nlp_module")
    assert undeploy_result["status"] == "undeployed", f"Test 4 Failed: Expected 'undeployed', got {undeploy_result['status']}"
    assert len(deployment_manager.get_deployed_services()) == 0, "Test 4 Failed: Component still deployed"
    logger.info("Test 4 (Undeploy Component) Passed.")

    # Test 5: Rollback deployment (should rollback the first app deployment)
    rollback_result = await deployment_manager.rollback_deployment("jarvis_nlp_service")
    assert rollback_result["status"] == "success", f"Test 5 Failed: Expected 'success', got {rollback_result['status']}"
    assert len(deployment_manager.get_deployment_history()) == 3, "Test 5 Failed: Rollback not recorded"
    logger.info("Test 5 (Rollback Deployment) Passed.")

    logger.info("--- Deployment Manager Tests Passed ---")
    return True

async def main():
    setup_logging(debug=True, log_level="DEBUG")
    logger.info("--- Running Phase 5 Tests ---")
    
    learning_passed = await test_self_learning_engine()
    collaboration_passed = await test_collaboration_hub()
    deployment_passed = await test_deployment_manager()

    if learning_passed and collaboration_passed and deployment_passed:
        logger.info("--- All Phase 5 Tests Passed Successfully! ---")
    else:
        logger.error("--- Some Phase 5 Tests Failed. Review logs for details. ---")

if __name__ == "__main__":
    asyncio.run(main())

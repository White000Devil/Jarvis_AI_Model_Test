"""
Jarvis AI - Phase 2 Test Script
Tests the functionality of the Vision Engine, Knowledge Integrator, Video UI, and API Integrations.
"""

import asyncio
import sys
import os
from pathlib import Path
import json

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils.logger import setup_logging, logger
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.knowledge_integrator import KnowledgeIntegrator
from core.memory_manager import MemoryManager  # Needed for KnowledgeIntegrator
from scripts.setup_environment import load_config
from interface.vision.video_ui import test_video_ui  # This will launch a Gradio UI
import cv2
import numpy as np

# Mock configuration for testing
TEST_CONFIG = {
    "app": {"debug": True, "log_level": "DEBUG"},
    "api_integrations": {
        "security_api_key": "TEST_SECURITY_KEY",
        "weather_api_key": "TEST_WEATHER_KEY",
        "news_api_key": "TEST_NEWS_KEY",  # Added for real-time feeds
        "threat_intel_api_key": "TEST_THREAT_INTEL_KEY"  # Added for real-time feeds
    },
    "vision": {
        "enabled": True,
        "model_name": "yolo-v8-nano",
        "cache_dir": "data/test_vision_cache",
        "video_analysis_cache_size_mb": 100
    }
}

async def test_api_integrations():
    logger.info("--- Testing API Integrations ---")
    api_integrations = APIIntegrations(TEST_CONFIG["api_integrations"])

    # Test 1: Security Analysis (mocked)
    sec_result = await api_integrations.security_analysis("example.com")
    assert sec_result["status"] == "completed", f"Test 1 Failed: Expected 'completed', got {sec_result['status']}"
    assert "vulnerabilities_found" in sec_result["results"], "Test 1 Failed: Missing vulnerabilities_found"
    logger.info("Test 1 (Security Analysis Mock) Passed.")

    # Test 2: Get Weather (mocked)
    weather_result = await api_integrations.get_weather("London")
    assert weather_result["status"] == "completed", f"Test 2 Failed: Expected 'completed', got {weather_result['status']}"
    assert "temperature_celsius" in weather_result, "Test 2 Failed: Missing temperature"
    logger.info("Test 2 (Get Weather Mock) Passed.")

    # Test 3: Get External Knowledge (mocked)
    kb_result = await api_integrations.get_external_knowledge("quantum physics")
    assert kb_result is not None, "Test 3 Failed: Expected knowledge content"
    assert "mock-knowledge-base" in kb_result, "Test 3 Failed: Expected mock content"
    logger.info("Test 3 (Get External Knowledge Mock) Passed.")

    # Test 4: Send Notification (mocked)
    notif_result = await api_integrations.send_notification("test@example.com", "Hello from JARVIS")
    assert notif_result is True, "Test 4 Failed: Expected notification to be sent"
    logger.info("Test 4 (Send Notification Mock) Passed.")

    # Test 5: Fetch Real-time News (mocked)
    news_result = await api_integrations.fetch_realtime_news("cybersecurity")
    assert news_result["status"] == "success", f"Test 5 Failed: Expected 'success', got {news_result['status']}"
    assert len(news_result["articles"]) > 0, "Test 5 Failed: Expected news articles"
    logger.info("Test 5 (Fetch Real-time News Mock) Passed.")

    # Test 6: Fetch Threat Intelligence (mocked)
    threat_result = await api_integrations.fetch_threat_intelligence("ransomware")
    assert threat_result["status"] == "success", f"Test 6 Failed: Expected 'success', got {threat_result['status']}"
    assert len(threat_result["threats"]) > 0, "Test 6 Failed: Expected threat intelligence"
    logger.info("Test 6 (Fetch Threat Intelligence Mock) Passed.")

    # Test 7: API Stats
    stats = api_integrations.get_api_stats()
    assert stats["total_requests"] >= 6, "Test 7 Failed: Total requests count incorrect"
    assert stats["successful_requests"] >= 6, "Test 7 Failed: Successful requests count incorrect"
    logger.info("Test 7 (API Stats) Passed.")

    logger.info("--- API Integrations Tests Passed ---")
    return True

async def test_vision_engine():
    logger.info("--- Testing Vision Engine ---")
    # Ensure a clean test cache
    if os.path.exists(TEST_CONFIG["vision"]["cache_dir"]):
        import shutil
        shutil.rmtree(TEST_CONFIG["vision"]["cache_dir"])
        logger.info(f"Cleaned up old test Vision cache at {TEST_CONFIG['vision']['cache_dir']}")
    os.makedirs(TEST_CONFIG["vision"]["cache_dir"], exist_ok=True)

    vision_engine = VisionEngine(TEST_CONFIG["vision"])

    # Test 1: Analyze Image (mocked)
    # Create a dummy image file for testing
    dummy_image_path = os.path.join(TEST_CONFIG["vision"]["cache_dir"], "dummy_image.jpg")
    with open(dummy_image_path, "w") as f:
        f.write("dummy image content")  # Just need a file to exist

    img_result = await vision_engine.analyze_image(dummy_image_path)
    assert img_result["status"] == "success", f"Test 1 Failed: Expected 'success', got {img_result['status']}"
    assert len(img_result["objects"]) > 0, "Test 1 Failed: Expected detected objects"
    logger.info("Test 1 (Analyze Image Mock) Passed.")

    # Test 2: Analyze Video Stream (mocked)
    stream_result = await vision_engine.analyze_video_stream("rtsp://mock.stream/live", duration_seconds=3)
    assert stream_result["status"] == "success", f"Test 2 Failed: Expected 'success', got {stream_result['status']}"
    assert len(stream_result["events"]) > 0, "Test 2 Failed: Expected detected events"
    logger.info("Test 2 (Analyze Video Stream Mock) Passed.")

    # Test 3: Facial Recognition (mocked)
    face_result = await vision_engine.facial_recognition(dummy_image_path)
    assert face_result["status"] == "success", f"Test 3 Failed: Expected 'success', got {face_result['status']}"
    assert len(face_result["faces"]) > 0, "Test 3 Failed: Expected detected faces"
    logger.info("Test 3 (Facial Recognition Mock) Passed.")

    # Test 4: Process Video File (mocked)
    dummy_video_path = os.path.join(TEST_CONFIG["vision"]["cache_dir"], "dummy_video.mp4")
    with open(dummy_video_path, "w") as f:
        f.write("dummy video content")  # Just need a file to exist

    video_file_result = await vision_engine.process_video_file(dummy_video_path)
    assert video_file_result["status"] == "success", f"Test 4 Failed: Expected 'success', got {video_file_result['status']}"
    assert len(video_file_result["analysis_results"]) > 0, "Test 4 Failed: Expected video analysis results"
    logger.info("Test 4 (Process Video File Mock) Passed.")

    # Clean up test cache
    if os.path.exists(TEST_CONFIG["vision"]["cache_dir"]):
        import shutil
        shutil.rmtree(TEST_CONFIG["vision"]["cache_dir"])
        logger.info(f"Cleaned up test Vision cache at {TEST_CONFIG['vision']['cache_dir']}")

    logger.info("--- Vision Engine Tests Passed ---")
    return True

async def test_phase2():
    """Tests Vision Engine and Knowledge Integrator functionalities."""
    logger.info("--- Starting Phase 2 Tests (Vision & Knowledge Integration) ---")
    
    config = load_config()
    
    # Initialize components
    vision_engine = VisionEngine(config)
    memory_manager = MemoryManager(config)  # KnowledgeIntegrator depends on MemoryManager
    knowledge_integrator = KnowledgeIntegrator(config, memory_manager)

    # Test 1: Vision Engine - Video Analysis (Mock)
    logger.info("\n--- Test 1: Vision Engine - Video Analysis ---")
    sample_video_path = "data/video_datasets/sample_security_footage.mp4"
    
    # Ensure the dummy video file exists for the test
    if not Path(sample_video_path).exists():
        logger.warning(f"Dummy video file '{sample_video_path}' not found. Creating a placeholder.")
        # Create a dummy file if it doesn't exist
        with open(sample_video_path, 'w') as f:
            f.write("This is a dummy video file for testing purposes.")

    analysis_result = await vision_engine.analyze_video(sample_video_path)
    logger.info(f"Video Analysis Result: {json.dumps(analysis_result, indent=2)}")
    assert analysis_result.get("status") == "completed", "Test 1 Failed: Video analysis did not complete."
    assert analysis_result.get("total_frames", 0) > 0, "Test 1 Failed: No frames processed."
    assert analysis_result.get("anomalies_detected") is not None, "Test 1 Failed: Anomalies detection not reported."
    logger.info("Test 1 Passed: Vision Engine analyzed video (mock) successfully.")

    # Test 2: Knowledge Integrator - Scrape and Integrate Security Data
    logger.info("\n--- Test 2: Knowledge Integrator - Scrape and Integrate Security Data ---")
    # Temporarily set a mock source for testing
    original_sources = config.get("SECURITY_DATA_SOURCES", [])
    config["SECURITY_DATA_SOURCES"] = ["https://mock-security-source.com/advisories"]
    
    scrape_results = await knowledge_integrator.scrape_and_integrate_security_data(max_items=2)
    logger.info(f"Scraping Results: {json.dumps(scrape_results, indent=2)}")
    assert scrape_results.get("total_scraped", 0) > 0, "Test 2 Failed: No items scraped."
    assert scrape_results.get("new_knowledge", 0) > 0, "Test 2 Failed: No new knowledge added."
    
    # Verify knowledge was added to memory
    search_query = "critical vulnerability"
    security_knowledge_results = await memory_manager.search_security_knowledge(search_query, limit=1)
    logger.info(f"Search in Memory for '{search_query}': {security_knowledge_results}")
    assert len(security_knowledge_results) > 0, "Test 2 Failed: Scraped knowledge not found in memory."
    logger.info("Test 2 Passed: Knowledge Integrator scraped and integrated security data successfully.")

    # Restore original sources
    config["SECURITY_DATA_SOURCES"] = original_sources

    # Test 3: Knowledge Integrator - Integrate Unstructured Text
    logger.info("\n--- Test 3: Knowledge Integrator - Integrate Unstructured Text ---")
    unstructured_text = "This document discusses the importance of multi-factor authentication (MFA) in preventing unauthorized access to systems."
    text_title = "MFA Best Practices"
    text_source = "Internal Document"
    text_tags = ["authentication", "security"]
    await knowledge_integrator.integrate_unstructured_text(unstructured_text, text_source, text_title, text_tags)
    logger.info("Unstructured text integrated.")

    # Verify unstructured text was added to general knowledge
    search_unstructured_query = "multi-factor authentication"
    general_knowledge_results = await memory_manager.search_knowledge(search_unstructured_query, limit=1)
    logger.info(f"Search in General Knowledge for '{search_unstructured_query}': {general_knowledge_results}")
    assert len(general_knowledge_results) > 0, "Test 3 Failed: Unstructured text not found in general knowledge."
    assert "multi-factor authentication" in general_knowledge_results[0]['document'].lower(), "Test 3 Failed: Irrelevant unstructured text found."
    logger.info("Test 3 Passed: Knowledge Integrator integrated unstructured text successfully.")

    logger.info("\n--- All Phase 2 Tests Completed Successfully! ---")

async def create_test_video():
    """Create a simple test video for analysis"""
    try:
        test_dir = Path("data/test_outputs")
        test_dir.mkdir(parents=True, exist_ok=True)
        video_path = test_dir / "test_video.mp4"
        
        # Create a simple test video with text
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(video_path), fourcc, 10.0, (640, 480))
        
        # Create frames with different text
        test_frames = [
            "Login Page",
            "Username: admin",
            "Password: ****",
            "Submit Button",
            "Success!"
        ]
        
        for i, text in enumerate(test_frames):
            # Create frame with text
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame.fill(50)  # Dark gray background
            
            # Add text
            cv2.putText(frame, text, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
            
            # Add some UI elements (rectangles as buttons)
            if "Button" in text:
                cv2.rectangle(frame, (200, 300), (440, 350), (100, 100, 255), -1)
                cv2.putText(frame, "CLICK", (280, 330), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Write frame multiple times to create duration
            for _ in range(20):  # 2 seconds per frame at 10 FPS
                out.write(frame)
        
        out.release()
        return str(video_path)
        
    except Exception as e:
        logger.error(f"Failed to create test video: {e}")
        return None

async def main():
    """Run all Phase 2 tests"""
    setup_logging(debug=True, log_level="DEBUG")
    logger.info("🧪 Running JARVIS AI Phase 2 Tests...")
    
    api_passed = await test_api_integrations()
    vision_passed = await test_vision_engine()
    phase2_passed = await test_phase2()

    if api_passed and vision_passed and phase2_passed:
        logger.info("--- All Phase 2 Tests Passed Successfully! ---")
    else:
        logger.error("--- Some Phase 2 Tests Failed. Review logs for details. ---")

if __name__ == "__main__":
    asyncio.run(main())

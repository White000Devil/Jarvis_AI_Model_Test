"""
Jarvis AI - Phase 2 Test Script
Tests the functionality of the Vision Engine, Knowledge Integrator, and Video UI.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.vision_engine import VisionEngine
from core.knowledge_integrator import KnowledgeIntegrator
from core.memory_manager import MemoryManager # Needed for KnowledgeIntegrator
from scripts.setup_environment import load_config
from interface.vision.video_ui import test_video_ui # This will launch a Gradio UI
from utils.logger import setup_logging, logger
import cv2
import numpy as np

async def test_phase2():
    """Tests Vision Engine and Knowledge Integrator functionalities."""
    logger.info("--- Starting Phase 2 Tests (Vision & Knowledge Integration) ---")
    
    config = load_config()
    
    # Initialize components
    vision_engine = VisionEngine(config)
    memory_manager = MemoryManager(config) # KnowledgeIntegrator depends on MemoryManager
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
    setup_logging(debug=True) # Ensure logging is set up for tests
    logger.info("🧪 Running JARVIS AI Phase 2 Tests...")
    
    results = {
        "vision_engine": False,
        "knowledge_integrator": False,
        "video_ui": False # Note: video_ui test requires manual interaction
    }
    
    logger.info("\n--- Testing Vision Engine ---")
    results["vision_engine"] = await test_phase2()
    
    logger.info("\n--- Testing Knowledge Integrator ---")
    results["knowledge_integrator"] = await test_phase2()
    
    logger.info("\n--- Testing Video UI (Requires Manual Interaction) ---")
    logger.info("Please open the Gradio link that appears and interact with the UI.")
    logger.info("Upload a dummy file for video analysis, and try the screen recording.")
    results["video_ui"] = await test_video_ui() # This will block until manual exit or server stop
    
    logger.info("\n--- Phase 2 Test Summary ---")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    final_status = "🎉 All Phase 2 tests passed!" if all_passed else "⚠️ Some Phase 2 tests failed."
    logger.info(f"\n{final_status}")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())

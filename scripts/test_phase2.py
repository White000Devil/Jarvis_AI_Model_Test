import asyncio
import sys
import os
from main import JarvisAI
from utils.logger import logger, setup_logging

async def test_phase2():
    """
    Tests Vision Engine functionalities.
    Phase 2: Vision Engine (Image Analysis, Video Analysis, Facial Recognition)
    """
    print("\n--- Running Phase 2 Tests: Vision Engine ---")
    
    # Temporarily set log level to INFO for tests to avoid excessive output
    setup_logging(debug=True, log_level="INFO")

    # Create dummy image/video files for testing
    dummy_image_path = os.path.join("data", "vision_cache", "dummy_image.jpg")
    dummy_video_path = os.path.join("data", "vision_cache", "dummy_video.mp4")
    
    os.makedirs(os.path.dirname(dummy_image_path), exist_ok=True)
    with open(dummy_image_path, "w") as f:
        f.write("dummy image content") # Create a placeholder file
    with open(dummy_video_path, "w") as f:
        f.write("dummy video content") # Create a placeholder file

    try:
        # Initialize JARVIS AI
        jarvis = JarvisAI(config_path="config.yaml")
        await jarvis.__aenter__() # Start async services

        if not jarvis.vision_engine.enabled:
            print("Vision Engine is disabled in config.yaml. Skipping Vision Engine tests.")
            return

        # Test 1: Image Analysis
        print("\nTesting Image Analysis...")
        image_analysis_result = await jarvis.vision_engine.analyze_image(dummy_image_path)
        assert image_analysis_result["status"] == "success", f"Test 1 Failed: Image analysis failed: {image_analysis_result.get('message')}"
        assert "objects" in image_analysis_result, "Test 1 Failed: 'objects' key missing in image analysis result"
        assert len(image_analysis_result["objects"]) > 0, "Test 1 Failed: No objects detected in dummy image"
        print(f"Image Analysis Test Passed: Detected {len(image_analysis_result['objects'])} objects.")

        # Test 2: Video Stream Analysis (Mock)
        print("\nTesting Video Stream Analysis (Mock)...")
        stream_url = "rtsp://mock.stream.com/feed1"
        duration = 5
        video_stream_result = await jarvis.vision_engine.analyze_video_stream(stream_url, duration)
        assert video_stream_result["status"] == "success", f"Test 2 Failed: Video stream analysis failed: {video_stream_result.get('message')}"
        assert "analysis_results" in video_stream_result, "Test 2 Failed: 'analysis_results' key missing in video stream analysis result"
        assert len(video_stream_result["analysis_results"]) > 0, "Test 2 Failed: No analysis results for mock stream"
        print(f"Video Stream Analysis Test Passed: Analyzed {len(video_stream_result['analysis_results'])} frames.")

        # Test 3: Video File Analysis (Mock)
        print("\nTesting Video File Analysis (Mock)...")
        video_file_result = await jarvis.vision_engine.process_video_file(dummy_video_path)
        assert video_file_result["status"] == "success", f"Test 3 Failed: Video file analysis failed: {video_file_result.get('message')}"
        assert "analysis_results" in video_file_result, "Test 3 Failed: 'analysis_results' key missing in video file analysis result"
        assert len(video_file_result["analysis_results"]) > 0, "Test 3 Failed: No analysis results for mock video file"
        print(f"Video File Analysis Test Passed: Analyzed {len(video_file_result['analysis_results'])} frames from file.")

        # Test 4: Facial Recognition
        print("\nTesting Facial Recognition...")
        face_recognition_result = await jarvis.vision_engine.identify_face(dummy_image_path)
        assert face_recognition_result["status"] == "success", f"Test 4 Failed: Facial recognition failed: {face_recognition_result.get('message')}"
        assert "faces" in face_recognition_result, "Test 4 Failed: 'faces' key missing in facial recognition result"
        assert len(face_recognition_result["faces"]) > 0, "Test 4 Failed: No faces identified in dummy image"
        print(f"Facial Recognition Test Passed: Identified {len(face_recognition_result['faces'])} faces.")

        print("\n--- All Phase 2 Tests Passed! ---")

    except AssertionError as e:
        print(f"Test Failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during tests: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await jarvis.__aexit__(None, None, None) # Ensure async services are properly shut down
        setup_logging(debug=jarvis.config["app"]["debug"], log_level=jarvis.config["app"]["log_level"]) # Restore original log level
        # Clean up dummy files
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
        if os.path.exists(dummy_video_path):
            os.remove(dummy_video_path)

if __name__ == "__main__":
    # Ensure the environment is set up before running tests
    from scripts.setup_environment import main as setup_env_main
    setup_env_main()
    
    asyncio.run(test_phase2())

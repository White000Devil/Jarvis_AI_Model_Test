import asyncio
import sys
import os
from main import JarvisAI
from utils.logger import logger, setup_logging

async def test_phase4():
    """
    Tests Voice Interface, API Integrations, Collaboration Hub, and Deployment Manager.
    Phase 4: Voice, API Integrations, Collaboration, Deployment
    """
    print("\n--- Running Phase 4 Tests: Voice, API, Collaboration, Deployment ---")
    
    # Temporarily set log level to INFO for tests to avoid excessive output
    setup_logging(debug=True, log_level="INFO")

    try:
        # Initialize JARVIS AI
        jarvis = JarvisAI(config_path="config.yaml")
        await jarvis.__aenter__() # Start async services

        # Test 1: Voice Interface - Speak (Mock)
        print("\nTesting Voice Interface (Speak)...")
        if not jarvis.voice_interface.enabled:
            print("Voice Interface is disabled in config.yaml. Skipping voice tests.")
        else:
            test_text = "Hello, this is a test of the JARVIS voice interface."
            await jarvis.voice_interface.speak(test_text)
            print("Voice Interface Speak Test Passed (check console for 'Speaking' log).")

        # Test 2: Voice Interface - Transcribe Speech (Mock)
        print("\nTesting Voice Interface (Transcribe Speech)...")
        if not jarvis.voice_interface.enabled:
            print("Voice Interface is disabled in config.yaml. Skipping voice tests.")
        else:
            # This will use Google Speech Recognition, requires microphone access and internet
            # For automated testing, this is hard to mock perfectly without a real audio input.
            # The mock in chat_interface.py's __main__ block is more suitable for isolated UI testing.
            # Here, we'll just call it and expect it not to crash.
            transcribed_text = await jarvis.voice_interface.transcribe_speech()
            print(f"Voice Interface Transcribe Test Executed. Transcribed: '{transcribed_text}' (may be empty if no speech detected/mocked).")
            # Assertions here would depend on actual audio input or a more sophisticated mock.
            print("Voice Interface Transcribe Test Passed (function executed without crash).")

        # Test 3: API Integrations - Get Weather (Mock/Real depending on API key)
        print("\nTesting API Integrations (Weather)...")
        weather_result = await jarvis.api_integrations.get_weather("New York")
        assert weather_result["status"] in ["success", "mocked"], f"Test 3 Failed: Weather API call failed: {weather_result}"
        print(f"API Integrations Weather Test Passed: {weather_result}")

        # Test 4: API Integrations - Security Analysis (Mock/Real depending on API key)
        print("\nTesting API Integrations (Security Analysis)...")
        security_result = await jarvis.api_integrations.security_analysis("example.com", "domain_check")
        assert security_result["status"] in ["completed", "mocked"], f"Test 4 Failed: Security API call failed: {security_result}"
        print(f"API Integrations Security Analysis Test Passed: {security_result}")

        # Test 5: Collaboration Hub - Create and Join Session
        print("\nTesting Collaboration Hub...")
        if not jarvis.collaboration_hub.enabled:
            print("Collaboration Hub is disabled in config.yaml. Skipping collaboration tests.")
        else:
            session_id = "test_collab_session_1"
            user_id_1 = "user_A"
            user_id_2 = "user_B"

            created = await jarvis.collaboration_hub.create_session(session_id, {"topic": "cybersecurity"})
            assert created, "Test 5 Failed: Failed to create collaboration session."
            print("Collaboration Hub Test 5.1 Passed: Session created.")

            joined1 = await jarvis.collaboration_hub.join_session(session_id, user_id_1)
            assert joined1, "Test 5 Failed: User A failed to join session."
            print("Collaboration Hub Test 5.2 Passed: User A joined.")

            joined2 = await jarvis.collaboration_hub.join_session(session_id, user_id_2)
            assert joined2, "Test 5 Failed: User B failed to join session."
            print("Collaboration Hub Test 5.3 Passed: User B joined.")

            session_context = await jarvis.collaboration_hub.get_session_context(session_id)
            assert session_context.get("topic") == "cybersecurity", "Test 5 Failed: Session context not retrieved correctly."
            assert user_id_1 in jarvis.collaboration_hub.active_sessions[session_id]["users"], "Test 5 Failed: User A not in session users."
            print("Collaboration Hub Test 5.4 Passed: Session context retrieved and users verified.")

            await jarvis.collaboration_hub.leave_session(session_id, user_id_1)
            assert user_id_1 not in jarvis.collaboration_hub.active_sessions[session_id]["users"], "Test 5 Failed: User A not removed."
            print("Collaboration Hub Test 5.5 Passed: User A left.")

            await jarvis.collaboration_hub.end_session(session_id)
            assert session_id not in jarvis.collaboration_hub.active_sessions, "Test 5 Failed: Session not ended."
            print("Collaboration Hub Test 5.6 Passed: Session ended.")

        # Test 6: Deployment Manager - Deploy Component (Mock)
        print("\nTesting Deployment Manager...")
        if not jarvis.deployment_manager.enabled:
            print("Deployment Manager is disabled in config.yaml. Skipping deployment tests.")
        else:
            deploy_result = await jarvis.deployment_manager.deploy_component("nlp_service", "1.0.0", "docker")
            assert deploy_result["status"] == "success", f"Test 6 Failed: Component deployment failed: {deploy_result}"
            assert len(jarvis.deployment_manager.get_deployed_services()) > 0, "Test 6 Failed: No services reported as deployed."
            print(f"Deployment Manager Deploy Test Passed: {deploy_result}")

            scale_result = await jarvis.deployment_manager.scale_component("nlp_service", 3, "docker")
            assert scale_result["status"] == "mocked" or scale_result["status"] == "success", f"Test 6 Failed: Component scaling failed: {scale_result}"
            print(f"Deployment Manager Scale Test Passed: {scale_result}")

            undeploy_result = await jarvis.deployment_manager.undeploy_component("nlp_service", "docker")
            assert undeploy_result["status"] == "success", f"Test 6 Failed: Component undeployment failed: {undeploy_result}"
            assert len(jarvis.deployment_manager.get_deployed_services()) == 0, "Test 6 Failed: Service still reported as deployed after undeploy."
            print(f"Deployment Manager Undeploy Test Passed: {undeploy_result}")

        print("\n--- All Phase 4 Tests Passed! ---")

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
    from scripts.setup_environment import main as setup_env_main
    setup_env_main()
    
    asyncio.run(test_phase4())

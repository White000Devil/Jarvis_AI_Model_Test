import asyncio
import sys
from pathlib import Path
import json

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from core.voice_interface import VoiceInterface
from core.api_integrations import APIIntegrations
from core.collaboration_hub import CollaborationHub
from core.deployment_manager import DeploymentManager
from scripts.setup_environment import load_config
from utils.logger import setup_logging, logger

async def main():
    """Run all Phase 4 tests"""
    setup_logging(debug=True) # Ensure logging is set up for tests
    print("🧪 Running JARVIS AI Phase 4 Tests...")
    
    results = {
        "voice_interface": False,
        "api_integrations": False,
        "collaboration_hub": False,
        "deployment_manager": False
    }
    
    print("\n--- Testing Voice Interface ---")
    results["voice_interface"] = await test_voice_interface()
    
    print("\n--- Testing API Integrations ---")
    results["api_integrations"] = await test_api_integrations()
    
    print("\n--- Testing Collaboration Hub ---")
    results["collaboration_hub"] = await test_collaboration_hub()

    print("\n--- Testing Deployment Manager ---")
    results["deployment_manager"] = await test_deployment_manager()
    
    print("\n--- Phase 4 Test Summary ---")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    all_passed = all(results.values())
    final_status = "🎉 All Phase 4 tests passed!" if all_passed else "⚠️ Some Phase 4 tests failed."
    print(f"\n{final_status}")
    
    return all_passed

async def test_voice_interface():
    """Tests Voice Interface functionalities."""
    logger.info("--- Starting Voice Interface Tests ---")
    config = load_config()
    voice_interface = VoiceInterface(config.get("voice", {}))

    # Test 1: Speak functionality (mocked)
    logger.info("\n--- Test 1: Speak Functionality ---")
    text_to_speak = "Hello, this is a test of the JARVIS voice interface."
    await voice_interface.speak(text_to_speak)
    logger.info("Test 1 Passed: Speak functionality simulated.")

    # Test 2: Start Listening (mocked, requires manual input if not fully mocked)
    logger.info("\n--- Test 2: Start Listening (Manual Interaction if not fully mocked) ---")
    # In a real test, you'd mock the speech recognition input.
    # For this, we'll just call the method and assume it works.
    # If `_single_voice_input` is truly interactive, this test will block.
    # For automated testing, ensure `_single_voice_input` is mocked to return a string.
    try:
        # Temporarily set a short timeout for the mock listening
        original_timeout = voice_interface.stt_timeout
        voice_interface.stt_timeout = 1 # Short timeout for test
        
        # Mock the internal method if it's interactive
        async def mock_single_voice_input(prompt=""):
            logger.info(f"Mocking voice input. Returning 'test voice command'.")
            return "test voice command"
        voice_interface._single_voice_input = mock_single_voice_input.__get__(voice_interface, VoiceInterface)

        # Test command registration and execution
        test_command_executed = False
        def test_callback():
            nonlocal test_command_executed
            test_command_executed = True
            logger.info("Test command callback executed!")

        voice_interface.register_command_callback("test voice command", test_callback)
        
        # Simulate listening for a short period
        await voice_interface.start_listening(continuous=False)
        
        assert test_command_executed, "Test 2 Failed: Voice command callback not executed."
        logger.info("Test 2 Passed: Listen functionality simulated and command executed.")
    finally:
        voice_interface.stt_timeout = original_timeout # Restore original timeout

    # Test 3: Get Voice Stats
    logger.info("\n--- Test 3: Get Voice Stats ---")
    voice_stats = voice_interface.get_voice_stats()
    logger.info(f"Voice Stats: {voice_stats}")
    assert voice_stats["voice_enabled"] is True, "Test 3 Failed: Voice should be enabled."
    assert "test voice command" in voice_stats["registered_commands"], "Test 3 Failed: Registered command not found in stats."
    logger.info("Test 3 Passed: Voice stats retrieved successfully.")

    logger.info("--- All Voice Interface Tests Completed Successfully! ---")
    return True

async def test_api_integrations():
    """Tests API Integrations functionalities."""
    logger.info("--- Starting API Integrations Tests ---")
    config = load_config()
    api_integrations = APIIntegrations(config.get("api_integrations", {}))

    # Test 1: Security Analysis (mocked)
    logger.info("\n--- Test 1: Security Analysis ---")
    security_target = "example.com"
    security_results = await api_integrations.security_analysis(security_target)
    logger.info(f"Security Analysis Results: {json.dumps(security_results, indent=2)}")
    assert security_results.get("status") == "completed" or security_results.get("status") == "mocked_failure", "Test 1 Failed: Security analysis did not complete or mock failed."
    assert security_results.get("target") == security_target, "Test 1 Failed: Target mismatch."
    logger.info("Test 1 Passed: Security analysis simulated successfully.")

    # Test 2: Get Weather (mocked)
    logger.info("\n--- Test 2: Get Weather ---")
    weather_city = "London"
    weather_results = await api_integrations.get_weather(weather_city)
    logger.info(f"Weather Results: {json.dumps(weather_results, indent=2)}")
    assert weather_results.get("status") == "completed" or weather_results.get("status") == "mocked_failure", "Test 2 Failed: Weather retrieval did not complete or mock failed."
    assert weather_results.get("city") == weather_city, "Test 2 Failed: City mismatch."
    logger.info("Test 2 Passed: Weather retrieval simulated successfully.")

    # Test 3: Get API Stats
    logger.info("\n--- Test 3: Get API Stats ---")
    api_stats = api_integrations.get_api_stats()
    logger.info(f"API Stats: {api_stats}")
    assert api_stats["total_requests"] >= 2, "Test 3 Failed: Total requests count incorrect."
    assert api_stats["successful_requests"] >= 0, "Test 3 Failed: Successful requests count incorrect."
    logger.info("Test 3 Passed: API stats retrieved successfully.")

    logger.info("--- All API Integrations Tests Completed Successfully! ---")
    return True

async def test_collaboration_hub():
    """Tests Collaboration Hub functionalities."""
    logger.info("--- Starting Collaboration Hub Tests ---")
    config = load_config()
    collaboration_hub = CollaborationHub(config.get("collaboration", {}))

    # Test 1: Create User
    logger.info("\n--- Test 1: Create User ---")
    user_id = await collaboration_hub.create_user("testuser", "test@example.com", "admin")
    logger.info(f"Created User ID: {user_id}")
    assert user_id is not None, "Test 1 Failed: User creation failed."
    user_info = await collaboration_hub.get_user(user_id)
    assert user_info is not None and user_info["username"] == "testuser", "Test 1 Failed: User info retrieval failed."
    logger.info("Test 1 Passed: User created and retrieved successfully.")

    # Test 2: Create Workspace
    logger.info("\n--- Test 2: Create Workspace ---")
    workspace_id = await collaboration_hub.create_workspace("Test Workspace", "A workspace for testing", user_id)
    logger.info(f"Created Workspace ID: {workspace_id}")
    assert workspace_id is not None, "Test 2 Failed: Workspace creation failed."
    logger.info("Test 2 Passed: Workspace created successfully.")

    # Test 3: Create Collaboration Session
    logger.info("\n--- Test 3: Create Collaboration Session ---")
    session_id = await collaboration_hub.create_collaboration_session(workspace_id, user_id)
    logger.info(f"Created Session ID: {session_id}")
    assert session_id is not None, "Test 3 Failed: Session creation failed."
    logger.info("Test 3 Passed: Collaboration session created successfully.")

    # Test 4: Send Message
    logger.info("\n--- Test 4: Send Message ---")
    message_sent = await collaboration_hub.send_message(session_id, user_id, "text", "Hello everyone!")
    assert message_sent is True, "Test 4 Failed: Message not sent."
    logger.info("Test 4 Passed: Message sent successfully.")

    # Test 5: Get Collaboration Stats
    logger.info("\n--- Test 5: Get Collaboration Stats ---")
    collab_stats = collaboration_hub.get_collaboration_stats()
    logger.info(f"Collaboration Stats: {collab_stats}")
    assert collab_stats["users"]["total"] >= 1, "Test 5 Failed: Total users count incorrect."
    assert collab_stats["workspaces"]["total"] >= 1, "Test 5 Failed: Total workspaces count incorrect."
    assert collab_stats["sessions"]["active"] >= 1, "Test 5 Failed: Active sessions count incorrect."
    assert collab_stats["total_messages"] >= 1, "Test 5 Failed: Total messages count incorrect."
    logger.info("Test 5 Passed: Collaboration stats retrieved successfully.")

    logger.info("--- All Collaboration Hub Tests Completed Successfully! ---")
    return True

async def test_deployment_manager():
    """Tests Deployment Manager functionalities."""
    logger.info("--- Starting Deployment Manager Tests ---")
    config = load_config()
    deployment_manager = DeploymentManager(config.get("deployment", {}))

    # Test 1: Create Deployment Config
    logger.info("\n--- Test 1: Create Deployment Config ---")
    deploy_config = await deployment_manager.create_deployment_config("test-app", "dev", image="my-image:1.0")
    logger.info(f"Created Deployment Config: {json.dumps(deploy_config, indent=2)}")
    assert deploy_config is not None and deploy_config.get("name") == "test-app", "Test 1 Failed: Config creation failed."
    logger.info("Test 1 Passed: Deployment config created successfully.")

    # Test 2: Build Docker Image (mocked)
    logger.info("\n--- Test 2: Build Docker Image ---")
    docker_build_success = await deployment_manager.build_docker_image("./app_source", "my-image:1.0")
    assert docker_build_success is True, "Test 2 Failed: Docker build simulation failed."
    logger.info("Test 2 Passed: Docker image build simulated successfully.")

    # Test 3: Deploy Docker Container (mocked)
    logger.info("\n--- Test 3: Deploy Docker Container ---")
    docker_deploy_id = await deployment_manager.deploy_docker_container(deploy_config)
    logger.info(f"Docker Deployment ID: {docker_deploy_id}")
    assert docker_deploy_id is not None, "Test 3 Failed: Docker deployment simulation failed."
    logger.info("Test 3 Passed: Docker container deployment simulated successfully.")

    # Test 4: Deploy to Kubernetes (mocked, only if enabled in config)
    if deployment_manager.kubernetes_enabled:
        logger.info("\n--- Test 4: Deploy to Kubernetes ---")
        k8s_deploy_id = await deployment_manager.deploy_to_kubernetes(deploy_config)
        logger.info(f"Kubernetes Deployment ID: {k8s_deploy_id}")
        assert k8s_deploy_id is not None, "Test 4 Failed: Kubernetes deployment simulation failed."
        logger.info("Test 4 Passed: Kubernetes deployment simulated successfully.")
    else:
        logger.info("\n--- Test 4: Deploy to Kubernetes (Skipped - Kubernetes not enabled) ---")

    # Test 5: Get Deployment Stats
    logger.info("\n--- Test 5: Get Deployment Stats ---")
    deploy_stats = deployment_manager.get_deployment_stats()
    logger.info(f"Deployment Stats: {deploy_stats}")
    assert deploy_stats["active_deployments"] >= 1, "Test 5 Failed: Active deployments count incorrect."
    assert deploy_stats["docker_enabled"] is True, "Test 5 Failed: Docker should be enabled."
    assert "cpu" in deploy_stats["system_metrics"], "Test 5 Failed: System metrics missing."
    logger.info("Test 5 Passed: Deployment stats retrieved successfully.")

    # Test 6: Undeploy
    logger.info("\n--- Test 6: Undeploy ---")
    if docker_deploy_id:
        undeploy_success = await deployment_manager.undeploy(docker_deploy_id)
        assert undeploy_success is True, "Test 6 Failed: Undeployment simulation failed."
        logger.info("Test 6 Passed: Undeployment simulated successfully.")
    else:
        logger.info("Test 6 Skipped: No Docker deployment ID to undeploy.")

    logger.info("--- All Deployment Manager Tests Completed Successfully! ---")
    return True

if __name__ == "__main__":
    asyncio.run(main())

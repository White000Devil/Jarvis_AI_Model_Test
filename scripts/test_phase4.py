"""
Jarvis AI - Phase 4 Test Script
Tests the functionality of the Voice Interface, API Integrations, Collaboration Hub, and Deployment Manager.
"""

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

async def test_phase4():
    """Tests Voice Interface, API Integrations, Collaboration Hub, and Deployment Manager functionalities."""
    logger.info("--- Starting Phase 4 Tests (Voice, API, Collaboration, Deployment) ---")
    
    config = load_config()
    
    # Initialize components
    voice_interface = VoiceInterface(config)
    api_integrations = APIIntegrations(config)
    collaboration_hub = CollaborationHub(config)
    deployment_manager = DeploymentManager(config)

    # Test 1: Voice Interface - Speak (Mock)
    logger.info("\n--- Test 1: Voice Interface - Speak ---")
    if voice_interface.voice_enabled:
        await voice_interface.speak("Hello, this is a test from JARVIS AI voice interface.")
        logger.info("Test 1 Passed: JARVIS spoke (check console/audio output).")
    else:
        logger.warning("Test 1 Skipped: Voice interface is disabled in config.")

    # Test 2: Voice Interface - Get Voice Stats
    logger.info("\n--- Test 2: Voice Interface - Get Voice Stats ---")
    voice_stats = voice_interface.get_voice_stats()
    logger.info(f"Voice Stats: {json.dumps(voice_stats, indent=2)}")
    assert voice_stats["voice_enabled"] == config["VOICE_ENABLED"], "Test 2 Failed: Voice enabled status mismatch."
    logger.info("Test 2 Passed: Voice stats retrieved successfully.")

    # Test 3: API Integrations - Security Analysis (Mock)
    logger.info("\n--- Test 3: API Integrations - Security Analysis ---")
    async with api_integrations: # Use async context manager
        analysis_result = await api_integrations.security_analysis("example.com", "web_scan")
        logger.info(f"Security Analysis Result: {json.dumps(analysis_result, indent=2)}")
        assert analysis_result.get("status") == "completed", "Test 3 Failed: Security analysis did not complete."
        logger.info("Test 3 Passed: API Integrations performed security analysis (mock) successfully.")

    # Test 4: API Integrations - Get API Stats
    logger.info("\n--- Test 4: API Integrations - Get API Stats ---")
    api_stats = api_integrations.get_api_stats()
    logger.info(f"API Stats: {json.dumps(api_stats, indent=2)}")
    assert api_stats["total_requests"] >= 1, "Test 4 Failed: Total API requests count incorrect."
    assert api_stats["successful_requests"] >= 1, "Test 4 Failed: Successful API requests count incorrect."
    logger.info("Test 4 Passed: API stats retrieved successfully.")

    # Test 5: Collaboration Hub - Create User and Workspace
    logger.info("\n--- Test 5: Collaboration Hub - Create User and Workspace ---")
    if collaboration_hub.collaboration_enabled:
        user_id = await collaboration_hub.create_user("test_user", "test@example.com", "admin")
        workspace_id = await collaboration_hub.create_workspace("Test Workspace", "For testing collaboration", user_id)
        logger.info(f"Created User ID: {user_id}, Workspace ID: {workspace_id}")
        assert user_id != "disabled", "Test 5 Failed: User creation failed."
        assert workspace_id != "disabled" and workspace_id != "workspace_not_found", "Test 5 Failed: Workspace creation failed."
        logger.info("Test 5 Passed: User and Workspace created successfully.")
    else:
        logger.warning("Test 5 Skipped: Collaboration Hub is disabled in config.")

    # Test 6: Collaboration Hub - Create and End Session
    logger.info("\n--- Test 6: Collaboration Hub - Create and End Session ---")
    if collaboration_hub.collaboration_enabled:
        session_id = await collaboration_hub.create_collaboration_session(workspace_id, user_id)
        logger.info(f"Created Session ID: {session_id}")
        assert session_id != "disabled" and session_id != "workspace_not_found" and session_id != "max_sessions_reached", "Test 6 Failed: Session creation failed."
        
        await collaboration_hub.send_message(session_id, user_id, "text", "Hello JARVIS, let's collaborate!")
        await collaboration_hub.send_message(session_id, "JARVIS_AI", "text", "Acknowledged. How can I assist?")
        
        ended = await collaboration_hub.end_collaboration_session(session_id)
        assert ended, "Test 6 Failed: Session did not end."
        logger.info("Test 6 Passed: Collaboration session created, messaged, and ended successfully.")
    else:
        logger.warning("Test 6 Skipped: Collaboration Hub is disabled in config.")

    # Test 7: Collaboration Hub - Get Collaboration Stats
    logger.info("\n--- Test 7: Collaboration Hub - Get Collaboration Stats ---")
    if collaboration_hub.collaboration_enabled:
        collab_stats = collaboration_hub.get_collaboration_stats()
        logger.info(f"Collaboration Stats: {json.dumps(collab_stats, indent=2)}")
        assert collab_stats["users"]["total"] >= 1, "Test 7 Failed: Total users count incorrect."
        assert collab_stats["workspaces"]["total"] >= 1, "Test 7 Failed: Total workspaces count incorrect."
        assert collab_stats["sessions"]["total"] >= 1, "Test 7 Failed: Total sessions count incorrect."
        logger.info("Test 7 Passed: Collaboration stats retrieved successfully.")
    else:
        logger.warning("Test 7 Skipped: Collaboration Hub is disabled in config.")

    # Test 8: Deployment Manager - Create Config and Deploy Docker (Mock)
    logger.info("\n--- Test 8: Deployment Manager - Create Config and Deploy Docker ---")
    if deployment_manager.docker_enabled:
        deploy_config = await deployment_manager.create_deployment_config("test-app", "dev", image="my-app:1.0")
        deploy_id = await deployment_manager.deploy_docker_container(deploy_config)
        logger.info(f"Docker Deployment ID: {deploy_id}")
        assert deploy_id != "disabled", "Test 8 Failed: Docker deployment failed."
        assert deploy_id in deployment_manager.active_deployments, "Test 8 Failed: Deployment not registered."
        logger.info("Test 8 Passed: Docker deployment created and deployed (mock) successfully.")
    else:
        logger.warning("Test 8 Skipped: Docker is disabled or not found.")

    # Test 9: Deployment Manager - Deploy to Kubernetes (Mock)
    logger.info("\n--- Test 9: Deployment Manager - Deploy to Kubernetes ---")
    if deployment_manager.kubernetes_enabled:
        deploy_config_k8s = await deployment_manager.create_deployment_config("test-k8s-app", "prod", image="my-k8s-app:1.0")
        deploy_id_k8s = await deployment_manager.deploy_to_kubernetes(deploy_config_k8s)
        logger.info(f"Kubernetes Deployment ID: {deploy_id_k8s}")
        assert deploy_id_k8s != "disabled", "Test 9 Failed: Kubernetes deployment failed."
        assert deploy_id_k8s in deployment_manager.active_deployments, "Test 9 Failed: K8s Deployment not registered."
        logger.info("Test 9 Passed: Kubernetes deployment created and deployed (mock) successfully.")
    else:
        logger.warning("Test 9 Skipped: Kubernetes is disabled or not found.")

    # Test 10: Deployment Manager - Get Deployment Stats
    logger.info("\n--- Test 10: Deployment Manager - Get Deployment Stats ---")
    deploy_stats = deployment_manager.get_deployment_stats()
    logger.info(f"Deployment Stats: {json.dumps(deploy_stats, indent=2)}")
    assert deploy_stats["active_deployments"] >= 0, "Test 10 Failed: Active deployments count incorrect."
    assert deploy_stats["docker_enabled"] == config["DOCKER_ENABLED"], "Test 10 Failed: Docker enabled status mismatch."
    logger.info("Test 10 Passed: Deployment stats retrieved successfully.")

    # Test 11: Deployment Manager - Undeploy (Mock)
    logger.info("\n--- Test 11: Deployment Manager - Undeploy ---")
    if deployment_manager.docker_enabled and deploy_id in deployment_manager.active_deployments:
        undeployed = await deployment_manager.undeploy(deploy_id)
        assert undeployed, "Test 11 Failed: Docker deployment did not undeploy."
        assert deploy_id not in deployment_manager.active_deployments, "Test 11 Failed: Docker deployment still active after undeploy."
        logger.info("Test 11 Passed: Docker deployment undeployed successfully.")
    else:
        logger.warning("Test 11 Skipped: No Docker deployment to undeploy or Docker disabled.")

    logger.info("\n--- All Phase 4 Tests Completed Successfully! ---")

if __name__ == "__main__":
    # Ensure logging is set up for tests
    config = load_config()
    setup_logging(debug=(config.get("LOG_LEVEL", "INFO").upper() == "DEBUG"))
    asyncio.run(test_phase4())

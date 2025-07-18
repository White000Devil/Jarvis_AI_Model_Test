import gradio as gr
import asyncio
from typing import Dict, Any
from utils.logger import logger

# Import all necessary engine classes
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from core.human_ai_teaming import HumanAITeaming
from core.self_correction import SelfCorrectionEngine
from core.self_learning import SelfLearningEngine
from core.collaboration_hub import CollaborationHub
from core.deployment_manager import DeploymentManager
from core.voice_interface import VoiceInterface

def create_admin_dashboard(
    nlp_engine: NLPEngine,
    memory_manager: MemoryManager,
    api_integrations: APIIntegrations,
    vision_engine: VisionEngine,
    ethical_ai_engine: EthicalAIEngine,
    reasoning_engine: ReasoningEngine,
    human_ai_teaming: HumanAITeaming,
    self_correction_engine: SelfCorrectionEngine,
    self_learning_engine: SelfLearningEngine, # Added
    collaboration_hub: CollaborationHub, # Added
    deployment_manager: DeploymentManager, # Added
    voice_interface: VoiceInterface # Added
):
    """
    Creates and returns the Gradio admin dashboard interface.
    This dashboard provides insights and controls for JARVIS AI's various components.
    """

    def get_system_status():
        """Returns a summary of the system's operational status."""
        status = {
            "NLP Engine": "Initialized" if nlp_engine else "Not Initialized",
            "Memory Manager": "Initialized" if memory_manager else "Not Initialized",
            "API Integrations": "Initialized" if api_integrations else "Not Initialized",
            "Vision Engine": "Enabled" if vision_engine.enabled else "Disabled",
            "Ethical AI": "Enabled" if ethical_ai_engine.enabled else "Disabled",
            "Reasoning Engine": "Enabled" if reasoning_engine.enabled else "Disabled",
            "Human-AI Teaming": "Enabled" if human_ai_teaming.enabled else "Disabled",
            "Self-Correction": "Enabled" if self_correction_engine.enabled else "Disabled",
            "Self-Learning": "Enabled" if self_learning_engine.feedback_collection_enabled or self_learning_engine.scraping_enabled else "Disabled",
            "Collaboration Hub": "Enabled" if collaboration_hub.enabled else "Disabled",
            "Deployment Manager": "Enabled" if deployment_manager.enabled else "Disabled",
            "Voice Interface": "Enabled" if voice_interface.enabled else "Disabled",
        }
        return "\n".join([f"{k}: {v}" for k, v in status.items()])

    async def get_memory_stats():
        """Returns statistics from the Memory Manager."""
        if not memory_manager:
            return "Memory Manager not initialized."
        
        # ChromaDB doesn't have direct "stats" methods, so we'll count documents
        conv_count = memory_manager.conversations_collection.count()
        kb_count = memory_manager.knowledge_collection.count()
        sec_kb_count = memory_manager.security_knowledge_collection.count()

        return (
            f"Memory Type: {memory_manager.db_type}\n"
            f"Conversations: {conv_count} entries\n"
            f"General Knowledge: {kb_count} articles\n"
            f"Security Knowledge: {sec_kb_count} articles\n"
            f"Embedding Model: {memory_manager.embedding_model}"
        )

    async def get_api_integration_stats():
        """Returns statistics from API Integrations."""
        if not api_integrations:
            return "API Integrations not initialized."
        stats = api_integrations.get_api_stats()
        return (
            f"Total Requests: {stats.get('total_requests', 0)}\n"
            f"Successful Requests: {stats.get('successful_requests', 0)}\n"
            f"Failed Requests: {stats.get('failed_requests', 0)}\n"
            f"Last Request: {stats.get('last_request_timestamp', 'N/A')}"
        )

    async def get_ethical_ai_stats():
        """Returns statistics from Ethical AI Engine."""
        if not ethical_ai_engine.enabled:
            return "Ethical AI Engine is disabled."
        stats = ethical_ai_engine.get_ethical_stats()
        return (
            f"Total Violations: {stats.get('total_violations', 0)}\n"
            f"High Severity: {stats.get('high_severity', 0)}\n"
            f"Critical Severity: {stats.get('critical_severity', 0)}\n"
            f"Last Violation: {stats.get('last_violation_timestamp', 'N/A')}\n"
            f"Violation Types: {stats.get('violation_types', {})}"
        )

    async def get_self_correction_stats():
        """Returns statistics from Self-Correction Engine."""
        if not self_correction_engine.enabled:
            return "Self-Correction Engine is disabled."
        stats = self_correction_engine.get_correction_stats()
        return (
            f"Total Corrections: {stats.get('total_corrections', 0)}\n"
            f"Low Confidence Corrections: {stats.get('low_confidence_corrections', 0)}\n"
            f"Inconsistency Corrections: {stats.get('inconsistency_corrections', 0)}\n"
            f"Last Correction: {stats.get('last_correction_timestamp', 'N/A')}"
        )

    async def get_collaboration_stats():
        """Returns statistics from Collaboration Hub."""
        if not collaboration_hub.enabled:
            return "Collaboration Hub is disabled."
        stats = collaboration_hub.get_status()
        return (
            f"Status: {stats.get('status', 'N/A')}\n"
            f"Active Sessions: {stats.get('active_sessions', 0)}\n"
            f"Max Sessions: {stats.get('max_active_sessions', 'N/A')}\n"
            f"Last Activity: {stats.get('last_activity', 'N/A')}"
        )

    async def get_deployment_stats():
        """Returns statistics from Deployment Manager."""
        if not deployment_manager.enabled:
            return "Deployment Manager is disabled."
        stats = deployment_manager.get_status()
        deployed_services = deployment_manager.get_deployed_services()
        services_list = "\n".join([f"- {s['name']} (v{s['version']}) on {s['target']}" for s in deployed_services]) if deployed_services else "None"
        return (
            f"Status: {stats.get('status', 'N/A')}\n"
            f"Docker Enabled: {stats.get('docker_enabled', 'N/A')}\n"
            f"Kubernetes Enabled: {stats.get('kubernetes_enabled', 'N/A')}\n"
            f"Total Deployments: {stats.get('deployment_count', 0)}\n"
            f"Last Deployment: {stats.get('last_deployment_timestamp', 'N/A')}\n"
            f"Deployed Services:\n{services_list}"
        )

    async def trigger_realtime_monitoring():
        """Triggers a single cycle of real-time feed monitoring."""
        if not self_learning_engine:
            return "Self-Learning Engine not initialized."
        if not self_learning_engine.config.get("realtime_feeds", {}).get("enabled", False):
            return "Real-time feeds are disabled in config.yaml."
        
        logger.info("Manually triggering real-time feed monitoring.")
        await self_learning_engine.knowledge_integrator.monitor_realtime_feeds()
        return "Real-time monitoring cycle completed. Check logs for details."

    async def trigger_web_scraping_manual():
        """Triggers a manual web scraping run."""
        if not self_learning_engine.scraping_enabled:
            return "Web scraping is disabled in config.yaml."
        
        logger.info("Manually triggering web scraping.")
        summary = await self_learning_engine.trigger_web_scraping()
        return f"Web scraping completed. Summary: {summary}"

    async def deploy_component_manual(component_name: str, version: str, target: str):
        """Manually triggers component deployment."""
        if not deployment_manager.enabled:
            return "Deployment Manager is disabled."
        
        logger.info(f"Manually deploying {component_name} v{version} to {target}.")
        result = await deployment_manager.deploy_component(component_name, version, target)
        return f"Deployment result: {result}"

    async def clear_memory_manual():
        """Manually clears all memory."""
        if not memory_manager:
            return "Memory Manager not initialized."
        
        logger.warning("Manually clearing all JARVIS memory. This action is irreversible.")
        memory_manager.clear_memory()
        return "All JARVIS memory cleared."

    with gr.Blocks() as demo:
        gr.Markdown("# JARVIS AI Admin Dashboard")
        gr.Markdown("Monitor and control JARVIS AI's core functionalities.")

        with gr.Tab("System Status"):
            status_output = gr.Textbox(label="Overall System Status", interactive=False, lines=10)
            refresh_status_btn = gr.Button("Refresh Status")
            refresh_status_btn.click(get_system_status, outputs=status_output)
            demo.load(get_system_status, outputs=status_output) # Load on startup

        with gr.Tab("Memory Management"):
            memory_stats_output = gr.Textbox(label="Memory Statistics", interactive=False, lines=10)
            refresh_memory_btn = gr.Button("Refresh Memory Stats")
            refresh_memory_btn.click(get_memory_stats, outputs=memory_stats_output)
            
            clear_memory_btn = gr.Button("Clear All Memory (DANGER!)", variant="stop")
            clear_memory_output = gr.Textbox(label="Clear Memory Status", interactive=False)
            clear_memory_btn.click(clear_memory_manual, outputs=clear_memory_output)

        with gr.Tab("API Integrations"):
            api_stats_output = gr.Textbox(label="API Call Statistics", interactive=False, lines=10)
            refresh_api_btn = gr.Button("Refresh API Stats")
            refresh_api_btn.click(get_api_integration_stats, outputs=api_stats_output)

        with gr.Tab("Real-time Feeds"):
            gr.Markdown("Trigger real-time data collection for news and threat intelligence.")
            realtime_trigger_btn = gr.Button("Trigger Real-time Monitoring Cycle")
            realtime_output = gr.Textbox(label="Real-time Monitoring Status", interactive=False)
            realtime_trigger_btn.click(trigger_realtime_monitoring, outputs=realtime_output)

        with gr.Tab("Web Scraping"):
            gr.Markdown("Manually trigger web scraping for security data.")
            scraping_trigger_btn = gr.Button("Trigger Web Scraping")
            scraping_output = gr.Textbox(label="Web Scraping Status", interactive=False)
            scraping_trigger_btn.click(trigger_web_scraping_manual, outputs=scraping_output)

        with gr.Tab("Ethical AI"):
            ethical_stats_output = gr.Textbox(label="Ethical AI Statistics", interactive=False, lines=10)
            refresh_ethical_btn = gr.Button("Refresh Ethical AI Stats")
            refresh_ethical_btn.click(get_ethical_ai_stats, outputs=ethical_stats_output)

        with gr.Tab("Self-Correction"):
            self_correction_stats_output = gr.Textbox(label="Self-Correction Statistics", interactive=False, lines=10)
            refresh_self_correction_btn = gr.Button("Refresh Self-Correction Stats")
            refresh_self_correction_btn.click(get_self_correction_stats, outputs=self_correction_stats_output)

        with gr.Tab("Collaboration Hub"):
            collaboration_stats_output = gr.Textbox(label="Collaboration Hub Statistics", interactive=False, lines=10)
            refresh_collaboration_btn = gr.Button("Refresh Collaboration Stats")
            refresh_collaboration_btn.click(get_collaboration_stats, outputs=collaboration_stats_output)

        with gr.Tab("Deployment Manager"):
            deployment_stats_output = gr.Textbox(label="Deployment Statistics", interactive=False, lines=15)
            refresh_deployment_btn = gr.Button("Refresh Deployment Stats")
            refresh_deployment_btn.click(get_deployment_stats, outputs=deployment_stats_output)

            gr.Markdown("### Deploy Component")
            with gr.Row():
                component_name_input = gr.Textbox(label="Component Name", placeholder="e.g., nlp_service")
                component_version_input = gr.Textbox(label="Version", value="latest")
                deployment_target_input = gr.Dropdown(label="Target", choices=["docker", "kubernetes"], value="docker")
            deploy_component_btn = gr.Button("Deploy Component", variant="primary")
            deploy_component_output = gr.Textbox(label="Deployment Result", interactive=False)
            deploy_component_btn.click(
                deploy_component_manual,
                inputs=[component_name_input, component_version_input, deployment_target_input],
                outputs=deploy_component_output
            )

    return demo

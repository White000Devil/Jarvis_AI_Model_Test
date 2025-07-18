import asyncio
import yaml
import os
from typing import Dict, Any, Optional
from utils.logger import setup_logging, logger
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
from core.knowledge_integrator import KnowledgeIntegrator # Import KnowledgeIntegrator

class JarvisAI:
    """
    The main class for JARVIS AI, orchestrating all its core components.
    """
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        setup_logging(debug=self.config["app"]["debug"], log_level=self.config["app"]["log_level"])
        logger.info("Initializing JARVIS AI...")

        # Initialize core components
        self.api_integrations = APIIntegrations(self.config.get("api_integrations", {}))
        self.memory_manager = MemoryManager(self.config.get("memory", {}))
        self.nlp_engine = NLPEngine(self.config.get("nlp", {}))
        self.vision_engine = VisionEngine(self.config.get("vision", {}))
        self.ethical_ai_engine = EthicalAIEngine(self.memory_manager, self.config.get("ethical_ai", {}))
        self.reasoning_engine = ReasoningEngine(
            self.nlp_engine, self.memory_manager, self.api_integrations, 
            self.vision_engine, self.ethical_ai_engine, self.config.get("reasoning", {})
        )
        self.knowledge_integrator = KnowledgeIntegrator(
            self.config.get("learning", {}), self.memory_manager, self.api_integrations # Pass APIIntegrations
        )
        self.self_learning_engine = SelfLearningEngine(
            self.memory_manager, self.knowledge_integrator, self.config.get("learning", {})
        )
        self.collaboration_hub = CollaborationHub(self.config.get("collaboration", {}))
        self.human_ai_teaming = HumanAITeaming(
            self.nlp_engine, self.memory_manager, 
            self.collaboration_hub, # Pass CollaborationHub instance
            self.config.get("human_ai_teaming", {})
        )
        self.self_correction_engine = SelfCorrectionEngine(
            self.nlp_engine, self.memory_manager, self.ethical_ai_engine, self.config.get("self_correction", {})
        )
        self.deployment_manager = DeploymentManager(self.config.get("deployment", {}))
        self.voice_interface = VoiceInterface(self.config.get("voice", {}))

        self.realtime_monitoring_task: Optional[asyncio.Task] = None
        logger.info("JARVIS AI initialized successfully.")

    async def __aenter__(self):
        """Context manager entry point for async setup."""
        logger.info("Starting JARVIS AI services...")
        # Start API integrations client
        await self.api_integrations.__aenter__()
        # Start real-time monitoring if enabled
        if self.config.get("realtime_feeds", {}).get("enabled", False):
            interval = self.config["realtime_feeds"].get("interval_seconds", 300)
            self.realtime_monitoring_task = asyncio.create_task(
                self._run_realtime_monitoring(interval)
            )
            logger.info(f"Real-time monitoring started with interval: {interval} seconds.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point for async cleanup."""
        logger.info("Shutting down JARVIS AI services...")
        # Cancel real-time monitoring task
        if self.realtime_monitoring_task:
            self.realtime_monitoring_task.cancel()
            try:
                await self.realtime_monitoring_task
            except asyncio.CancelledError:
                logger.info("Real-time monitoring task cancelled.")
        # Close API integrations client
        await self.api_integrations.__aexit__(exc_type, exc_val, exc_tb)
        self.memory_manager.persist_memory() # Persist ChromaDB on exit
        logger.info("JARVIS AI shutdown complete.")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Loads configuration from a YAML file."""
        if not os.path.exists(config_path):
            logger.error(f"Config file not found at {config_path}")
            raise FileNotFoundError(f"Config file not found at {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    async def _run_realtime_monitoring(self, interval_seconds: int):
        """Background task to periodically run real-time feed monitoring."""
        while True:
            try:
                await self.knowledge_integrator.monitor_realtime_feeds()
            except Exception as e:
                logger.error(f"Error during real-time monitoring cycle: {e}")
            await asyncio.sleep(interval_seconds)

    async def process_user_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a user's input through the entire JARVIS AI pipeline.
        """
        if context is None:
            context = {}

        logger.info(f"Processing user input: '{user_input}'")

        # 1. NLP Processing
        nlp_result = await self.nlp_engine.process_query(user_input, context)
        context["nlp_intent"] = nlp_result["metadata"]["intent"]
        context["nlp_confidence"] = nlp_result["metadata"]["confidence"]
        context["nlp_entities"] = nlp_result["metadata"]["entities"]
        context["nlp_summary"] = nlp_result["metadata"]["summary"]
        context["user_sentiment"] = nlp_result["metadata"]["sentiment"] # Add user sentiment to context
        logger.debug(f"NLP Result: {nlp_result}")

        # 2. Memory Recall (retrieve relevant past conversations and knowledge)
        conversation_history = await self.memory_manager.search_conversations(user_input, limit=3)
        knowledge_recall = await self.memory_manager.search_knowledge(user_input, limit=2)
        security_knowledge_recall = await self.memory_manager.search_security_knowledge(user_input, limit=2)
        
        context["conversation_history"] = conversation_history
        context["knowledge_recall"] = knowledge_recall
        context["security_knowledge_recall"] = security_knowledge_recall
        logger.debug(f"Memory Recall: {len(conversation_history)} convs, {len(knowledge_recall)} kb, {len(security_knowledge_recall)} sec_kb")

        # 3. Reasoning and Planning
        reasoning_output = await self.reasoning_engine.reason_on_query(user_input, nlp_result, context)
        jarvis_response = reasoning_output["response"]
        context["reasoning_steps"] = reasoning_output["reasoning_steps"]
        context["final_plan"] = reasoning_output["final_plan"]
        context["jarvis_confidence"] = reasoning_output["confidence"]
        logger.debug(f"Reasoning Output: {reasoning_output}")

        # 4. Self-Correction (assess confidence and consistency)
        confidence = await self.self_correction_engine.assess_confidence(jarvis_response, context)
        is_inconsistent, inconsistency_reason = await self.self_correction_engine.detect_inconsistency(jarvis_response, conversation_history)
        
        context["confidence_score"] = confidence
        context["is_inconsistent"] = is_inconsistent
        context["inconsistency_reason"] = inconsistency_reason

        if confidence < self.self_correction_engine.confidence_threshold:
            logger.warning(f"Low confidence ({confidence:.2f}) detected. Triggering self-correction.")
            jarvis_response = await self.self_correction_engine.propose_correction(
                jarvis_response, "low_confidence", user_input, context
            )
            context["self_corrected"] = True
        elif is_inconsistent:
            logger.warning(f"Inconsistency detected. Triggering self-correction: {inconsistency_reason}")
            jarvis_response = await self.self_correction_engine.propose_correction(
                jarvis_response, f"inconsistency: {inconsistency_reason}", user_input, context
            )
            context["self_corrected"] = True
        else:
            context["self_corrected"] = False
        logger.debug(f"Self-Correction Applied: {context['self_corrected']}")

        # 5. Ethical AI Check
        is_ethical, ethical_violations = await self.ethical_ai_engine.check_response_for_ethics(user_input, jarvis_response, context)
        context["ethical_violations"] = ethical_violations
        context["is_ethical"] = is_ethical

        if not is_ethical:
            logger.warning("Ethical violation detected. Applying guardrails.")
            jarvis_response = await self.ethical_ai_engine.apply_ethical_guardrails(user_input, jarvis_response, ethical_violations)
            context["ethical_guardrail_applied"] = True
        else:
            context["ethical_guardrail_applied"] = False
        logger.debug(f"Ethical Guardrail Applied: {context['ethical_guardrail_applied']}")

        # 6. Human-AI Teaming (adapt communication, clarify if needed)
        clarification_needed = await self.human_ai_teaming.clarify_request(user_input, confidence, context)
        if clarification_needed:
            jarvis_response = clarification_needed
            context["clarification_issued"] = True
        else:
            jarvis_response = await self.human_ai_teaming.adapt_communication(user_input, jarvis_response, context)
            context["clarification_issued"] = False
        logger.debug(f"Communication Adapted / Clarification: {context['clarification_issued']}")

        # 7. Memory Storage (store the interaction)
        await self.memory_manager.add_conversation(user_input, jarvis_response, context)
        logger.debug("Interaction stored in memory.")

        final_response_data = {
            "response": jarvis_response,
            "context": context
        }
        logger.info("User input processing complete.")
        return final_response_data

    async def run_chat_interface(self):
        """Runs the Gradio chat interface."""
        from interface.chat_interface import ChatInterface
        chat_ui = ChatInterface(self)
        logger.info("Starting chat interface...")
        await chat_ui.create_interface().launch(share=False, inbrowser=True)

    async def run_admin_dashboard(self):
        """Runs the Gradio admin dashboard."""
        from interface.admin.admin_dashboard import create_admin_dashboard
        admin_ui = create_admin_dashboard(
            self.nlp_engine, self.memory_manager, self.api_integrations, 
            self.vision_engine, self.ethical_ai_engine, self.reasoning_engine,
            self.human_ai_teaming, self.self_correction_engine, self.self_learning_engine,
            self.collaboration_hub, self.deployment_manager, self.voice_interface
        )
        logger.info("Starting admin dashboard...")
        await admin_ui.launch(share=False, inbrowser=True)

    async def run_feedback_ui(self):
        """Runs the Gradio feedback UI."""
        from interface.learning.feedback_ui import create_feedback_ui
        feedback_ui = create_feedback_ui(self.self_learning_engine)
        logger.info("Starting feedback UI...")
        await feedback_ui.launch(share=False, inbrowser=True)

    async def run_video_analysis_ui(self):
        """Runs the Gradio video analysis UI."""
        from interface.vision.video_ui import VideoUI
        video_ui = VideoUI(self.vision_engine) # Pass instance of VisionEngine
        logger.info("Starting video analysis UI...")
        await video_ui.create_interface().launch(share=False, inbrowser=True)

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run JARVIS AI in different modes.")
    parser.add_argument("--mode", type=str, default="chat", 
                        choices=["chat", "admin", "feedback", "video_analysis", "vision", "learning"],
                        help="Mode to run JARVIS AI in.")
    args = parser.parse_args()

    async with JarvisAI() as jarvis:
        if args.mode == "chat":
            await jarvis.run_chat_interface()
        elif args.mode == "admin":
            await jarvis.run_admin_dashboard()
        elif args.mode == "feedback" or args.mode == "learning":
            await jarvis.run_feedback_ui()
        elif args.mode == "video_analysis" or args.mode == "vision":
            await jarvis.run_video_analysis_ui()

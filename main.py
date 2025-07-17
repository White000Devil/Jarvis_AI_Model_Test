import asyncio
import argparse
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure project root is in sys.path for imports
PROJECT_ROOT = Path(__file__).parent.parent
import sys
sys.path.append(str(PROJECT_ROOT))

from utils.logger import setup_logging, logger
from scripts.setup_environment import setup_environment, load_config

# Import all core engines
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.vision_engine import VisionEngine
from core.knowledge_integrator import KnowledgeIntegrator
from core.self_learning import SelfLearningEngine
from core.voice_interface import VoiceInterface
from core.api_integrations import APIIntegrations
from core.collaboration_hub import CollaborationHub
from core.deployment_manager import DeploymentManager
from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from core.human_ai_teaming import HumanAITeaming
from core.self_correction import SelfCorrectionEngine

# Import all UI interfaces
from interface.chat_interface import ChatInterface
from interface.vision.video_ui import VideoUI
from interface.learning.feedback_ui import FeedbackUI
from interface.admin.admin_dashboard import create_admin_dashboard # Function to create dashboard

class JarvisAI:
    """
    The main orchestrator for the JARVIS AI Assistant.
    Initializes and manages all core engines and interfaces.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.debug_mode = config.get("app", {}).get("debug", False)
        
        # Initialize core engines
        self.nlp_engine = NLPEngine(config.get("nlp", {}))
        self.memory_manager = MemoryManager(config.get("memory", {}))
        self.api_integrations = APIIntegrations(config.get("api_integrations", {}))
        self.vision_engine = VisionEngine(config.get("vision", {}))
        self.knowledge_integrator = KnowledgeIntegrator(config.get("learning", {}), self.memory_manager)
        self.self_learning_engine = SelfLearningEngine(self.memory_manager, config.get("learning", {}))
        self.voice_interface = VoiceInterface(config.get("voice", {}))
        self.collaboration_hub = CollaborationHub(config.get("collaboration", {}))
        self.deployment_manager = DeploymentManager(config.get("deployment", {}))
        self.ethical_ai_engine = EthicalAIEngine(self.memory_manager, config.get("ethical_ai", {}))
        self.reasoning_engine = ReasoningEngine(
            self.nlp_engine, self.memory_manager, self.api_integrations,
            self.vision_engine, self.ethical_ai_engine, config.get("reasoning", {})
        )
        self.human_ai_teaming = HumanAITeaming(
            self.nlp_engine, self.memory_manager, self.collaboration_hub, config.get("human_ai_teaming", {})
        )
        self.self_correction_engine = SelfCorrectionEngine(
            self.nlp_engine, self.memory_manager, self.ethical_ai_engine, config.get("self_correction", {})
        )

        logger.info("All JARVIS AI core engines initialized.")

    async def chat(self, user_input: str) -> str:
        """
        Processes a user's chat input through the entire JARVIS pipeline.
        """
        logger.info(f"Processing chat input: '{user_input}'")
        
        # 1. NLP Processing
        nlp_result = await self.nlp_engine.process_query(user_input)
        intent = nlp_result["metadata"]["intent"]
        confidence = nlp_result["metadata"]["confidence"]
        
        # 2. Human-AI Teaming: Clarification
        clarification_needed = await self.human_ai_teaming.clarify_request(user_input, confidence, nlp_result["metadata"])
        if clarification_needed:
            return clarification_needed

        # 3. Reasoning Engine: Formulate a plan/response
        reasoning_context = {
            "nlp_confidence": confidence,
            "user_role": "admin" # Example: could be dynamic based on auth
        }
        reasoning_output = await self.reasoning_engine.reason_on_query(user_input, nlp_result, reasoning_context)
        jarvis_response = reasoning_output["response"]
        
        # 4. Ethical AI: Check and apply guardrails
        is_ethical, violations = await self.ethical_ai_engine.check_response_for_ethics(user_input, jarvis_response, reasoning_output)
        if not is_ethical:
            jarvis_response = await self.ethical_ai_engine.apply_ethical_guardrails(user_input, jarvis_response, violations)
            logger.warning(f"Ethical guardrails applied to response: {jarvis_response}")

        # 5. Self-Correction: Assess and correct if needed
        response_confidence = await self.self_correction_engine.assess_confidence(jarvis_response, {"nlp_confidence": confidence})
        if response_confidence < self.self_correction_engine.confidence_threshold:
            # Simulate searching memory for conflicting info
            historical_context = await self.memory_manager.search_conversations(user_input, limit=3)
            is_inconsistent, inconsistency_explanation = await self.self_correction_engine.detect_inconsistency(jarvis_response, historical_context)
            
            if is_inconsistent:
                logger.warning(f"Inconsistency detected: {inconsistency_explanation}. Attempting self-correction.")
                jarvis_response = await self.self_correction_engine.propose_correction(
                    original_response=jarvis_response,
                    error_explanation=inconsistency_explanation,
                    user_input=user_input,
                    context={"nlp_result": nlp_result, "reasoning_output": reasoning_output}
                )
            else:
                logger.info(f"Response confidence {response_confidence:.2f} is low, but no inconsistency detected. Proceeding.")

        # 6. Human-AI Teaming: Adapt communication style
        jarvis_response = await self.human_ai_teaming.adapt_communication(user_input, jarvis_response, {"user_sentiment": nlp_result["metadata"].get("sentiment_label", "neutral")})

        # 7. Memory Management: Store conversation
        await self.memory_manager.add_conversation(user_input, jarvis_response, nlp_result["metadata"])

        logger.info(f"Final JARVIS response: '{jarvis_response}'")
        return jarvis_response

    async def run_chat_interface(self):
        """Runs the Gradio chat interface."""
        chat_ui = ChatInterface(self).create_interface()
        logger.info("Launching Chat Interface...")
        chat_ui.launch(
            server_name="0.0.0.0",
            server_port=7860, # Default Gradio port
            share=False,
            debug=self.debug_mode
        )

    async def run_admin_dashboard(self):
        """Runs the Gradio admin dashboard."""
        admin_dashboard_ui = create_admin_dashboard(
            self.nlp_engine, self.memory_manager, self.api_integrations,
            self.vision_engine, self.ethical_ai_engine, self.reasoning_engine,
            self.human_ai_teaming, self.self_correction_engine,
            self.self_learning_engine, self.collaboration_hub, self.deployment_manager,
            self.voice_interface
        )
        logger.info("Launching Admin Dashboard...")
        admin_dashboard_ui.launch(
            server_name="0.0.0.0",
            server_port=7862,
            share=False,
            debug=self.debug_mode
        )

    async def run_vision_ui(self):
        """Runs the Gradio video analysis UI."""
        vision_ui = VideoUI(self.vision_engine).create_interface()
        logger.info("Launching Vision UI...")
        vision_ui.launch(
            server_name="0.0.0.0",
            server_port=7861,
            share=False,
            debug=self.debug_mode
        )

    async def run_learning_ui(self):
        """Runs the Gradio feedback and learning UI."""
        learning_ui = FeedbackUI(self.self_learning_engine).create_interface()
        logger.info("Launching Learning UI...")
        learning_ui.launch(
            server_name="0.0.0.0",
            server_port=7863,
            share=False,
            debug=self.debug_mode
        )

async def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant")
    parser.add_argument("--mode", type=str, default="chat",
                        choices=["chat", "admin", "vision", "learning"],
                        help="Mode to run JARVIS AI in (chat, admin, vision, learning)")
    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Setup logging based on config
    setup_logging(debug=config.get("app", {}).get("debug", False))
    logger.info(f"Starting JARVIS AI in {args.mode} mode...")

    # Ensure environment is set up (directories, dummy env vars)
    setup_environment()

    jarvis = JarvisAI(config)

    if args.mode == "chat":
        await jarvis.run_chat_interface()
    elif args.mode == "admin":
        await jarvis.run_admin_dashboard()
    elif args.mode == "vision":
        await jarvis.run_vision_ui()
    elif args.mode == "learning":
        await jarvis.run_learning_ui()
    else:
        logger.error(f"Unknown mode: {args.mode}")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point
Phase 0: Basic setup and initialization
Phase 1: Chat mode implementation
Phase 2: Video learning capabilities
Phase 3: Self-learning and feedback
Phase 4: Voice commands, API integrations, Collaboration Hub, and Deployment Manager
Phase 5: Ethical AI, Advanced Reasoning, Human-AI Teaming, and Self-Correction
"""

import argparse
import asyncio
import sys
from pathlib import Path
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from scripts.setup_environment import load_config, setup_directories
from utils.logger import setup_logging, logger

# Import all core components
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.knowledge_integrator import KnowledgeIntegrator
from core.self_learning import SelfLearningEngine
from core.voice_interface import VoiceInterface
from core.collaboration_hub import CollaborationHub
from core.deployment_manager import DeploymentManager
from core.ethical_ai import EthicalAIEngine
from core.reasoning_engine import ReasoningEngine
from core.human_ai_teaming import HumanAITeaming
from core.self_correction import SelfCorrectionEngine

# Import all interface components
from interface.chat_interface import ChatInterface
from interface.vision.video_ui import VideoUI
from interface.learning.feedback_ui import FeedbackUI
from interface.admin.admin_dashboard import create_admin_dashboard # Import the function

class JarvisAI:
    """
    Main class for the JARVIS AI Assistant, integrating all core components.
    """
    def __init__(self, config: dict):
        self.config = config
        
        # Initialize core components
        self.nlp_engine = NLPEngine(self.config)
        self.memory_manager = MemoryManager(self.config)
        self.api_integrations = APIIntegrations(self.config)
        self.vision_engine = VisionEngine(self.config)
        self.knowledge_integrator = KnowledgeIntegrator(self.config, self.memory_manager)
        self.self_learning_engine = SelfLearningEngine(self.memory_manager, self.config)
        self.voice_interface = VoiceInterface(self.config)
        self.collaboration_hub = CollaborationHub(self.config)
        self.deployment_manager = DeploymentManager(self.config)
        
        # Initialize Phase 5 components
        self.ethical_ai_engine = EthicalAIEngine(self.memory_manager, self.config)
        self.reasoning_engine = ReasoningEngine(
            self.nlp_engine, self.memory_manager, self.api_integrations,
            self.vision_engine, self.ethical_ai_engine, self.config
        )
        self.human_ai_teaming = HumanAITeaming(
            self.nlp_engine, self.memory_manager, self.collaboration_hub, self.config
        )
        self.self_correction_engine = SelfCorrectionEngine(
            self.nlp_engine, self.memory_manager, self.ethical_ai_engine, self.config
        )

        logger.info("JARVIS AI core components initialized.")

    async def chat(self, user_query: str) -> str:
        """
        Processes a user query through the entire JARVIS AI pipeline.
        """
        logger.info(f"User: {user_query}")
        
        context = {"user_id": "test_user", "session_id": "test_session"} # Example context
        
        # 1. NLP Processing
        nlp_result = await self.nlp_engine.process_query(user_query, context)
        jarvis_response_content = nlp_result["content"]
        jarvis_response_metadata = nlp_result["metadata"]
        
        # 2. Reasoning Engine (if enabled)
        if self.config.get("REASONING_ENABLED", False):
            reasoning_output = await self.reasoning_engine.reason_on_query(user_query, context)
            jarvis_response_content = reasoning_output["response"] # Use reasoning's refined response
            logger.debug(f"Reasoning steps: {reasoning_output['reasoning_steps']}")
            logger.debug(f"Final plan: {reasoning_output['final_plan']}")

        # 3. Ethical AI Check
        is_ethical, violations = await self.ethical_ai_engine.check_response_for_ethics(user_query, jarvis_response_content, context)
        if not is_ethical:
            jarvis_response_content = await self.ethical_ai_engine.apply_ethical_guardrails(user_query, jarvis_response_content, violations)
            logger.warning("Ethical guardrails applied to response.")

        # 4. Human-AI Teaming (Clarification/Adaptation)
        clarification_needed = await self.human_ai_teaming.clarify_request(user_query, jarvis_response_metadata, context)
        if clarification_needed:
            jarvis_response_content = clarification_needed
            logger.info("JARVIS seeking clarification.")
        else:
            jarvis_response_content = await self.human_ai_teaming.adapt_communication(user_query, jarvis_response_content, context)
            logger.debug("JARVIS adapted communication style.")

        # 5. Self-Correction (Post-response assessment)
        if self.config.get("SELF_CORRECTION_ENABLED", False):
            confidence = await self.self_correction_engine.assess_confidence(jarvis_response_metadata, context)
            if confidence < self.config.get("CONFIDENCE_THRESHOLD_FOR_CORRECTION", 0.6):
                logger.warning(f"Low confidence ({confidence:.2f}) detected. Triggering self-correction.")
                jarvis_response_content = await self.self_correction_engine.propose_correction(user_query, jarvis_response_content, ["low_confidence"])
            
            # Example of inconsistency check (requires more sophisticated logic)
            # inconsistency_score = await self.self_correction_engine.detect_inconsistency(jarvis_response_content, await self.memory_manager.search_conversations(user_query, limit=5))
            # if inconsistency_score > 0.7:
            #     logger.warning(f"Inconsistency detected ({inconsistency_score:.2f}). Triggering self-correction.")
            #     jarvis_response_content = await self.self_correction_engine.propose_correction(user_query, jarvis_response_content, ["inconsistency"])

        # 6. Store conversation in Memory
        await self.memory_manager.add_conversation(user_query, jarvis_response_content, jarvis_response_metadata)
        
        logger.info(f"JARVIS: {jarvis_response_content}")
        return jarvis_response_content

    async def run_ui(self, mode: str):
        """Runs the appropriate Gradio UI based on the mode."""
        if mode == "chat":
            chat_ui = ChatInterface(self)
            interface = chat_ui.create_interface()
            logger.info("Launching Chat Interface...")
        elif mode == "vision":
            vision_ui = VideoUI(self.vision_engine)
            interface = vision_ui.create_interface()
            logger.info("Launching Video Analysis UI...")
        elif mode == "learning":
            feedback_ui = FeedbackUI(self.self_learning_engine)
            interface = feedback_ui.create_interface()
            logger.info("Launching Self-Learning & Feedback UI...")
        elif mode == "admin":
            # Pass all necessary engine instances to the admin dashboard creator
            interface = create_admin_dashboard(
                self.nlp_engine,
                self.memory_manager,
                self.api_integrations,
                self.vision_engine,
                self.ethical_ai_engine,
                self.reasoning_engine,
                self.human_ai_teaming,
                self.self_correction_engine,
                self.self_learning_engine, # Pass learning engine
                self.collaboration_hub, # Pass collaboration hub
                self.deployment_manager, # Pass deployment manager
                self.voice_interface # Pass voice interface
            )
            logger.info("Launching Admin Dashboard...")
        else:
            logger.error(f"Unknown UI mode: {mode}")
            sys.exit(1)

        interface.launch(
            server_name="0.0.0.0",
            server_port=7860 if mode == "chat" else (7861 if mode == "vision" else (7862 if mode == "admin" else 7863)),
            share=False,
            debug=True
        )

async def main():
    parser = argparse.ArgumentParser(description="JARVIS AI Assistant")
    parser.add_argument("--mode", type=str, default="chat",
                        help="Operation mode: 'chat', 'vision', 'learning', 'admin', or 'test'.")
    parser.add_argument("--test_phase", type=int,
                        help="Specify which phase to test (1-5) if mode is 'test'.")
    
    args = parser.parse_args()

    # Load configuration
    config = load_config()
    
    # Setup logging based on config
    setup_logging(debug=(config.get("LOG_LEVEL", "INFO").upper() == "DEBUG"))
    logger.info(f"Starting JARVIS AI in {args.mode} mode...")

    # Ensure necessary directories exist
    setup_directories(config)

    if args.mode == "test":
        if args.test_phase is None:
            logger.error("Please specify --test_phase (1-5) when using --mode test.")
            sys.exit(1)
        
        if args.test_phase == 1:
            from scripts.test_phase1 import test_phase1
            await test_phase1()
        elif args.test_phase == 2:
            from scripts.test_phase2 import test_phase2
            await test_phase2()
        elif args.test_phase == 3:
            from scripts.test_phase3 import test_phase3
            await test_phase3()
        elif args.test_phase == 4:
            from scripts.test_phase4 import test_phase4
            await test_phase4()
        elif args.test_phase == 5:
            from scripts.test_phase5 import test_phase5
            await test_phase5()
        else:
            logger.error(f"Invalid test phase: {args.test_phase}. Choose between 1 and 5.")
            sys.exit(1)
    else:
        jarvis = JarvisAI(config)
        await jarvis.run_ui(args.mode)

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine

class ReasoningEngine:
    """
    The core reasoning and planning engine for JARVIS AI.
    It takes processed NLP input, consults memory and other engines,
    and formulates a plan to generate a comprehensive response or action.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager,
                 api_integrations: APIIntegrations, vision_engine: VisionEngine,
                 ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.config = config
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.api_integrations = api_integrations
        self.vision_engine = vision_engine
        self.ethical_ai_engine = ethical_ai_engine
        
        self.enabled = config.get("REASONING_ENABLED", True)
        self.planning_depth = config.get("PLANNING_DEPTH", 3) # How many steps ahead JARVIS plans
        self.decision_threshold = config.get("DECISION_THRESHOLD", 0.7) # Confidence threshold for making decisions

        self._total_reasoning_cycles = 0
        self._successful_plans = 0
        self._failed_plans = 0

        if self.enabled:
            logger.info("Reasoning Engine initialized.")
        else:
            logger.warning("Reasoning Engine is disabled in configuration.")

    async def reason_on_query(self, query: str, nlp_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs multi-step reasoning to understand the query, gather information,
        and formulate a plan to generate a response or execute an action.
        """
        if not self.enabled:
            return {"response": "Reasoning engine is disabled.", "reasoning_steps": [], "final_plan": "N/A", "decisions": []}

        self._total_reasoning_cycles += 1
        logger.info(f"Starting reasoning for query: '{query}' (Intent: {nlp_result['metadata']['intent']})")
        
        reasoning_steps: List[str] = []
        decisions: List[Dict[str, Any]] = []
        final_plan: List[str] = []
        response_content = "I am thinking about how to best respond to your request."

        try:
            intent = nlp_result["metadata"]["intent"]
            confidence = nlp_result["metadata"]["confidence"]

            reasoning_steps.append(f"1. Initial NLP intent: {intent} (Confidence: {confidence:.2f})")

            # Step 2: Consult Memory for relevant context/knowledge
            relevant_conversations = await self.memory_manager.search_conversations(query, limit=2)
            relevant_knowledge = await self.memory_manager.search_knowledge(query, limit=2)
            relevant_security_knowledge = await self.memory_manager.search_security_knowledge(query, limit=2)
            
            reasoning_steps.append(f"2. Consulted Memory: Found {len(relevant_conversations)} conversations, {len(relevant_knowledge)} general knowledge, {len(relevant_security_knowledge)} security knowledge.")

            # Step 3: Decision Making based on intent and confidence
            if confidence < self.decision_threshold:
                decisions.append({"type": "clarification_needed", "reason": "Low NLP confidence."})
                response_content = "I'm not entirely confident about my understanding. Could you please provide more details?"
                final_plan.append("Request clarification.")
                self._failed_plans += 1
                return {"response": response_content, "reasoning_steps": reasoning_steps, "final_plan": final_plan, "decisions": decisions}

            if intent == "security_query":
                reasoning_steps.append("3. Intent is 'security_query'. Planning security analysis.")
                final_plan.append("Perform security analysis via API.")
                
                # Simulate identifying target from query or context
                target = context.get("target", "example.com") # Default target
                if "vulnerability" in query.lower():
                    analysis_type = "vulnerability_scan"
                elif "threat" in query.lower():
                    analysis_type = "threat_intelligence"
                else:
                    analysis_type = "general_scan"

                security_results = await self.api_integrations.security_analysis(target, analysis_type)
                reasoning_steps.append(f"4. Executed API: Security analysis for {target} returned {security_results.get('status')}.")
                
                if security_results.get("status") == "completed":
                    vulnerabilities = security_results.get("vulnerabilities_found", 0)
                    response_content = f"Security analysis for {target} completed. Found {vulnerabilities} vulnerabilities."
                    if vulnerabilities > 0:
                        response_content += f" Details: {security_results.get('details', 'N/A')}"
                else:
                    response_content = f"Failed to perform security analysis for {target}: {security_results.get('error', 'Unknown error')}."
                
                decisions.append({"type": "executed_security_analysis", "target": target, "status": security_results.get('status')})

            elif intent == "video_analysis_request":
                reasoning_steps.append("3. Intent is 'video_analysis_request'. Planning video analysis.")
                final_plan.append("Perform video analysis via Vision Engine.")
                
                video_path = context.get("video_path", "data/video_datasets/sample_security_footage.mp4")
                if not Path(video_path).exists():
                    response_content = f"Video file not found at {video_path}. Please provide a valid path."
                    decisions.append({"type": "missing_resource", "resource": "video_file"})
                    self._failed_plans += 1
                else:
                    analysis_results = await self.vision_engine.analyze_video(video_path)
                    reasoning_steps.append(f"4. Executed Vision Engine: Video analysis for {video_path} returned {analysis_results.get('status')}.")
                    
                    if analysis_results.get("status") == "completed":
                        response_content = f"Video analysis of {video_path} completed. Summary: {analysis_results.get('summary')}"
                    else:
                        response_content = f"Failed to analyze video {video_path}: {analysis_results.get('reason', 'Unknown error')}."
                    decisions.append({"type": "executed_video_analysis", "path": video_path, "status": analysis_results.get('status')})

            elif intent == "deployment_request":
                reasoning_steps.append("3. Intent is 'deployment_request'. Planning deployment.")
                final_plan.append("Simulate deployment via Deployment Manager.")
                
                # Mock deployment parameters
                deploy_name = context.get("deploy_name", "my-app")
                deploy_env = context.get("deploy_env", "staging")
                
                deploy_config = await self.api_integrations.create_deployment_config(deploy_name, deploy_env)
                if self.api_integrations.docker_enabled: # Use docker if available
                    deploy_id = await self.api_integrations.deploy_docker_container(deploy_config)
                    deploy_type = "Docker"
                elif self.api_integrations.kubernetes_enabled: # Fallback to k8s
                    deploy_id = await self.api_integrations.deploy_to_kubernetes(deploy_config)
                    deploy_type = "Kubernetes"
                else:
                    deploy_id = None
                    deploy_type = "N/A"

                if deploy_id:
                    response_content = f"Simulated {deploy_type} deployment '{deploy_name}' initiated successfully with ID: {deploy_id}."
                else:
                    response_content = f"Failed to initiate simulated deployment for '{deploy_name}'. Deployment features might be disabled or unavailable."
                decisions.append({"type": "executed_deployment", "name": deploy_name, "id": deploy_id})

            elif intent == "general_query" or intent == "greeting" or intent == "gratitude":
                reasoning_steps.append("3. Intent is general/greeting. Providing direct response.")
                final_plan.append("Provide direct NLP response.")
                response_content = nlp_result["content"] # Use the direct NLP response
                decisions.append({"type": "direct_response"})
            
            else:
                reasoning_steps.append("3. Intent not explicitly handled. Searching memory for best match.")
                final_plan.append("Search memory and synthesize response.")
                
                # Fallback: search all memory types and synthesize
                all_relevant_data = []
                all_relevant_data.extend(await self.memory_manager.search_conversations(query, limit=1))
                all_relevant_data.extend(await self.memory_manager.search_knowledge(query, limit=1))
                all_relevant_data.extend(await self.memory_manager.search_security_knowledge(query, limit=1))

                if all_relevant_data:
                    # Simple synthesis: combine documents
                    combined_content = "Based on my knowledge: " + " ".join([d["document"] for d in all_relevant_data])
                    response_content = combined_content[:500] + "..." if len(combined_content) > 500 else combined_content
                    decisions.append({"type": "synthesized_from_memory", "sources": [d["metadata"]["source"] for d in all_relevant_data]})
                else:
                    response_content = "I don't have enough information to provide a detailed answer to that. Can you rephrase or provide more context?"
                    decisions.append({"type": "insufficient_knowledge"})
                
            self._successful_plans += 1

        except Exception as e:
            self._failed_plans += 1
            logger.error(f"Error during reasoning for query '{query}': {e}")
            response_content = f"An internal reasoning error occurred: {e}"
            decisions.append({"type": "reasoning_error", "error": str(e)})
            final_plan.append("Error handling.")

        logger.info(f"Reasoning completed for query: '{query}'. Final response: '{response_content[:100]}...'")
        return {
            "response": response_content,
            "reasoning_steps": reasoning_steps,
            "final_plan": final_plan,
            "decisions": decisions
        }

    def get_reasoning_stats(self) -> Dict[str, Any]:
        """Returns statistics about the reasoning engine's performance."""
        return {
            "enabled": self.enabled,
            "planning_depth": self.planning_depth,
            "decision_threshold": self.decision_threshold,
            "total_reasoning_cycles": self._total_reasoning_cycles,
            "successful_plans": self._successful_plans,
            "failed_plans": self._failed_plans,
            "last_updated": datetime.now().isoformat()
        }

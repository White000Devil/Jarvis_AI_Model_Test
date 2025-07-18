import asyncio
from typing import Dict, Any, List, Tuple
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine

class ReasoningEngine:
    """
    Enables JARVIS AI to perform complex reasoning, planning, and decision-making.
    Integrates information from NLP, Memory, APIs, and Vision to formulate responses.
    """
    def __init__(self, nlp_engine: NLPEngine, memory_manager: MemoryManager, 
                 api_integrations: APIIntegrations, vision_engine: VisionEngine,
                 ethical_ai_engine: EthicalAIEngine, config: Dict[str, Any]):
        self.nlp_engine = nlp_engine
        self.memory_manager = memory_manager
        self.api_integrations = api_integrations
        self.vision_engine = vision_engine
        self.ethical_ai_engine = ethical_ai_engine
        self.config = config
        self.enabled = config.get("enabled", True)
        self.planning_depth = config.get("planning_depth", 3) # How many steps ahead JARVIS plans
        self.decision_threshold = config.get("decision_threshold", 0.7) # Confidence threshold for making decisions

        if self.enabled:
            logger.info("Reasoning Engine initialized.")
        else:
            logger.info("Reasoning Engine is disabled in configuration.")

    async def reason_on_query(self, user_input: str, nlp_result: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Performs multi-step reasoning to formulate a comprehensive response.
        """
        if not self.enabled:
            return {"response": nlp_result["content"], "reasoning_steps": ["Reasoning engine disabled."], "final_plan": "N/A"}

        logger.info(f"Reasoning on query: '{user_input}' (Intent: {nlp_result['metadata']['intent']})")
        reasoning_steps = []
        final_plan = []
        jarvis_response = "I am processing your request."
        
        intent = nlp_result["metadata"]["intent"]
        entities = nlp_result["metadata"]["entities"]

        # Step 1: Information Gathering
        reasoning_steps.append("Step 1: Information Gathering")
        relevant_knowledge = []
        if intent == "security_query":
            target = next((e["entity"] for e in entities if e["type"] == "URL" or e["type"] == "IP"), None)
            if target:
                security_knowledge = await self.memory_manager.search_security_knowledge(target, limit=3)
                relevant_knowledge.extend(security_knowledge)
                reasoning_steps.append(f"  - Searched security knowledge for '{target}'.")
            else:
                reasoning_steps.append("  - No specific target found for security query. Searching general security knowledge.")
                general_security_knowledge = await self.memory_manager.search_security_knowledge("cybersecurity best practices", limit=2)
                relevant_knowledge.extend(general_security_knowledge)
        elif intent == "weather_query":
            city = next((e["entity"] for e in entities if e["type"] == "GPE"), None) # Geo-Political Entity
            if city:
                weather_data = await self.api_integrations.get_weather(city)
                if weather_data and weather_data.get("status") == "completed":
                    relevant_knowledge.append({"content": f"Weather in {city}: {weather_data['temperature_celsius']}°C, {weather_data['conditions']}", "source": "Weather API"})
                    reasoning_steps.append(f"  - Fetched weather for '{city}' from API.")
                else:
                    reasoning_steps.append(f"  - Failed to fetch weather for '{city}'.")
            else:
                reasoning_steps.append("  - No city found for weather query.")
        
        # Always search general knowledge
        general_knowledge = await self.memory_manager.search_knowledge(user_input, limit=3)
        relevant_knowledge.extend(general_knowledge)
        reasoning_steps.append("  - Searched general knowledge base.")

        # Step 2: Plan Formulation (simplified multi-step planning)
        reasoning_steps.append("Step 2: Plan Formulation")
        plan_confidence = 0.0
        
        if intent == "security_query":
            final_plan.append("Assess existing security knowledge.")
            if target:
                final_plan.append(f"Perform a simulated security scan on {target}.")
                scan_results = await self.api_integrations.security_analysis(target)
                if scan_results and scan_results.get("status") == "completed":
                    jarvis_response = f"Based on my knowledge and a simulated scan of {target}, I found {scan_results['results'].get('vulnerabilities_found', 0)} vulnerabilities. Details: {scan_results['results'].get('severity', 'N/A')} severity. Recommendations: {', '.join(scan_results['results'].get('recommendations', ['N/A']))}"
                    plan_confidence = 0.9
                else:
                    jarvis_response = f"I can provide general security advice, but the simulated scan for {target} encountered an issue. {scan_results.get('reason', '')}"
                    plan_confidence = 0.6
            else:
                jarvis_response = "To secure a small business network against ransomware, I recommend implementing strong backups, regular security awareness training, multi-factor authentication, and endpoint protection. Would you like more details on any of these?"
                plan_confidence = 0.8
            final_plan.append("Provide security recommendations.")
        elif intent == "weather_query" and relevant_knowledge:
            jarvis_response = relevant_knowledge[0]["content"] # Use the fetched weather data
            plan_confidence = 0.9
        elif intent == "learning_query":
            jarvis_response = "I can help you learn! What specific topic are you interested in, or would you like to provide feedback on my performance?"
            plan_confidence = 0.7
        elif intent == "vision_query":
            jarvis_response = "I can analyze images or video streams. Please provide an image path or a stream URL."
            plan_confidence = 0.7
        elif intent == "deployment_query":
            jarvis_response = "I can assist with application deployments. What application and version would you like to deploy, and to which environment?"
            plan_confidence = 0.7
        elif intent == "collaboration_query":
            jarvis_response = "I can facilitate collaboration. Would you like to start a new session or join an existing one?"
            plan_confidence = 0.7
        elif intent == "ethical_ai_query":
            jarvis_response = "Ethical AI ensures that AI systems are fair, transparent, and accountable. I have built-in guardrails to prevent harmful outputs."
            plan_confidence = 0.8
        elif intent == "reasoning_query":
            jarvis_response = "I am designed to reason and plan. Please give me a problem or a goal, and I will try to formulate a solution."
            plan_confidence = 0.8
        elif intent == "self_correction_query":
            jarvis_response = "I can self-correct my responses if I detect inconsistencies or low confidence. How can I help you with this feature?"
            plan_confidence = 0.8
        else:
            # Default response if no specific intent matched or no relevant knowledge
            if relevant_knowledge:
                jarvis_response = f"Based on what I know: {relevant_knowledge[0]['content']}"
                plan_confidence = 0.5
            else:
                jarvis_response = await self.nlp_engine.generate_response(user_input)
                plan_confidence = nlp_result["metadata"]["confidence"] * 0.8 # Lower confidence for generic response
            final_plan.append("Generate a general response.")
        
        reasoning_steps.append(f"  - Formulated plan with confidence: {plan_confidence:.2f}")
        final_plan_str = " -> ".join(final_plan) if final_plan else "No specific plan formulated."
        reasoning_steps.append(f"  - Final Plan: {final_plan_str}")

        # Step 3: Decision Making (if confidence is high enough)
        reasoning_steps.append("Step 3: Decision Making")
        if plan_confidence < self.decision_threshold:
            jarvis_response = f"I'm not entirely confident in my ability to provide a comprehensive answer to that. My confidence score was {plan_confidence:.2f}. Could you provide more details or rephrase your request?"
            reasoning_steps.append("  - Decision: Seek clarification due to low confidence.")
        else:
            reasoning_steps.append("  - Decision: Proceed with the formulated response.")

        logger.info(f"Reasoning complete. Final response: '{jarvis_response[:50]}...'")
        return {
            "response": jarvis_response,
            "reasoning_steps": reasoning_steps,
            "final_plan": final_plan_str,
            "confidence": plan_confidence
        }

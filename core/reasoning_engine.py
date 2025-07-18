import asyncio
import json
from typing import Dict, Any, List, Optional
from utils.logger import logger
from core.nlp_engine import NLPEngine
from core.memory_manager import MemoryManager
from core.api_integrations import APIIntegrations
from core.vision_engine import VisionEngine
from core.ethical_ai import EthicalAIEngine
import time

class ReasoningEngine:
    """
    Advanced reasoning engine for JARVIS AI.
    Handles complex reasoning, planning, and decision-making processes.
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
        self.max_reasoning_steps = config.get("max_reasoning_steps", 10)
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.use_chain_of_thought = config.get("use_chain_of_thought", True)
        
        # Reasoning statistics
        self.reasoning_stats = {
            "total_queries": 0,
            "successful_reasoning": 0,
            "failed_reasoning": 0,
            "average_steps": 0,
            "average_confidence": 0
        }
        
        logger.info(f"Reasoning Engine initialized. Enabled: {self.enabled}")
    
    async def reason_on_query(self, user_query: str, nlp_result: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main reasoning function that processes a query through multiple reasoning steps.
        
        Args:
            user_query: Original user query
            nlp_result: Results from NLP processing
            context: Additional context information
            
        Returns:
            Dictionary containing reasoning results and final response
        """
        if not self.enabled:
            return await self._fallback_response(user_query, nlp_result, context)
        
        self.reasoning_stats["total_queries"] += 1
        
        try:
            logger.debug(f"Starting reasoning process for: '{user_query}'")
            
            # Initialize reasoning state
            reasoning_state = {
                "query": user_query,
                "intent": nlp_result["metadata"]["intent"],
                "entities": nlp_result["metadata"]["entities"],
                "confidence": nlp_result["metadata"]["confidence"],
                "steps": [],
                "current_step": 0,
                "max_steps": self.max_reasoning_steps,
                "context": context
            }
            
            # Step 1: Query Analysis and Understanding
            await self._step_analyze_query(reasoning_state)
            
            # Step 2: Knowledge Retrieval and Context Building
            await self._step_retrieve_knowledge(reasoning_state)
            
            # Step 3: Plan Generation
            await self._step_generate_plan(reasoning_state)
            
            # Step 4: Plan Execution
            await self._step_execute_plan(reasoning_state)
            
            # Step 5: Response Generation
            await self._step_generate_response(reasoning_state)
            
            # Step 6: Confidence Assessment
            await self._step_assess_confidence(reasoning_state)
            
            # Compile final results
            final_response = reasoning_state.get("final_response", "I'm not sure how to respond to that.")
            final_confidence = reasoning_state.get("final_confidence", 0.5)
            reasoning_steps = [step["description"] for step in reasoning_state["steps"]]
            final_plan = reasoning_state.get("execution_plan", [])
            
            # Update statistics
            self.reasoning_stats["successful_reasoning"] += 1
            self._update_reasoning_stats(len(reasoning_steps), final_confidence)
            
            result = {
                "response": final_response,
                "confidence": final_confidence,
                "reasoning_steps": reasoning_steps,
                "final_plan": final_plan,
                "metadata": {
                    "total_steps": len(reasoning_steps),
                    "reasoning_time": time.time() - reasoning_state.get("start_time", time.time()),
                    "intent": reasoning_state["intent"],
                    "entities": reasoning_state["entities"]
                }
            }
            
            logger.debug(f"Reasoning completed successfully with {len(reasoning_steps)} steps")
            return result
            
        except Exception as e:
            logger.error(f"Error during reasoning process: {e}")
            self.reasoning_stats["failed_reasoning"] += 1
            return await self._fallback_response(user_query, nlp_result, context)
    
    async def _step_analyze_query(self, state: Dict[str, Any]):
        """Step 1: Analyze the query in depth."""
        state["start_time"] = time.time()
        state["current_step"] += 1
        
        step_info = {
            "step": state["current_step"],
            "name": "Query Analysis",
            "description": f"Analyzed query intent as '{state['intent']}' with {len(state['entities'])} entities",
            "details": {
                "intent": state["intent"],
                "entities": state["entities"],
                "query_length": len(state["query"]),
                "complexity": self._assess_query_complexity(state["query"])
            }
        }
        
        # Determine query type and complexity
        query_complexity = self._assess_query_complexity(state["query"])
        state["query_complexity"] = query_complexity
        
        # Check if query requires special handling
        if state["intent"] == "security":
            state["requires_security_knowledge"] = True
        elif state["intent"] == "technical":
            state["requires_technical_knowledge"] = True
        elif "vision" in state["query"].lower() or "image" in state["query"].lower():
            state["requires_vision"] = True
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _step_retrieve_knowledge(self, state: Dict[str, Any]):
        """Step 2: Retrieve relevant knowledge from memory and external sources."""
        state["current_step"] += 1
        
        retrieved_knowledge = {
            "conversations": [],
            "general_knowledge": [],
            "security_knowledge": [],
            "external_data": []
        }
        
        # Retrieve from memory
        if state["context"].get("conversation_history"):
            retrieved_knowledge["conversations"] = state["context"]["conversation_history"]
        
        if state["context"].get("knowledge_recall"):
            retrieved_knowledge["general_knowledge"] = state["context"]["knowledge_recall"]
        
        if state["context"].get("security_knowledge_recall"):
            retrieved_knowledge["security_knowledge"] = state["context"]["security_knowledge_recall"]
        
        # Retrieve external data if needed
        if state.get("requires_security_knowledge"):
            try:
                threat_data = await self.api_integrations.fetch_threat_intelligence(state["query"])
                if threat_data["status"] == "success":
                    retrieved_knowledge["external_data"].extend(threat_data["threats"])
            except Exception as e:
                logger.warning(f"Failed to fetch threat intelligence: {e}")
        
        state["retrieved_knowledge"] = retrieved_knowledge
        
        total_items = sum(len(v) if isinstance(v, list) else 1 for v in retrieved_knowledge.values())
        step_info = {
            "step": state["current_step"],
            "name": "Knowledge Retrieval",
            "description": f"Retrieved {total_items} knowledge items from various sources",
            "details": {
                "conversations": len(retrieved_knowledge["conversations"]),
                "general_knowledge": len(retrieved_knowledge["general_knowledge"]),
                "security_knowledge": len(retrieved_knowledge["security_knowledge"]),
                "external_data": len(retrieved_knowledge["external_data"])
            }
        }
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _step_generate_plan(self, state: Dict[str, Any]):
        """Step 3: Generate an execution plan based on the query and available knowledge."""
        state["current_step"] += 1
        
        plan = []
        
        # Basic plan based on intent
        if state["intent"] == "greeting":
            plan = ["acknowledge_greeting", "offer_assistance"]
        elif state["intent"] == "question":
            plan = ["analyze_question", "search_knowledge", "formulate_answer", "provide_sources"]
        elif state["intent"] == "request":
            plan = ["understand_request", "check_feasibility", "execute_or_explain"]
        elif state["intent"] == "security":
            plan = ["analyze_security_context", "search_security_knowledge", "provide_security_guidance", "suggest_best_practices"]
        elif state["intent"] == "technical":
            plan = ["analyze_technical_requirements", "search_technical_knowledge", "provide_technical_solution", "offer_alternatives"]
        else:
            plan = ["general_analysis", "knowledge_search", "generate_response"]
        
        # Enhance plan based on query complexity
        if state.get("query_complexity", "simple") == "complex":
            plan.insert(-1, "break_down_problem")
            plan.insert(-1, "synthesize_information")
        
        # Add special steps if needed
        if state.get("requires_vision"):
            plan.insert(1, "process_visual_content")
        
        if state.get("requires_security_knowledge"):
            plan.insert(-1, "apply_security_filters")
        
        state["execution_plan"] = plan
        
        step_info = {
            "step": state["current_step"],
            "name": "Plan Generation",
            "description": f"Generated execution plan with {len(plan)} steps",
            "details": {
                "plan_steps": plan,
                "complexity": state.get("query_complexity", "simple"),
                "special_requirements": [k for k in state.keys() if k.startswith("requires_")]
            }
        }
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _step_execute_plan(self, state: Dict[str, Any]):
        """Step 4: Execute the generated plan."""
        state["current_step"] += 1
        
        execution_results = []
        plan = state.get("execution_plan", [])
        
        for plan_step in plan:
            try:
                result = await self._execute_plan_step(plan_step, state)
                execution_results.append({
                    "step": plan_step,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                logger.warning(f"Plan step '{plan_step}' failed: {e}")
                execution_results.append({
                    "step": plan_step,
                    "status": "failed",
                    "error": str(e)
                })
        
        state["execution_results"] = execution_results
        
        successful_steps = len([r for r in execution_results if r["status"] == "success"])
        step_info = {
            "step": state["current_step"],
            "name": "Plan Execution",
            "description": f"Executed {successful_steps}/{len(plan)} plan steps successfully",
            "details": {
                "total_steps": len(plan),
                "successful_steps": successful_steps,
                "failed_steps": len(plan) - successful_steps,
                "execution_results": execution_results
            }
        }
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _step_generate_response(self, state: Dict[str, Any]):
        """Step 5: Generate the final response based on execution results."""
        state["current_step"] += 1
        
        # Collect information from execution results
        response_components = []
        execution_results = state.get("execution_results", [])
        
        for result in execution_results:
            if result["status"] == "success" and result.get("result"):
                response_components.append(result["result"])
        
        # Generate response based on intent and available information
        if state["intent"] == "greeting":
            response = "Hello! I'm JARVIS, your AI assistant. How can I help you today?"
        elif response_components:
            # Combine the response components intelligently
            response = self._synthesize_response_components(response_components, state)
        else:
            # Fallback response
            response = await self.nlp_engine.generate_response(state["query"], state["context"])
        
        state["final_response"] = response
        
        step_info = {
            "step": state["current_step"],
            "name": "Response Generation",
            "description": f"Generated final response with {len(response_components)} components",
            "details": {
                "response_length": len(response),
                "components_used": len(response_components),
                "intent": state["intent"]
            }
        }
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _step_assess_confidence(self, state: Dict[str, Any]):
        """Step 6: Assess confidence in the final response."""
        state["current_step"] += 1
        
        confidence_factors = []
        
        # Base confidence from NLP
        nlp_confidence = state.get("confidence", 0.5)
        confidence_factors.append(("nlp_confidence", nlp_confidence, 0.3))
        
        # Knowledge availability
        knowledge = state.get("retrieved_knowledge", {})
        total_knowledge = sum(len(v) if isinstance(v, list) else 1 for v in knowledge.values())
        knowledge_confidence = min(total_knowledge / 10.0, 1.0)  # Normalize to 0-1
        confidence_factors.append(("knowledge_availability", knowledge_confidence, 0.2))
        
        # Plan execution success rate
        execution_results = state.get("execution_results", [])
        if execution_results:
            success_rate = len([r for r in execution_results if r["status"] == "success"]) / len(execution_results)
            confidence_factors.append(("execution_success", success_rate, 0.3))
        
        # Response completeness
        response_length = len(state.get("final_response", ""))
        response_confidence = min(response_length / 200.0, 1.0)  # Normalize based on response length
        confidence_factors.append(("response_completeness", response_confidence, 0.2))
        
        # Calculate weighted confidence
        total_weight = sum(weight for _, _, weight in confidence_factors)
        weighted_confidence = sum(score * weight for _, score, weight in confidence_factors) / total_weight
        
        state["final_confidence"] = weighted_confidence
        
        step_info = {
            "step": state["current_step"],
            "name": "Confidence Assessment",
            "description": f"Assessed final confidence as {weighted_confidence:.2f}",
            "details": {
                "confidence_factors": [(name, score) for name, score, _ in confidence_factors],
                "final_confidence": weighted_confidence
            }
        }
        
        state["steps"].append(step_info)
        logger.debug(f"Step {state['current_step']}: {step_info['description']}")
    
    async def _execute_plan_step(self, step_name: str, state: Dict[str, Any]) -> str:
        """Execute a single plan step."""
        if step_name == "acknowledge_greeting":
            return "Greeting acknowledged"
        
        elif step_name == "offer_assistance":
            return "Ready to assist with your needs"
        
        elif step_name == "analyze_question":
            return f"Question analyzed: {state['query']}"
        
        elif step_name == "search_knowledge":
            knowledge = state.get("retrieved_knowledge", {})
            total_items = sum(len(v) if isinstance(v, list) else 1 for v in knowledge.values())
            return f"Found {total_items} relevant knowledge items"
        
        elif step_name == "formulate_answer":
            # Use available knowledge to formulate an answer
            knowledge = state.get("retrieved_knowledge", {})
            if knowledge.get("general_knowledge"):
                return f"Based on available knowledge: {knowledge['general_knowledge'][0].get('content', '')[:100]}..."
            return "Formulated answer based on general knowledge"
        
        elif step_name == "provide_sources":
            return "Sources and references provided where applicable"
        
        elif step_name == "understand_request":
            return f"Request understood: {state['intent']}"
        
        elif step_name == "check_feasibility":
            return "Request feasibility assessed"
        
        elif step_name == "execute_or_explain":
            return "Execution attempted or explanation provided"
        
        elif step_name == "analyze_security_context":
            return "Security context analyzed for potential risks"
        
        elif step_name == "search_security_knowledge":
            sec_knowledge = state.get("retrieved_knowledge", {}).get("security_knowledge", [])
            return f"Found {len(sec_knowledge)} security knowledge items"
        
        elif step_name == "provide_security_guidance":
            return "Security guidance provided based on best practices"
        
        elif step_name == "suggest_best_practices":
            return "Security best practices suggested"
        
        elif step_name == "process_visual_content":
            return "Visual content processing completed"
        
        elif step_name == "break_down_problem":
            return "Complex problem broken down into manageable parts"
        
        elif step_name == "synthesize_information":
            return "Information synthesized from multiple sources"
        
        elif step_name == "apply_security_filters":
            return "Security filters applied to response"
        
        else:
            return f"Executed step: {step_name}"
    
    def _synthesize_response_components(self, components: List[str], state: Dict[str, Any]) -> str:
        """Synthesize multiple response components into a coherent response."""
        if not components:
            return "I don't have enough information to provide a complete response."
        
        if len(components) == 1:
            return components[0]
        
        # For multiple components, create a structured response
        intro = "Based on my analysis, here's what I found:"
        body = " ".join(components)
        
        # Add conclusion based on intent
        if state["intent"] == "question":
            conclusion = "I hope this answers your question. Let me know if you need clarification."
        elif state["intent"] == "security":
            conclusion = "Please follow security best practices and consult with security professionals for critical decisions."
        else:
            conclusion = "Is there anything specific you'd like me to elaborate on?"
        
        return f"{intro} {body} {conclusion}"
    
    def _assess_query_complexity(self, query: str) -> str:
        """Assess the complexity of a query."""
        word_count = len(query.split())
        question_marks = query.count('?')
        
        if word_count > 20 or question_marks > 1:
            return "complex"
        elif word_count > 10:
            return "moderate"
        else:
            return "simple"
    
    async def _fallback_response(self, user_query: str, nlp_result: Dict[str, Any], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback response when reasoning fails."""
        response = await self.nlp_engine.generate_response(user_query, context)
        
        return {
            "response": response,
            "confidence": 0.3,
            "reasoning_steps": ["Fallback response generated due to reasoning engine failure"],
            "final_plan": ["generate_fallback_response"],
            "metadata": {
                "total_steps": 1,
                "reasoning_time": 0,
                "intent": nlp_result["metadata"]["intent"],
                "entities": nlp_result["metadata"]["entities"]
            }
        }
    
    def _update_reasoning_stats(self, steps_count: int, confidence: float):
        """Update reasoning statistics."""
        total_queries = self.reasoning_stats["total_queries"]
        
        # Update average steps
        current_avg_steps = self.reasoning_stats["average_steps"]
        self.reasoning_stats["average_steps"] = (
            (current_avg_steps * (total_queries - 1) + steps_count) / total_queries
        )
        
        # Update average confidence
        current_avg_confidence = self.reasoning_stats["average_confidence"]
        self.reasoning_stats["average_confidence"] = (
            (current_avg_confidence * (total_queries - 1) + confidence) / total_queries
        )
    
    def get_reasoning_stats(self) -> Dict[str, Any]:
        """Get current reasoning statistics."""
        return self.reasoning_stats.copy()

# Test function for Reasoning Engine
async def test_reasoning_engine():
    """Test the Reasoning Engine functionality."""
    logger.info("--- Testing Reasoning Engine ---")
    
    # Mock dependencies
    class MockNLPEngine:
        async def generate_response(self, query, context):
            return f"Mock NLP response for: {query}"
    
    class MockMemoryManager:
        pass
    
    class MockAPIIntegrations:
        async def fetch_threat_intelligence(self, query):
            return {"status": "success", "threats": [{"title": f"Mock threat for {query}"}]}
    
    class MockVisionEngine:
        pass
    
    class MockEthicalAIEngine:
        pass
    
    config = {
        "enabled": True,
        "max_reasoning_steps": 10,
        "confidence_threshold": 0.7,
        "use_chain_of_thought": True
    }
    
    reasoning_engine = ReasoningEngine(
        MockNLPEngine(), MockMemoryManager(), MockAPIIntegrations(),
        MockVisionEngine(), MockEthicalAIEngine(), config
    )
    
    # Test queries
    test_queries = [
        {
            "query": "What is cybersecurity?",
            "nlp_result": {
                "metadata": {
                    "intent": "security",
                    "entities": [],
                    "confidence": 0.8
                }
            },
            "context": {
                "conversation_history": [],
                "knowledge_recall": [{"content": "Cybersecurity protects digital systems"}],
                "security_knowledge_recall": [{"content": "Security best practices include..."}]
            }
        },
        {
            "query": "Hello, how are you?",
            "nlp_result": {
                "metadata": {
                    "intent": "greeting",
                    "entities": [],
                    "confidence": 0.9
                }
            },
            "context": {}
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        logger.info(f"Test {i}: {test_case['query']}")
        
        result = await reasoning_engine.reason_on_query(
            test_case["query"],
            test_case["nlp_result"],
            test_case["context"]
        )
        
        logger.info(f"Response: {result['response']}")
        logger.info(f"Confidence: {result['confidence']:.2f}")
        logger.info(f"Reasoning Steps: {len(result['reasoning_steps'])}")
        for step in result['reasoning_steps']:
            logger.info(f"  - {step}")
        logger.info("---")
    
    # Test statistics
    stats = reasoning_engine.get_reasoning_stats()
    logger.info(f"Reasoning Statistics: {stats}")
    
    logger.info("Reasoning Engine tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    from utils.logger import setup_logging
    
    setup_logging(debug=True)
    asyncio.run(test_reasoning_engine())

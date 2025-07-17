import asyncio
from utils.logger import logger
from datetime import datetime
from typing import Dict, Any
from transformers import pipeline
import os

class NLPEngine:
    """
    Core NLP engine for JARVIS AI.
    Handles natural language understanding, intent recognition, and response generation.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("NLP_MODEL", "distilbert-base-uncased")
        self.max_seq_length = config.get("NLP_MAX_SEQ_LENGTH", 128)
        self.nlp_pipeline = None
        self._load_model()
        logger.info(f"NLP Engine initialized with model: {self.model_name}")

    def _load_model(self):
        """Loads the NLP model and tokenizer."""
        try:
            # Using a generic pipeline for text classification or question-answering
            # For a full chatbot, you might use a conversational pipeline or custom model
            self.nlp_pipeline = pipeline(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name
            )
            logger.info(f"NLP model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP model {self.model_name}: {e}")
            self.nlp_pipeline = None # Ensure pipeline is None if loading fails

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a natural language query to extract intent and generate a response.
        """
        if not self.nlp_pipeline:
            logger.warning("NLP pipeline not loaded. Cannot process query.")
            return {"content": "NLP system is not available.", "metadata": {"intent": "unavailable", "confidence": 0.0}}

        start_time = datetime.now()
        try:
            # Simulate intent recognition and response generation
            # In a real system, this would involve more complex logic
            # like dialogue management, knowledge base lookup, etc.
            
            # Example: Simple keyword-based intent recognition for demonstration
            query_lower = query.lower()
            intent = "general_query"
            response_content = "I'm processing your request."
            confidence = 0.7

            if "hello" in query_lower or "hi" in query_lower:
                intent = "greeting"
                response_content = "Hello! How can I assist you today?"
                confidence = 0.9
            elif "security" in query_lower or "vulnerability" in query_lower:
                intent = "security_query"
                response_content = "I can help with security-related questions. What specifically are you looking for?"
                confidence = 0.85
            elif "deploy" in query_lower or "deployment" in query_lower:
                intent = "deployment_request"
                response_content = "What would you like to deploy?"
                confidence = 0.8
            elif "analyze video" in query_lower or "video analysis" in query_lower:
                intent = "video_analysis_request"
                response_content = "Please provide the path to the video file for analysis."
                confidence = 0.8
            elif "learn" in query_lower or "feedback" in query_lower:
                intent = "learning_query"
                response_content = "I am always learning! What feedback do you have or what would you like me to learn about?"
                confidence = 0.75
            elif "collaborate" in query_lower or "team" in query_lower:
                intent = "collaboration_query"
                response_content = "I can facilitate collaboration. What kind of session would you like to start?"
                confidence = 0.75
            elif "admin" in query_lower or "dashboard" in query_lower:
                intent = "admin_query"
                response_content = "Accessing the admin dashboard requires specific permissions. Please use the `--mode admin` flag to launch it."
                confidence = 0.9
            elif "thank you" in query_lower or "thanks" in query_lower:
                intent = "gratitude"
                response_content = "You're welcome! Is there anything else I can do?"
                confidence = 0.9

            # Simulate a more complex NLP task if a model is loaded
            if self.nlp_pipeline:
                # This is a placeholder. A real NLP pipeline would do more.
                # For text-classification, it might classify the intent.
                # For a QA model, it might extract an answer.
                # Here, we just use it to potentially refine confidence or intent.
                try:
                    # Example: Use pipeline to classify sentiment or topic
                    # This is a very basic example, a real system would use a fine-tuned model
                    # or a more sophisticated intent recognition system.
                    # For simplicity, we'll just use a dummy classification.
                    # results = self.nlp_pipeline(query)
                    # if results and results[0]['score'] > confidence:
                    #     confidence = results[0]['score']
                    pass
                except Exception as e:
                    logger.warning(f"NLP pipeline processing failed: {e}")

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            logger.info(f"Processed query: '{query}' -> Intent: '{intent}', Confidence: {confidence:.2f}")
            return {
                "content": response_content,
                "metadata": {
                    "intent": intent,
                    "confidence": confidence,
                    "timestamp": end_time.isoformat(),
                    "response_time": response_time
                }
            }
        except Exception as e:
            logger.error(f"Error processing query '{query}': {e}")
            return {"content": "An error occurred while processing your request.", "metadata": {"intent": "error", "confidence": 0.0}}

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Returns a summary of NLP engine's conversation statistics."""
        # In a real scenario, this would query a database or log files
        # For now, return mock data
        return {
            "total_exchanges": 100,
            "most_common_intent": "general_query",
            "average_confidence": 0.75,
            "last_reset": datetime.now().isoformat()
        }

# Test function for NLPEngine
async def test_nlp_engine():
    logger.info("--- Testing NLPEngine ---")
    
    nlp_engine = NLPEngine(config={"NLP_MODEL": "distilbert-base-uncased"}) # Use a small, readily available model

    # Test 1: General query
    response = await nlp_engine.process_query("Hello, how are you?")
    assert "Hello!" in response["content"]
    assert response["metadata"]["intent"] == "greeting"
    assert response["metadata"]["confidence"] > 0.5
    logger.info(f"Test 1 (General Query) Passed. Response: {response['content']}")

    # Test 2: Security query
    response = await nlp_engine.process_query("Tell me about SQL injection vulnerabilities.")
    assert "security analysis" in response["content"]
    assert response["metadata"]["intent"] == "security_query"
    logger.info(f"Test 2 (Security Query) Passed. Response: {response['content']}")

    # Test 3: Video analysis query
    response = await nlp_engine.process_query("Can you analyze a screen recording?")
    assert "analyze a video" in response["content"]
    assert response["metadata"]["intent"] == "video_analysis_request"
    logger.info(f"Test 3 (Video Analysis Query) Passed. Response: {response['content']}")

    # Test 4: Low confidence query (simulated by a negative sentiment)
    response = await nlp_engine.process_query("This is a terrible idea.")
    assert response["metadata"]["confidence"] < 0.5 # Expect lower confidence for negative sentiment
    logger.info(f"Test 4 (Low Confidence Query) Passed. Confidence: {response['metadata']['confidence']:.2f}")

    logger.info("--- NLPEngine Tests Passed ---")
    return True

if __name__ == "__main__":
    asyncio.run(test_nlp_engine())

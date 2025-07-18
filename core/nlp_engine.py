from transformers import pipeline
from typing import Dict, Any, List
from utils.logger import logger
from datetime import datetime # Added for timestamp in metadata

class NLPEngine:
    """
    Handles Natural Language Processing tasks for JARVIS AI.
    Includes text classification, sentiment analysis, entity recognition, and summarization.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "distilbert-base-uncased")
        self.max_seq_length = config.get("max_seq_length", 128)
        
        # Initialize NLP pipelines
        try:
            self.classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            self.ner_recognizer = pipeline("ner", grouped_entities=True)
            self.summarizer = pipeline("summarization")
            logger.info(f"NLP Engine initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}. Please ensure models are downloaded or available.")
            self.classifier = None
            self.ner_recognizer = None
            self.summarizer = None

    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a natural language query to extract intent, entities, and sentiment.
        """
        logger.info(f"Processing NLP query: '{query}'")
        
        intent = "general_query"
        sentiment_label = "neutral"
        sentiment_score = 0.0
        entities = []
        summary = ""

        # Sentiment Analysis
        if self.classifier:
            try:
                sentiment_result = self.classifier(query)[0]
                sentiment_label = sentiment_result['label']
                sentiment_score = sentiment_result['score']
                logger.debug(f"Sentiment: {sentiment_label} (Score: {sentiment_score:.2f})")
            except Exception as e:
                logger.warning(f"Sentiment analysis failed: {e}")

        # Entity Recognition
        if self.ner_recognizer:
            try:
                ner_results = self.ner_recognizer(query)
                entities = [{"entity": ent['word'], "type": ent['entity_group']} for ent in ner_results]
                logger.debug(f"Entities: {entities}")
            except Exception as e:
                logger.warning(f"Entity recognition failed: {e}")

        # Intent Classification (simplified for now, could use a dedicated model)
        # This is a very basic rule-based intent classification.
        # In a real system, you'd train a classification model.
        query_lower = query.lower()
        if any(word in query_lower for word in ["security", "vulnerability", "threat"]):
            intent = "security_query"
        elif any(word in query_lower for word in ["weather", "temperature", "forecast"]):
            intent = "weather_query"
        elif any(word in query_lower for word in ["learn", "teach", "feedback"]):
            intent = "learning_query"
        elif any(word in query_lower for word in ["show", "analyze", "video"]):
            intent = "vision_query"
        elif any(word in query_lower for word in ["deploy", "build", "release"]):
            intent = "deployment_query"
        elif any(word in query_lower for word in ["collaborate", "share", "team"]):
            intent = "collaboration_query"
        elif any(word in query_lower for word in ["ethical", "bias", "fairness"]):
            intent = "ethical_ai_query"
        elif any(word in query_lower for word in ["reason", "plan", "decision"]):
            intent = "reasoning_query"
        elif any(word in query_lower for word in ["correct", "inconsistent", "error"]):
            intent = "self_correction_query"
        elif any(word in query_lower for word in ["hello", "hi", "hey"]):
            intent = "greeting"
        elif any(word in query_lower for word in ["thank", "thanks"]):
            intent = "gratitude"
        
        # Summarization (if query is long enough)
        if self.summarizer and len(query) > 50: # Only summarize longer queries
            try:
                summary_result = self.summarizer(query, max_length=self.max_seq_length, min_length=20, do_sample=False)[0]
                summary = summary_result['summary_text']
                logger.debug(f"Summary: {summary}")
            except Exception as e:
                logger.warning(f"Summarization failed: {e}")

        response = {
            "content": query, # Original query, can be modified by other engines
            "metadata": {
                "intent": intent,
                "confidence": sentiment_score, # Using sentiment score as a proxy for confidence for now
                "sentiment_label": sentiment_label,
                "sentiment_score": sentiment_score,
                "entities": entities,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "context": context if context else {}
            }
        }
        logger.info(f"NLP processing complete. Intent: {intent}, Confidence: {sentiment_score:.2f}")
        return response

    async def generate_response(self, prompt: str, max_length: int = 100) -> str:
        """
        Generates a natural language response based on a prompt.
        This would typically use a more advanced LLM.
        """
        logger.info(f"Generating response for prompt: '{prompt[:50]}...'")
        # Placeholder for a more advanced text generation model (e.g., OpenAI, Hugging Face LLM)
        # For now, a simple rule-based or echo response.
        if "hello" in prompt.lower():
            return "Hello there! How can I assist you today?"
        elif "weather" in prompt.lower():
            return "I can fetch weather information. What city are you interested in?"
        elif "security" in prompt.lower():
            return "I can help with security analysis. What target would you like to scan?"
        elif "thank you" in prompt.lower():
            return "You're welcome! Is there anything else I can do?"
        else:
            return f"I understand you said: '{prompt}'. How can I help further?"

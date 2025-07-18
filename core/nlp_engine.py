from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Any, List, Optional
from utils.logger import logger
import torch
from datetime import datetime # Added for timestamp in metadata
import asyncio

class NLPEngine:
    """
    Manages Natural Language Processing (NLP) capabilities for JARVIS AI.
    Includes intent recognition, entity extraction, summarization, and response generation.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_name = config.get("model_name", "microsoft/DialoGPT-medium")
        self.max_seq_length = config.get("max_seq_length", 128)
        self.max_length = config.get("max_length", 512)
        self.temperature = config.get("temperature", 0.7)
        self.confidence_threshold = config.get("confidence_threshold", 0.6)
        self.use_local_model = config.get("use_local_model", False)
        self.fallback_responses = config.get("fallback_responses", [
            "I'm not sure about that. Could you rephrase your question?",
            "Let me think about that differently. Can you provide more context?",
            "I need more information to give you a proper answer."
        ])
        
        self.sentiment_pipeline = None
        self.ner_pipeline = None
        self.summarization_pipeline = None
        self.qa_pipeline = None # For question answering
        self.tokenizer = None
        self.model = None
        self.sentiment_analyzer = None
        self.intent_classifier = None
        
        logger.info(f"NLP Engine initialized with model: {self.model_name}")
        
    async def initialize_models(self):
        """Initialize NLP models asynchronously."""
        try:
            if self.use_local_model:
                logger.info("Loading local NLP models...")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                
                # Add padding token if it doesn't exist
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    
            # Initialize sentiment analysis
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Initialize NLP pipelines
            # Using 'text-classification' for intent/sentiment
            self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
            # Using 'ner' for entity extraction
            self.ner_pipeline = pipeline("ner", grouped_entities=True)
            # Using 'summarization' for text summarization
            self.summarization_pipeline = pipeline("summarization")
            # Using 'question-answering' for direct QA
            self.qa_pipeline = pipeline("question-answering")

            logger.info("NLP models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            raise
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes a natural language query to extract intent, entities, and other metadata.
        """
        if context is None:
            context = {}

        logger.info(f"Processing query with NLP: '{query}'")
        
        intent = "unknown"
        confidence = 0.0
        entities = []
        summary = ""
        sentiment = {"label": "neutral", "score": 0.5}
        answer = None

        # Simulate async processing
        await asyncio.sleep(0.1) 

        try:
            # Clean and preprocess the query
            cleaned_query = self._preprocess_text(query)
            
            # Extract entities
            entities = self._extract_entities(cleaned_query)
            
            # Classify intent
            intent = self._classify_intent(cleaned_query)
            
            # Analyze sentiment
            sentiment = await self._analyze_sentiment(cleaned_query)
            
            # Generate summary
            summary = self._generate_summary(cleaned_query)
            
            # Calculate confidence
            confidence = self._calculate_confidence(cleaned_query, intent, sentiment)
            
            result = {
                "original_query": query,
                "cleaned_query": cleaned_query,
                "metadata": {
                    "intent": intent,
                    "entities": entities,
                    "sentiment": sentiment,
                    "summary": summary,
                    "confidence": confidence,
                    "length": len(query),
                    "word_count": len(query.split())
                },
                "content": cleaned_query
            }
            
            logger.debug(f"Query processed successfully: {result['metadata']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "original_query": query,
                "cleaned_query": query,
                "metadata": {
                    "intent": "unknown",
                    "entities": [],
                    "sentiment": {"label": "neutral", "score": 0.5},
                    "summary": query[:100],
                    "confidence": 0.0,
                    "length": len(query),
                    "word_count": len(query.split())
                },
                "content": query
            }
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\?\!\,\;\:]', '', text)
        
        return text
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text (simplified implementation)."""
        entities = []
        
        # Simple pattern-based entity extraction
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "url": r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\$$\$$,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "phone": r'\b\d{3}-\d{3}-\d{4}\b|\b$$\d{3}$$\s*\d{3}-\d{4}\b'
        }
        
        for entity_type, pattern in patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "type": entity_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end()
                })
        
        return entities
    
    def _classify_intent(self, text: str) -> str:
        """Classify the intent of the text."""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        return "general_query"
    
    async def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text."""
        try:
            if self.sentiment_analyzer:
                results = self.sentiment_analyzer(text)
                # Get the highest scoring sentiment
                best_result = max(results[0], key=lambda x: x['score'])
                return {
                    "label": best_result['label'].lower(),
                    "score": best_result['score']
                }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
        
        return {"label": "neutral", "score": 0.5}
    
    def _generate_summary(self, text: str) -> str:
        """Generate a summary of the text."""
        # Simple summary: first 100 characters or first sentence
        sentences = text.split('.')
        if sentences and len(sentences[0]) > 0:
            return sentences[0].strip() + ('.' if len(sentences) > 1 else '')
        return text[:100] + ('...' if len(text) > 100 else '')
    
    def _calculate_confidence(self, text: str, intent: str, sentiment: Dict[str, Any]) -> float:
        """Calculate confidence score for the processing."""
        confidence = 0.5  # Base confidence
        
        # Adjust based on text length
        if len(text) > 10:
            confidence += 0.1
        if len(text) > 50:
            confidence += 0.1
            
        # Adjust based on intent clarity
        if intent != "general_query":
            confidence += 0.2
            
        # Adjust based on sentiment confidence
        confidence += sentiment["score"] * 0.2
        
        return min(confidence, 1.0)
    
    async def generate_response(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate a response to a query."""
        if context is None:
            context = {}
            
        try:
            if self.use_local_model and self.model and self.tokenizer:
                # Use local model for generation
                inputs = self.tokenizer.encode(query, return_tensors="pt")
                
                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs,
                        max_length=self.max_length,
                        temperature=self.temperature,
                        do_sample=True,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                
                response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Remove the input query from the response
                response = response[len(query):].strip()
                
                if response:
                    return response
            
            # Fallback to rule-based responses
            return self._generate_fallback_response(query, context)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._generate_fallback_response(query, context)
    
    def _generate_fallback_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate a fallback response when model generation fails."""
        intent = context.get("nlp_intent", "general_query")
        
        responses = {
            "greeting": "Hello! I'm JARVIS, your AI assistant. How can I help you today?",
            "farewell": "Goodbye! Feel free to ask me anything anytime.",
            "security": "I understand you're asking about security. Let me help you with that.",
            "technical": "I see you have a technical question. I'll do my best to assist you.",
            "question": "That's an interesting question. Let me think about that.",
            "request": "I'll help you with that request."
        }
        
        if intent in responses:
            return responses[intent]
        
        # Return a random fallback response
        import random
        return random.choice(self.fallback_responses)

# Test function for NLPEngine
async def test_nlp_engine():
    """Test the NLP Engine functionality."""
    logger.info("--- Testing NLP Engine ---")
    
    config = {
        "model_name": "microsoft/DialoGPT-medium",
        "max_seq_length": 128,
        "max_length": 512,
        "temperature": 0.7,
        "confidence_threshold": 0.6,
        "use_local_model": False
    }
    
    nlp_engine = NLPEngine(config)
    await nlp_engine.initialize_models()
    
    # Test queries
    test_queries = [
        "Hello, how are you?",
        "What is cybersecurity?",
        "Can you help me with programming?",
        "Tell me about machine learning",
        "Goodbye!"
    ]
    
    for query in test_queries:
        result = await nlp_engine.process_query(query)
        response = await nlp_engine.generate_response(query, result["metadata"])
        
        logger.info(f"Query: {query}")
        logger.info(f"Intent: {result['metadata']['intent']}")
        logger.info(f"Sentiment: {result['metadata']['sentiment']}")
        logger.info(f"Confidence: {result['metadata']['confidence']:.2f}")
        logger.info(f"Response: {response}")
        logger.info("---")
    
    logger.info("NLP Engine tests completed successfully!")

if __name__ == "__main__":
    import asyncio
    from utils.logger import setup_logging
    
    setup_logging(debug=True)
    asyncio.run(test_nlp_engine())

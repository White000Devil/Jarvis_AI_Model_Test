import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger
import chromadb
from chromadb.utils import embedding_functions
import tiktoken # For token counting

# Define a simple embedding function for ChromaDB (replace with a real model in production)
class MiniLMEmbeddingFunction(embedding_functions.SentenceTransformerEmbeddingFunction):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        super().__init__(model_name=model_name, device=device)

class MemoryManager:
    """
    Manages JARVIS AI's long-term and short-term memory using ChromaDB.
    Stores conversations, knowledge base articles, security data, and ethical violations.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config.get("CHROMA_DB_PATH", "data/chroma_db"))
        self.embedding_model_name = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model_name
        )
        
        # Collections for different types of memory
        self.conversation_collection = self._get_or_create_collection("conversations")
        self.knowledge_collection = self._get_or_create_collection("general_knowledge")
        self.security_collection = self._get_or_create_collection("security_knowledge")
        self.ethical_violations_collection = self._get_or_create_collection("ethical_violations")
        
        self.tokenizer = tiktoken.get_encoding("cl100k_base") # For token counting
        
        logger.info(f"Memory Manager initialized. ChromaDB at: {self.db_path}")
        logger.info(f"Embedding model: {self.embedding_model_name}")

    def _get_or_create_collection(self, name: str):
        """Helper to get or create a ChromaDB collection."""
        try:
            collection = self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embedding_function # type: ignore
            )
            logger.info(f"ChromaDB collection '{name}' ready. Count: {collection.count()}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get or create ChromaDB collection '{name}': {e}")
            raise

    async def add_conversation(self, user_message: str, jarvis_response: str, metadata: Dict[str, Any]):
        """Adds a conversation turn to memory."""
        try:
            doc_id = f"conv_{datetime.now().timestamp()}"
            document = f"User: {user_message}\nJARVIS: {jarvis_response}"
            
            # Add token count to metadata
            metadata["user_tokens"] = len(self.tokenizer.encode(user_message))
            metadata["jarvis_tokens"] = len(self.tokenizer.encode(jarvis_response))
            metadata["timestamp"] = datetime.now().isoformat()

            self.conversation_collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added conversation to memory: {doc_id}")
        except Exception as e:
            logger.error(f"Error adding conversation to memory: {e}")

    async def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches past conversations relevant to the query."""
        try:
            results = self.conversation_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched conversations for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching conversations: {e}")
            return []

    async def add_knowledge_article(self, title: str, content: str, source: str, tags: List[str] = None):
        """Adds a new knowledge article to memory."""
        try:
            doc_id = f"kb_{datetime.now().timestamp()}"
            metadata = {
                "title": title,
                "source": source,
                "tags": tags if tags else [],
                "timestamp": datetime.now().isoformat(),
                "tokens": len(self.tokenizer.encode(content))
            }
            self.knowledge_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added knowledge article: {title}")
        except Exception as e:
            logger.error(f"Error adding knowledge article '{title}': {e}")

    async def search_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches the general knowledge base."""
        try:
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched knowledge for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching knowledge: {e}")
            return []

    async def add_security_knowledge(self, title: str, content: str, source: str, vulnerability_type: str = "general"):
        """Adds security-specific knowledge to memory."""
        try:
            doc_id = f"sec_{datetime.now().timestamp()}"
            metadata = {
                "title": title,
                "source": source,
                "vulnerability_type": vulnerability_type,
                "timestamp": datetime.now().isoformat(),
                "tokens": len(self.tokenizer.encode(content))
            }
            self.security_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Added security knowledge: {title} from {source}")
        except Exception as e:
            logger.error(f"Error adding security knowledge '{title}': {e}")

    async def search_security_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Searches the security knowledge base."""
        try:
            results = self.security_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            formatted_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched security knowledge for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching security knowledge: {e}")
            return []

    async def add_ethical_violation(self, user_input: str, jarvis_response: str, violation_type: str, severity: str, explanation: str):
        """Logs an ethical violation."""
        try:
            doc_id = f"eth_viol_{datetime.now().timestamp()}"
            document = f"User Input: {user_input}\nJARVIS Response: {jarvis_response}"
            metadata = {
                "violation_type": violation_type,
                "severity": severity,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat(),
                "user_input_tokens": len(self.tokenizer.encode(user_input)),
                "jarvis_response_tokens": len(self.tokenizer.encode(jarvis_response))
            }
            self.ethical_violations_collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.warning(f"Logged ethical violation: {violation_type} (Severity: {severity})")
            # Also log to a file for easier review
            logger.info(json.dumps({"log_type": "ethical_violation", "id": doc_id, **metadata, "document": document}), extra={"log_type": "ethical_violation"})
        except Exception as e:
            logger.error(f"Error logging ethical violation: {e}")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Returns statistics about the memory usage."""
        try:
            stats = {
                "total_items": 0,
                "conversations": {"count": self.conversation_collection.count()},
                "general_knowledge": {"count": self.knowledge_collection.count()},
                "security_knowledge": {"count": self.security_collection.count()},
                "ethical_violations": {"count": self.ethical_violations_collection.count()},
                "last_updated": datetime.now().isoformat()
            }
            stats["total_items"] = sum(col["count"] for col in stats.values() if isinstance(col, dict) and "count" in col)
            return stats
        except Exception as e:
            logger.error(f"Error getting memory stats: {e}")
            return {"error": str(e)}

    async def cleanup_memory(self, collection_name: str = None, older_than_days: int = 30):
        """
        Cleans up old entries from memory.
        If collection_name is None, cleans up all collections.
        """
        # This is a placeholder. ChromaDB doesn't have direct date-based deletion.
        # You'd need to query by metadata timestamp and then delete by ID.
        logger.info(f"Simulating memory cleanup for '{collection_name or 'all collections'}' older than {older_than_days} days.")
        # Example:
        # if collection_name == "conversations":
        #     # Query for old conversations and delete
        #     pass
        return {"status": "cleanup_simulated", "collection": collection_name, "older_than_days": older_than_days}

# Test function for MemoryManager
async def test_memory_manager():
    logger.info("--- Testing MemoryManager ---")
    
    # Use a temporary path for testing ChromaDB
    test_chroma_path = Path("data/test_chroma_db")
    if test_chroma_path.exists():
        import shutil
        shutil.rmtree(test_chroma_path) # Clean up previous test data
    test_chroma_path.mkdir(parents=True, exist_ok=True)

    memory_manager = MemoryManager(config={"CHROMA_DB_PATH": str(test_chroma_path), "EMBEDDING_MODEL": "all-MiniLM-L6-v2"})

    # Test 1: Add conversation
    conv_data = {
        "user_message": "What is SQL injection?",
        "jarvis_response": "SQL injection is a code injection technique...",
        "intent": "security_query",
        "timestamp": datetime.now().isoformat(),
        "response_time": 1.2
    }
    await memory_manager.add_conversation(conv_data["user_message"], conv_data["jarvis_response"], conv_data)
    logger.info("Test 1 (Add Conversation) Passed.")

    # Test 2: Search conversations
    await asyncio.sleep(0.1) # Give ChromaDB a moment
    search_results = await memory_manager.search_conversations("SQL injection")
    assert len(search_results) > 0, "Search conversations failed"
    assert "SQL injection is a code injection technique" in search_results[0]["document"], "Search results content incorrect"
    logger.info(f"Test 2 (Search Conversations) Passed. Found {len(search_results)} results.")

    # Test 3: Add security knowledge
    sec_data = {
        "title": "XSS Vulnerability",
        "description": "Cross-Site Scripting (XSS) is a type of security vulnerability...",
        "vulnerability_type": "XSS",
        "severity": "medium",
        "cve_id": "CVE-2023-1234",
        "source": "OWASP",
        "timestamp": datetime.now().isoformat()
    }
    await memory_manager.add_security_knowledge(sec_data["title"], sec_data["description"], sec_data["source"], sec_data["vulnerability_type"])
    logger.info("Test 3 (Add Security Knowledge) Passed.")

    # Test 4: Search security knowledge
    await asyncio.sleep(0.1) # Give ChromaDB a moment
    search_results = await memory_manager.search_security_knowledge("XSS")
    assert len(search_results) > 0, "Search security knowledge failed"
    assert "Cross-Site Scripting (XSS)" in search_results[0]["document"], "Security knowledge content incorrect"
    logger.info(f"Test 4 (Search Security Knowledge) Passed. Found {len(search_results)} results.")

    # Test 5: Add ethical violation
    ethical_data = {
        "type": "privacy_concern",
        "description": "Detected sensitive data keyword in input.",
        "context": "User asked for SSN.",
        "severity": "warning",
        "user_input": "What is my SSN?",
        "timestamp": datetime.now().isoformat()
    }
    await memory_manager.add_ethical_violation(ethical_data["user_input"], ethical_data["description"], ethical_data["type"], ethical_data["severity"], ethical_data["context"])
    logger.info("Test 5 (Add Ethical Violation) Passed.")

    # Test 6: Get memory stats
    stats = memory_manager.get_memory_stats()
    assert stats["conversations"]["count"] >= 1, "Conversation count incorrect"
    assert stats["security_knowledge"]["count"] >= 1, "Security knowledge count incorrect"
    assert stats["ethical_violations"]["count"] >= 1, "Ethical violations count incorrect"
    assert stats["total_items"] >= 3, "Total items count incorrect"
    logger.info(f"Test 6 (Get Memory Stats) Passed. Stats: {stats}")

    logger.info("--- MemoryManager Tests Passed ---")
    
    # Clean up test data
    import shutil
    shutil.rmtree(test_chroma_path)
    logger.info(f"Cleaned up test ChromaDB at {test_chroma_path}")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_memory_manager())

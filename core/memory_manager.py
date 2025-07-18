import chromadb
from chromadb.utils import embedding_functions
from typing import Dict, Any, List, Optional
from utils.logger import logger
import os
import json
import time

class MemoryManager:
    """
    Manages JARVIS AI's memory, including conversation history, general knowledge,
    and security-specific knowledge using ChromaDB.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = config.get("db_type", "chromadb")
        self.chroma_path = config.get("chroma_path", "data/chroma_db")
        self.embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")

        if self.db_type == "chromadb":
            self.client = chromadb.PersistentClient(path=self.chroma_path)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )
            
            # Get or create collections
            self.conversations_collection = self.client.get_or_create_collection(
                name="conversations", embedding_function=self.embedding_function
            )
            self.knowledge_collection = self.client.get_or_create_collection(
                name="general_knowledge", embedding_function=self.embedding_function
            )
            self.security_knowledge_collection = self.client.get_or_create_collection(
                name="security_knowledge", embedding_function=self.embedding_function
            )
            self.ethical_violations_collection = self.client.get_or_create_collection(
                name="ethical_violations", embedding_function=self.embedding_function
            )
            logger.info(f"ChromaDB Memory Manager initialized at {self.chroma_path}")
        elif self.db_type == "neo4j":
            logger.warning("Neo4j integration is a placeholder. Requires Neo4j setup.")
            # Placeholder for Neo4j client initialization
            self.neo4j_client = None
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def persist_memory(self):
        """
        Ensures ChromaDB data is written to disk.
        For PersistentClient, this is often handled automatically on shutdown,
        but explicit calls can be useful.
        """
        if self.db_type == "chromadb":
            # ChromaDB PersistentClient handles persistence automatically on exit
            # or when the client object is garbage collected.
            # No explicit 'save' method is typically needed.
            logger.info("ChromaDB memory persistence handled automatically by PersistentClient.")
        elif self.db_type == "neo4j":
            logger.info("Neo4j persistence is handled by the Neo4j database itself.")

    async def add_conversation(self, user_message: str, jarvis_response: str, metadata: Dict[str, Any]):
        """
        Adds a conversation turn to memory.
        """
        if self.db_type == "chromadb":
            content = f"User: {user_message}\nJARVIS: {jarvis_response}"
            doc_id = f"conv_{int(time.time() * 1000)}_{len(self.conversations_collection.peek()['ids'])}"
            
            # Ensure metadata is JSON serializable
            safe_metadata = {k: v for k, v in metadata.items() if isinstance(v, (str, int, float, bool, type(None)))}
            safe_metadata["user_message"] = user_message
            safe_metadata["jarvis_response"] = jarvis_response
            safe_metadata["timestamp"] = time.time()

            self.conversations_collection.add(
                documents=[content],
                metadatas=[safe_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added conversation to ChromaDB: {doc_id}")
        elif self.db_type == "neo4j":
            # Placeholder for Neo4j
            logger.info(f"Mock: Added conversation to Neo4j: {user_message} -> {jarvis_response}")

    async def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches conversation history for relevant turns.
        """
        if self.db_type == "chromadb":
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            parsed_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    parsed_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched conversations for '{query}', found {len(parsed_results)} results.")
            return parsed_results
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Searching Neo4j conversations for '{query}'")
            return []
        return []

    async def add_knowledge(self, content: str, metadata: Dict[str, Any]):
        """
        Adds a piece of general knowledge to memory.
        """
        if self.db_type == "chromadb":
            doc_id = f"kb_{int(time.time() * 1000)}_{len(self.knowledge_collection.peek()['ids'])}"
            safe_metadata = {k: v for k, v in metadata.items() if isinstance(v, (str, int, float, bool, type(None)))}
            safe_metadata["timestamp"] = time.time()
            self.knowledge_collection.add(
                documents=[content],
                metadatas=[safe_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added general knowledge to ChromaDB: {doc_id}")
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Added general knowledge to Neo4j: {content[:50]}...")

    async def add_knowledge_article(self, title: str, content: str, source: str, tags: List[str] = None):
        """
        Adds a knowledge article with structured metadata.
        """
        metadata = {
            "title": title,
            "source": source,
            "tags": tags or [],
            "timestamp": time.time()
        }
        await self.add_knowledge(content, metadata)
        logger.debug(f"Added knowledge article: {title}")

    async def search_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Searches general knowledge base for relevant information.
        """
        if self.db_type == "chromadb":
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            parsed_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    parsed_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched general knowledge for '{query}', found {len(parsed_results)} results.")
            return parsed_results
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Searching Neo4j general knowledge for '{query}'")
            return []
        return []

    async def add_security_knowledge(self, content: str, metadata: Dict[str, Any]):
        """
        Adds a piece of security-specific knowledge to memory.
        """
        if self.db_type == "chromadb":
            doc_id = f"sec_kb_{int(time.time() * 1000)}_{len(self.security_knowledge_collection.peek()['ids'])}"
            safe_metadata = {k: v for k, v in metadata.items() if isinstance(v, (str, int, float, bool, type(None)))}
            safe_metadata["timestamp"] = time.time()
            self.security_knowledge_collection.add(
                documents=[content],
                metadatas=[safe_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added security knowledge to ChromaDB: {doc_id}")
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Added security knowledge to Neo4j: {content[:50]}...")

    async def search_security_knowledge(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Searches security-specific knowledge base for relevant information.
        """
        if self.db_type == "chromadb":
            results = self.security_knowledge_collection.query(
                query_texts=[query],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            parsed_results = []
            if results and results['documents']:
                for i in range(len(results['documents'][0])):
                    parsed_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i]
                    })
            logger.debug(f"Searched security knowledge for '{query}', found {len(parsed_results)} results.")
            return parsed_results
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Searching Neo4j security knowledge for '{query}'")
            return []
        return []

    async def add_ethical_violation(self, violation_data: Dict[str, Any]):
        """
        Adds a record of an ethical violation to a dedicated collection.
        """
        if self.db_type == "chromadb":
            content = f"Ethical Violation: {violation_data.get('violations', [])[0].get('description', 'N/A')}"
            doc_id = f"ethical_violation_{int(time.time() * 1000)}_{len(self.ethical_violations_collection.peek()['ids'])}"
            
            # Ensure metadata is JSON serializable
            safe_metadata = {k: v for k, v in violation_data.items() if isinstance(v, (str, int, float, bool, type(None)))}
            safe_metadata["timestamp"] = time.time()
            
            self.ethical_violations_collection.add(
                documents=[content],
                metadatas=[safe_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Added ethical violation to ChromaDB: {doc_id}")
        elif self.db_type == "neo4j":
            logger.info(f"Mock: Added ethical violation to Neo4j: {violation_data.get('violations', [])}")

    def clear_memory(self):
        """
        Clears all data from all ChromaDB collections.
        This action is irreversible.
        """
        if self.db_type == "chromadb":
            logger.warning("Clearing all ChromaDB collections. This action is irreversible.")
            try:
                self.client.delete_collection(name="conversations")
                self.client.delete_collection(name="general_knowledge")
                self.client.delete_collection(name="security_knowledge")
                self.client.delete_collection(name="ethical_violations")
                
                # Re-create empty collections
                self.conversations_collection = self.client.get_or_create_collection(
                    name="conversations", embedding_function=self.embedding_function
                )
                self.knowledge_collection = self.client.get_or_create_collection(
                    name="general_knowledge", embedding_function=self.embedding_function
                )
                self.security_knowledge_collection = self.client.get_or_create_collection(
                    name="security_knowledge", embedding_function=self.embedding_function
                )
                self.ethical_violations_collection = self.client.get_or_create_collection(
                    name="ethical_violations", embedding_function=self.embedding_function
                )
                logger.info("All ChromaDB collections cleared and re-initialized.")
            except Exception as e:
                logger.error(f"Error clearing ChromaDB collections: {e}")
        elif self.db_type == "neo4j":
            logger.warning("Mock: Clearing all Neo4j memory.")
            # Placeholder for Neo4j clear operation

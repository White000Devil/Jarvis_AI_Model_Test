import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from chromadb import Client, Settings
from chromadb.utils import embedding_functions
from utils.logger import logger

class MemoryManager:
    """
    Manages JARVIS AI's long-term and short-term memory using ChromaDB.
    Stores conversations, knowledge articles, and security-specific data.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = config.get("db_type", "chromadb")
        self.chroma_path = config.get("chroma_path", "data/chroma_db")
        self.embedding_model = config.get("embedding_model", "all-MiniLM-L6-v2")

        if self.db_type == "chromadb":
            self.client = Client(Settings(persist_directory=self.chroma_path, anonymized_telemetry=False))
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=self.embedding_model)
            
            # Get or create collections
            self.conversations_collection = self.client.get_or_create_collection(
                name="jarvis_conversations",
                embedding_function=self.embedding_function
            )
            self.knowledge_collection = self.client.get_or_create_collection(
                name="jarvis_knowledge",
                embedding_function=self.embedding_function
            )
            self.security_knowledge_collection = self.client.get_or_create_collection(
                name="jarvis_security_knowledge",
                embedding_function=self.embedding_function
            )
            logger.info(f"ChromaDB Memory Manager initialized at {self.chroma_path}")
        elif self.db_type == "neo4j":
            logger.warning("Neo4j integration is a placeholder. Actual implementation required.")
            # Placeholder for Neo4j connection
            self.neo4j_driver = None # Replace with actual Neo4j driver
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    async def add_conversation(self, user_input: str, jarvis_response: str, metadata: Dict[str, Any]):
        """Adds a conversation turn to memory."""
        if self.db_type == "chromadb":
            doc_id = f"conv_{datetime.now().timestamp()}"
            content = f"User: {user_input}\nJARVIS: {jarvis_response}"
            full_metadata = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "jarvis_response": jarvis_response,
                **metadata
            }
            self.conversations_collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Conversation added: {doc_id}")
        elif self.db_type == "neo4j":
            logger.info("Adding conversation to Neo4j (placeholder).")
            # Neo4j implementation here
        
    async def search_conversations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches past conversations for relevant context."""
        if self.db_type == "chromadb":
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=limit,
                include=["documents", "metadatas", "distances"]
            )
            formatted_results = []
            if results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            logger.debug(f"Searched conversations for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        elif self.db_type == "neo4j":
            logger.info("Searching conversations in Neo4j (placeholder).")
            return []
        return []

    async def add_knowledge_article(self, title: str, content: str, source: str, tags: List[str] = None):
        """Adds a knowledge article to memory."""
        if self.db_type == "chromadb":
            doc_id = f"kb_{datetime.now().timestamp()}"
            full_metadata = {
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "source": source,
                "tags": tags if tags is not None else []
            }
            self.knowledge_collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Knowledge article added: {title}")
        elif self.db_type == "neo4j":
            logger.info("Adding knowledge article to Neo4j (placeholder).")

    async def search_knowledge(self, query: str, limit: int = 5, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Searches general knowledge base."""
        if self.db_type == "chromadb":
            where_clause = {"tags": {"$contains": tag} for tag in tags} if tags else {}
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            formatted_results = []
            if results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            logger.debug(f"Searched knowledge for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        elif self.db_type == "neo4j":
            logger.info("Searching knowledge in Neo4j (placeholder).")
            return []
        return []

    async def add_security_knowledge(self, title: str, content: str, source: str, vulnerability_type: str = "general"):
        """Adds security-specific knowledge to memory."""
        if self.db_type == "chromadb":
            doc_id = f"sec_{datetime.now().timestamp()}"
            full_metadata = {
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "source": source,
                "vulnerability_type": vulnerability_type
            }
            self.security_knowledge_collection.add(
                documents=[content],
                metadatas=[full_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Security knowledge added: {title}")
        elif self.db_type == "neo4j":
            logger.info("Adding security knowledge to Neo4j (placeholder).")

    async def search_security_knowledge(self, query: str, limit: int = 5, vulnerability_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Searches security-specific knowledge base."""
        if self.db_type == "chromadb":
            where_clause = {"vulnerability_type": vulnerability_type} if vulnerability_type else {}
            results = self.security_knowledge_collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            formatted_results = []
            if results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i]
                    })
            logger.debug(f"Searched security knowledge for '{query}', found {len(formatted_results)} results.")
            return formatted_results
        elif self.db_type == "neo4j":
            logger.info("Searching security knowledge in Neo4j (placeholder).")
            return []
        return []

    def persist_memory(self):
        """Persists the ChromaDB client to disk."""
        if self.db_type == "chromadb":
            self.client.persist()
            logger.info(f"ChromaDB persisted to {self.chroma_path}")
        else:
            logger.info("Persistence not applicable or implemented for selected DB type.")

    def clear_memory(self):
        """Clears all data from ChromaDB collections."""
        if self.db_type == "chromadb":
            try:
                self.client.delete_collection(name="jarvis_conversations")
                self.client.delete_collection(name="jarvis_knowledge")
                self.client.delete_collection(name="jarvis_security_knowledge")
                logger.info("All ChromaDB collections cleared.")
            except Exception as e:
                logger.error(f"Error clearing ChromaDB collections: {e}")
        else:
            logger.info("Clear memory not applicable or implemented for selected DB type.")

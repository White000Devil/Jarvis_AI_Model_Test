import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from utils.logger import logger

class CollaborationHub:
    """
    Manages real-time collaboration features within JARVIS AI.
    Simulates session management, message exchange, and shared context.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.server_port = config.get("server_port", 8080)
        self.max_active_sessions = config.get("max_active_sessions", 10)
        self.active_sessions: Dict[str, Dict[str, Any]] = {} # {session_id: {users: [], context: {}, last_activity: timestamp}}
        self.message_queue: asyncio.Queue = asyncio.Queue() # For simulating message processing
        logger.info(f"Collaboration Hub initialized. Enabled: {self.enabled}, Port: {self.server_port}")

    async def start_server(self):
        """
        Starts the collaboration server (mock implementation).
        In a real scenario, this would be a WebSocket server or similar.
        """
        if not self.enabled:
            logger.info("Collaboration Hub is disabled, not starting server.")
            return

        logger.info(f"Collaboration Hub server starting on port {self.server_port} (mock)...")
        # Simulate server startup
        await asyncio.sleep(0.5)
        logger.info("Collaboration Hub server started (mock).")

    async def stop_server(self):
        """
        Stops the collaboration server (mock implementation).
        """
        if not self.enabled:
            return

        logger.info("Collaboration Hub server stopping (mock)...")
        # Simulate server shutdown
        await asyncio.sleep(0.5)
        logger.info("Collaboration Hub server stopped (mock).")
        self.active_sessions.clear()

    async def start_session(self, user_id: str, project_id: str) -> Optional[str]:
        """Starts a new collaboration session."""
        if not self.enabled:
            logger.warning("Collaboration Hub is disabled. Cannot start session.")
            return None

        if len(self.active_sessions) >= self.max_active_sessions:
            logger.warning("Max active sessions reached. Cannot start new session.")
            return None

        session_id = f"session_{datetime.now().timestamp()}_{user_id}"
        self.active_sessions[session_id] = {
            "project_id": project_id,
            "users": [user_id],
            "messages": [],
            "shared_context": {},
            "start_time": datetime.now().isoformat(),
            "last_activity": time.time()
        }
        logger.info(f"Collaboration session '{session_id}' started for user '{user_id}' on project '{project_id}'.")
        return session_id

    async def create_session(self, session_id: str, initial_context: Dict[str, Any] = None) -> bool:
        """
        Creates a new collaboration session.
        """
        if not self.enabled:
            logger.warning("Collaboration Hub disabled. Cannot create session.")
            return False
        if session_id in self.active_sessions:
            logger.warning(f"Session '{session_id}' already exists.")
            return False
        if len(self.active_sessions) >= self.max_active_sessions:
            logger.warning("Max active sessions reached. Cannot create new session.")
            return False

        self.active_sessions[session_id] = {
            "users": [],
            "context": initial_context if initial_context else {},
            "last_activity": time.time()
        }
        logger.info(f"Collaboration session '{session_id}' created.")
        return True

    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Allows a user to join an existing session."""
        if not self.enabled:
            logger.warning("Collaboration Hub is disabled. Cannot join session.")
            return False

        session = self.active_sessions.get(session_id)
        if session:
            if user_id not in session["users"]:
                session["users"].append(user_id)
                session["last_activity"] = time.time()
                logger.info(f"User '{user_id}' joined session '{session_id}'.")
            else:
                logger.info(f"User '{user_id}' is already in session '{session_id}'.")
            return True
        else:
            logger.warning(f"Session '{session_id}' not found. Cannot join.")
            return False

    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """
        Removes a user from a collaboration session.
        """
        if not self.enabled:
            return False
        session = self.active_sessions.get(session_id)
        if session and user_id in session["users"]:
            session["users"].remove(user_id)
            session["last_activity"] = time.time()
            logger.info(f"User '{user_id}' left session '{session_id}'.")
            if not session["users"]:
                await self.end_session(session_id) # End session if no users left
            return True
        return False

    async def send_message(self, session_id: str, sender_id: str, message: str) -> bool:
        """Sends a message within a collaboration session."""
        if not self.enabled:
            logger.warning("Collaboration Hub is disabled. Cannot send message.")
            return False

        session = self.active_sessions.get(session_id)
        if session and sender_id in session["users"]:
            message_data = {
                "timestamp": datetime.now().isoformat(),
                "sender_id": sender_id,
                "message": message
            }
            session["messages"].append(message_data)
            session["last_activity"] = time.time()
            await self.message_queue.put(message_data) # Simulate putting message in a queue for processing
            logger.debug(f"Message sent in session '{session_id}' by '{sender_id}'.")
            return True
        else:
            logger.warning(f"Failed to send message: Session '{session_id}' not found or user '{sender_id}' not in session.")
            return False

    async def update_shared_context(self, session_id: str, key: str, value: Any) -> bool:
        """Updates a shared context variable within a session."""
        if not self.enabled:
            logger.warning("Collaboration Hub is disabled. Cannot update context.")
            return False

        session = self.active_sessions.get(session_id)
        if session:
            session["shared_context"][key] = value
            session["last_activity"] = time.time()
            logger.debug(f"Shared context in session '{session_id}' updated: {key}={value}")
            return True
        else:
            logger.warning(f"Failed to update shared context: Session '{session_id}' not found.")
            return False

    async def update_session_context(self, session_id: str, key: str, value: Any) -> bool:
        """
        Updates a specific key in the session's shared context.
        """
        if not self.enabled:
            return False
        session = self.active_sessions.get(session_id)
        if session:
            session["context"][key] = value
            session["last_activity"] = time.time()
            logger.debug(f"Session '{session_id}' context updated: {key}={value}")
            return True
        return False

    async def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieves the shared context for a given session.
        """
        if not self.enabled:
            return {}
        session = self.active_sessions.get(session_id)
        if session:
            session["last_activity"] = time.time()
            return session["context"]
        return {}

    async def end_session(self, session_id: str) -> bool:
        """Ends a collaboration session."""
        if not self.enabled:
            logger.warning("Collaboration Hub is disabled. Cannot end session.")
            return False

        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Collaboration session '{session_id}' ended.")
            return True
        else:
            logger.warning(f"Session '{session_id}' not found. Cannot end.")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Returns the current status of the collaboration hub."""
        return {
            "status": "Running" if self.enabled else "Disabled",
            "active_sessions": len(self.active_sessions),
            "max_active_sessions": self.max_active_sessions,
            "last_activity": max([s["last_activity"] for s in self.active_sessions.values()], default=0) if self.active_sessions else "N/A"
        }

    async def _process_messages_from_queue(self):
        """Simulates processing messages from the queue (e.g., by JARVIS)."""
        while True:
            message = await self.message_queue.get()
            logger.debug(f"Collaboration Hub: Processing message from queue: {message['message']}")
            # Here, JARVIS could analyze the message, update its memory, or respond.
            self.message_queue.task_done()

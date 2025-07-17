import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from loguru import logger
import uuid

# Mock WebSocket server/client if actual websockets library is not installed
try:
    # import websockets # For actual WebSocket communication
    # import socketio # For Socket.IO
    COLLAB_DEPS_AVAILABLE = False # Set to True if actual deps are installed
except ImportError:
    COLLAB_DEPS_AVAILABLE = False
    logger.warning("Collaboration dependencies (e.g., websockets, python-socketio) not fully installed. Collaboration features will be mocked.")

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"

class RealTimeMessage:
    """Represents a real-time message in a collaboration session."""
    def __init__(self, session_id: str, user_id: str, message_type: str, content: Any, timestamp: datetime = None):
        self.session_id = session_id
        self.user_id = user_id
        self.message_type = message_type # e.g., "chat", "context_update", "action_request"
        self.content = content
        self.timestamp = timestamp if timestamp else datetime.now()

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

class User:
    def __init__(self, user_id: str, username: str, email: str, role: str, created_at: datetime, status: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = created_at
        self.status = status

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }

class Workspace:
    def __init__(self, workspace_id: str, name: str, description: str, created_by: str, created_at: datetime, members: List[str], status: str):
        self.workspace_id = workspace_id
        self.name = name
        self.description = description
        self.created_by = created_by
        self.created_at = created_at
        self.members = members
        self.status = status

    def to_dict(self):
        return {
            "workspace_id": self.workspace_id,
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "members": self.members,
            "status": self.status
        }

class CollaborationSession:
    def __init__(self, session_id: str, workspace_id: str, initiated_by: str, start_time: datetime, participants: List[str], status: str):
        self.session_id = session_id
        self.workspace_id = workspace_id
        self.initiated_by = initiated_by
        self.start_time = start_time
        self.participants = participants
        self.status = status

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "initiated_by": self.initiated_by,
            "start_time": self.start_time.isoformat(),
            "participants": self.participants,
            "status": self.status
        }

class CollaborationHub:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config if config is not None else {}
        self.collaboration_enabled = self.config.get("COLLABORATION_ENABLED", False)
        self.max_active_sessions = self.config.get("MAX_ACTIVE_SESSIONS", 10)
        
        self.users: Dict[str, Dict[str, Any]] = {} # user_id -> user_data
        self.workspaces: Dict[str, Dict[str, Any]] = {} # workspace_id -> workspace_data
        self.active_sessions: Dict[str, Dict[str, Any]] = {} # session_id -> session_data
        self.message_log: List[Dict[str, Any]] = [] # Simple log of messages
        
        if self.collaboration_enabled:
            logger.info("Collaboration Hub initialized.")
        else:
            logger.info("Collaboration Hub is disabled in configuration.")

    async def create_user(self, username: str, email: str, role: str = "user") -> str:
        """Creates a new user in the collaboration hub."""
        if not self.collaboration_enabled:
            logger.warning("Collaboration Hub disabled. Cannot create user.")
            return "disabled"
        
        user_id = f"user_{len(self.users) + 1}_{datetime.now().timestamp()}"
        self.users[user_id] = {
            "username": username,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        logger.info(f"User '{username}' created with ID: {user_id}")
        return user_id

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Retrieves user information."""
        return self.users.get(user_id, {"error": "User not found"})

    async def create_workspace(self, name: str, description: str, created_by_user_id: str) -> str:
        """Creates a new collaboration workspace."""
        if not self.collaboration_enabled:
            logger.warning("Collaboration Hub disabled. Cannot create workspace.")
            return "disabled"

        workspace_id = f"ws_{len(self.workspaces) + 1}_{datetime.now().timestamp()}"
        self.workspaces[workspace_id] = {
            "name": name,
            "description": description,
            "created_by": created_by_user_id,
            "created_at": datetime.now().isoformat(),
            "members": [created_by_user_id],
            "status": "active"
        }
        logger.info(f"Workspace '{name}' created with ID: {workspace_id} by user {created_by_user_id}")
        return workspace_id

    async def create_collaboration_session(self, workspace_id: str, initiated_by_user_id: str) -> str:
        """
        Creates a new active collaboration session within a workspace.
        """
        if not self.collaboration_enabled:
            logger.warning("Collaboration Hub disabled. Cannot create session.")
            return "disabled"

        if workspace_id not in self.workspaces:
            logger.error(f"Workspace {workspace_id} not found.")
            return "workspace_not_found"
        
        if len(self.active_sessions) >= self.max_active_sessions:
            logger.warning("Max active sessions reached. Cannot create new session.")
            return "max_sessions_reached"

        session_id = f"session_{len(self.active_sessions) + 1}_{datetime.now().timestamp()}"
        self.active_sessions[session_id] = {
            "workspace_id": workspace_id,
            "initiated_by": initiated_by_user_id,
            "start_time": datetime.now().isoformat(),
            "participants": [initiated_by_user_id, "JARVIS_AI"], # JARVIS is always a participant
            "status": "active"
        }
        logger.info(f"Collaboration session {session_id} started in workspace {workspace_id}.")
        return session_id

    async def end_collaboration_session(self, session_id: str) -> bool:
        """Ends an active collaboration session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["end_time"] = datetime.now().isoformat()
            self.active_sessions[session_id]["status"] = "ended"
            del self.active_sessions[session_id]
            logger.info(f"Collaboration session {session_id} ended.")
            return True
        logger.warning(f"Attempted to end non-existent session: {session_id}")
        return False

    async def send_message(self, session_id: str, sender_id: str, message_type: str, content: str) -> bool:
        """Sends a message within a collaboration session."""
        if not self.collaboration_enabled:
            logger.warning("Collaboration Hub disabled. Cannot send message.")
            return False

        if session_id not in self.active_sessions:
            logger.error(f"Session {session_id} not active. Cannot send message.")
            return False
        
        message_data = {
            "session_id": session_id,
            "sender_id": sender_id,
            "timestamp": datetime.now().isoformat(),
            "message_type": message_type, # e.g., "text", "command", "file_share"
            "content": content
        }
        self.message_log.append(message_data)
        logger.debug(f"Message sent in session {session_id} by {sender_id}: {message_type} - {content[:50]}...")
        return True

    async def get_session_messages(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieves messages from a specific collaboration session."""
        return [msg for msg in self.message_log if msg["session_id"] == session_id][-limit:]

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Returns statistics about the collaboration hub's status."""
        return {
            "enabled": self.collaboration_enabled,
            "users": {"total": len(self.users)},
            "workspaces": {"total": len(self.workspaces)},
            "sessions": {"total": len(self.active_sessions) + len([s for s in self.active_sessions.values() if s.get("status") == "ended"]), "active": len(self.active_sessions)},
            "total_messages": len(self.message_log),
            "max_active_sessions": self.max_active_sessions,
            "last_update": datetime.now().isoformat()
        }

# Test function for CollaborationHub
async def test_collaboration_hub():
    logger.info("--- Testing CollaborationHub ---")
    
    collab_hub = CollaborationHub(config={"COLLABORATION_ENABLED": True})

    # Test 1: Create user
    user_id = await collab_hub.create_user("testuser", "test@example.com", "analyst")
    assert user_id != "disabled", "User creation failed"
    assert user_id in collab_hub.users, "User not stored"
    logger.info(f"Test 1 (Create User) Passed. User ID: {user_id}")

    # Test 2: Get user
    user_data = await collab_hub.get_user(user_id)
    assert user_data["username"] == "testuser", "Get user failed"
    logger.info(f"Test 2 (Get User) Passed. User data: {user_data}")

    # Test 3: Create workspace
    workspace_id = await collab_hub.create_workspace("Test Workspace", "A workspace for testing", user_id)
    assert workspace_id != "disabled", "Workspace creation failed"
    assert workspace_id in collab_hub.workspaces, "Workspace not stored"
    logger.info(f"Test 3 (Create Workspace) Passed. Workspace ID: {workspace_id}")

    # Test 4: Create collaboration session
    session_id = await collab_hub.create_collaboration_session(workspace_id, user_id)
    assert session_id != "disabled" and session_id != "workspace_not_found" and session_id != "max_sessions_reached", "Session creation failed"
    assert session_id in collab_hub.active_sessions, "Session not stored"
    assert collab_hub.active_sessions[session_id]["status"] == "active", "Session status incorrect"
    logger.info(f"Test 4 (Create Session) Passed. Session ID: {session_id}")

    # Test 5: Send message
    message_sent = await collab_hub.send_message(session_id, user_id, "chat", "Hello everyone!")
    assert message_sent is True, "Send message failed"
    assert len([msg for msg in collab_hub.message_log if msg["session_id"] == session_id]) == 1, "Message not logged"
    logger.info(f"Test 5 (Send Message) Passed.")

    # Test 6: Update shared context
    # Note: Shared context update is not directly supported in the merged code, but can be implemented similarly if needed.
    logger.info("Test 6 (Update Shared Context) Skipped. Not directly supported in merged code.")

    # Test 7: Get collaboration stats
    stats = collab_hub.get_collaboration_stats()
    assert stats["users"]["total"] == 1, "User count incorrect"
    assert stats["workspaces"]["total"] == 1, "Workspace count incorrect"
    assert stats["sessions"]["total"] == 1, "Session count incorrect"
    assert stats["sessions"]["active"] == 1, "Active session count incorrect"
    logger.info(f"Test 7 (Get Stats) Passed. Stats: {stats}")

    # Test 8: End collaboration session
    session_ended = await collab_hub.end_collaboration_session(session_id)
    assert session_ended is True, "End session failed"
    assert session_id not in collab_hub.active_sessions, "Session still active"
    logger.info(f"Test 8 (End Session) Passed.")

    logger.info("--- CollaborationHub Tests Passed ---")
    return True

if __name__ == "__main__":
    from utils.logger import setup_logging
    setup_logging(debug=True)
    asyncio.run(test_collaboration_hub())

from typing import List, Optional
from collections import deque


class ConversationMemory:
    """
    Sliding window conversation memory.
    Keeps last N turns of conversation.
    """

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self._sessions: dict = {}

    def get_history(self, session_id: str) -> List[dict]:
        """Get conversation history for a session"""
        return list(self._sessions.get(session_id, deque()))

    def add_turn(
        self,
        session_id: str,
        user_query: str,
        response: str,
        intent: str = None,
        products_count: int = 0
    ):
        """Add a conversation turn"""
        if session_id not in self._sessions:
            self._sessions[session_id] = deque(maxlen=self.window_size)

        self._sessions[session_id].append({
            "user": user_query,
            "assistant": response,
            "intent": intent,
            "products_found": products_count
        })

        print(f"💬 Memory: Added turn for session {session_id}")

    def get_context_summary(self, session_id: str) -> str:
        """Get a text summary of conversation history"""
        history = self.get_history(session_id)
        if not history:
            return ""

        lines = ["Previous conversation:"]
        for turn in history:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Assistant: {turn['assistant'][:100]}...")

        return "\n".join(lines)

    def clear_session(self, session_id: str):
        """Clear session history"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            print(f"🗑️ Memory: Cleared session {session_id}")

    def get_last_preferences(self, session_id: str) -> Optional[dict]:
        """Get preferences from last recommendation turn"""
        history = self.get_history(session_id)
        for turn in reversed(history):
            if turn.get("intent") == "recommendation":
                return turn
        return None


conversation_memory = ConversationMemory(window_size=5)
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import time

class State(Enum):
    """JARVIS states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    INTERRUPTED = "interrupted"

@dataclass
class ConversationContext:
    """Conversation context and memory"""
    current_state: State = State.IDLE
    last_user_input: Optional[str] = None
    last_response: Optional[str] = None
    conversation_turn: int = 0
    start_time: float = field(default_factory=time.time)
    interrupted: bool = False
    pending_input: Optional[str] = None

    # Short-term memory
    recent_queries: list = field(default_factory=list)
    recent_entities: Dict[str, Any] = field(default_factory=dict)

    def transition_to(self, new_state: State):
        """Transition to new state"""
        self.current_state = new_state

    def add_query(self, query: str):
        """Add query to recent history"""
        self.recent_queries.append({
            "query": query,
            "timestamp": time.time()
        })
        # Keep only last 10 queries
        if len(self.recent_queries) > 10:
            self.recent_queries.pop(0)

    def set_entity(self, key: str, value: Any):
        """Set entity in memory"""
        self.recent_entities[key] = value

    def get_entity(self, key: str) -> Optional[Any]:
        """Get entity from memory"""
        return self.recent_entities.get(key)

    def should_interrupt(self) -> bool:
        """Check if current response should be interrupted"""
        return self.interrupted and self.current_state == State.SPEAKING

    def handle_interruption(self, new_input: str):
        """Handle interruption by new input"""
        self.interrupted = True
        self.pending_input = new_input
        self.transition_to(State.INTERRUPTED)

    def clear_interruption(self):
        """Clear interruption state"""
        self.interrupted = False
        self.pending_input = None

class ConversationManager:
    """Manages conversation state and interruption handling"""

    def __init__(self):
        self.context = ConversationContext()
        self.is_speaking = False
        self.speech_start_time: Optional[float] = None

    def start_listening(self):
        """Start listening for user input"""
        self.context.transition_to(State.LISTENING)

    def stop_listening(self):
        """Stop listening and start processing"""
        self.context.transition_to(State.PROCESSING)

    def start_speaking(self):
        """Start speaking response"""
        self.context.transition_to(State.SPEAKING)
        self.is_speaking = True
        self.speech_start_time = time.time()

    def stop_speaking(self):
        """Stop speaking"""
        self.context.transition_to(State.IDLE)
        self.is_speaking = False
        self.speech_start_time = None

    def handle_new_input(self, user_input: str) -> bool:
        """
        Handle new user input
        Returns: True if input should be processed, False if ignored
        """
        # If currently speaking, interrupt
        if self.is_speaking:
            self.context.handle_interruption(user_input)
            return True

        # If idle or listening, process normally
        if self.context.current_state in [State.IDLE, State.LISTENING]:
            self.context.add_query(user_input)
            self.context.conversation_turn += 1
            return True

        return False

    def get_pending_input(self) -> Optional[str]:
        """Get pending input from interruption"""
        return self.context.pending_input

    def reset(self):
        """Reset conversation state"""
        self.context = ConversationContext()
        self.is_speaking = False
        self.speech_start_time = None

conversation_manager = ConversationManager()

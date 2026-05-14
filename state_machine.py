import threading
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


class JarvisState(Enum):
    IDLE = "idle"                         
    LISTENING = "listening"                
    WAKE = "wake"                    
    VOICE_VERIFICATION = "voice_verification" 
    ACTIVE_LISTENING = "active_listening"   
    PROCESSING = "processing"               
    RESPONDING = "responding"          
    INTERRUPTING = "interrupting"        


class IntentType(Enum):
    INTERRUPT = "interrupt"      # Stop what you're doing (stop, wait, jarvis)
    COMMAND = "command"         
    QUESTION = "question"       
    MEMORY = "memory"            
    NOISE = "noise"              
    WAKE_WORD = "wake_word"      


class Priority(Enum):
    NOISE = 0                    # Ignore
    QUESTION = 1                 # Send to AI
    COMMAND = 2                  # Execute system command
    INTERRUPT = 3                # Stop everything immediately


#  STATE CONTEXT

@dataclass
class InputContext:
    raw_text: str                           
    cleaned_text: str             
    intent: IntentType           ]
    priority: Priority            
    timestamp: float            
    is_verified: bool = False
    user_name: str = "User"                ]
    confidence: float = 1.0                


@dataclass
class StateContext:
    """Tracks JARVIS state and context"""
    current_state: JarvisState              
    previous_state: JarvisState            
    is_speaking: bool = False                
    user_active: bool = False             
    voice_verified: bool = False             
    session_start: float = 0
    last_response: str = ""                 
    response_history: list = None            
    
    def __post_init__(self):
        if self.response_history is None:
            self.response_history = []



class StateMachine:
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Current state
        self.state = StateContext(
            current_state=JarvisState.IDLE,
            previous_state=JarvisState.IDLE,
            session_start=datetime.now().timestamp()
        )
        
        # Current input being processed
        self.current_input = None
        
        # State transition callbacks
        self._callbacks = {}
        
    
    def get_state(self) -> JarvisState:
        """Get current state (thread-safe)"""
        with self._lock:
            return self.state.current_state
    
    def is_speaking(self) -> bool:
        """Check if JARVIS is currently speaking (thread-safe)"""
        with self._lock:
            return self.state.is_speaking
    
    def is_verified(self) -> bool:
        """Check if user is voice-verified (thread-safe)"""
        with self._lock:
            return self.state.voice_verified
    
    def is_active(self) -> bool:
        """Check if system is active (thread-safe)"""
        with self._lock:
            return self.state.user_active
    
    def get_context(self) -> StateContext:
        """Get full state context (thread-safe)"""
        with self._lock:
            return self.state
    
    #  STATE TRANSITIONS
    
    def transition_to(self, new_state: JarvisState, reason: str = ""):
        """
        Transition to new state with validation.
        
        Args:
            new_state: Target state
            reason: Human-readable reason for transition
        """
        with self._lock:
            old_state = self.state.current_state
            
            # Validate transition
            if not self._is_valid_transition(old_state, new_state):
                print(f"⚠️ Invalid transition: {old_state.value} -> {new_state.value}")
                return False
            
            self.state.previous_state = old_state
            self.state.current_state = new_state
            
            print(f"🔄 STATE: {old_state.value} → {new_state.value} ({reason})")
            
            # Call registered callbacks
            self._trigger_callbacks(new_state)
            
            return True
    
    def _is_valid_transition(self, from_state: JarvisState, to_state: JarvisState) -> bool:
        """Define valid state transitions"""
        valid_transitions = {
            JarvisState.IDLE: [JarvisState.LISTENING],
            JarvisState.LISTENING: [JarvisState.WAKE, JarvisState.IDLE],
            JarvisState.WAKE: [JarvisState.VOICE_VERIFICATION, JarvisState.LISTENING],
            JarvisState.VOICE_VERIFICATION: [JarvisState.ACTIVE_LISTENING, JarvisState.LISTENING],
            JarvisState.ACTIVE_LISTENING: [JarvisState.PROCESSING, JarvisState.LISTENING],
            JarvisState.PROCESSING: [JarvisState.RESPONDING, JarvisState.LISTENING],
            JarvisState.RESPONDING: [JarvisState.ACTIVE_LISTENING, JarvisState.LISTENING, JarvisState.IDLE],
            JarvisState.INTERRUPTING: [JarvisState.ACTIVE_LISTENING, JarvisState.LISTENING],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def _trigger_callbacks(self, new_state: JarvisState):
        """Execute registered callbacks for state change"""
        if new_state in self._callbacks:
            for callback in self._callbacks[new_state]:
                try:
                    callback()
                except Exception as e:
                    print(f"Callback error: {e}")
    
    def on_state_enter(self, state: JarvisState, callback):
        """Register callback when entering state"""
        if state not in self._callbacks:
            self._callbacks[state] = []
        self._callbacks[state].append(callback)
    

    def set_speaking(self, is_speaking: bool):
        """Update speaking state (thread-safe)"""
        with self._lock:
            self.state.is_speaking = is_speaking
            if is_speaking:
                print(" Speaking started")
            else:
                print(" Speaking ended")
    

    def set_verified(self, verified: bool, user_name: str = "User"):
        """Update verification state (thread-safe)"""
        with self._lock:
            self.state.voice_verified = verified
            self.state.user_name = user_name
            self.state.user_active = verified
            if verified:
                print(f" Voice verified: {user_name}")
            else:
                print(f" Voice verification failed")
    
    
    def record_response(self, response: str):
        """Record response for anti-loop detection (thread-safe)"""
        with self._lock:
            self.state.last_response = response
            
            # Keep last 10 responses
            self.state.response_history.append({
                'text': response,
                'timestamp': datetime.now().timestamp()
            })
            if len(self.state.response_history) > 10:
                self.state.response_history.pop(0)
    
    def get_response_history(self) -> list:
        """Get response history (thread-safe)"""
        with self._lock:
            return self.state.response_history.copy()
    
    #  DIAGNOSTICS
    
    def get_status(self) -> str:
        """Get human-readable status"""
        with self._lock:
            status = f"""
╔═══════════════════════════════════════════════════════════╗
║             JARVIS STATE MACHINE STATUS               ║
╠═══════════════════════════════════════════════════════════╣
║ State:          {self.state.current_state.value:40} ║
║ Speaking:       {str(self.state.is_speaking):40} ║
║ Verified:       {str(self.state.voice_verified):40} ║
║ Active:         {str(self.state.user_active):40} ║
║ User:           {self.state.user_name:40} ║
║ Last Response:  {self.state.last_response[:40]:40} ║

            """
            return status



_global_state_machine = None


def get_state_machine() -> StateMachine:
    """Get or create global state machine"""
    global _global_state_machine
    if _global_state_machine is None:
        _global_state_machine = StateMachine()
    return _global_state_machine


def reset_state_machine():
    """Reset state machine (for testing)"""
    global _global_state_machine
    _global_state_machine = StateMachine()

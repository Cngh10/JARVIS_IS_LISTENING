"""
🤖 IRON MAN LEVEL VALIDATION & INTENT DETECTION
Ensures Jarvis only processes meaningful input with intelligent priority system.

Features:
- Input validation (3+ words, no garbage)
- Intent classification (interrupt, command, question, memory, noise)
- Priority system (INTERRUPT > COMMAND > QUESTION > NOISE)
- Anti-loop detection (prevent repeated responses)
- Wake word and context awareness
"""

import re
import threading
from datetime import datetime, timedelta

# 🔒 THREAD SAFETY
VALIDATION_LOCK = threading.Lock()
RESPONSE_HISTORY = []
LAST_RESPONSES_TIMESTAMP = {}  # Track time of last similar responses

# 🗑️ GARBAGE PATTERNS - What NOT to process
GARBAGE_PATTERNS = [
    r"^\d[\s\d]*$",           # Only numbers: "1 2 3 4"
    r"^([a-z]\s+)+$",         # Single letters: "a b c"
    r"(.)\1{3,}",             # Repeated chars: "aaaa"
    r"^test[\s\d]*$",         # Test phrases
    r"^hello[\s\w]*hello",    # Repeated greetings
    r"^\s*$",                 # Only whitespace
]

# 🎙️ WAKE WORDS - Activate the system
WAKE_WORDS = ["jarvis", "hey jarvis", "okay jarvis"]

# 🛑 INTERRUPT KEYWORDS - Can stop Jarvis while speaking
INTERRUPT_KEYWORDS = ["stop", "wait", "hold on", "quiet", "shush", "silence"]

# 🟢 COMMAND KEYWORDS - Execute system actions
COMMAND_KEYWORDS = [
    "open", "launch", "start", "play", "search",
    "volume", "mute", "unmute", "brightness",
    "shutdown", "restart", "sleep",
    "whatsapp", "message", "call", "email",
    "take", "screenshot", "photo"
]

# 🤔 QUESTION KEYWORDS - Send to AI
QUESTION_KEYWORDS = [
    "what", "why", "how", "explain", "tell me", "describe",
    "what's", "what is", "who", "where", "when", "which",
    "can you", "could you", "would you", "should", "is it",
    "does", "do you", "information", "meaning", "definition"
]

# 💾 MEMORY KEYWORDS
MEMORY_KEYWORDS_REMEMBER = ["remember", "save", "store", "note"]
MEMORY_KEYWORDS_RECALL = ["recall", "what is my", "remind me"]

# 🔁 COMMON LOOP RESPONSES - Avoid repeating these
LOOP_PATTERNS = [
    "how can i assist",
    "how can i help",
    "tell me more",
    "is there anything else",
    "what else",
    "i can help you with",
    "what would you like",
    "ask me anything",
]

# 🧹 JUNK PHRASES - Always filter
JUNK_PHRASES = [
    "thanks for watching", "subscribe", "uh", "um", "hmm",
    "yeah okay", "bye bye", "see you", "next time",
    "welcome back", "thanks", "goodbye",
    "that's all", "the end", "thanks for watching",
    "hit the bell", "like and subscribe"
]


# ═══════════════════════════════════════════════════════════════════════════
# ✅ INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def is_valid_input(text):
    """
    ✅ INPUT VALIDATOR (Iron Man Level)
    
    Rules:
    1. Not empty
    2. At least 2 words for greetings (hello jarvis)
    3. At least 3 words for commands/questions
    4. Not garbage/junk patterns
    5. Not repeated junk phrases
    
    Returns: bool (True if valid, False if should be ignored)
    """
    if not text or not text.strip():
        return False
    
    text_lower = text.lower().strip()
    words = text_lower.split()
    
    # Allow 2-word greetings like "hello jarvis"
    is_greeting = any(g in text_lower for g in ["hello", "hi", "hey"])
    if is_greeting and len(words) >= 2:
        pass  # Allow greetings with 2+ words
    elif len(words) < 3:
        return False  # Require 3+ words for non-greetings
    
    # Check for garbage patterns
    for pattern in GARBAGE_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    
    # Filter known junk phrases
    for junk in JUNK_PHRASES:
        if junk in text_lower:
            return False
    
    return True


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 INTENT CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

def classify_intent(text):
    """
    🎯 CLASSIFY INPUT INTENT (Iron Man Level)
    
    Determines what to do with the input:
    1. INTERRUPT - Stop what we're doing (stop, wait, etc)
    2. WAKE_WORD - Activate system (jarvis)
    3. COMMAND - Execute action (open chrome, play music)
    4. QUESTION - Send to AI (what is, why does)
    5. MEMORY - Remember/recall (remember X, what is my Y)
    6. NOISE - Ignore (background noise, garbage)
    
    Returns: tuple (intent_type: str, priority: int)
    - priority: 3=INTERRUPT, 2=COMMAND, 1=QUESTION, 0=NOISE
    """
    if not text:
        return "noise", 0
    
    text_lower = text.lower().strip()
    
    # Priority 3: INTERRUPT - Immediate action
    if any(kw in text_lower for kw in INTERRUPT_KEYWORDS):
        return "interrupt", 3
    
    # Priority HIGH: WAKE WORD
    if any(kw in text_lower for kw in WAKE_WORDS):
        return "wake_word", 3.5
    
    # Priority 2: COMMAND - Execute instantly
    if any(kw in text_lower for kw in COMMAND_KEYWORDS):
        return "command", 2
    
    # Priority 1.5: MEMORY - Store/retrieve info
    if any(kw in text_lower for kw in MEMORY_KEYWORDS_REMEMBER):
        return "memory_remember", 1.5
    if any(kw in text_lower for kw in MEMORY_KEYWORDS_RECALL):
        return "memory_recall", 1.5
    
    # Priority 1: QUESTION - Send to AI
    if is_question(text_lower):
        return "question", 1
    
    # Priority 0: NOISE - Ignore
    return "noise", 0


def get_response_priority(intent_type: str) -> int:
    """
    Get priority level for intent type.
    Higher = process faster
    """
    priorities = {
        "interrupt": 3,           # HIGHEST - Stop immediately
        "wake_word": 3,
        "command": 2,             # HIGH - Execute now
        "memory_remember": 1.5,   # MEDIUM - Store
        "memory_recall": 1.5,
        "question": 1,            # NORMAL - Send to AI
        "noise": 0,               # LOWEST - Ignore
    }
    return priorities.get(intent_type, 0)


# ═══════════════════════════════════════════════════════════════════════════
# 🤔 QUESTION DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def is_question(text):
    """
    🤔 QUESTION DETECTOR
    
    Detects if input is a question (should trigger AI).
    
    Returns: bool
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    
    # Check for question keywords
    for keyword in QUESTION_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check for question mark
    if "?" in text:
        return True
    
    # Accept long, complex sentences (proper input)
    words = text_lower.split()
    if len(text) >= 20 and len(words) >= 4:
        return True
    
    return False


# ═══════════════════════════════════════════════════════════════════════════
# 🛑 INTERRUPT DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def should_interrupt(text, currently_speaking=True):
    """
    🛑 INTERRUPT DETECTOR (Iron Man Level)
    
    Only allow interruption with specific keywords:
    - "stop"
    - "wait"
    - "hold on"
    - "quiet"
    - "jarvis" (wake word - special priority)
    
    Args:
        text: User input
        currently_speaking: Is Jarvis currently speaking?
    
    Returns: bool (True if should interrupt)
    """
    if not currently_speaking or not text:
        return False
    
    text_lower = text.lower().strip()
    
    for keyword in INTERRUPT_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Wake word can interrupt too
    if "jarvis" in text_lower:
        return True
    
    return False


def is_wake_word(text):
    """
    🔑 WAKE WORD DETECTION
    
    Returns: bool (True if wake word detected)
    """
    if not text:
        return False
    
    text_lower = text.lower().strip()
    return any(kw in text_lower for kw in WAKE_WORDS)


# ═══════════════════════════════════════════════════════════════════════════
# 🔁 ANTI-LOOP DETECTION
# ═══════════════════════════════════════════════════════════════════════════

def is_repeated_response(new_response):
    """
    🔁 ANTI-LOOP DETECTOR (Iron Man Level)
    
    Checks if new response is too similar to recent responses.
    Prevents: "How can I assist?" spam, repeated patterns.
    
    Args:
        new_response: New response to check
    
    Returns: bool (True if should skip speaking due to repetition)
    """
    if not new_response:
        return False
    
    new_response_lower = new_response.lower().strip()
    
    with VALIDATION_LOCK:
        # Check against recent history
        for past_response in RESPONSE_HISTORY[-3:]:
            if similarity_score(new_response_lower, past_response) > 0.7:
                print("🔁 LOOP DETECTED: Similar response in history")
                return True
        
        # Check for common loop patterns
        for pattern in LOOP_PATTERNS:
            if pattern in new_response_lower:
                print(f"🔁 LOOP PATTERN DETECTED: '{pattern}'")
                return True
    
    return False


def record_response(response):
    """Record AI response to prevent loops (thread-safe)."""
    if not response:
        return
    
    with VALIDATION_LOCK:
        RESPONSE_HISTORY.append(response.lower().strip())
        # Keep last 5 responses for comparison
        if len(RESPONSE_HISTORY) > 5:
            RESPONSE_HISTORY.pop(0)
        
        print(f"📝 Response recorded (history size: {len(RESPONSE_HISTORY)})")


def similarity_score(text1, text2):
    """
    Calculate similarity between two texts (0.0 to 1.0).
    Uses simple word overlap (Jaccard similarity).
    
    Args:
        text1, text2: Texts to compare
    
    Returns: float (0.0 = no similarity, 1.0 = identical)
    """
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def should_speak_response(response):
    """
    🎤 SHOULD SPEAK CHECK
    
    Determines if response should be spoken (not a loop).
    
    Args:
        response: AI response text
    
    Returns: bool (True if should speak, False if should skip)
    """
    return not is_repeated_response(response)


# ═══════════════════════════════════════════════════════════════════════════
# 🧹 RESPONSE CLEANING
# ═══════════════════════════════════════════════════════════════════════════

def clean_response(response):
    """
    🧹 CLEAN RESPONSE MODE (Iron Man Level)
    
    Prepares response for speaking:
    - Remove unnecessary follow-up questions
    - Avoid "How can I help?"
    - Keep responses short but complete
    - Remove excessive politeness
    - Good for speaking (not too long)
    
    Args:
        response: Raw AI response
    
    Returns: str (cleaned response suitable for speaking)
    """
    if not response:
        return response
    
    response = response.strip()
    
    # Remove common unnecessary suffixes FIRST
    unnecessary_suffixes = [
        "how can i help you further?",
        "how can i help you?",
        "how can i help?",
        "is there anything else i can help with?",
        "is there anything else?",
        "can i assist you with anything else?",
        "is that helpful?",
        "let me know if you need more",
        "feel free to ask if you have more questions",
        "hope this helps!",
        "hope that answers your question!",
        "thanks for your question.",
        "thanks for asking.",
    ]
    
    response_lower = response.lower()
    for suffix in unnecessary_suffixes:
        if suffix in response_lower:
            # Find and remove the suffix
            idx = response_lower.rfind(suffix)
            if idx != -1:
                response = response[:idx].strip()
                break
    
    # Remove excessive politeness markers
    politeness_markers = [
        "thanks for asking",
        "i appreciate the question",
        "that's a great question",
    ]
    
    for marker in politeness_markers:
        response = response.replace(marker, "")
    
    # Clean up extra spaces
    response = " ".join(response.split())
    
    # For speaking: aim for 2-4 sentences max (good balance)
    sentences = [s.strip() for s in response.split(".") if s.strip()]
    
    if len(sentences) > 4:
        # Keep first 3-4 sentences
        response = ". ".join(sentences[:4]) + "."
    
    return response.strip()


# ═══════════════════════════════════════════════════════════════════════════
# 🎯 PRIORITY GETTER
# ═══════════════════════════════════════════════════════════════════════════

def get_response_priority(text):
    """
    🎯 GET RESPONSE PRIORITY (Iron Man Level)
    
    Determines handling priority:
    - "interrupt" → Stop immediately
    - "command" → Execute system command
    - "question" → Send to AI
    - "ignore" → Discard input
    
    Returns: str (priority level)
    """
    if not text:
        return "ignore"
    
    if not is_valid_input(text):
        return "ignore"
    
    if should_interrupt(text, currently_speaking=True):
        return "interrupt"
    
    if is_question(text):
        return "question"
    
    return "ignore"


def should_interrupt(text, currently_speaking=True):
    """
    🛑 INTERRUPT DETECTOR
    
    Only allow interruption with specific keywords:
    - "stop"
    - "jarvis"
    - "wait"
    - "hold on"
    - "quiet"
    
    Returns: bool
    """
    if not currently_speaking or not text:
        return False
    
    text_lower = text.lower().strip()
    
    for keyword in INTERRUPT_KEYWORDS:
        if keyword in text_lower:
            return True
    
    return False


def is_repeated_response(new_response):
    """
    🔁 ANTI-LOOP DETECTOR
    
    Checks if new response is too similar to recent responses.
    Prevents: "How can I assist?" spam, etc.
    
    Returns: bool (True if should skip speaking)
    """
    if not new_response:
        return False
    
    new_response_lower = new_response.lower().strip()
    
    with VALIDATION_LOCK:
        # Check against recent history
        for past_response in RESPONSE_HISTORY[-3:]:
            if similarity_score(new_response_lower, past_response) > 0.7:
                print("🔁 LOOP DETECTED: Similar response in history")
                return True
        
        # Check for common loop patterns
        for pattern in LOOP_PATTERNS:
            if pattern in new_response_lower:
                print(f"🔁 LOOP PATTERN: '{pattern}' detected in response")
                return True
    
    return False


def record_response(response):
    """Record AI response to prevent loops."""
    with VALIDATION_LOCK:
        RESPONSE_HISTORY.append(response.lower().strip())
        # Keep last 5 responses
        if len(RESPONSE_HISTORY) > 5:
            RESPONSE_HISTORY.pop(0)


def similarity_score(text1, text2):
    """
    Calculate similarity between two texts (0.0 to 1.0).
    Simple word overlap method.
    """
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def get_response_priority(text):
    """
    🎯 PRIORITY SYSTEM
    
    Returns priority level:
    - "interrupt" (stop, jarvis, wait)
    - "command" (system commands)
    - "question" (what, why, how, explain)
    - "ignore" (garbage, noise, invalid)
    """
    if not text:
        return "ignore"
    
    if not is_valid_input(text):
        return "ignore"
    
    if should_interrupt(text):
        return "interrupt"
    
    # Commands will be checked separately in main.py
    # This is just for AI queries
    if is_question(text):
        return "question"
    
    return "ignore"


def clean_response(response):
    """
    🧹 CLEAN RESPONSE MODE
    
    - Remove unnecessary follow-up questions
    - Avoid "How can I help?"
    - Keep responses short and direct
    """
    if not response:
        return response
    
    # Remove common unnecessary suffixes
    unnecessary = [
        "how can i help you further?",
        "is there anything else?",
        "can i assist you with anything else?",
        "is that helpful?",
        "let me know if you need more.",
    ]
    
    response_lower = response.lower()
    for phrase in unnecessary:
        if response_lower.endswith(phrase):
            # Remove the last sentence
            sentences = response.rsplit(".", 1)
            if len(sentences) > 1:
                response = sentences[0].strip() + "."
    
    return response.strip()

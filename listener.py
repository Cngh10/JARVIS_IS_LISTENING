from voice import listen, LAST_SPOKEN_TIME, SPEECH_COOLDOWN
from validation import is_valid_input
import threading
import time

# 🔒 THREAD SAFETY
LISTENER_LOCK = threading.Lock()
LATEST_INPUT = ""
LAST_INPUT_TIME = 0

# 🎙️ DEBOUNCE: Ignore rapid updates (e.g., same input within 300ms)
DEBOUNCE_MS = 600


def get_latest_input():
    """Thread-safe: Get latest input."""
    with LISTENER_LOCK:
        return LATEST_INPUT


def set_latest_input(text):
    """
    Thread-safe: Set latest input with debouncing and PHASE 20 validation.
    
    Filters:
    - Empty input
    - Garbage/junk phrases  
    - Input with < 3 words
    - Rapid duplicate inputs
    
    Returns: bool (True if accepted, False if filtered)
    """
    global LATEST_INPUT, LAST_INPUT_TIME

    current_time = time.time()
    
    # 🔥 PHASE 20: Validate input before processing
    if not is_valid_input(text):
        return False  # Filtered as garbage
    
    with LISTENER_LOCK:
        # 🔥 DEBOUNCE: Don't update if same text within 300ms
        if text == LATEST_INPUT and (current_time - LAST_INPUT_TIME) < (DEBOUNCE_MS / 1000):
            return False  # Ignored due to debounce

        LATEST_INPUT = text
        LAST_INPUT_TIME = current_time
        return True  # Updated


def clear_latest_input():
    """Clear the latest input."""
    global LATEST_INPUT
    with LISTENER_LOCK:
        LATEST_INPUT = ""


def start_listener():
    """
    🎙️ PHASE 20: Background listener thread with smart filtering.
    
    Continuously captures audio and updates LATEST_INPUT with:
    - Validation (3+ words, not garbage)
    - Debouncing (300ms min interval)
    - Self-speech filtering (via voice.py)
    """
    print("🎤 Listener started with PHASE 20 filtering")

    while True:
        try:
            # If we're within the assistant's post-speech cooldown, skip listening
            try:
                if LAST_SPOKEN_TIME and (time.time() - LAST_SPOKEN_TIME) < SPEECH_COOLDOWN:
                    # small sleep to yield
                    time.sleep(0.05)
                    continue
            except Exception:
                pass

            text = listen()

            if text:
                # Only log if actually updated (not debounced)
                if set_latest_input(text):
                    print(f"📥 Valid input accepted: {text[:50]}")
                # else: silently ignore if validation fails or debounced

            time.sleep(0.05)  # Small sleep to prevent CPU spin

        except Exception as e:
            print(f"Listener error: {e}")
            time.sleep(1)
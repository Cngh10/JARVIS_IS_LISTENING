import requests
import threading
import time
from validation import record_response, is_repeated_response, clean_response, should_speak_response

# 🔒 THREAD SAFETY
AI_LOCK = threading.Lock()
AI_RESPONSE = None
AI_READY_EVENT = threading.Event()  # Signals when response is ready
AI_BUSY = False

# 🧠 CHAT HISTORY
CHAT_HISTORY = []

# 🔁 ANTI-LOOP: Track last response to prevent repetition
LAST_AI_RESPONSE = None


def ask_ai_async(prompt):
    """
    🤖 ASYNC AI REQUEST (Iron Man Level)
    
    Send prompt to Ollama asynchronously.
    Uses threading.Event() for proper synchronization.
    
    Features:
    - Non-blocking execution
    - 30-second timeout
    - Thread-safe response storage
    - Error handling with fallback
    
    Args:
        prompt: Question for AI
    """
    global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

    with AI_LOCK:
        AI_RESPONSE = None
        AI_BUSY = True
        AI_READY_EVENT.clear()  # Reset event before starting

    def run():
        global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

        try:
            print("🤖 Asking AI...", prompt[:50])

            # 🔥 CRITICAL: Set timeout for request
            res = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi",
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7
                },
                timeout=30
            )

            if res.status_code != 200:
                raise Exception(f"Ollama returned {res.status_code}")

            data = res.json()
            response = data.get("response", "").strip()

            if not response:
                response = "I couldn't generate a response."

            with AI_LOCK:
                AI_RESPONSE = response

            print("✅ AI RESPONSE READY:", response[:100])

        except requests.exceptions.Timeout:
            print("❌ AI TIMEOUT (Ollama not responding)")
            with AI_LOCK:
                AI_RESPONSE = None  # None = timeout

        except requests.exceptions.ConnectionError:
            print("❌ AI CONNECTION ERROR")
            with AI_LOCK:
                AI_RESPONSE = None

        except Exception as e:
            print("❌ AI ERROR:", str(e))
            with AI_LOCK:
                AI_RESPONSE = None

        finally:
            # 🔥 ALWAYS signal that response is ready (even if error)
            AI_READY_EVENT.set()

            with AI_LOCK:
                AI_BUSY = False

    # Start thread as daemon so it doesn't block shutdown
    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def get_ai_response():
    """Get the current AI response (thread-safe)."""
    with AI_LOCK:
        return AI_RESPONSE


def wait_for_ai_response(timeout=10):
    """
    ⏱️ WAIT FOR AI RESPONSE WITH TIMEOUT (Iron Man Level)
    
    Blocks until AI responds or timeout occurs.
    
    Args:
        timeout: Maximum seconds to wait (default 10s)
    
    Returns:
        str: AI response, or None if timeout
        
    Behavior:
    - If response arrives before timeout → return response
    - If timeout occurs → return None (timeout message will be used)
    """
    # Wait for signal with timeout
    if AI_READY_EVENT.wait(timeout=timeout):
        # Response ready
        with AI_LOCK:
            return AI_RESPONSE
    else:
        # Timeout occurred
        print(f"⏱️ AI TIMEOUT: Waited {timeout}s, no response")
        with AI_LOCK:
            AI_RESPONSE = None
            AI_BUSY = False
        return None


def is_ai_busy():
    """Check if AI is still processing."""
    with AI_LOCK:
        return AI_BUSY


def process_response(response):
    """
    🧹 PROCESS AI RESPONSE (Iron Man Level)
    
    Prepares response for output:
    - Cleans unnecessary text
    - Removes follow-up questions
    - Records for anti-loop detection
    
    Args:
        response: Raw AI response
    
    Returns:
        str: Cleaned response
    """
    if not response:
        return ""
    
    # Clean response (remove unnecessary suffixes)
    cleaned = clean_response(response)
    
    # Record for anti-loop detection
    record_response(cleaned)
    
    return cleaned


def add_to_history(user_input, ai_response):
    """Add exchange to conversation history (thread-safe)."""
    with AI_LOCK:
        CHAT_HISTORY.append({
            'user': user_input,
            'ai': ai_response,
            'timestamp': time.time()
        })
        
        # Keep last 20 exchanges
        if len(CHAT_HISTORY) > 20:
            CHAT_HISTORY.pop(0)


def wait_for_ai_response(timeout=10):
    """
    ⏱ PHASE 20: Wait for AI response with 10-second timeout.
    
    If AI doesn't respond within 10 seconds:
    → Return timeout message: "I am having trouble thinking right now."
    
    Returns response or None if timeout.
    """
    # Wait for response to be ready (with timeout)
    is_ready = AI_READY_EVENT.wait(timeout=timeout)

    if not is_ready:
        print("❌ AI TIMEOUT: No response within", timeout, "seconds")
        print("   🎙️ Will respond: 'I am having trouble thinking right now.'")
        return None

    return get_ai_response()


def add_to_history(user, ai):
    """Add conversation to history."""
    with AI_LOCK:
        CHAT_HISTORY.append((user, ai))
        if len(CHAT_HISTORY) > 10:
            CHAT_HISTORY.pop(0)


def get_history():
    """Get chat history."""
    with AI_LOCK:
        return list(CHAT_HISTORY)


def should_speak_response(response):
    """
    🔁 PHASE 20: Anti-loop system
    
    Check if response should be spoken or skipped.
    - Skip if response is too similar to recent responses
    - Skip if it's a common loop pattern
    
    Returns: bool (True = speak, False = skip)
    """
    if not response:
        return False
    
    if is_repeated_response(response):
        print("🔁 SKIPPING: Response is too similar to recent output")
        return False
    
    return True


def process_response(response):
    """
    🧹 PHASE 20: Clean and validate AI response
    
    - Remove unnecessary follow-up questions
    - Record response for anti-loop detection
    - Return clean response
    """
    if not response:
        return response
    
    # Clean response (remove unnecessary follow-ups)
    cleaned = clean_response(response)
    
    # Record for anti-loop detection
    record_response(cleaned)
    
    return cleaned
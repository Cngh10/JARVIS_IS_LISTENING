import requests
import threading
import time
from validation import record_response, is_repeated_response, clean_response, should_speak_response

AI_LOCK = threading.Lock()
AI_RESPONSE = None
AI_READY_EVENT = threading.Event()  # Signals when response is ready
AI_BUSY = False

CHAT_HISTORY = []

LAST_AI_RESPONSE = None


def ask_ai_async(prompt):

    global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

    with AI_LOCK:
        AI_RESPONSE = None
        AI_BUSY = True
        AI_READY_EVENT.clear()  
    def run():
        global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

        try:
            print("Asking AI...", prompt[:50])

            # Set timeout for request
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

            print("AI RESPONSE READY:", response[:100])

        except requests.exceptions.Timeout:
            print("AI TIMEOUT (Ollama not responding)")
            with AI_LOCK:
                AI_RESPONSE = None  

        except requests.exceptions.ConnectionError:
            print(" AI CONNECTION ERROR")
            with AI_LOCK:
                AI_RESPONSE = None

        except Exception as e:
            print("AI ERROR:", str(e))
            with AI_LOCK:
                AI_RESPONSE = None

        finally:
            AI_READY_EVENT.set()

            with AI_LOCK:
                AI_BUSY = False

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def get_ai_response():
    with AI_LOCK:
        return AI_RESPONSE


def wait_for_ai_response(timeout=10):
    
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
    with AI_LOCK:
        return AI_BUSY


def process_response(response):
    if not response:
        return ""
    
    # Clean response
    cleaned = clean_response(response)
    
    # Record for anti-loop detection
    record_response(cleaned)
    
    return cleaned


def add_to_history(user_input, ai_response):
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
   
    is_ready = AI_READY_EVENT.wait(timeout=timeout)

    if not is_ready:
        print("AI TIMEOUT: No response within", timeout, "seconds")
        print(" Will respond: 'I am having trouble thinking right now.'")
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
    if not response:
        return False
    
    if is_repeated_response(response):
        print("SKIPPING: Response is too similar to recent output")
        return False
    
    return True


def process_response(response):
    if not response:
        return response
    cleaned = clean_response(response)
    
    record_response(cleaned)
    return cleaned

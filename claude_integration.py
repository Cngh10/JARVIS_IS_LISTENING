#claude AI Integration

import anthropic
import threading
import time
from typing import Optional, List, Dict, Any

AI_LOCK = threading.Lock()
AI_RESPONSE = None
AI_READY_EVENT = threading.Event()
AI_BUSY = False

CHAT_HISTORY = []
MAX_HISTORY = 10

JARVIS_SYSTEM_PROMPT = """You are Jarvis, an advanced real-time AI assistant, designed to operate as a highly intelligent, responsive, and interruptible voice-based system that assists the user seamlessly in a conversational and task-oriented manner.

Your primary objective is to listen, understand, and respond accurately while maintaining a natural, human-like interaction flow.

BEHAVIOR RULES:
1. Only respond when a clear and meaningful user query is detected
2. Avoid unnecessary or random outputs caused by noise or incomplete input
3. Process user speech in real-time, showing awareness of partial input but only generating a final response after the user finishes speaking
4. Your responses should be concise, intelligent, and context-aware
5. Avoid generic or repetitive phrases like "As an AI model" or "I'm an AI"
6. Support full interruption handling: if the user speaks while you are responding, immediately stop your current output
7. Prioritize clarity, usefulness, and speed
8. Maintain a confident and slightly futuristic tone
9. Differentiate between system commands (like opening apps, sending messages, controlling system functions) and informational queries
10. Execute commands instantly and answer questions thoughtfully
11. Maintain short-term conversational memory to preserve context
12. Avoid hallucinations when context is unclear—ask for clarification instead
13. Ignore background noise, meaningless phrases, or low-confidence input
14. Act as a proactive but controlled assistant: assist when asked, suggest improvements when relevant, but never overwhelm the user

Your ultimate behavior should feel like a real-time operating system assistant—precise, interruptible, adaptive, and always focused on the user's intent.

RESPONSE STYLE:
- Keep responses concise (under 100 words when possible)
- Use natural, conversational language
- Be direct and helpful
- Avoid unnecessary pleasantries or follow-up questions
- Match the user's tone (formal for serious queries, casual for casual ones)
- Use technical terms when appropriate, but explain when needed"""

class ClaudeEngine:

    def __init__(self, api_key: Optional[str] = None):
        
        self.api_key = api_key
        self.client = None
        self.model = "claude-3-5-sonnet-20241022"
        self._initialize()

    def _initialize(self):
        try:
            import os
            key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not key:
                print("ANTHROPIC_API_KEY not set - Claude integration disabled")
                return

            self.client = anthropic.Anthropic(api_key=key)
            print("Claude engine initialized")
        except Exception as e:
            print(f"Claude initialization failed: {e}")

    def is_available(self) -> bool:
        """Check if Claude is available"""
        return self.client is not None

    def ask_async(self, prompt: str, timeout: int = 30):
        global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

        if not self.is_available():
            print("Claude not available")
            with AI_LOCK:
                AI_READY_EVENT.set()
                AI_BUSY = False
            return

        with AI_LOCK:
            AI_RESPONSE = None
            AI_BUSY = True
            AI_READY_EVENT.clear()

        def run():
            global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

            try:
                print(f" Asking Claude: {prompt[:50]}...")

                # Prepare messages with history
                messages = []
                for entry in CHAT_HISTORY[-5:]:  # Last 5 exchanges
                    messages.append({"role": "user", "content": entry['user']})
                    messages.append({"role": "assistant", "content": entry['ai']})

                messages.append({"role": "user", "content": prompt})

                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=JARVIS_SYSTEM_PROMPT,
                    messages=messages
                )

                ai_text = response.content[0].text

                with AI_LOCK:
                    AI_RESPONSE = ai_text

                print(f"Claude responded: {ai_text[:80]}...")

            except anthropic.APITimeoutError:
                print(" Claude request timeout")
                with AI_LOCK:
                    AI_RESPONSE = None

            except anthropic.APIError as e:
                print(f" Claude API error: {e}")
                with AI_LOCK:
                    AI_RESPONSE = None

            except Exception as e:
                print(f" Claude error: {e}")
                with AI_LOCK:
                    AI_RESPONSE = None

            finally:
                AI_READY_EVENT.set()
                with AI_LOCK:
                    AI_BUSY = False

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def wait_for_response(self, timeout: int = 10) -> Optional[str]:
   
        if AI_READY_EVENT.wait(timeout=timeout):
            with AI_LOCK:
                return AI_RESPONSE
        else:
            print(f"⏱️ Claude timeout after {timeout}s")
            with AI_LOCK:
                AI_RESPONSE = None
                AI_BUSY = False
            return None

    def add_to_history(self, user_input: str, ai_response: str):
        global CHAT_HISTORY

        with AI_LOCK:
            CHAT_HISTORY.append({
                'user': user_input,
                'ai': ai_response,
                'timestamp': time.time()
            })

            if len(CHAT_HISTORY) > MAX_HISTORY:
                CHAT_HISTORY.pop(0)

    def get_history(self) -> List[Dict[str, Any]]:
        with AI_LOCK:
            return list(CHAT_HISTORY)

    def clear_history(self):
        global CHAT_HISTORY
        with AI_LOCK:
            CHAT_HISTORY = []

    def is_busy(self) -> bool:
        """Check if Claude is processing"""
        with AI_LOCK:
            return AI_BUSY

claude_engine = ClaudeEngine()

def ask_ai_async(prompt: str):
    """Send async request to Claude"""
    claude_engine.ask_async(prompt)

def wait_for_ai_response(timeout: int = 10) -> Optional[str]:
    return claude_engine.wait_for_response(timeout)

def get_ai_response() -> Optional[str]:
    global AI_RESPONSE
    with AI_LOCK:
        return AI_RESPONSE

def is_ai_busy() -> bool:
    return claude_engine.is_busy()

def add_to_history(user_input: str, ai_response: str):
    claude_engine.add_to_history(user_input, ai_response)

def get_history() -> List[Dict[str, Any]]:
    return claude_engine.get_history()

def clear_history():
    claude_engine.clear_history()

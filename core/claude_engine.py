import anthropic
from jarvis.core.config import settings
from typing import Optional, List, Dict, Any

class ClaudeEngine:
    """Claude AI integration for JARVIS"""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history = 10

        self.system_prompt = f"""You are Jarvis, an advanced real-time AI assistant inspired by Iron Man, designed to operate as a highly intelligent, responsive, and interruptible voice-based system that assists the user seamlessly in a conversational and task-oriented manner.

Your primary objective is to listen, understand, and respond accurately while maintaining a natural, human-like interaction flow.

BEHAVIOR RULES:
1. Only respond when a clear and meaningful user query is detected
2. Avoid unnecessary or random outputs caused by noise or incomplete input
3. When the user says the wake word "Jarvis," transition into an active verified state
4. Once verified, greet the user personally (e.g., "Hello {settings.user_name}, how can I assist you today?")
5. Process user speech in real-time, showing awareness of partial input but only generating a final response after the user finishes speaking
6. Your responses should be concise, intelligent, and context-aware
7. Avoid generic or repetitive phrases like "As an AI model"
8. Support full interruption handling: if the user speaks while you are responding, immediately stop your current output
9. Prioritize clarity, usefulness, and speed
10. Maintain a confident and slightly futuristic tone
11. Differentiate between system commands (like opening apps, sending messages, controlling system functions) and informational queries
12. Execute commands instantly and answer questions thoughtfully
13. Maintain short-term conversational memory to preserve context
14. Avoid hallucinations when context is unclear—ask for clarification instead
15. Ignore background noise, meaningless phrases, or low-confidence input
16. Act as a proactive but controlled assistant: assist when asked, suggest improvements when relevant, but never overwhelm the user

Your ultimate behavior should feel like a real-time operating system assistant—precise, interruptible, adaptive, and always focused on the user's intent.

The user's name is {settings.user_name}."""

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})

        # Keep history within limit
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_response(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get response from Claude
        Args:
            user_input: The user's input text
            context: Additional context (system state, etc.)
        """
        # Add user message to history
        self.add_message("user", user_input)

        # Prepare messages for API
        messages = self.conversation_history.copy()

        try:
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=messages
            )

            assistant_message = response.content[0].text
            self.add_message("assistant", assistant_message)

            return assistant_message

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def is_system_command(self, user_input: str) -> tuple[bool, Optional[str]]:
        """
        Check if input is a system command
        Returns: (is_command, command_type)
        """
        command_patterns = {
            "open": "open_app",
            "close": "close_app",
            "launch": "open_app",
            "search": "web_search",
            "find": "web_search",
            "run": "execute_command",
            "execute": "execute_command",
            "terminal": "execute_command",
            "play": "media_control",
            "pause": "media_control",
            "stop": "media_control",
            "volume": "volume_control",
            "brightness": "display_control",
            "shutdown": "system_power",
            "restart": "system_power",
            "sleep": "system_power",
            "what time": "time_query",
            "what's the time": "time_query",
            "weather": "weather_query",
        }

        input_lower = user_input.lower()

        for pattern, cmd_type in command_patterns.items():
            if pattern in input_lower:
                return True, cmd_type

        return False, None

claude_engine = ClaudeEngine()

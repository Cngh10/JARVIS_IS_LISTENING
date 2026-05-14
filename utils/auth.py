import random
import time
from jarvis.core.config import settings

class VoiceAuthenticator:
    """Simulated voice authentication system"""

    def __init__(self):
        self.verified = False
        self.last_verification = None
        self.verification_duration = 3600  # 1 hour

    def verify_voice_print(self, audio_data: bytes = None) -> tuple[bool, str]:
        """
        Simulate voice print verification
        Returns: (success, message)
        """
        # Simulate processing time
        time.sleep(0.5)

        # In production, this would use actual voice biometrics
        # For now, we simulate with a high success rate
        success_rate = 0.95
        success = random.random() < success_rate

        if success:
            self.verified = True
            self.last_verification = time.time()
            return True, f"Voice print verified. Hello {settings.user_name}, how can I assist you today?"
        else:
            return False, "Voice print verification failed. Please try again."

    def is_verified(self) -> bool:
        """Check if current session is verified"""
        if not self.verified:
            return False

        if self.last_verification:
            elapsed = time.time() - self.last_verification
            if elapsed > self.verification_duration:
                self.verified = False
                return False

        return True

    def get_greeting(self) -> str:
        """Get personalized greeting"""
        greetings = [
            f"Hello {settings.user_name}, how can I assist you today?",
            f"Good to see you, {settings.user_name}. What can I do for you?",
            f"Welcome back, {settings.user_name}. How may I help?",
            f"Hello {settings.user_name}. Systems are ready. What would you like me to do?"
        ]
        return random.choice(greetings)

    def reset(self):
        """Reset verification state"""
        self.verified = False
        self.last_verification = None

authenticator = VoiceAuthenticator()

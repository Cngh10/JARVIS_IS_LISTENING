"""
🚀 JARVIS ENHANCED - Environment Sensing & Guidance (Iron Man Level)

Complete JARVIS system with real-time environment sensing and guidance.
Features:
- Computer vision for obstacle detection
- Audio environment sensing
- Real-time guidance for navigation
- Emergency alerts
- Voice interaction
- Claude AI integration
"""

import threading
import time
from typing import Optional, Dict, Any

from voice import speak, stop_speaking, get_is_speaking
from commands import execute, is_system_command
from claude_integration import claude_engine, ask_ai_async, wait_for_ai_response, add_to_history
from auth import verify_voice, VOICE_VERIFICATION_AVAILABLE
from memory import remember, recall
from listener import start_listener, get_latest_input, clear_latest_input
from environment_sensor import EnvironmentSensor
from audio_sensor import AudioSensor
from guidance_system import GuidanceSystem, UrgencyLevel

class JarvisEnhanced:
    """Enhanced JARVIS with environment sensing"""

    def __init__(self):
        """Initialize enhanced JARVIS"""
        # Sensors
        self.environment_sensor = EnvironmentSensor()
        self.audio_sensor = AudioSensor()
        self.guidance_system = GuidanceSystem()

        # State
        self.running = False
        self.active = False
        self.guidance_mode = False  # Continuous guidance mode

        # Thread
        self.guidance_thread = None

        # Configuration
        self.guidance_interval = 3.0  # seconds between guidance updates
        self.last_guidance_time = 0.0

    def start(self):
        """Start enhanced JARVIS"""
        if self.running:
            return

        try:
            print("=" * 70)
            print("🚀 JARVIS ENHANCED - Environment Sensing & Guidance")
            print("=" * 70)

            # Start sensors
            print("📡 Starting sensors...")
            self.environment_sensor.start()
            self.audio_sensor.start()
            self.guidance_system.start()

            # Start listener
            print("🎤 Starting voice listener...")
            listener_thread = threading.Thread(target=start_listener, daemon=True)
            listener_thread.start()

            # Start guidance thread
            self.running = True
            self.guidance_thread = threading.Thread(target=self._guidance_loop, daemon=True)
            self.guidance_thread.start()

            # Greet user
            print("🔊 Speaking startup message...")
            speak("Jarvis enhanced is ready. Environment sensors active.")

            time.sleep(2)

            print("\n" + "=" * 70)
            print("🎯 SYSTEMS ONLINE")
            print("=" * 70)
            print("✅ Environment sensing: Active")
            print("✅ Audio sensing: Active")
            print("✅ Guidance system: Active")
            print("✅ Voice listener: Active")
            print("✅ Claude AI: " + ("Active" if claude_engine.is_available() else "Unavailable"))
            print("=" * 70)
            print("\nVoice Commands:")
            print("  • 'Jarvis' - Activate")
            print("  • 'start guidance' - Enable continuous guidance")
            print("  • 'stop guidance' - Disable continuous guidance")
            print("  • 'what's around me' - Get environment summary")
            print("  • 'help' - Get help")
            print("=" * 70 + "\n")

            # Main loop
            self._main_loop()

        except Exception as e:
            print(f"❌ Failed to start: {e}")

    def stop(self):
        """Stop enhanced JARVIS"""
        self.running = False
        if self.guidance_thread:
            self.guidance_thread.join(timeout=1.0)
        self.environment_sensor.stop()
        self.audio_sensor.stop()
        self.guidance_system.stop()
        speak("Jarvis shutting down.")
        print("✅ JARVIS enhanced stopped")

    def _guidance_loop(self):
        """Continuous guidance loop"""
        while self.running:
            try:
                # Only provide guidance if in guidance mode
                if self.guidance_mode:
                    current_time = time.time()

                    # Check interval
                    if current_time - self.last_guidance_time >= self.guidance_interval:
                        guidance = self.guidance_system.get_guidance()

                        if guidance and not get_is_speaking():
                            # Speak guidance based on urgency
                            if guidance.urgency in [UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]:
                                speak(guidance.message)
                                self.last_guidance_time = current_time
                            elif guidance.urgency == UrgencyLevel.MEDIUM:
                                speak(guidance.message)
                                self.last_guidance_time = current_time

                time.sleep(0.1)

            except Exception as e:
                print(f"❌ Guidance loop error: {e}")
                time.sleep(0.1)

    def _main_loop(self):
        """Main processing loop"""
        while self.running:
            try:
                # Get input
                current_input = get_latest_input()

                if not current_input:
                    time.sleep(0.1)
                    continue

                lower_input = current_input.lower()

                # Check for wake word
                if "jarvis" in lower_input:
                    print("🔑 Wake word detected")

                    # Verify voice
                    if VOICE_VERIFICATION_AVAILABLE:
                        speak("Verifying voice")
                        if verify_voice():
                            speak("Access granted")
                            self.active = True
                        else:
                            speak("Access denied")
                            self.active = False
                    else:
                        self.active = True
                        speak("Jarvis activated")

                    clear_latest_input()
                    continue

                # Only process if active
                if not self.active:
                    time.sleep(0.1)
                    continue

                # Handle interrupts
                if get_is_speaking():
                    if any(k in lower_input for k in ["stop", "wait", "quiet", "jarvis"]):
                        print("🛑 Interrupt detected")
                        stop_speaking()
                    else:
                        time.sleep(0.1)
                        continue

                # Handle commands
                if "start guidance" in lower_input:
                    self.guidance_mode = True
                    speak("Guidance mode activated. I'll help you navigate.")
                    clear_latest_input()
                    continue

                if "stop guidance" in lower_input:
                    self.guidance_mode = False
                    speak("Guidance mode deactivated.")
                    clear_latest_input()
                    continue

                if "what's around me" in lower_input or "what is around me" in lower_input:
                    summary = self.guidance_system.get_environment_summary()
                    self._speak_summary(summary)
                    clear_latest_input()
                    continue

                if "help" in lower_input:
                    self._speak_help()
                    clear_latest_input()
                    continue

                if "sleep" in lower_input or "stop" in lower_input:
                    self.active = False
                    speak("Going to sleep")
                    clear_latest_input()
                    continue

                # Handle system commands
                if is_system_command(current_input):
                    result = execute(current_input)
                    speak(result)
                    clear_latest_input()
                    continue

                # Handle questions with Claude
                if "?" in current_input or any(w in lower_input for w in ["what", "how", "why", "where", "when", "who"]):
                    ask_ai_async(current_input)
                    ai_response = wait_for_ai_response(timeout=15)

                    if ai_response:
                        speak(ai_response)
                        add_to_history(current_input, ai_response)
                    else:
                        speak("I'm having trouble thinking right now.")

                    clear_latest_input()
                    continue

                # Default: ignore
                clear_latest_input()
                time.sleep(0.1)

            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.stop()
                break

            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(0.1)

    def _speak_summary(self, summary: Dict[str, Any]):
        """Speak environment summary"""
        visual = summary.get("visual", {})
        audio = summary.get("audio", {})

        messages = []

        # Visual summary
        if visual.get("path_clear"):
            messages.append("Path is clear ahead.")
        else:
            messages.append(f"Path blocked. {visual.get('recommended_action', 'Watch out.')}")

        if visual.get("obstacles_count", 0) > 0:
            nearest = visual.get("nearest_obstacle")
            if nearest:
                messages.append(f"Nearest obstacle is {nearest:.1f} meters away.")

        # Audio summary
        if audio.get("is_emergency"):
            messages.append(audio.get("guidance", "Emergency detected!"))
        elif audio.get("dominant_sound"):
            messages.append(f"I can hear {audio.get('dominant_sound')}.")

        # Speak summary
        if messages:
            summary_text = " ".join(messages)
            speak(summary_text)
        else:
            speak("Environment looks normal.")

    def _speak_help(self):
        """Speak help information"""
        help_text = """
            I can help you with:
            Navigation guidance - Say 'start guidance'
            Environment awareness - Say 'what's around me'
            System commands - Like 'open safari' or 'search for'
            Questions - Ask me anything
            Say 'stop guidance' to disable navigation help
        """
        speak(help_text)

def main():
    """Main entry point"""
    jarvis = JarvisEnhanced()
    try:
        jarvis.start()
    except KeyboardInterrupt:
        jarvis.stop()

if __name__ == "__main__":
    main()

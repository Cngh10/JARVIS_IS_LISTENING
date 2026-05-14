"""
🧭 REAL-TIME GUIDANCE SYSTEM (Iron Man Level)

Comprehensive guidance system combining vision and audio sensors.
Features:
- Real-time obstacle avoidance
- Navigation assistance
- Emergency alerts
- Environmental awareness
- Safe path recommendations
"""

import threading
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from environment_sensor import EnvironmentSensor, Obstacle, Path, DangerLevel
from audio_sensor import AudioSensor, SoundEvent, SoundType

class UrgencyLevel(Enum):
    """Urgency levels for guidance"""
    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Guidance:
    """Guidance information"""
    message: str
    urgency: UrgencyLevel
    visual_guidance: Optional[str]
    audio_guidance: Optional[str]
    recommended_action: str
    confidence: float

class GuidanceSystem:
    """Real-time guidance system"""

    def __init__(self):
        """Initialize guidance system"""
        self.environment_sensor = EnvironmentSensor()
        self.audio_sensor = AudioSensor()

        self.running = False
        self.thread = None

        # Current guidance
        self.current_guidance: Optional[Guidance] = None
        self.guidance_lock = threading.Lock()

        # Guidance history
        self.guidance_history: List[Guidance] = []
        self.history_lock = threading.Lock()

        # Last guidance time (to prevent spam)
        self.last_guidance_time = 0.0
        self.guidance_cooldown = 2.0  # seconds

        # Emergency state
        self.emergency_active = False
        self.emergency_lock = threading.Lock()

    def start(self):
        """Start guidance system"""
        if self.running:
            return

        try:
            # Start sensors
            self.environment_sensor.start()
            self.audio_sensor.start()

            # Start guidance thread
            self.running = True
            self.thread = threading.Thread(target=self._guidance_loop, daemon=True)
            self.thread.start()

            print("✅ Guidance system started")

        except Exception as e:
            print(f"❌ Failed to start guidance system: {e}")

    def stop(self):
        """Stop guidance system"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.environment_sensor.stop()
        self.audio_sensor.stop()
        print("✅ Guidance system stopped")

    def _guidance_loop(self):
        """Main guidance loop"""
        while self.running:
            try:
                # Get sensor data
                visual_path = self.environment_sensor.get_path()
                visual_obstacles = self.environment_sensor.get_obstacles()
                audio_env = self.audio_sensor.get_current_environment()

                # Generate guidance
                guidance = self._generate_guidance(visual_path, visual_obstacles, audio_env)

                # Update current guidance
                with self.guidance_lock:
                    self.current_guidance = guidance

                # Add to history
                self._add_to_history(guidance)

                # Check for emergency
                self._check_emergency(guidance, audio_env)

                # Small delay
                time.sleep(0.1)

            except Exception as e:
                print(f"❌ Guidance error: {e}")
                time.sleep(0.1)

    def _generate_guidance(
        self,
        visual_path: Optional[Path],
        visual_obstacles: List[Obstacle],
        audio_env: Optional[Any]
    ) -> Guidance:
        """
        Generate comprehensive guidance

        Args:
            visual_path: Visual path information
            visual_obstacles: Visual obstacles
            audio_env: Audio environment

        Returns:
            Guidance information
        """
        urgency = UrgencyLevel.INFO
        visual_msg = ""
        audio_msg = ""
        recommended_action = "Continue straight."
        confidence = 0.7

        # Check visual guidance
        if visual_path:
            if not visual_path.clear:
                urgency = UrgencyLevel.HIGH
                recommended_action = visual_path.recommended_action
                visual_msg = visual_path.recommended_action
            else:
                # Check for nearby obstacles
                nearby = [o for o in visual_obstacles if o.distance < 2.0]
                if nearby:
                    closest = nearby[0]
                    if closest.danger_level == DangerLevel.DANGER:
                        urgency = UrgencyLevel.CRITICAL
                        recommended_action = f"STOP! {closest.type.value} {closest.distance:.1f}m to your {closest.direction}."
                        visual_msg = recommended_action
                    elif closest.danger_level == DangerLevel.WARNING:
                        urgency = UrgencyLevel.MEDIUM
                        recommended_action = f"Warning: {closest.type.value} {closest.distance:.1f}m to your {closest.direction}."
                        visual_msg = recommended_action

        # Check audio guidance
        if audio_env:
            if audio_env.is_emergency:
                urgency = UrgencyLevel.CRITICAL
                audio_msg = audio_env.guidance
                recommended_action = audio_env.guidance
            elif audio_env.guidance and "Vehicle" in audio_env.guidance:
                urgency = UrgencyLevel.HIGH
                audio_msg = audio_env.guidance
                recommended_action = audio_env.guidance

        # Combine messages
        if visual_msg and audio_msg:
            message = f"{visual_msg} {audio_msg}"
        elif visual_msg:
            message = visual_msg
        elif audio_msg:
            message = audio_msg
        else:
            message = "Path clear. Continue straight."

        return Guidance(
            message=message,
            urgency=urgency,
            visual_guidance=visual_msg,
            audio_guidance=audio_msg,
            recommended_action=recommended_action,
            confidence=confidence
        )

    def _add_to_history(self, guidance: Guidance):
        """Add guidance to history"""
        with self.history_lock:
            self.guidance_history.append(guidance)

            # Keep last 50 entries
            if len(self.guidance_history) > 50:
                self.guidance_history.pop(0)

    def _check_emergency(self, guidance: Guidance, audio_env: Optional[Any]):
        """Check for emergency conditions"""
        with self.emergency_lock:
            if guidance.urgency == UrgencyLevel.CRITICAL:
                self.emergency_active = True
            elif audio_env and audio_env.is_emergency:
                self.emergency_active = True
            else:
                self.emergency_active = False

    def get_guidance(self) -> Optional[Guidance]:
        """Get current guidance"""
        with self.guidance_lock:
            return self.current_guidance

    def get_guidance_message(self) -> str:
        """
        Get guidance message (with cooldown)

        Returns:
            Guidance message or empty string if in cooldown
        """
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_guidance_time < self.guidance_cooldown:
            # Only return if critical urgency
            guidance = self.get_guidance()
            if guidance and guidance.urgency == UrgencyLevel.CRITICAL:
                self.last_guidance_time = current_time
                return guidance.message
            return ""

        guidance = self.get_guidance()

        if guidance:
            self.last_guidance_time = current_time
            return guidance.message

        return ""

    def is_emergency(self) -> bool:
        """Check if emergency is active"""
        with self.emergency_lock:
            return self.emergency_active

    def get_environment_summary(self) -> Dict[str, Any]:
        """
        Get complete environment summary

        Returns:
            Environment summary dictionary
        """
        visual_path = self.environment_sensor.get_path()
        visual_obstacles = self.environment_sensor.get_obstacles()
        audio_env = self.audio_sensor.get_current_environment()

        return {
            "visual": {
                "path_clear": visual_path.clear if visual_path else True,
                "obstacles_count": len(visual_obstacles),
                "nearest_obstacle": visual_obstacles[0].distance if visual_obstacles else None,
                "recommended_action": visual_path.recommended_action if visual_path else "Continue straight."
            },
            "audio": {
                "noise_level": audio_env.noise_level if audio_env else 0.0,
                "dominant_sound": audio_env.dominant_sound.value if audio_env and audio_env.dominant_sound else None,
                "is_emergency": audio_env.is_emergency if audio_env else False,
                "guidance": audio_env.guidance if audio_env else "Normal."
            },
            "emergency": self.is_emergency(),
            "guidance": self.get_guidance_message()
        }

# Global instance
guidance_system = GuidanceSystem()

"""
🎯 JARVIS Enhanced - Final Demo

Shows the complete system working with all improvements.
"""

import time
from environment_sensor import EnvironmentSensor
from audio_sensor import AudioSensor
from guidance_system import GuidanceSystem

def main():
    print("=" * 70)
    print("🎯 JARVIS Enhanced - Final Demo")
    print("=" * 70)
    print("\n📡 Initializing systems...")

    # Initialize sensors
    env_sensor = EnvironmentSensor()
    audio_sensor = AudioSensor()
    guidance = GuidanceSystem()

    # Start sensors
    env_sensor.start()
    audio_sensor.start()
    guidance.start()

    print("✅ All systems operational")
    print("\n" + "=" * 70)
    print("🌍 REAL-TIME ENVIRONMENT MONITORING")
    print("=" * 70)
    print("Monitoring your surroundings...\n")

    try:
        iteration = 0
        while True:
            iteration += 1

            # Get current data
            obstacles = env_sensor.get_obstacles()
            path = env_sensor.get_path()
            audio_env = audio_sensor.get_current_environment()
            guidance_data = guidance.get_guidance()

            # Clear screen for cleaner output
            print("\033c", end="")

            # Header
            print("=" * 70)
            print(f"🎯 JARVIS Enhanced - Iteration {iteration}")
            print("=" * 70)

            # Visual Environment
            print("\n📷 VISUAL ENVIRONMENT")
            print("-" * 70)
            if obstacles:
                print(f"Obstacles detected: {len(obstacles)}")
                for i, obs in enumerate(obstacles[:3]):
                    danger_icon = "🔴" if obs.danger_level.value >= 3 else "🟡" if obs.danger_level.value >= 2 else "🟢"
                    print(f"  {danger_icon} {obs.type.value.upper():10} | {obs.distance:5.1f}m | {obs.direction:6} | {obs.danger_level.name}")
            else:
                print("✅ No obstacles detected in navigation zone")

            print(f"\nPath Status: {'🟢 CLEAR' if path and path.clear else '🔴 BLOCKED'}")
            if path:
                print(f"Recommended: {path.recommended_action}")

            # Audio Environment
            print("\n🔊 AUDIO ENVIRONMENT")
            print("-" * 70)
            if audio_env:
                noise_icon = "🔴" if audio_env.noise_level > 70 else "🟡" if audio_env.noise_level > 50 else "🟢"
                print(f"Noise Level: {noise_icon} {audio_env.noise_level:.1f} dB")

                if audio_env.dominant_sound:
                    print(f"Sound Type: {audio_env.dominant_sound.value}")

                if audio_env.is_emergency:
                    print("🚨 EMERGENCY SOUND DETECTED!")

                if audio_env.is_speech_present:
                    print("🗣️ Speech detected")

            # Guidance
            print("\n🧭 GUIDANCE SYSTEM")
            print("-" * 70)
            if guidance_data:
                urgency_icon = "🔴" if guidance_data.urgency.value >= 4 else "🟡" if guidance_data.urgency.value >= 2 else "🟢"
                print(f"Urgency: {urgency_icon} {guidance_data.urgency.name}")
                print(f"Message: {guidance_data.message}")
                print(f"Action: {guidance_data.recommended_action}")

            # Status
            print("\n" + "=" * 70)
            print("📊 SYSTEM STATUS")
            print("-" * 70)
            print(f"Environment Sensor: {'🟢 Active' if env_sensor.running else '🔴 Inactive'}")
            print(f"Audio Sensor: {'🟢 Active' if audio_sensor.running else '🔴 Inactive'}")
            print(f"Guidance System: {'🟢 Active' if guidance.running else '🔴 Inactive'}")
            print("=" * 70)
            print("Press Ctrl+C to stop\n")

            # Wait before next update
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down systems...")

    finally:
        env_sensor.stop()
        audio_sensor.stop()
        guidance.stop()
        print("✅ All systems stopped")
        print("\n🎉 JARVIS Enhanced demo complete!")

if __name__ == "__main__":
    main()

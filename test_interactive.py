"""
🧪 JARVIS Enhanced - Interactive Test

Shows real-time output from all sensors.
"""

import time
from environment_sensor import EnvironmentSensor
from audio_sensor import AudioSensor
from guidance_system import GuidanceSystem

def main():
    print("=" * 70)
    print("🧪 JARVIS Enhanced - Interactive Sensor Test")
    print("=" * 70)

    # Start sensors
    print("\n📡 Starting sensors...")
    env_sensor = EnvironmentSensor()
    audio_sensor = AudioSensor()
    guidance = GuidanceSystem()

    env_sensor.start()
    audio_sensor.start()
    guidance.start()

    print("✅ All sensors started")
    print("\n" + "=" * 70)
    print("🎯 REAL-TIME MONITORING")
    print("=" * 70)
    print("Press Ctrl+C to stop\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")

            # Get environment data
            obstacles = env_sensor.get_obstacles()
            path = env_sensor.get_path()

            # Get audio data
            audio_env = audio_sensor.get_current_environment()

            # Get guidance
            guidance_data = guidance.get_guidance()

            # Display visual data
            print(f"📷 Visual:")
            print(f"   Obstacles: {len(obstacles)}")
            if obstacles:
                for i, obs in enumerate(obstacles[:3]):
                    print(f"   {i+1}. {obs.type.value} - {obs.distance:.1f}m ({obs.direction})")
            print(f"   Path: {'CLEAR' if path and path.clear else 'BLOCKED'}")
            if path:
                print(f"   Action: {path.recommended_action}")

            # Display audio data
            print(f"\n🔊 Audio:")
            if audio_env:
                print(f"   Noise: {audio_env.noise_level:.1f} dB")
                print(f"   Sound: {audio_env.dominant_sound.value if audio_env.dominant_sound else 'None'}")
                print(f"   Emergency: {'YES' if audio_env.is_emergency else 'NO'}")
                print(f"   Guidance: {audio_env.guidance}")

            # Display guidance
            print(f"\n🧭 Guidance:")
            if guidance_data:
                print(f"   Urgency: {guidance_data.urgency.name}")
                print(f"   Message: {guidance_data.message}")
                print(f"   Action: {guidance_data.recommended_action}")

            print("\n" + "-" * 70)

            # Wait before next update
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n👋 Stopping sensors...")

    finally:
        env_sensor.stop()
        audio_sensor.stop()
        guidance.stop()
        print("✅ All sensors stopped")

if __name__ == "__main__":
    main()

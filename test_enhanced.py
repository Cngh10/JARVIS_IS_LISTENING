"""
🧪 JARVIS ENHANCED - Quick Test

Test script to verify all systems are working.
"""

import sys
import time

def test_imports():
    """Test all imports"""
    print("🔍 Testing imports...")

    try:
        from environment_sensor import EnvironmentSensor
        print("✅ Environment sensor imported")
    except Exception as e:
        print(f"❌ Environment sensor failed: {e}")
        return False

    try:
        from audio_sensor import AudioSensor
        print("✅ Audio sensor imported")
    except Exception as e:
        print(f"❌ Audio sensor failed: {e}")
        return False

    try:
        from guidance_system import GuidanceSystem
        print("✅ Guidance system imported")
    except Exception as e:
        print(f"❌ Guidance system failed: {e}")
        return False

    try:
        from claude_integration import claude_engine
        print("✅ Claude integration imported")
        if claude_engine.is_available():
            print("✅ Claude API is available")
        else:
            print("⚠️ Claude API not configured (set ANTHROPIC_API_KEY)")
    except Exception as e:
        print(f"❌ Claude integration failed: {e}")
        return False

    try:
        from voice import speak
        print("✅ Voice system imported")
    except Exception as e:
        print(f"❌ Voice system failed: {e}")
        return False

    return True

def test_camera():
    """Test camera"""
    print("\n📷 Testing camera...")

    try:
        import cv2

        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera working - Resolution: {frame.shape[1]}x{frame.shape[0]}")
                cap.release()
                return True
            else:
                print("❌ Camera opened but couldn't capture frame")
                cap.release()
                return False
        else:
            print("❌ Could not open camera")
            return False
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_microphone():
    """Test microphone"""
    print("\n🎤 Testing microphone...")

    try:
        import sounddevice as sd

        # List available devices
        devices = sd.query_devices()
        print(f"📋 Found {len(devices)} audio devices")

        # Try to record a short sample
        duration = 1.0
        sample_rate = 44100
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        if recording is not None and len(recording) > 0:
            print(f"✅ Microphone working - Recorded {len(recording)} samples")
            return True
        else:
            print("❌ Microphone test failed")
            return False
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_voice():
    """Test voice output"""
    print("\n🔊 Testing voice output...")

    try:
        from voice import speak
        print("🗣️ Speaking test message...")
        speak("Jarvis test. Voice system is working.")
        time.sleep(2)
        print("✅ Voice output working")
        return True
    except Exception as e:
        print(f"❌ Voice test failed: {e}")
        return False

def test_environment_sensing():
    """Test environment sensing"""
    print("\n🌍 Testing environment sensing...")

    try:
        from environment_sensor import EnvironmentSensor

        sensor = EnvironmentSensor()
        sensor.start()

        print("⏳ Waiting for sensor data...")
        time.sleep(2)

        obstacles = sensor.get_obstacles()
        path = sensor.get_path()

        print(f"✅ Detected {len(obstacles)} obstacles")
        if path:
            print(f"✅ Path analysis: {'Clear' if path.clear else 'Blocked'}")

        sensor.stop()
        return True
    except Exception as e:
        print(f"❌ Environment sensing test failed: {e}")
        return False

def test_audio_sensing():
    """Test audio sensing"""
    print("\n🔊 Testing audio sensing...")

    try:
        from audio_sensor import AudioSensor

        sensor = AudioSensor()
        sensor.start()

        print("⏳ Listening for audio...")
        time.sleep(2)

        env = sensor.get_current_environment()
        if env:
            print(f"✅ Audio sensing working - Noise level: {env.noise_level:.1f} dB")

        sensor.stop()
        return True
    except Exception as e:
        print(f"❌ Audio sensing test failed: {e}")
        return False

def test_guidance():
    """Test guidance system"""
    print("\n🧭 Testing guidance system...")

    try:
        from guidance_system import GuidanceSystem

        system = GuidanceSystem()
        system.start()

        print("⏳ Waiting for guidance...")
        time.sleep(2)

        guidance = system.get_guidance()
        if guidance:
            print(f"✅ Guidance system working - Urgency: {guidance.urgency.name}")

        system.stop()
        return True
    except Exception as e:
        print(f"❌ Guidance system test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 JARVIS ENHANCED - System Test")
    print("=" * 70)

    results = []

    # Test imports
    results.append(("Imports", test_imports()))

    # Test hardware
    results.append(("Camera", test_camera()))
    results.append(("Microphone", test_microphone()))

    # Test voice
    results.append(("Voice Output", test_voice()))

    # Test sensors
    results.append(("Environment Sensing", test_environment_sensing()))
    results.append(("Audio Sensing", test_audio_sensing()))
    results.append(("Guidance System", test_guidance()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 All systems operational! You can start JARVIS with:")
        print("   python jarvis_enhanced.py")
    else:
        print("\n⚠️ Some systems need attention. Check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

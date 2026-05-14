#!/usr/bin/env python3
"""
🎤 TEST GREETING VOICE
Debug the greeting voice output issue
"""

from voice import speak
import time

print("=" * 70)
print("🎤 JARVIS GREETING VOICE TEST")
print("=" * 70)

print("\n✅ TEST 1: Direct greeting")
print("-" * 70)
print("About to speak: 'Hello Chandan, what's up?'")
print("Waiting for audio...")

speak("Hello Chandan, what's up?")

# Wait for speech to complete
print("\nWaiting for speech to complete...")
for i in range(10):
    time.sleep(0.5)
    print(f"  [{i+1}/10] Waiting...")

print("\n✅ TEST 2: Longer greeting")
print("-" * 70)
greeting = "Hello Chandan, I am Jarvis. How can I help you today?"
print(f"Speaking: '{greeting}'")
speak(greeting)

print("\nWaiting for speech to complete...")
for i in range(15):
    time.sleep(0.5)
    print(f"  [{i+1}/15] Waiting...")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
print("\nIf you heard both greetings clearly, the voice system is working!")
print("If you didn't hear anything, check:")
print("  1. Speaker is connected and volume is up")
print("  2. System volume is not muted")
print("  3. Run diagnose_voice.py to check audio devices")

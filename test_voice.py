#!/usr/bin/env python3
"""
🎤 VOICE SYSTEM DIAGNOSTIC
Test microphone input, audio recognition, and speaker output
"""

import sounddevice as sd
import numpy as np
import time
from voice import listen, speak

print("=" * 70)
print("🎤 JARVIS VOICE DIAGNOSTIC TEST")
print("=" * 70)

# Test 1: Test microphone input
print("\n🎤 TEST 1: Recording 3 seconds of audio...")
print("Speak now: Say 'hello jarvis'")
print("-" * 70)

try:
    fs = 16000
    duration = 3
    
    recording = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    audio = recording.flatten()
    audio_level = np.max(np.abs(audio))
    
    print(f"✅ Audio recorded")
    print(f"  - Duration: {duration}s")
    print(f"  - Sample rate: {fs}Hz")
    print(f"  - Peak level: {audio_level:.3f}")
    
    if audio_level < 0.01:
        print("⚠️  WARNING: Very quiet audio. Check microphone levels.")
    else:
        print(f"✅ Audio level OK")
        
except Exception as e:
    print(f"❌ Microphone error: {e}")

# Test 2: Test speech recognition
print("\n🎙️ TEST 2: Testing speech recognition with listen()...")
print("Speak now: Say 'hello jarvis'")
print("-" * 70)

try:
    text = listen(timeout=4)
    
    if text:
        print(f"✅ Recognized: '{text}'")
    else:
        print("⚠️  No text recognized. Check:")
        print("  1. Microphone is plugged in and working")
        print("  2. Speak clearly and loud enough")
        print("  3. No background noise is too loud")
        
except Exception as e:
    print(f"❌ Recognition error: {e}")

# Test 3: Test speaker output
print("\n🔊 TEST 3: Testing speaker output...")
print("-" * 70)

try:
    print("Speaking: 'Hello, this is Jarvis'")
    speak("Hello, this is Jarvis. Voice system is working.")
    print("✅ Speaking completed")
except Exception as e:
    print(f"❌ Speaker error: {e}")

print("\n" + "=" * 70)
print("✅ DIAGNOSTIC TEST COMPLETE")
print("=" * 70)

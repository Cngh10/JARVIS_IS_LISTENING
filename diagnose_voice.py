import sounddevice as sd
import numpy as np
import sys

print("=" * 70)
print("JARVIS VOICE SYSTEM DIAGNOSTIC")
print("=" * 70)

# TEST 1: Check Audio Devices
print("\nTEST 1: Checking Audio Devices")
print("-" * 70)

try:
    devices = sd.query_devices()
    print(f" Found {len(devices)} audio devices:\n")
    
    for i, device in enumerate(devices):
        name = device['name']
        input_ch = device['max_input_channels']
        output_ch = device['max_output_channels']
        
        device_type = []
        if input_ch > 0:
            device_type.append(f"INPUT({input_ch}ch)")
        if output_ch > 0:
            device_type.append(f"OUTPUT({output_ch}ch)")
        
        print(f"{i}: {name}")
        print(f"   {', '.join(device_type)}")
    
    default_input = sd.default.device[0]
    default_output = sd.default.device[1]
    print(f"\n Default Input Device: {devices[default_input]['name']}")
    print(f" Default Output Device: {devices[default_output]['name']}")
    
except Exception as e:
    print(f" Error checking devices: {e}")
    sys.exit(1)

# TEST 2: Test Microphone Recording
print("\n TEST 2: Testing Microphone Recording")
print("-" * 70)

try:
    print("Recording 2 seconds... SPEAK NOW!")
    
    fs = 16000
    duration = 2
    
    recording = sd.rec(
        int(duration * fs),
        samplerate=fs,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    audio = recording.flatten()
    audio_level = np.max(np.abs(audio))
    
    print(f" Recording successful")
    print(f"   - Samples: {len(audio)}")
    print(f"   - Peak level: {audio_level:.4f}")
    print(f"   - Average level: {np.mean(np.abs(audio)):.4f}")
    
    if audio_level < 0.001:
        print("\n  WARNING: Very quiet audio!")
        print("   - Check microphone is properly connected")
        print("   - Check microphone levels in system settings")
        print("   - Try speaking louder")
    elif audio_level < 0.01:
        print("\n  Audio is quiet but might work")
    else:
        print("\n Audio level looks good!")
        
except Exception as e:
    print(f" Microphone error: {e}")
    print("   - Check microphone is connected")
    print("   - Check sounddevice is installed: pip install sounddevice")

# TEST 3: Test Speaker Output
print("\n TEST 3: Testing Speaker Output")
print("-" * 70)

try:
    print("Generating test tone...")
    
    fs = 22050
    duration = 1
    freq = 440  # A4 note
    
    t = np.linspace(0, duration, int(fs * duration))
    tone = 0.3 * np.sin(2 * np.pi * freq * t).astype('float32')
    
    print(f"Playing 1-second 440Hz tone (A note)...")
    sd.play(tone, fs)
    sd.wait()
    
    print(" Speaker test successful!")
    print("   - If you heard a beep, speaker is working")
    print("   - If no sound, check:")
    print("     • Speaker is connected and turned on")
    print("     • Volume is not muted")
    print("     • Default output device is correct")
    
except Exception as e:
    print(f" Speaker error: {e}")

# TEST 4: Test Whisper Speech Recognition
print("\n TEST 4: Testing Speech Recognition (Whisper)")
print("-" * 70)

try:
    import whisper
    print("Loading Whisper model...")
    model = whisper.load_model("small")
    print(" Whisper model loaded")
    
    print("\n Whisper is ready for speech recognition")
    print("   Run test_voice.py for a live recognition test")
    
except Exception as e:
    print(f" Whisper error: {e}")
    print("   Install: pip install openai-whisper")

# TEST 5: Test pyttsx3 Text-to-Speech
print("\n  TEST 5: Testing Text-to-Speech (pyttsx3)")
print("-" * 70)

try:
    import pyttsx3
    print("Initializing text-to-speech engine...")
    
    engine = pyttsx3.init()
    engine.setProperty('rate', 180)
    
    print(" TTS engine initialized")
    print("   Rate: 180 words per minute")
    
    print("\nSpeaking: 'Hello, this is a test'")
    engine.say("Hello, this is a test")
    engine.runAndWait()
    print(" Speech successful!")
    
except Exception as e:
    print(f" TTS error: {e}")
    print("   Install: pip install pyttsx3")

# SUMMARY
print("\n" + "=" * 70)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 70)

print("\n📝 NEXT STEPS:")
print("\n1. If all tests passed:")
print("   - Run: python main.py")
print("   - Say: 'hello jarvis'")
print("   - Expected: Jarvis responds 'Hello [Name], what's up?'")

print("\n2. If microphone test failed:")
print("   - Check device list above")
print("   - Make sure default input device is your microphone")
print("   - Try: python test_voice.py")

print("\n3. If speaker test failed:")
print("   - Check system volume is not muted")
print("   - Make sure default output device is your speaker")
print("   - Try adjusting system audio settings")

print("\n4. If Whisper test failed:")
print("   - Install: pip install openai-whisper")
print("   - First load might take time as it downloads the model")

print("\n5. If TTS test failed:")
print("   - Install: pip install pyttsx3")
print("   - Some systems may need additional dependencies")

print("\n" + "=" * 70)

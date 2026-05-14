# 🔧 JARVIS OS - ADVANCED TROUBLESHOOTING

## 🎯 Problem Diagnosis Guide

Use this to identify and fix issues systematically.

---

## 1. ❌ AI NOT RESPONDING

### Symptoms:
- User asks question
- Logs say "🤖 Sending to AI..."
- But response never comes
- Loop times out after 15 seconds
- Or system skips AI call entirely

### Diagnosis Steps:

#### **Step 1: Check Ollama is Running**
```bash
# Terminal 1: Start Ollama
ollama serve

# Should see:
# Listening on 127.0.0.1:11434
```

#### **Step 2: Test Direct Connection**
```bash
# In Terminal 2:
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"phi","prompt":"What is AI?","stream":false}'

# Should get JSON response with "response" field
```

If curl fails:
- ❌ Ollama not running → start it
- ❌ Wrong port → check it's 11434
- ❌ Wrong hostname → should be localhost or 127.0.0.1

#### **Step 3: Check Model Installed**
```bash
ollama list

# Should show:
# NAME        ID              SIZE    MODIFIED
# phi:latest  ...             3.3GB   2 hours ago
```

If phi not listed:
```bash
ollama pull phi
```

#### **Step 4: Monitor brain.py Thread**
Add debug prints to brain.py:
```python
def ask_ai_async(prompt):
    print(f"[BRAIN] ask_ai_async called with: {prompt[:50]}")
    global AI_RESPONSE, AI_BUSY, AI_READY_EVENT

    with AI_LOCK:
        AI_RESPONSE = None
        AI_BUSY = True
        AI_READY_EVENT.clear()
        print("[BRAIN] State reset, event cleared")

    def run():
        global AI_RESPONSE, AI_BUSY, AI_READY_EVENT
        print("[BRAIN] Thread started")
        try:
            print("[BRAIN] Making request to Ollama...")
            # ... rest of code
            print(f"[BRAIN] Got response: {response[:50]}")
            AI_READY_EVENT.set()
            print("[BRAIN] Event set!")
```

### Solutions:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Connection refused | Ollama not running | `ollama serve` in terminal 1 |
| Connection timeout | Ollama slow/hanging | Restart Ollama |
| Empty response | Model not loaded | `ollama pull phi` |
| Thread never finishes | Request timeout too short | Increase timeout in brain.py |
| Response set but main loop doesn't see it | Event not signaled | Check `AI_READY_EVENT.set()` called |

---

## 2. 🎤 GARBAGE INPUT FROM WHISPER

### Symptoms:
- Says "hello" → transcribed as "hello dadwis"
- Says "what" → transcribed as "subscribe"
- Random phrases appear
- Intent detection fails

### Diagnosis:

#### **Check Whisper Model**
```python
import whisper
model = whisper.load_model("small")

# Record a test audio file
import sounddevice as sd
import scipy.io.wavfile as wav

audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
wav.write("test.wav", 16000, audio)

# Transcribe
result = model.transcribe("test.wav", language="en")
print(result["text"])

# Check if it matches what you said
```

#### **Listen to Raw Audio**
```python
# Save before transcription to diagnose:
import sounddevice as sd
import scipy.io.wavfile as wav

audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
wav.write("debug_audio.wav", 16000, audio)

# Now listen to debug_audio.wav with:
# - Audacity (free audio editor)
# - QuickTime
# - VLC

# Check if audio quality is good
```

### Solutions:

1. **Add phrase to junk filter** (voice.py):
```python
JUNK_PHRASES = [
    "dadwis",  # Add noisy output here
    "subscribe",
    "thanks for watching"
]
```

2. **Increase silence threshold** (voice.py):
```python
# More aggressive silence detection
if audio_level < 0.03:  # Was 0.02
    return ""
```

3. **Use better microphone**
- USB microphone (better than built-in)
- Noise-canceling headset
- Close to mouth (6 inches)

4. **Record in quiet room**
- Close windows
- Minimize fan noise
- Turn off TV/music

---

## 3. 🔄 LISTENER INTERRUPTS AI

### Symptoms:
- AI starts responding
- User makes small noise
- AI response gets cancelled
- Jumps to next input

### Root Cause:
Listener thread updates LATEST_INPUT while AI is responding

### Diagnosis:

Add debugging to listener.py:
```python
def set_latest_input(text):
    global LATEST_INPUT, LAST_INPUT_TIME
    current_time = time.time()

    with LISTENER_LOCK:
        if text == LATEST_INPUT and (current_time - LAST_INPUT_TIME) < (DEBOUNCE_MS / 1000):
            print(f"[LISTENER] Debounced: {text}")  # Ignored
            return False

        print(f"[LISTENER] Updated: {LATEST_INPUT} → {text}")  # Changed
        LATEST_INPUT = text
        LAST_INPUT_TIME = current_time
        return True
```

### Solutions:

1. **Increase debounce time** (listener.py):
```python
DEBOUNCE_MS = 500  # Was 300 - more aggressive debouncing
```

2. **Increase AI response timeout** (main.py):
```python
ai_response = wait_for_ai_response(timeout=20)  # Was 15
```

3. **Clear input immediately after use** (main.py):
```python
clear_latest_input()  # Prevents re-listening while responding
```

4. **Better interrupt logic** (main.py):
```python
# Only interrupt if VERY different input
def should_interrupt_response(new_text, original_text):
    # ... only interrupt if > 70% different words
    if difference > len(original_words) * 0.7:  # Was 0.5
        return True
```

---

## 4. 🗣️ VOICE OUTPUT ISSUES

### Symptoms:
- No sound from speaker
- Audio cuts off mid-sentence
- Speaking too fast/slow
- Bad pronunciation

### Diagnosis:

#### **Check System Volume**
```bash
# macOS
osascript -e "output volume of (get volume settings)"
```

#### **Check if pyttsx3 Working**
```python
import pyttsx3
engine = pyttsx3.init()
engine.say("Testing microphone")
engine.runAndWait()
# Should hear "Testing microphone"
```

#### **Check Voice Settings**
```python
import pyttsx3
engine = pyttsx3.init()

# List available voices
for voice in engine.getProperty('voices'):
    print(f"Voice: {voice.id}")

# Set specific voice
engine.setProperty('voice', voices[0].id)
```

### Solutions:

1. **Increase system volume**
```bash
# macOS - set to 50%
osascript -e "set volume output volume 50"
```

2. **Adjust TTS speed** (voice.py):
```python
engine.setProperty('rate', 200)  # 150-200 is good
# Lower = slower, Higher = faster
```

3. **Adjust TTS volume** (voice.py):
```python
engine.setProperty('volume', 0.9)  # 0.0-1.0
```

4. **Pick different voice** (voice.py):
```python
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # Try different index
```

---

## 5. 🎤 NO MICROPHONE INPUT

### Symptoms:
- "🎤 You:" never prints
- listen() always returns ""
- Audio appears to record but silence

### Diagnosis:

#### **Check Microphone Permission** (macOS)
```
System Preferences → Security & Privacy → Microphone
→ Python3 should be in list
```

#### **List Audio Devices**
```python
import sounddevice as sd
print(sd.query_devices())

# Output should show your microphone
# Look for your device name (e.g., "Built-in Microphone")
```

#### **Test Recording Directly**
```python
import sounddevice as sd
import scipy.io.wavfile as wav

print("Recording for 3 seconds...")
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
print("Recording complete")

wav.write("test_audio.wav", 16000, audio)
print("Saved to test_audio.wav - listen to check audio quality")
```

#### **Test Whisper Separately**
```python
# Use test_audio.wav from above
import whisper
model = whisper.load_model("small")
result = model.transcribe("test_audio.wav")
print(result["text"])
```

### Solutions:

1. **Grant microphone permission** (macOS)
```
System Preferences → Security & Privacy → Microphone
→ Add Terminal/Python to list
→ Restart Terminal
```

2. **Specify device explicitly** (voice.py):
```python
# After finding device number from sd.query_devices()
recording = sd.rec(
    int(duration * fs),
    samplerate=fs,
    channels=1,
    dtype='float32',
    device=2  # Change to your device number
)
```

3. **Use USB microphone**
- Better audio quality
- More reliable
- Less interference

---

## 6. ⚡ PERFORMANCE ISSUES

### Symptoms:
- AI takes 30+ seconds to respond
- Microphone lags
- CPU at 100%
- System feels slow

### Diagnosis:

#### **Monitor Resource Usage**
```bash
# macOS
# Activity Monitor → CPU/Memory tabs
# Watch while running main.py

top -o %CPU  # CPU-sorted
```

#### **Check Ollama Performance**
```bash
# Monitor Ollama separately
# If CPU is 100%, Ollama is maxed out
```

#### **Profile Whisper**
```python
import time
import whisper

model = whisper.load_model("small")

# Time transcription
start = time.time()
result = model.transcribe("test.wav")
duration = time.time() - start

print(f"Transcription took: {duration:.2f} seconds")
```

### Solutions:

1. **Use faster Whisper model** (voice.py):
```python
# Small model is baseline
# Tiny model is faster but less accurate
model = whisper.load_model("tiny")  # or "base"
```

2. **Use faster Ollama model** (brain.py):
```python
"model": "neural-chat"  # Faster than phi
# or
"model": "orca-mini"  # Smaller model
```

3. **Reduce listening timeout** (voice.py):
```python
def listen(timeout=2):  # Was 3
```

4. **Close other applications**
- Chrome
- Slack
- Email
- Streaming services

5. **Check internet speed** (if using cloud services)
```bash
# macOS
networkQuality  # or use speedtest-cli
```

---

## 7. 🔐 VOICE AUTHENTICATION NOT WORKING

### Symptoms:
- Says "Jarvis" and gives "Access denied"
- Voice profile not saved
- Always fails auth

### Diagnosis:

#### **Check Voice Profile Exists**
```bash
ls -la voice_profile.npy
# Should exist (binary file)
```

#### **Test Voice Encoder**
```python
from resemblyzer import VoiceEncoder
import sounddevice as sd
import scipy.io.wavfile as wav
from resemblyzer import preprocess_wav

encoder = VoiceEncoder()

# Record test voice
print("Recording...")
audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
sd.wait()
wav.write("voice_test.wav", 16000, audio)

# Test encoding
wav_data = preprocess_wav("voice_test.wav")
embedding = encoder.embed_utterance(wav_data)
print(f"Embedding shape: {embedding.shape}")
print(f"Embedding: {embedding}")
```

### Solutions:

1. **Re-enroll voice** (auth.py):
```bash
python3 -c "from auth import enroll_voice; enroll_voice()"
# Speak clearly 3 times
```

2. **Lower similarity threshold** (auth.py):
```python
return similarity > 0.30  # Was 0.35 - more permissive
```

3. **Better microphone**
- Background noise affects encoding
- Use quiet room
- Use quality microphone

4. **Clear old profile first**
```bash
rm voice_profile.npy
python3 -c "from auth import enroll_voice; enroll_voice()"
```

---

## 8. 💾 MEMORY NOT WORKING

### Symptoms:
- "Remember my name is John" says "Got it"
- "What is my name" says "I don't know"
- Memory file corrupted

### Diagnosis:

#### **Check Memory File**
```bash
cat memory.json  # Should be valid JSON
# Or
python3 -c "import json; print(json.load(open('memory.json')))"
```

#### **Test Memory Functions Directly**
```python
from memory import remember, recall, get_all_memory

# Test remember
remember("test_key", "test_value")

# Test recall
result = recall("test_key")
print(f"Recalled: {result}")  # Should print "test_value"

# View all
print(get_all_memory())
```

### Solutions:

1. **Reset memory**
```bash
rm memory.json
# System will recreate on first remember()
```

2. **Fix corrupted JSON**
```bash
python3
>>> import json
>>> # Edit memory.json in text editor
>>> # Make sure it's valid JSON
```

3. **Check file permissions**
```bash
chmod 644 memory.json
```

---

## 🎯 SYSTEMATIC DEBUGGING

### When in doubt, follow this process:

1. **Check logs** - Read terminal output carefully
2. **Verify components** - Run verify_system.py
3. **Test in isolation** - Test each part separately
4. **Add debug prints** - Insert print statements
5. **Monitor resources** - Check CPU/memory usage
6. **Check configuration** - Review settings
7. **Search known issues** - Check this guide
8. **Isolate the problem** - Does it happen always? Sometimes?

### Useful Debug Commands:

```bash
# Kill all Python processes (⚠️ careful!)
pkill -f python3

# Check if Ollama is running
ps aux | grep ollama

# Test connectivity
nc -zv localhost 11434

# View system logs (macOS)
log stream --predicate 'process == "Python"'

# Memory usage
top -o rsize

# Network activity
sudo tcpdump -i en0  # Your interface
```

---

## 🚨 Emergency Recovery

If everything is broken:

```bash
# 1. Stop everything
pkill -f python3
pkill -f ollama

# 2. Clean up
rm memory.json
rm voice_profile.npy

# 3. Restart fresh
ollama serve  # Terminal 1
python3 main.py  # Terminal 2

# 4. Re-enroll
# When prompted, say "Jarvis" for voice auth setup
```

---

**Still stuck? Check ARCHITECTURE.md for detailed explanations!** 🚀

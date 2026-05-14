# 🚀 JARVIS OS - QUICK START GUIDE

## 📋 Prerequisites

### 1. **Ollama** (The AI Engine)
- Download from: https://ollama.ai
- Start it: `ollama serve` (runs on localhost:11434)
- Add the phi model: `ollama pull phi`

### 2. **Python 3.8+**
```bash
python3 --version
```

### 3. **Required Libraries**
```bash
pip install sounddevice openai-whisper pyttsx3 requests numpy scipy resemblyzer pywhatkit
```

---

## ✅ System Check

Before running, verify everything is installed:

```bash
python3 verify_system.py
```

Output should show all ✅ checks passing.

---

## 🎬 Running JARVIS OS

### **Terminal 1: Start Ollama**
```bash
ollama serve
```

Wait for:
```
Listening on 127.0.0.1:11434
```

### **Terminal 2: Start JARVIS**
```bash
python3 main.py
```

Expected output:
```
============================================================
🚀 JARVIS OS INITIALIZING...
============================================================
✅ Listener started
🔊 Jarvis is ready
```

---

## 🎙️ How to Use

### **Activation**
Say: "**Jarvis**"
→ Verifies your voice
→ Responds "Access granted" (if voice matches)

### **Ask Questions**
Say: "**What is machine learning?**"
→ Sends to AI (Ollama)
→ Speaks response

### **System Commands**
Say: "**Open Chrome**" or "**Play music on YouTube**"
→ Executes command immediately

### **Memory**
Say: "**Remember my name is John**"
→ Stores in memory.json
→ Later: "**What is my name?**" → "John"

### **Deactivate**
Say: "**Sleep**"
→ Deactivates listening (saves battery)

---

## 🔍 What's Happening Behind the Scenes

```
Input Flow:
🎤 Microphone (3 sec recording)
   ↓
🧠 Whisper (speech-to-text)
   ↓
🔍 Intent Classification (command vs AI)
   ↓
⚙️ Execute (command) OR 🤖 AI (question)
   ↓
🔊 pyttsx3 (text-to-speech response)
```

---

## ⚠️ Common Issues

### **"AI is not responding"**
- Check Ollama is running: `curl http://localhost:11434/api/generate`
- Restart Ollama: `ollama serve`
- Verify model: `ollama list` (should show phi)

### **"Microphone not working"**
- Check permissions (macOS: System Preferences → Security & Privacy → Microphone)
- Test audio: `python3 -c "import sounddevice; print(sounddevice.query_devices())"`

### **"Doesn't understand my voice"**
- Speak clearly and slowly
- Minimize background noise
- Increase speaker volume for initial enrollment

### **"Wrong commands executing"**
- Could be Whisper transcription error
- Check logs to see what was transcribed
- Speak more clearly

---

## 📊 Files Explained

| File | Purpose |
|------|---------|
| **main.py** | Main event loop (state machine) |
| **brain.py** | AI integration (Ollama requests) |
| **voice.py** | Microphone input + speaker output |
| **listener.py** | Background audio capture thread |
| **commands.py** | System command execution |
| **auth.py** | Voice authentication |
| **memory.py** | Persistent memory (JSON) |
| **intent.py** | Intent classification |
| **verify_system.py** | System health check |

---

## 🔧 Configuration

### **Adjust voice input timeout** (voice.py)
```python
def listen(timeout=3):  # Change 3 to desired seconds
```

### **Adjust AI response timeout** (main.py)
```python
ai_response = wait_for_ai_response(timeout=15)  # Change 15
```

### **Change Ollama model** (brain.py)
```python
"model": "phi"  # Change to: neural-chat, orca-mini, etc.
```

### **Adjust speaking speed** (voice.py)
```python
engine.setProperty('rate', 180)  # Lower = slower, higher = faster
```

### **Add more junk filters** (voice.py)
```python
JUNK_PHRASES = [
    "existing phrases...",
    "your new phrase"
]
```

---

## 🚀 Next Steps

1. **Test all features**
   - Wake word activation
   - Simple questions (what is AI?)
   - Commands (open chrome, youtube)
   - Memory (remember/recall)

2. **Monitor logs**
   - Watch for errors
   - Check AI response times
   - Verify voice transcription

3. **Optimize**
   - Adjust timeouts for your network
   - Fine-tune interrupt sensitivity
   - Add custom commands

4. **Extend**
   - Add more commands in commands.py
   - Add custom actions
   - Connect to APIs (weather, news, etc.)

---

## 📞 Debugging

### **Enable verbose logging**
Modify main.py to add more prints:
```python
print(f"DEBUG: state = {state}")
print(f"DEBUG: current_input = {current_input}")
```

### **Test components separately**

**Test Whisper:**
```python
import whisper
model = whisper.load_model("small")
result = model.transcribe("audio.wav")
print(result["text"])
```

**Test Ollama:**
```bash
curl http://localhost:11434/api/generate \
  -d '{"model":"phi","prompt":"Hello"}'
```

**Test Microphone:**
```python
import sounddevice as sd
print(sd.query_devices())
```

---

## 🎯 Performance Tips

1. **Faster startup**: Pre-load Whisper model
2. **Faster AI**: Use smaller model (orca-mini instead of phi)
3. **Faster voice**: Increase TTS rate
4. **Less noise**: Better microphone or noise-canceling headset

---

## 🆘 Getting Help

1. Check ARCHITECTURE.md for detailed explanations
2. Review logs for error messages
3. Run verify_system.py to check setup
4. Test individual components in isolation

---

**Happy voice commanding! 🎤🤖**

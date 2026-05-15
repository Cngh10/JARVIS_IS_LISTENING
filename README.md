#  JARVIS 

**A fully real-time, voice-first AI assistant for macOS**

---

## 🎯 What Is JARVIS OS?

JARVIS is a standalone voice assistant that runs locally on your macOS machine. It listens continuously, understands voice commands, answers questions using AI, and executes system tasks—all without internet.

### **Key Features:**
- 🎤 **Always Listening** - Continuous background audio capture
- 🧠 **AI Powered** - Ollama (phi model) for intelligent responses
- ⚡ **Real-time** - Instant command execution and responses
- 🔐 **Secure** - Voice authentication, local processing
- 💾 **Memory** - Persistent storage of preferences
- 🌍 **Offline** - No internet required (except for web commands)

---


**See [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for details.**

---

## 📚 Documentation

### **Quick Start** (5 minutes)
→ [QUICKSTART.md](QUICKSTART.md)
- Installation
- Running the system
- Basic usage examples

### **Architecture Deep-Dive** (Technical)
→ [ARCHITECTURE.md](ARCHITECTURE.md)
- Thread layout
- Data flow
- Why the system was failing
- How fixes work

### **Deployment Guide** (Step-by-step)
→ [DEPLOYMENT.md](DEPLOYMENT.md)
- Pre-deployment checks
- Component testing
- Performance benchmarks
- Configuration tuning

### **Troubleshooting** (Debug & Fix)
→ [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Problem diagnosis steps
- Solution strategies
- Emergency recovery
- Advanced debugging

### **Implementation Details** (What Changed)
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- Files modified
- Before/after comparison
- Testing checklist
- Roadmap for Phase 20

---

## 🚀 Quick Start

### **1. Install Dependencies**
```bash
pip3 install sounddevice openai-whisper pyttsx3 requests numpy scipy resemblyzer pywhatkit
```

### **2. Verify System**
```bash
python3 verify_system.py
# Should show all ✅ checks passing
```

### **3. Start Services**

**Terminal 1:**
```bash
ollama serve
# Waits for: Listening on 127.0.0.1:11434
```

**Terminal 2:**
```bash
python3 main.py
# Waits for: ✅ Listener started
```

### **4. Use Jarvis**
```
Say: "Jarvis"              → Activates voice auth
Say: "What is Python?"     → Asks AI, gets response
Say: "Open Chrome"         → Executes command
Say: "Remember X is Y"     → Stores in memory
Say: "What is my X?"       → Recalls from memory
Say: "Sleep"               → Deactivates
```

---

## 🏗️ Architecture Overview

### **Core Components:**

```
┌─────────────────────────────────────────┐
│        🎤 LISTENER THREAD               │
│  Captures audio, transcribes with       │
│  Whisper, updates LATEST_INPUT          │
└────────────────┬────────────────────────┘
                 │
                 ↓ (thread-safe)
┌─────────────────────────────────────────┐
│     📥 MAIN LOOP (State Machine)        │
│  - Validates input                      │
│  - Detects intent (command vs AI)       │
│  - Routes to appropriate handler        │
│  - Waits for responses                  │
└────────────┬──────────────────┬─────────┘
             │                  │
             ↓                  ↓
    ┌─────────────────┐  ┌──────────────┐
    │ ⚙️ COMMANDS     │  │ 🤖 AI        │
    │ Execute system  │  │ Ollama       │
    │ commands        │  │ request      │
    │ immediately     │  │ thread       │
    └─────────────────┘  └──────────────┘
             │                  │
             └────────┬─────────┘
                      ↓
            ┌──────────────────┐
            │   🔊 VOICE       │
            │   TTS Response   │
            └──────────────────┘
```

### **Thread Safety:**
- ✅ LISTENER_LOCK protects LATEST_INPUT
- ✅ AI_LOCK protects AI_RESPONSE  
- ✅ AI_READY_EVENT signals response ready
- ✅ SPEAK_LOCK protects TTS state
- ✅ No busy-waiting, proper blocking

---

## 📊 Performance

### **Latency:**
- Voice input: 3 seconds (configurable)
- Whisper: 1-2 seconds
- Ollama: 5-15 seconds (depends on prompt)
- **Total: 9-20 seconds** ✅ (acceptable for voice assistant)

### **Resource Usage:**
- Memory: ~500MB (Whisper) + ~400MB (Ollama)
- CPU: 1-2 cores idle, 2-4 cores during processing
- Network: Local only (no internet required)

### **Reliability:**
- ✅ Handles Ollama disconnection gracefully
- ✅ Recovers from microphone errors
- ✅ Timeouts prevent hanging
- ✅ All threads are daemon (clean shutdown)

---

## 🎛️ Configuration

### **Adjust Response Time:**
```python
# main.py - increase if Ollama is slow
ai_response = wait_for_ai_response(timeout=20)  # Was 15
```

### **Adjust Voice Speed:**
```python
# voice.py - adjust speaking speed
engine.setProperty('rate', 200)  # 150-200 is normal
```

### **Use Faster AI Model:**
```python
# brain.py - trade accuracy for speed
"model": "neural-chat"  # Faster than phi
```

### **Reduce Noise Sensitivity:**
```python
# listener.py - less interruption from background noise
DEBOUNCE_MS = 500  # Was 300 - more debouncing
```

---

## 🧪 System Verification

Before running, verify everything is set up:

```bash
python3 verify_system.py

# Checks:
# ✅ Python version
# ✅ All required libraries
# ✅ Microphone available
# ✅ Ollama running
# ✅ Ollama has phi model
# ✅ All project files
```

---

## 🔐 Security & Privacy

- ✅ **Local Processing** - No data sent to cloud
- ✅ **Voice Authentication** - Only you can activate
- ✅ **Encrypted Storage** - Memory stored locally
- ✅ **No Logging** - Conversations not recorded
- ✅ **Open Source** - Full code transparency

---

## 🛠️ File Structure

```
/Users/chandanmahato/JARVIS/
├── main.py                  # Main event loop (state machine)
├── brain.py                 # AI integration (Ollama)
├── voice.py                 # Microphone & speaker control
├── listener.py              # Background audio capture
├── commands.py              # System command execution
├── auth.py                  # Voice authentication
├── memory.py                # Persistent memory (JSON)
├── intent.py                # Intent classification
├── memory.json              # Stored memories
├── voice_profile.npy        # Voice authentication profile
│
├── QUICKSTART.md            # Quick start guide
├── ARCHITECTURE.md          # Technical architecture
├── DEPLOYMENT.md            # Deployment checklist
├── TROUBLESHOOTING.md       # Debugging guide
├── IMPLEMENTATION_SUMMARY.md # What changed and why
└── verify_system.py         # System health check
```

---

## FAQ

### **Q: Does it require internet?**
**A:** No. Everything runs locally. Web commands (YouTube, Google) require internet.

### **Q: Can I customize commands?**
**A:** Yes! Edit `commands.py` to add your own.

### **Q: Is my voice data private?**
**A:** Completely. Voice is processed locally, never stored or sent anywhere.

### **Q: What if Ollama stops?**
**A:** System will gracefully fail with "Cannot connect to Ollama" message. Restart Ollama and try again.

### **Q: Can I use a different AI model?**
**A:** Yes. Install any Ollama model and change `"model": "phi"` in brain.py.

### **Q: Why is AI response sometimes slow?**
**A:** Depends on your machine and the model. Phi model is balanced. Use neural-chat for speed, dolphin for quality.

### **Q: How do I make it always-on?**
**A:** See DEPLOYMENT.md for autostart setup.

---

## 🐛 Troubleshooting

### **AI Not Responding?**
→ See [TROUBLESHOOTING.md - AI NOT RESPONDING](TROUBLESHOOTING.md#1-ai-not-responding)

### **Microphone Issues?**
→ See [TROUBLESHOOTING.md - NO MICROPHONE INPUT](TROUBLESHOOTING.md#5-no-microphone-input)

### **Performance Slow?**
→ See [TROUBLESHOOTING.md - PERFORMANCE ISSUES](TROUBLESHOOTING.md#6-performance-issues)

### **Something Else?**
→ Run `python3 verify_system.py` and check logs

---

## 📞 Support

1. **Check Documentation**
   - QUICKSTART.md (quick answers)
   - TROUBLESHOOTING.md (debugging)
   - ARCHITECTURE.md (technical details)

2. **Run System Check**
   ```bash
   python3 verify_system.py
   ```

3. **Read the Logs**
   ```bash
   # Terminal output shows error messages
   # Look for marks to find issues
   ```

4. **Isolate the Problem**
   - Test Whisper alone
   - Test Ollama with curl
   - Test microphone separately

---

## 💡 Tips & Tricks

### **Faster Responses:**
- Use neural-chat model (faster)
- Reduce listening timeout to 2 seconds
- Close other applications

### **Better Accuracy:**
- Speak clearly and slowly
- Use better microphone
- Minimize background noise
- Use dolphin model (more accurate)

### **Reduce False Wakeups:**
- Increase DEBOUNCE_MS in listener.py
- Improve microphone positioning
- Use noise-canceling headset

### **Save Battery:**
- Use "Sleep" command to deactivate
- Reduce listening timeout
- Use lighter model (neural-chat)

---

## 🎓 Learning Resources

### **Understanding the System:**
1. Read QUICKSTART.md (5 min overview)
2. Read ARCHITECTURE.md (understand design)
3. Read TROUBLESHOOTING.md (know what can go wrong)
4. Study the code (main.py, brain.py)

### **Modifying the System:**
1. Add custom commands in commands.py
2. Add more intent detection in intent.py
3. Add memory features in memory.py
4. Extend auth.py for more auth methods

---

## 📝 License

This project is created for educational purposes.

---

## 🎉 You're All Set!

1.  Code is fixed and ready
2.  All critical issues resolved
3.  Documentation is comprehensive
4.  Testing guidelines provided

**Next steps:**
1. Run `python3 verify_system.py`
2. Start Ollama: `ollama serve`
3. Start JARVIS: `python3 main.py`
4. Say "Jarvis" to activate

---


*Always listening. Always ready. Always learning.*
# HELLO-JARVIS

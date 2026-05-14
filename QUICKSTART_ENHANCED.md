# 🚀 JARVIS Enhanced - Quick Start Guide

Get JARVIS Enhanced with environment sensing up and running in 5 minutes.

## 📋 Prerequisites

### 1. **Python 3.8+**
```bash
python3 --version
```

### 2. **Required Libraries**
```bash
pip install -r requirements.txt
```

### 3. **Hardware**
- Camera (webcam)
- Microphone
- Speakers

---

## ✅ System Check

Before running, verify everything is installed:

```bash
python test_enhanced.py
```

This will test:
- ✅ Camera
- ✅ Microphone
- ✅ Voice output
- ✅ Environment sensors
- ✅ Guidance system

---

## 🔑 API Configuration

### Anthropic Claude API (Required for AI)

1. Get API key from: https://console.anthropic.com/
2. Create `.env` file:
```bash
cp .env.example .env
```
3. Add your API key:
```
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

---

## 🎬 Running JARVIS Enhanced

```bash
python jarvis_enhanced.py
```

Expected output:
```
======================================================================
🚀 JARVIS ENHANCED - Environment Sensing & Guidance
======================================================================
📡 Starting sensors...
✅ Environment sensing started
✅ Audio sensing started
✅ Guidance system started
🎤 Starting voice listener...
🔊 Speaking startup message...
Jarvis enhanced is ready. Environment sensors active.

======================================================================
🎯 SYSTEMS ONLINE
======================================================================
✅ Environment sensing: Active
✅ Audio sensing: Active
✅ Guidance system: Active
✅ Voice listener: Active
✅ Claude AI: Active
======================================================================
```

---

## 🎙️ How to Use

### **Activation**
Say: "**Jarvis**"
→ Verifies your voice
→ Responds "Access granted"

### **Navigation Guidance**
Say: "**Start guidance**"
→ Enables continuous navigation assistance
→ JARVIS will warn you of obstacles and hazards

Say: "**Stop guidance**"
→ Disables navigation assistance

### **Environment Awareness**
Say: "**What's around me?**"
→ JARVIS describes your environment
→ Lists nearby obstacles
→ Reports audio conditions

### **System Commands**
Say: "**Open Safari**"
→ Opens Safari browser

Say: "**Search for weather**"
→ Searches the web

Say: "**Run ls -la**"
→ Executes terminal command

### **Questions**
Say: "**What is the capital of France?**"
→ JARVIS answers using Claude AI

### **Deactivate**
Say: "**Sleep**"
→ Deactivates JARVIS

---

## 🌍 Environment Sensing Features

### **Obstacle Detection**
- Detects obstacles in your path
- Estimates distance to obstacles
- Classifies obstacle types (walls, objects, doors)
- Provides danger level warnings

### **Audio Awareness**
- Detects emergency sounds (sirens, alarms)
- Identifies vehicles approaching
- Locates sound direction
- Monitors noise levels

### **Navigation Guidance**
- Safe path recommendations
- Turn-by-turn directions
- Obstacle avoidance
- Emergency alerts

---

## ⚠️ Common Issues

### **"Camera not working"**
- Check camera permissions (macOS: System Preferences → Security & Privacy → Camera)
- Ensure camera is not in use by another app
- Try different camera index

### **"Microphone not working"**
- Check microphone permissions (macOS: System Preferences → Security & Privacy → Microphone)
- Ensure microphone is not muted
- Test with system sound settings

### **"Claude API not working"**
- Verify API key in `.env` file
- Check internet connection
- Ensure API credits are available

### **"High CPU usage"**
- Reduce camera resolution
- Increase processing intervals
- Disable unused features

---

## 📊 Files Explained

| File | Purpose |
|------|---------|
| **jarvis_enhanced.py** | Main enhanced system with sensors |
| **environment_sensor.py** | Computer vision for obstacle detection |
| **audio_sensor.py** | Audio environment sensing |
| **guidance_system.py** | Navigation guidance logic |
| **claude_integration.py** | Claude AI integration |
| **test_enhanced.py** | System test script |

---

## 🔧 Configuration

### **Adjust guidance interval** (jarvis_enhanced.py)
```python
self.guidance_interval = 3.0  # Seconds between guidance updates
```

### **Change camera index** (environment_sensor.py)
```python
self.camera_index = 0  # Try 1, 2, etc. if 0 doesn't work
```

### **Adjust danger thresholds** (environment_sensor.py)
```python
self.danger_thresholds = {
    DangerLevel.SAFE: 3.0,    # meters
    DangerLevel.CAUTION: 2.0,
    DangerLevel.WARNING: 1.0,
    DangerLevel.DANGER: 0.5
}
```

### **Change voice rate** (voice.py)
```python
engine.setProperty('rate', 150)  # Lower = slower
```

---

## 🚀 Next Steps

1. **Test all features**
   - Wake word activation
   - Navigation guidance
   - Environment awareness
   - System commands
   - AI questions

2. **Monitor performance**
   - Check CPU usage
   - Verify sensor accuracy
   - Test response times

3. **Customize**
   - Adjust guidance sensitivity
   - Add custom commands
   - Modify voice settings

---

## 🎯 Performance Tips

1. **Faster startup**: Use smaller Whisper model
2. **Lower CPU usage**: Increase guidance interval
3. **Better accuracy**: Use higher resolution camera
4. **Clearer audio**: Use external microphone

---

## 🆘 Getting Help

1. Run `python test_enhanced.py` to diagnose issues
2. Check the test output for specific errors
3. Review system logs for detailed information
4. Ensure all permissions are granted

---

**Happy navigating! 🧭🤖**

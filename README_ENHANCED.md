# 🚀 JARVIS Enhanced - Environment Sensing & Guidance

Iron Man level AI assistant with real-time environment sensing and navigation guidance.

## Features

### 🌍 Environment Sensing
- **Computer Vision**: Real-time obstacle detection and distance estimation
- **Audio Analysis**: Sound source localization and emergency detection
- **Path Analysis**: Safe path recommendations and navigation assistance

### 🧭 Guidance System
- **Real-time Guidance**: Continuous navigation assistance
- **Emergency Alerts**: Immediate warnings for dangerous situations
- **Obstacle Avoidance**: Smart path recommendations
- **Audio Awareness**: Vehicle, siren, and alarm detection

### 🎤 Voice Interaction
- **Wake Word**: "Jarvis" activation
- **Voice Commands**: Natural language control
- **Interruption Handling**: Stop responses with "stop" or "wait"
- **Voice Authentication**: Optional voice print verification

### 🧠 AI Intelligence
- **Claude Integration**: Advanced reasoning with Anthropic Claude
- **Context Awareness**: Conversation memory and context
- **Smart Responses**: Intelligent answers to questions

### ⚙️ System Control
- **App Control**: Open/close applications
- **File Operations**: Navigate and manage files
- **Web Search**: Search the internet
- **Terminal Commands**: Execute system commands

## Installation

### Prerequisites
- Python 3.8+
- macOS/Linux/Windows
- Camera (for environment sensing)
- Microphone (for voice interaction)

### Setup

1. **Clone or navigate to the jarvis directory**
```bash
cd jarvis
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Required API Keys

- **Anthropic API Key**: For Claude AI integration
  - Get from: https://console.anthropic.com/
  - Set in `.env`: `ANTHROPIC_API_KEY=your_key_here`

- **Picovoice Access Key**: For wake word detection (optional)
  - Get from: https://console.picovoice.ai/
  - Set in `.env`: `PORCUPINE_ACCESS_KEY=your_key_here`

## Usage

### Start Enhanced JARVIS

```bash
python jarvis_enhanced.py
```

### Voice Commands

- **"Jarvis"** - Activate JARVIS
- **"Start guidance"** - Enable continuous navigation guidance
- **"Stop guidance"** - Disable navigation guidance
- **"What's around me"** - Get environment summary
- **"Help"** - Get help information
- **"Sleep"** or **"Stop"** - Deactivate JARVIS

### System Commands

- **"Open [app]"** - Open an application
- **"Close [app]"** - Close an application
- **"Search for [query]"** - Search the web
- **"Run [command]"** - Execute terminal command

### Questions

Ask any question and JARVIS will provide intelligent answers using Claude AI.

## System Requirements

### Minimum
- 4GB RAM
- Dual-core CPU
- 720p webcam
- Built-in microphone

### Recommended
- 8GB+ RAM
- Quad-core CPU
- 1080p webcam
- External microphone
- GPU (for faster computer vision)

## Troubleshooting

### Camera not working
- Check camera permissions
- Ensure camera is not in use by another app
- Try different camera index (modify `camera_index` in code)

### Microphone not working
- Check microphone permissions
- Ensure microphone is not muted
- Test with system sound settings

### Claude API not working
- Verify API key is correct
- Check internet connection
- Ensure API credits are available

### High CPU usage
- Reduce camera resolution
- Increase processing intervals
- Disable unused features

## Architecture

```
jarvis/
├── jarvis_enhanced.py      # Main enhanced system
├── environment_sensor.py   # Computer vision sensing
├── audio_sensor.py         # Audio environment sensing
├── guidance_system.py      # Navigation guidance
├── claude_integration.py  # Claude AI integration
├── voice.py               # Text-to-speech
├── listener.py            # Speech recognition
├── commands.py            # System commands
├── auth.py               # Voice authentication
├── memory.py             # Memory system
└── main.py              # Original JARVIS system
```

## Safety Features

- **Emergency Detection**: Automatic alerts for sirens and alarms
- **Obstacle Warning**: Distance-based danger levels
- **Safe Path**: Always recommends safest route
- **Interruptible**: Stop any response instantly

## Future Enhancements

- [ ] GPS integration for outdoor navigation
- [ ] Smart home device control
- [ ] Weather integration
- [ ] Calendar and reminders
- [ ] Mobile app interface
- [ ] Multi-language support

## License

This project is for educational and personal use.

## Credits

Inspired by Iron Man's JARVIS AI assistant.

Built with:
- Anthropic Claude API
- OpenCV
- SoundDevice
- FastAPI
- React (for web interface)

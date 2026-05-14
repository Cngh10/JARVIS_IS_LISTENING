#!/usr/bin/env python3
"""
🧪 JARVIS OS - SYSTEM VERIFICATION SCRIPT

This script checks if all components are properly installed and configured.
Run this before starting main.py to diagnose issues.
"""

import sys
import subprocess
import json

print("\n" + "="*70)
print("🧪 JARVIS OS SYSTEM VERIFICATION")
print("="*70 + "\n")

CHECKS = []


def check(name, test_func):
    """Helper to run and record checks."""
    try:
        result = test_func()
        status = "✅" if result else "❌"
        CHECKS.append((name, status, result))
        print(f"{status} {name}")
        return result
    except Exception as e:
        CHECKS.append((name, "❌", False))
        print(f"❌ {name}: {str(e)[:50]}")
        return False


# ═══════════════════════════════════════════════════════════════
# 🐍 PYTHON ENVIRONMENT
# ═══════════════════════════════════════════════════════════════

print("\n[1] PYTHON ENVIRONMENT")

check("Python version", lambda: sys.version_info >= (3, 8))

try:
    import sounddevice
    check("sounddevice library", lambda: True)
except:
    check("sounddevice library", lambda: False)

try:
    import whisper
    check("Whisper (OpenAI)", lambda: True)
except:
    check("Whisper (OpenAI)", lambda: False)

try:
    import pyttsx3
    check("pyttsx3 (TTS)", lambda: True)
except:
    check("pyttsx3 (TTS)", lambda: False)

try:
    import requests
    check("requests library", lambda: True)
except:
    check("requests library", lambda: False)

try:
    import numpy
    check("NumPy", lambda: True)
except:
    check("NumPy", lambda: False)

try:
    import scipy
    check("SciPy", lambda: True)
except:
    check("SciPy", lambda: False)

try:
    from resemblyzer import VoiceEncoder
    check("Resemblyzer (voice auth)", lambda: True)
except:
    check("Resemblyzer (voice auth)", lambda: False)

try:
    import pywhatkit
    check("PyWhatsKit (commands)", lambda: True)
except:
    check("PyWhatsKit (commands)", lambda: False)


# ═══════════════════════════════════════════════════════════════
# 🎤 MICROPHONE & AUDIO
# ═══════════════════════════════════════════════════════════════

print("\n[2] MICROPHONE & AUDIO")

def check_mic():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        return devices is not None and len(devices) > 0
    except:
        return False

check("Microphone detected", check_mic)


# ═══════════════════════════════════════════════════════════════
# 🤖 OLLAMA SERVICE
# ═══════════════════════════════════════════════════════════════

print("\n[3] OLLAMA SERVICE")

def check_ollama_connection():
    try:
        import requests
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi",
                "prompt": "Hello",
                "stream": False
            },
            timeout=5
        )
        return res.status_code == 200
    except:
        return False

check("Ollama running on localhost:11434", check_ollama_connection)

def check_ollama_model():
    try:
        import requests
        res = requests.get("http://localhost:11434/api/tags", timeout=5)
        data = res.json()
        models = data.get("models", [])
        return any("phi" in m.get("name", "") for m in models)
    except:
        return False

check("Ollama has 'phi' model", check_ollama_model)


# ═══════════════════════════════════════════════════════════════
# 📁 PROJECT FILES
# ═══════════════════════════════════════════════════════════════

print("\n[4] PROJECT FILES")

import os

files_needed = [
    "main.py",
    "brain.py",
    "voice.py",
    "listener.py",
    "commands.py",
    "auth.py",
    "memory.py",
    "intent.py",
]

for file in files_needed:
    check(f"File exists: {file}", lambda f=file: os.path.exists(f))


# ═══════════════════════════════════════════════════════════════
# 📊 SUMMARY
# ═══════════════════════════════════════════════════════════════

print("\n" + "="*70)
print("📊 VERIFICATION SUMMARY")
print("="*70 + "\n")

passed = sum(1 for _, status, _ in CHECKS if status == "✅")
total = len(CHECKS)

print(f"Passed: {passed}/{total}")

if passed == total:
    print("\n✅ ALL CHECKS PASSED! Ready to run: python3 main.py\n")
    sys.exit(0)
else:
    print("\n❌ SOME CHECKS FAILED. See above for details.\n")
    print("Missing components? Install with:")
    print("  pip install sounddevice openai-whisper pyttsx3 requests numpy scipy resemblyzer pywhatkit")
    print("\nNeed Ollama? Download from: https://ollama.ai")
    print("Then: ollama pull phi\n")
    sys.exit(1)

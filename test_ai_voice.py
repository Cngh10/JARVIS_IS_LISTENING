#!/usr/bin/env python3
"""
✅ TEST JARVIS VOICE - Quick test of the fixed system
"""

from voice import speak
from brain import ask_ai_async, wait_for_ai_response, process_response
from validation import clean_response
import time

print("=" * 70)
print("✅ JARVIS VOICE - FIXED VERSION TEST")
print("=" * 70)

# Test 1: Greeting
print("\n🎤 TEST 1: Greeting")
print("-" * 70)
print("Speaking: 'Hello Chandan, what's up?'")
speak("Hello Chandan, what's up?")

# Test 2: Ask AI a question
print("\n🤖 TEST 2: AI Response (what is machine learning?)")
print("-" * 70)
print("Asking AI...")

ask_ai_async("what is machine learning?")
ai_response = wait_for_ai_response(timeout=10)

if ai_response:
    print(f"\n✅ AI Response: {ai_response[:100]}")
    
    # Clean it
    cleaned = clean_response(ai_response)
    print(f"🧹 Cleaned: {cleaned[:100]}")
    
    # Speak it
    print(f"\n🔊 Speaking response...")
    speak(cleaned)
else:
    print("⏱️  AI timeout - would speak: 'I am having trouble thinking right now.'")
    speak("I am having trouble thinking right now.")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
print("\n📝 Next step: Run 'python main.py' and test with voice input!")

#!/usr/bin/env python3
"""
🎤 COMPLETE JARVIS VOICE SYSTEM TEST
Tests greeting, AI responses, and voice quality
"""

from voice import speak
from brain import ask_ai_async, wait_for_ai_response, process_response
import time

print("=" * 70)
print("🎤 JARVIS VOICE SYSTEM - COMPLETE TEST")
print("=" * 70)

# Test 1: Greeting
print("\n✅ TEST 1: Greeting Response")
print("-" * 70)
print("Testing: 'Hello Chandan, what's up?'")
print("Expected: Clear, loud voice speaking the greeting\n")

speak("Hello Chandan, what's up?")
time.sleep(3)

# Test 2: Short AI answer
print("\n✅ TEST 2: Short AI Response")
print("-" * 70)
print("Testing: 'What is AI?'")
print("Expected: AI definition spoken clearly\n")

ask_ai_async("What is artificial intelligence?")
response = wait_for_ai_response(timeout=10)

if response:
    cleaned = process_response(response)
    print(f"Response: {cleaned[:100]}\n")
    speak(cleaned)
    time.sleep(4)
else:
    speak("I am having trouble thinking right now.")
    time.sleep(2)

# Test 3: Another question
print("\n✅ TEST 3: Another AI Response")
print("-" * 70)
print("Testing: 'What is machine learning?'")
print("Expected: Smooth response with complete answer\n")

ask_ai_async("What is machine learning?")
response = wait_for_ai_response(timeout=10)

if response:
    cleaned = process_response(response)
    print(f"Response: {cleaned[:100]}\n")
    speak(cleaned)
    time.sleep(4)
else:
    speak("I am having trouble thinking right now.")
    time.sleep(2)

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)

print("\n📝 OBSERVATIONS:")
print("  ✓ Greeting should be crystal clear")
print("  ✓ AI responses should start from beginning (not middle)")
print("  ✓ Responses should be complete and smooth")
print("  ✓ No breaking or jumping in speech")
print("  ✓ Voice should be loud and clear")

print("\n🚀 NEXT STEP: Run 'python main.py' for full voice control!")

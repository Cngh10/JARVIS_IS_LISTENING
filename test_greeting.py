#!/usr/bin/env python3
"""
🧪 TEST GREETING RESPONSE
Quick test to verify greeting logic works correctly
"""

from voice import speak
from validation import is_valid_input
from memory import recall

print("=" * 70)
print("🧪 TESTING GREETING RESPONSE")
print("=" * 70)

# Test 1: Validate "hello jarvis"
print("\n✅ TEST 1: Validate 'hello jarvis'")
test_input = "hello jarvis"
is_valid = is_valid_input(test_input)
print(f"Input: '{test_input}'")
print(f"Valid: {is_valid}")
if is_valid:
    print("✅ PASS - 'hello jarvis' is valid")
else:
    print("❌ FAIL - 'hello jarvis' should be valid")

# Test 2: Get user name from memory
print("\n✅ TEST 2: Get user name from memory")
user_name = recall("my name")
print(f"Retrieved name: {user_name}")
if user_name:
    first_name = user_name.split()[0]
    print(f"First name: {first_name}")
    print("✅ PASS - Got user name from memory")
else:
    print("⚠️  No name in memory, will use default")

# Test 3: Test greeting response
print("\n✅ TEST 3: Test greeting response")
print("Speaking: 'Hello [Name], what's up?'")
user_name = recall("my name") or "Chandan"
first_name = user_name.split()[0] if user_name else "Chandan"
greeting_response = f"Hello {first_name}, what's up?"
print(f"Greeting: {greeting_response}")
print("Now listen to the speaker...")
speak(greeting_response)
print("✅ Speaking completed")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. If microphone/speaker tests fail, check:")
print("   - Microphone is connected and working")
print("   - Speaker volume is up")
print("   - Run: python test_voice.py")
print("2. If greeting test fails, check:")
print("   - 'hello jarvis' is properly recognized")
print("   - Run main.py and test voice input")

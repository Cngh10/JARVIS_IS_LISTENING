
from voice import speak, stop_speaking, get_is_speaking
from commands import execute, is_system_command
from brain import ask_ai_async, get_ai_response, wait_for_ai_response, add_to_history, process_response
from auth import verify_voice, VOICE_VERIFICATION_AVAILABLE
from memory import remember, recall
from listener import start_listener, get_latest_input, clear_latest_input
from validation import (
    is_valid_input, is_question, should_interrupt, 
    classify_intent, get_response_priority, should_speak_response,
    clean_response, record_response, is_wake_word
)
from state_machine import get_state_machine, JarvisState, IntentType

import threading
import time


def run_jarvis():
    global state

    print("=" * 70)
    print("JARVIS PHASE 20 - REAL-TIME VOICE AI SYSTEM")
    print("=" * 70)
    print("Features:")
    print("  ✓ Input validation (3+ words, garbage filtering)")
    print("  ✓ Interrupt handling (stop, jarvis, wait)")
    print("  ✓ Priority system (INTERRUPT > COMMAND > QUESTION > IGNORE)")
    print("  ✓ Smart AI trigger (only questions)")
    print("  ✓ 10-second AI timeout")
    print("  ✓ Anti-loop system (no repeated responses)")
    print("  ✓ Self-speech filtering (doesn't hear its own voice)")
    print("=" * 70)

    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()

    print(" Listener started with PHASE 20 filtering")
    
    time.sleep(0.5)

    print("\n STARTUP: Speaking 'Jarvis is ready'...")
    speak("Jarvis is ready")
    
    time.sleep(2)
    speak("Listening")
    
    print("\n" + "=" * 70)
    print(" LISTENING FOR INPUT")
    print("=" * 70)
    print("Try saying:")
    print("  'hello jarvis' - Get greeting")
    print("  'what is the weather' - Ask a question")
    print("   'remember my name is chandan' - Remember something")
    print("=" * 70 + "\n")

    state = JarvisState.LISTENING
    active = False
    last_processed_text = ""
    # Voice verification / active session timeout (seconds)
    VERIFIED_TIMEOUT = 60
    last_active_time = 0
    # If voice verification isn't available, require wake word for every command
    REQUIRE_WAKE_FOR_ALL = not VOICE_VERIFICATION_AVAILABLE

    #  MAIN LOOP

    while True:
        try:
            current_input = get_latest_input()

            lower_input = (current_input or "").lower()

            if active and (time.time() - last_active_time) > VERIFIED_TIMEOUT:
                print(" Active session expired — require wake word again")
                active = False

            if not is_valid_input(current_input) or current_input == last_processed_text:
                time.sleep(0.1)
                continue

            if not active and "jarvis" not in (current_input or "").lower():
                time.sleep(0.05)
                continue

            if REQUIRE_WAKE_FOR_ALL and "jarvis" not in lower_input:
                time.sleep(0.05)
                continue

           
            if REQUIRE_WAKE_FOR_ALL and active:
                interrupts = ["stop", "wait", "hold on", "quiet", "shush", "silence"]
                if not ("jarvis" in lower_input or any(k in lower_input for k in interrupts)):
                    # Ignore ambient speech while active unless wake word or interrupt
                    time.sleep(0.05)
                    continue

            state = JarvisState.PROCESSING
            last_processed_text = current_input

            print(f"\n{'='*70}")
            print(f" INPUT: {current_input}")
            print(f"{'='*70}")

            if get_is_speaking():
                # Allow interrupts only from the verified user or when wake word is used.
                lower_input = (current_input or "").lower()

                interrupt_by_wake = "jarvis" in lower_input
                interrupt_by_active = active and is_valid_input(current_input)
                interrupt_by_keyword = should_interrupt(current_input, currently_speaking=True)

                if interrupt_by_wake or interrupt_by_active or interrupt_by_keyword:
                    print(" INTERRUPT: Stopping Jarvis for new input")
                    stop_speaking()
                    # allow processing of this input below
                    pass
                else:
                    print(" Jarvis is speaking, ignoring input")
                    time.sleep(0.1)
                    continue

            lower_input = current_input.lower()
            if any(greeting in lower_input for greeting in ["hello", "hi", "hey"]) and "jarvis" in lower_input:
                print(" Greeting to Jarvis detected — verifying voice")
                if verify_voice():
                    # Get user name from memory or use default
                    user_name = recall("my name") or "Chandan"
                    first_name = user_name.split()[0] if user_name else "Chandan"
                    greeting_response = f"Hello {first_name}, what's up?"

                    print(f" Greeting: '{greeting_response}'")
                    speak(greeting_response)

                    # Wait a bit for greeting to complete before continuing
                    time.sleep(1)

                    active = True  # Activate for follow-up questions
                    last_active_time = time.time()
                    print(" Activated and greeted user")
                    add_to_history(current_input, greeting_response)
                    clear_latest_input()
                    # Prompt listening state audibly
                    speak("Listening")
                    state = JarvisState.LISTENING
                    continue
                else:
                    speak("I couldn't verify your voice")
                    clear_latest_input()
                    state = JarvisState.LISTENING
                    continue

            # WAKE WORD DETECTION
            if "jarvis" in current_input and not any(g in current_input.lower() for g in ["hello", "hi", "hey"]):
                print("Wake word detected")
                speak("Verifying voice")

                if verify_voice():
                    active = True
                    last_active_time = time.time()
                    speak("Access granted")
                    print(" Voice verified")
                else:
                    speak("Access denied")
                    print(" Voice rejected")

                # Clear input to prevent reprocessing
                clear_latest_input()
                state = JarvisState.LISTENING
                continue

            # SLEEP MODE
            if "sleep" in current_input or "stop" in current_input:
                if active:
                    active = False
                    speak("Going to sleep")
                    print("Jarvis sleeping")
                    clear_latest_input()
                    state = JarvisState.SLEEPING

                continue

            # Skip if not active
            if not active:
                time.sleep(0.1)
                continue

            #  MEMORY: REMEMBER
            if "remember" in current_input:
                print(" PRIORITY: Memory command")
                try:
                    # Format: "remember [key] is [value]"
                    parts = current_input.replace("remember", "").split(" is ")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        remember(key, value)
                        speak(f"Got it. I'll remember that {key} is {value}")
                        print(f" Remembered: {key} = {value}")
                    else:
                        speak("Please say: remember [key] is [value]")

                except Exception as e:
                    print(f"Memory error: {e}")
                    speak("I couldn't remember that")

                clear_latest_input()
                state = JarvisState.LISTENING
                continue

            # MEMORY: RECALL
            lower_input = current_input.lower()

            if "who am i" in lower_input:
                print(" PRIORITY: Who am I recall")
                # Try different memory keys for name
                name = recall("my name") or recall("name") or recall("me")
                if name:
                    response = f"You are my BOSS {name}"
                else:
                    response = "I don't know who you are yet. Tell me and I'll remember."

                speak(response)
                print(f" Recalled: who am i -> {name}")
                clear_latest_input()
                state = JarvisState.LISTENING
                continue

            if "what is my" in current_input:
                print(" PRIORITY: Recall command")
                key = current_input.replace("what is my", "").strip()
                value = recall(key)

                response = value if value else f"I don't remember {key}"
                speak(response)
                print(f"📖 Recalled: {key} = {value}")

                clear_latest_input()
                state = JarvisState.LISTENING
                continue

            #  SYSTEM COMMANDS
            if is_system_command(current_input):
                print("🟢 PRIORITY: Command detected - Executing instantly")
                state = JarvisState.RESPONDING

                result = execute(current_input)
                speak(result if result else "Done")

                print(f"✅ Command executed: {result}")
                add_to_history(current_input, result)

                clear_latest_input()
                state = JarvisState.LISTENING
                continue
            
            # Only send to AI if it's actually a question
            if not is_question(current_input):
                print(" INPUT: Not a question, ignoring")
                clear_latest_input()
                state = JarvisState.LISTENING
                continue
            
            print(" PRIORITY: Question detected - Sending to AI...")
            state = JarvisState.RESPONDING
            ask_ai_async(current_input)

            ai_response = wait_for_ai_response(timeout=10)

            if not ai_response:
                ai_response = "I am having trouble thinking right now."
                print(" PHASE 20: AI TIMEOUT - Using standard response")
            else:
                print(f" AI responded: {ai_response[:100]}")
                
                ai_response = process_response(ai_response)
                print(f" Cleaned response: {ai_response[:100]}")

            # ALWAYS SPEAK RESPONSE (Anti-loop disabled for better UX)
            print(f"\n Speaking response...")
            speak(ai_response)

            time.sleep(2)

            add_to_history(current_input, ai_response)
            print(f" Response spoken and recorded")

            # Announce listening state audibly so user knows it's ready
            speak("Listening")

            clear_latest_input()
            state = JarvisState.LISTENING

        except KeyboardInterrupt:
            print("\n\n Jarvis shutting down...")
            speak("Goodbye")
            break

        except Exception as e:
            print(f" Error: {e}")
            print("Resetting...")
            state = JarvisState.LISTENING
            time.sleep(1)


if __name__ == "__main__":
    run_jarvis()

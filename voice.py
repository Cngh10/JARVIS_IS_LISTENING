try:
    import sounddevice as sd
    SD_AVAILABLE = True
except Exception:
    sd = None
    SD_AVAILABLE = False
    print("⚠️ sounddevice not available - microphone tests will be disabled")
import numpy as np
try:
    import whisper
except Exception:
    whisper = None
    print("⚠️ whisper not available - speech recognition disabled")
import tempfile
import scipy.io.wavfile as wav
import pyttsx3
import threading
import time
import sys
import subprocess
import shutil

# 🔥 Whisper model (lazy-loaded)
model = None
# Last text spoken by Jarvis (used to avoid hearing our own TTS)
LAST_SPOKEN_TEXT = ""
LAST_SPOKEN_TIME = 0.0
# Increase cooldown to better avoid capturing TTS echoes
SPEECH_COOLDOWN = 2.5  # seconds to ignore audio after speaking to avoid echoes

# 🔊 INITIALIZE TEXT-TO-SPEECH ENGINE (High Quality)
def init_engine():
    """Initialize pyttsx3 with optimal settings for clear, loud speech."""
    # If macOS `say` will be used, skip pyttsx3 initialization (avoids pyobjc dependency)
    if sys.platform == "darwin" and shutil.which("say") is not None:
        print("ℹ️ Using macOS 'say' for TTS; skipping pyttsx3 initialization")
        return None

    engine = None
    try:
        engine = pyttsx3.init()
    except Exception as e:
        print(f"⚠️ pyttsx3 init failed: {e}")
        return None
    
    # Set speech rate (slower = clearer) - 150 is good for clarity
    engine.setProperty('rate', 150)
    
    # Set volume (0.0 to 1.0) - maximum volume
    engine.setProperty('volume', 1.0)
    
    # Try to use a female voice for better clarity
    try:
        voices = engine.getProperty('voices')
        if voices:
            # Prefer female voice (usually index 1, male is 0)
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            else:
                engine.setProperty('voice', voices[0].id)
            print(f"✅ Voice selected: {voices[0].name if len(voices) > 0 else 'default'}")
    except Exception:
        pass
    
    return engine

# Prefer macOS `say` if available (more reliable audibility on macOS)
USE_SAY = sys.platform == "darwin" and shutil.which("say") is not None

engine = init_engine()

# 🎙️ SPEAKING STATE
SPEAK_LOCK = threading.Lock()
is_speaking = False
INTERRUPT = False


def get_is_speaking():
    """Get current speaking state (thread-safe)."""
    with SPEAK_LOCK:
        return is_speaking


def speak(text):
    """
    🎙️ SPEAK TEXT - Crystal Clear Voice (Iron Man Level)
    
    Features:
    - Speaks complete text from start to finish (no jumping/breaking)
    - Loud and clear voice (150 WPM, max volume)
    - Can be interrupted with "stop", "jarvis", "wait"
    - Updates is_speaking flag so listener doesn't process our voice
    - Runs in background thread (non-blocking)
    
    Args:
        text: Text to speak (complete sentence/paragraph)
    """
    global is_speaking, INTERRUPT
    
    if not text or not text.strip():
        print("⚠️ Empty text, skipping speak")
        return

    with SPEAK_LOCK:
        is_speaking = True
        INTERRUPT = False
        # Record last spoken text so listen() can ignore self-speech
        global LAST_SPOKEN_TEXT
        LAST_SPOKEN_TEXT = text.strip().lower()
        global LAST_SPOKEN_TIME
        LAST_SPOKEN_TIME = time.time()

    def run():
        global is_speaking, INTERRUPT, LAST_SPOKEN_TEXT

        try:
            text_to_speak = text.strip()
            print(f"\n🔊 SPEAKING (loud & clear): {text_to_speak[:80]}...")
            print(f"   [Full text: {len(text_to_speak)} characters]")
            
            # Clear any pending speech
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass
            time.sleep(0.1)
            
            if USE_SAY:
                # Use macOS `say` for reliable audible output
                print("   ▶️  Using macOS 'say' for TTS")
                try:
                    subprocess.run(["say", text_to_speak])
                except Exception as e:
                    print(f"❌ 'say' failed: {e}")
                    # Fallback to pyttsx3
                    if engine is not None:
                        engine.say(text_to_speak)
                        print(f"   ▶️  Playing audio via pyttsx3 fallback...")
                        engine.runAndWait()
                    else:
                        print("❌ No TTS engine available to speak the fallback text")
            else:
                # Queue the entire text at once (no splitting)
                if engine is None:
                    print("❌ No pyttsx3 engine available to speak this text")
                else:
                    engine.say(text_to_speak)
                    
                    # Run the engine until all queued speech is finished
                    print(f"   ▶️  Playing audio via pyttsx3...")
                    engine.runAndWait()
            
            print(f"✅ SPEECH COMPLETE")

        except Exception as e:
            print(f"❌ Speech error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            with SPEAK_LOCK:
                is_speaking = False
                INTERRUPT = False

            # clear last spoken text after finishing to be safe
            try:
                LAST_SPOKEN_TEXT = ""
            except Exception:
                pass
            try:
                LAST_SPOKEN_TIME = time.time()
            except Exception:
                pass

    # Start as daemon thread (non-blocking)
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    
    # Give thread a moment to start
    time.sleep(0.05)


def stop_speaking():
    """
    🛑 STOP SPEAKING IMMEDIATELY (Iron Man Level)
    
    Stops the speech engine and sets interrupt flag.
    Instant response with no delays.
    """
    global INTERRUPT, is_speaking
    
    print("🛑 INTERRUPT: Stopping speech immediately")
    
    INTERRUPT = True
    
    try:
        # If using macOS `say`, kill the say process
        if USE_SAY:
            try:
                subprocess.run(["killall", "say"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        engine.stop()
    except:
        pass
    
    time.sleep(0.1)
    
    with SPEAK_LOCK:
        is_speaking = False


# 🎤 LISTEN WITH CONFIDENCE FILTERING
JUNK_PHRASES = [
    "thanks for watching",
    "subscribe",
    "dadwis",
    "uh",
    "um",
    "hmm",
    "yeah",
    "okay",
    "bye bye",
    "see you",
    "next time",
    "one two three",
    "1 2 3",
    "test",
    "hello hello",
]


def is_junk_output(text):
    """
    🔥 PHASE 20: Filter garbage transcriptions
    
    Ignores:
    - Empty/too short input
    - Known junk phrases
    - Single words
    - Numbers only
    - Repeated words
    """
    if not text:
        return True
    
    text_lower = text.lower().strip()

    # Empty or too short
    if len(text_lower) < 3:
        return True

    # Known junk phrases
    for junk in JUNK_PHRASES:
        if junk in text_lower:
            return True

    # Single word (too short for meaningful command)
    if len(text_lower.split()) < 2:
        return True
    
    # Only numbers
    if text_lower.replace(" ", "").replace(".", "").isdigit():
        return True
    
    # Repeated words (same word multiple times)
    words = text_lower.split()
    if len(words) >= 3 and len(set(words)) == 1:
        return True

    return False


def listen(timeout=5, silence_threshold=0.035):
    """
    🎤 PHASE 20: Listen for audio input with self-speech filtering
    
    Args:
        timeout: Recording duration in seconds
        silence_threshold: Minimum audio level to process
    
    Returns:
        Transcribed text (empty string if junk, silent, or self-speech)
        
    Features:
    - Ignores self-generated speech
    - Filters garbage transcriptions
    - Only processes meaningful input
    """
    global is_speaking, model
    
    # 🛑 PHASE 20: If Jarvis is speaking, allow a short, low-latency
    # interrupt-only listen window so the user can say keywords like
    # "stop jarvish" to interrupt current speech. For non-interrupt
    # audio while speaking we still return empty to avoid self-speech.
    if get_is_speaking():
        try:
            # Short listen window for interrupts (1.5s)
            short_duration = min(1.5, timeout)
            fs = 16000
            recording = sd.rec(
                int(short_duration * fs),
                samplerate=fs,
                channels=1,
                dtype='float32'
            )
            sd.wait()

            if recording is None or len(recording) == 0:
                return ""

            audio = recording.flatten()
            audio_level = np.max(np.abs(audio))
            if audio_level < silence_threshold:
                return ""

            # Write temp file and transcribe like normal
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav.write(temp_file.name, fs, audio)

            # Lazy-load model if necessary
            if model is None:
                try:
                    model = whisper.load_model("small")
                except Exception:
                    return ""

            result = model.transcribe(temp_file.name, fp16=False, language="en")
            text = result.get("text", "").strip().lower()

            # If we're within a short cooldown after speaking, ignore to avoid
            # processing echoes of our own TTS.
            try:
                if LAST_SPOKEN_TIME and (time.time() - LAST_SPOKEN_TIME) < SPEECH_COOLDOWN:
                    print("🔇 Ignoring audio during post-speech cooldown")
                    return ""
            except Exception:
                pass

            # If the transcription matches or is similar to what Jarvis just spoke,
            # ignore it to avoid processing our own TTS or nearby audio copies.
            try:
                last_spoken = (LAST_SPOKEN_TEXT or "").strip().lower()
                if last_spoken:
                    words_a = set(w for w in last_spoken.split() if w)
                    words_b = set(w for w in text.split() if w)
                    if words_a and words_b:
                        intersection = len(words_a & words_b)
                        union = len(words_a | words_b)
                        similarity = intersection / union if union > 0 else 0.0
                    else:
                        similarity = 0.0

                    # If transcription is highly similar to last spoken text, ignore
                    if similarity > 0.5 or last_spoken in text:
                        # Debug log for developers
                        print(f"🔇 Ignoring self-speech transcription (similarity={similarity:.2f}): {text}")
                        return ""
            except Exception:
                pass

            # Only return text if it contains interrupt keywords to avoid
            # Jarvis hearing itself and acting on non-user speech.
            if any(k in text for k in ["stop", "hold on", "wait", "quiet", "jarvis", "stop jarvish", "stop jarvis"]):
                print(f"🎤 INTERRUPT DETECTED WHILE SPEAKING: {text}")
                return text
            return ""
        except Exception as e:
            print(f"Interrupt-listen error: {e}")
            return ""

    # If sounddevice is not available, skip listening
    if not SD_AVAILABLE:
        print("⚠️ listen() skipped: sounddevice not available")
        time.sleep(0.2)
        return ""

    # Lazy-load whisper model to avoid heavy initialization at import time
    if model is None:
        try:
            print("🔁 Loading Whisper model (lazy)...")
            model = whisper.load_model("small")
            print("✅ Whisper model loaded")
        except Exception as e:
            print(f"❌ Could not load Whisper model: {e}")
            return ""

    try:
        fs = 16000
        duration = timeout

        # 🎤 RECORD AUDIO
        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype='float32'
        )
        sd.wait()

        if recording is None or len(recording) == 0:
            return ""

        audio = recording.flatten()

        # 🔇 FILTER SILENCE
        audio_level = np.max(np.abs(audio))

        if audio_level < silence_threshold:
            return ""

        # 📊 NORMALIZE AUDIO
        audio = audio / audio_level if audio_level > 0 else audio

        # 💾 WRITE TO TEMP FILE
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(temp_file.name, fs, audio)

        # 🔥 TRANSCRIBE WITH WHISPER (FORCE ENGLISH)
        result = model.transcribe(
            temp_file.name,
            fp16=False,
            language="en"
        )

        text = result.get("text", "").strip().lower()

        # 🔍 GARBAGE FILTERING
        if is_junk_output(text):
            return ""

        if text:
            print(f"🎤 You: {text}")

        return text

    except Exception as e:
        print(f"Mic error: {e}")
        return ""
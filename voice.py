try:
    import sounddevice as sd
    SD_AVAILABLE = True
except Exception:
    sd = None
    SD_AVAILABLE = False
    print(" sounddevice not available - microphone tests will be disabled")
import numpy as np
try:
    import whisper
except Exception:
    whisper = None
    print(" whisper not available - speech recognition disabled")
import tempfile
import scipy.io.wavfile as wav
import pyttsx3
import threading
import time
import sys
import subprocess
import shutil

# Whisper model (lazy-loaded)
model = None
LAST_SPOKEN_TEXT = ""
LAST_SPOKEN_TIME = 0.0
SPEECH_COOLDOWN = 2.5  # seconds to ignore audio after speaking to avoid echoes

def init_engine():
    """Initialize pyttsx3 with optimal settings for clear, loud speech."""
    if sys.platform == "darwin" and shutil.which("say") is not None:
        print(" Using macOS 'say' for TTS; skipping pyttsx3 initialization")
        return None

    engine = None
    try:
        engine = pyttsx3.init()
    except Exception as e:
        print(f" pyttsx3 init failed: {e}")
        return None
    
    engine.setProperty('rate', 150)
    
    # Set volume (0.0 to 1.0) - maximum volume
    engine.setProperty('volume', 1.0)
    
    try:
        voices = engine.getProperty('voices')
        if voices:
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
            else:
                engine.setProperty('voice', voices[0].id)
            print(f"Voice selected: {voices[0].name if len(voices) > 0 else 'default'}")
    except Exception:
        pass
    
    return engine

USE_SAY = sys.platform == "darwin" and shutil.which("say") is not None

engine = init_engine()

SPEAK_LOCK = threading.Lock()
is_speaking = False
INTERRUPT = False


def get_is_speaking():
    with SPEAK_LOCK:
        return is_speaking


def speak(text):
    global is_speaking, INTERRUPT
    
    if not text or not text.strip():
        print(" Empty text, skipping speak")
        return

    with SPEAK_LOCK:
        is_speaking = True
        INTERRUPT = False
        global LAST_SPOKEN_TEXT
        LAST_SPOKEN_TEXT = text.strip().lower()
        global LAST_SPOKEN_TIME
        LAST_SPOKEN_TIME = time.time()

    def run():
        global is_speaking, INTERRUPT, LAST_SPOKEN_TEXT

        try:
            text_to_speak = text.strip()
            print(f"\n SPEAKING (loud & clear): {text_to_speak[:80]}...")
            print(f"   [Full text: {len(text_to_speak)} characters]")
            
            if engine is not None:
                try:
                    engine.stop()
                except Exception:
                    pass
            time.sleep(0.1)
            
            if USE_SAY:
                print(" Using macOS 'say' for TTS")
                try:
                    subprocess.run(["say", text_to_speak])
                except Exception as e:
                    print(f" 'say' failed: {e}")
                    # Fallback to pyttsx3
                    if engine is not None:
                        engine.say(text_to_speak)
                        print(f"  Playing audio via pyttsx3 fallback...")
                        engine.runAndWait()
                    else:
                        print("No TTS engine available to speak the fallback text")
            else:
                if engine is None:
                    print(" No pyttsx3 engine available to speak this text")
                else:
                    engine.say(text_to_speak)
                    
                    # Run the engine until all queued speech is finished
                    print(f" Playing audio via pyttsx3...")
                    engine.runAndWait()
            
            print(f"SPEECH COMPLETE")

        except Exception as e:
            print(f" Speech error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            with SPEAK_LOCK:
                is_speaking = False
                INTERRUPT = False

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
    global INTERRUPT, is_speaking
    
    print("INTERRUPT: Stopping speech immediately")
    
    INTERRUPT = True
    
    try:
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


# LISTEN WITH CONFIDENCE FILTERING
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
    if not text:
        return True
    
    text_lower = text.lower().strip()

    if len(text_lower) < 3:
        return True

    for junk in JUNK_PHRASES:
        if junk in text_lower:
            return True

    if len(text_lower.split()) < 2:
        return True
    
    if text_lower.replace(" ", "").replace(".", "").isdigit():
        return True
    
    # Repeated words
    words = text_lower.split()
    if len(words) >= 3 and len(set(words)) == 1:
        return True

    return False


def listen(timeout=5, silence_threshold=0.035):
    global is_speaking, model

    if get_is_speaking():
        try:
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

            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            wav.write(temp_file.name, fs, audio)

            if model is None:
                try:
                    model = whisper.load_model("small")
                except Exception:
                    return ""

            result = model.transcribe(temp_file.name, fp16=False, language="en")
            text = result.get("text", "").strip().lower()


            try:
                if LAST_SPOKEN_TIME and (time.time() - LAST_SPOKEN_TIME) < SPEECH_COOLDOWN:
                    print("Ignoring audio during post-speech cooldown")
                    return ""
            except Exception:
                pass

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
                        print(f"ignoring self-speech transcription (similarity={similarity:.2f}): {text}")
                        return ""
            except Exception:
                pass

            if any(k in text for k in ["stop", "hold on", "wait", "quiet", "jarvis", "stop jarvish", "stop jarvis"]):
                print(f" INTERRUPT DETECTED WHILE SPEAKING: {text}")
                return text
            return ""
        except Exception as e:
            print(f"Interrupt-listen error: {e}")
            return ""

    # If sounddevice is not available, skip listening
    if not SD_AVAILABLE:
        print(" listen() skipped: sounddevice not available")
        time.sleep(0.2)
        return ""

    if model is None:
        try:
            print(" Loading Whisper model (lazy)...")
            model = whisper.load_model("small")
            print(" Whisper model loaded")
        except Exception as e:
            print(f" Could not load Whisper model: {e}")
            return ""

    try:
        fs = 16000
        duration = timeout

        # RECORD AUDIO
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

        audio_level = np.max(np.abs(audio))

        if audio_level < silence_threshold:
            return ""

        # NORMALIZE AUDIO
        audio = audio / audio_level if audio_level > 0 else audio

        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(temp_file.name, fs, audio)

        #  TRANSCRIBE WITH WHISPER (FORCE ENGLISH)
        result = model.transcribe(
            temp_file.name,
            fp16=False,
            language="en"
        )

        text = result.get("text", "").strip().lower()

        #  GARBAGE FILTERING
        if is_junk_output(text):
            return ""

        if text:
            print(f" You: {text}")

        return text

    except Exception as e:
        print(f"Mic error: {e}")
        return ""

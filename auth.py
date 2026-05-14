try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    import numpy as np
    import sounddevice as sd
    import scipy.io.wavfile as wav
    import tempfile

    encoder = VoiceEncoder()
    PROFILE_PATH = "voice_profile.npy"

    def record_sample(seconds=3):
        fs = 16000
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait()

        temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(temp.name, fs, recording)
        return temp.name

    def enroll_voice():
        print("Recording your voice for enrollment...")
        file = record_sample()

        wav_data = preprocess_wav(file)
        embedding = encoder.embed_utterance(wav_data)

        np.save(PROFILE_PATH, embedding)
        print("Voice profile saved!")

    def verify_voice():
        # If there's no profile, allow access by default
        try:
            saved = np.load(PROFILE_PATH)
        except Exception:
            return True

        file = record_sample()

        wav_data = preprocess_wav(file)
        new = encoder.embed_utterance(wav_data)

        similarity = np.dot(saved, new)
        print("Voice similarity:", similarity)

        return similarity > 0.35
except Exception:
    print(" resemblyzer or audio deps missing  voice verification disabled")

    def enroll_voice():
        print("Enroll not available (missing dependencies)")

    def verify_voice():
        return True

    VOICE_VERIFICATION_AVAILABLE = False
else:
    VOICE_VERIFICATION_AVAILABLE = True

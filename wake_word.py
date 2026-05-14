# import pvporcupine
# import sounddevice as sd
# import numpy as np
# from config import PORCUPINE_ACCESS_KEY

# def detect_wake_word():
#     if PORCUPINE_ACCESS_KEY == "your_porcupine_access_key_here":
#         print("Note: Porcupine access key not set. Please add your key to config.py")
#         print("Waiting for 'Jarvis' wake word...")
#         input("Press Enter to continue (simulating wake word detection): ")
#         return
    
#     porcupine = pvporcupine.create(access_key=PORCUPINE_ACCESS_KEY, keywords=["jarvis"])

#     def audio_callback(indata, frames, time, status):
#         pcm = np.frombuffer(indata, dtype=np.int16)
#         result = porcupine.process(pcm)
#         if result >= 0:
#             raise KeyboardInterrupt

#     with sd.RawInputStream(
#         samplerate=porcupine.sample_rate,
#         blocksize=porcupine.frame_length,
#         dtype='int16',
#         channels=1,
#         callback=audio_callback
#     ):
#         print("Waiting for 'Jarvis'...")
#         try:
#             while True:
#                 pass
#         except KeyboardInterrupt:
#             print("Wake word detected!")

#     porcupine.delete()
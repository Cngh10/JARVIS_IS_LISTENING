"""
🔊 AUDIO ENVIRONMENT SENSING (Iron Man Level)

Real-time audio analysis for environment awareness.
Features:
- Sound source localization
- Noise level monitoring
- Emergency sound detection (sirens, alarms, etc.)
- Speech detection
- Footstep detection
- Vehicle detection
"""

import numpy as np
import sounddevice as sd
import threading
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum
import queue

class SoundType(Enum):
    """Types of sounds"""
    SPEECH = "speech"
    NOISE = "noise"
    SIREN = "siren"
    ALARM = "alarm"
    VEHICLE = "vehicle"
    FOOTSTEPS = "footsteps"
    DOOR = "door"
    GLASS = "glass"
    UNKNOWN = "unknown"

class SoundDirection(Enum):
    """Direction of sound"""
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"
    ALL_AROUND = "all_around"
    UNKNOWN = "unknown"

@dataclass
class SoundEvent:
    """Sound event information"""
    type: SoundType
    direction: SoundDirection
    intensity: float  # 0.0 to 1.0
    frequency: float  # Hz
    duration: float  # seconds
    timestamp: float
    confidence: float

@dataclass
class AudioEnvironment:
    """Audio environment state"""
    noise_level: float  # dB
    dominant_sound: Optional[SoundType]
    sound_events: List[SoundEvent]
    is_speech_present: bool
    is_emergency: bool
    guidance: str

class AudioSensor:
    """Audio environment sensing"""

    def __init__(self, sample_rate: int = 44100, channels: Optional[int] = None):
        """
        Initialize audio sensor

        Args:
            sample_rate: Audio sample rate
            channels: Number of audio channels (None = auto-detect)
        """
        self.sample_rate = sample_rate

        # Auto-detect available channels
        if channels is None:
            try:
                devices = sd.query_devices()
                # Find default input device
                for device in devices:
                    if device['max_input_channels'] > 0:
                        self.channels = min(device['max_input_channels'], 2)
                        break
                else:
                    self.channels = 1  # Fallback to mono
            except:
                self.channels = 1  # Fallback to mono
        else:
            self.channels = channels

        self.running = False
        self.thread = None

        # Audio queue
        self.audio_queue = queue.Queue(maxsize=100)

        # Current environment state
        self.current_environment: Optional[AudioEnvironment] = None
        self.env_lock = threading.Lock()

        # Sound detection thresholds
        self.speech_threshold = 0.3  # Minimum speech intensity
        self.noise_threshold = 0.1  # Minimum noise intensity
        self.emergency_threshold = 0.5  # Emergency sound threshold

        # Frequency ranges for sound types (Hz)
        self.frequency_ranges = {
            SoundType.SPEECH: (300, 3400),
            SoundType.SIREN: (500, 2000),
            SoundType.ALARM: (800, 3000),
            SoundType.VEHICLE: (100, 500),
            SoundType.FOOTSTEPS: (100, 500),
            SoundType.DOOR: (200, 1000),
            SoundType.GLASS: (2000, 8000),
        }

        # Emergency sound patterns (simplified)
        self.emergency_patterns = {
            SoundType.SIREN: [500, 600, 700, 800],  # Alternating frequencies
            SoundType.ALARM: [1000, 1200, 1400],  # Rising frequencies
        }

    def start(self):
        """Start audio sensing"""
        if self.running:
            return

        try:
            self.running = True

            # Start audio stream
            self.stream = sd.InputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback
            )
            self.stream.start()

            # Start processing thread
            self.thread = threading.Thread(target=self._process_loop, daemon=True)
            self.thread.start()

            print("✅ Audio sensing started")

        except Exception as e:
            print(f"❌ Failed to start audio sensing: {e}")
            self.running = False

    def stop(self):
        """Stop audio sensing"""
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.thread:
            self.thread.join(timeout=1.0)
        print("✅ Audio sensing stopped")

    def _audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback"""
        if status:
            print(f"Audio callback status: {status}")

        # Put audio data in queue
        try:
            self.audio_queue.put_nowait(indata.copy())
        except queue.Full:
            pass  # Drop if queue is full

    def _process_loop(self):
        """Main processing loop"""
        buffer = []
        buffer_duration = 0.1  # 100ms buffer

        while self.running:
            try:
                # Get audio data
                try:
                    data = self.audio_queue.get(timeout=0.1)
                    buffer.append(data)
                except queue.Empty:
                    continue

                # Check if we have enough data
                current_duration = len(buffer) * len(data[0]) / self.sample_rate
                if current_duration < buffer_duration:
                    continue

                # Concatenate buffer
                audio_data = np.concatenate(buffer, axis=0)
                buffer = []

                # Process audio
                environment = self._analyze_audio(audio_data)

                # Update environment
                with self.env_lock:
                    self.current_environment = environment

            except Exception as e:
                print(f"❌ Audio processing error: {e}")
                time.sleep(0.1)

    def _analyze_audio(self, audio_data: np.ndarray) -> AudioEnvironment:
        """
        Analyze audio data

        Args:
            audio_data: Audio data array

        Returns:
            Audio environment state
        """
        try:
            # Calculate RMS (noise level)
            rms = np.sqrt(np.mean(audio_data ** 2))
            noise_level_db = 20 * np.log10(rms + 1e-10)

            # Normalize intensity
            intensity = min(rms * 10, 1.0)

            # Perform FFT for frequency analysis
            if len(audio_data.shape) == 2:
                audio_mono = np.mean(audio_data, axis=1)
            else:
                audio_mono = audio_data

            fft = np.fft.fft(audio_mono)
            frequencies = np.fft.fftfreq(len(audio_mono), 1 / self.sample_rate)
            magnitude = np.abs(fft)

            # Get dominant frequency
            dominant_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
            dominant_frequency = abs(frequencies[dominant_freq_idx])

            # Detect sound type
            sound_type = self._detect_sound_type(dominant_frequency, intensity)

            # Detect direction (using stereo channels)
            direction = self._detect_direction(audio_data)

            # Check for emergency sounds
            is_emergency = self._is_emergency_sound(sound_type, dominant_frequency, intensity)

            # Check for speech
            is_speech = self._is_speech(audio_data, dominant_frequency, intensity)

            # Create sound event
            sound_event = SoundEvent(
                type=sound_type,
                direction=direction,
                intensity=intensity,
                frequency=dominant_frequency,
                duration=len(audio_data) / self.sample_rate,
                timestamp=time.time(),
                confidence=0.7
            )

            # Generate guidance
            guidance = self._generate_guidance(sound_event, is_emergency, noise_level_db)

            return AudioEnvironment(
                noise_level=noise_level_db,
                dominant_sound=sound_type,
                sound_events=[sound_event],
                is_speech_present=is_speech,
                is_emergency=is_emergency,
                guidance=guidance
            )

        except Exception as e:
            print(f"❌ Audio analysis error: {e}")
            return AudioEnvironment(
                noise_level=0.0,
                dominant_sound=None,
                sound_events=[],
                is_speech_present=False,
                is_emergency=False,
                guidance="Unable to analyze audio."
            )

    def _detect_sound_type(self, frequency: float, intensity: float) -> SoundType:
        """
        Detect sound type based on frequency and intensity

        Args:
            frequency: Dominant frequency
            intensity: Sound intensity

        Returns:
            Detected sound type
        """
        if intensity < self.noise_threshold:
            return SoundType.NOISE

        # Check each sound type's frequency range
        for sound_type, (min_freq, max_freq) in self.frequency_ranges.items():
            if min_freq <= frequency <= max_freq:
                return sound_type

        return SoundType.UNKNOWN

    def _detect_direction(self, audio_data: np.ndarray) -> SoundDirection:
        """
        Detect sound direction using stereo channels

        Args:
            audio_data: Stereo audio data

        Returns:
            Sound direction
        """
        if len(audio_data.shape) < 2 or audio_data.shape[1] < 2:
            return SoundDirection.UNKNOWN

        # Calculate energy in each channel
        left_energy = np.mean(audio_data[:, 0] ** 2)
        right_energy = np.mean(audio_data[:, 1] ** 2)

        # Compare energies
        if left_energy > right_energy * 1.5:
            return SoundDirection.LEFT
        elif right_energy > left_energy * 1.5:
            return SoundDirection.RIGHT
        else:
            return SoundDirection.CENTER

    def _is_emergency_sound(self, sound_type: SoundType, frequency: float, intensity: float) -> bool:
        """
        Check if sound is an emergency sound

        Args:
            sound_type: Detected sound type
            frequency: Dominant frequency
            intensity: Sound intensity

        Returns:
            True if emergency sound detected
        """
        if sound_type in [SoundType.SIREN, SoundType.ALARM]:
            return intensity > self.emergency_threshold

        return False

    def _is_speech(self, audio_data: np.ndarray, frequency: float, intensity: float) -> bool:
        """
        Check if audio contains speech

        Args:
            audio_data: Audio data
            frequency: Dominant frequency
            intensity: Sound intensity

        Returns:
            True if speech detected
        """
        # Check frequency range
        speech_min, speech_max = self.frequency_ranges[SoundType.SPEECH]

        if not (speech_min <= frequency <= speech_max):
            return False

        # Check intensity
        if intensity < self.speech_threshold:
            return False

        return True

    def _generate_guidance(self, sound_event: SoundEvent, is_emergency: bool, noise_level: float) -> str:
        """
        Generate guidance message based on audio

        Args:
            sound_event: Current sound event
            is_emergency: Whether emergency sound detected
            noise_level: Current noise level in dB

        Returns:
            Guidance message
        """
        if is_emergency:
            if sound_event.type == SoundType.SIREN:
                return f"EMERGENCY: Siren detected to your {sound_event.direction.value}!"
            elif sound_event.type == SoundType.ALARM:
                return f"EMERGENCY: Alarm detected to your {sound_event.direction.value}!"

        if sound_event.type == SoundType.VEHICLE:
            return f"Vehicle approaching from your {sound_event.direction.value}."

        if sound_event.type == SoundType.FOOTSTEPS:
            return f"Footsteps detected to your {sound_event.direction.value}."

        if sound_event.type == SoundType.DOOR:
            return f"Door sound to your {sound_event.direction.value}."

        if sound_event.type == SoundType.SPEECH:
            return f"Speech detected to your {sound_event.direction.value}."

        if noise_level > 70:
            return f"Loud environment: {noise_level:.1f} dB. Be careful."

        return "Audio environment normal."

    def get_current_environment(self) -> Optional[AudioEnvironment]:
        """Get current audio environment"""
        with self.env_lock:
            return self.current_environment

    def get_guidance(self) -> str:
        """
        Get real-time audio guidance

        Returns:
            Guidance message
        """
        env = self.get_current_environment()

        if not env:
            return "Unable to analyze audio environment."

        return env.guidance

# Global instance
audio_sensor = AudioSensor()

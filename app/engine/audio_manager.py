"""
SONIC VOICE STUDIO — Audio Device Manager
Handles microphone enumeration, stream lifecycle, and audio level metering.
"""

import sounddevice as sd
import numpy as np
import threading
import queue
import time


class AudioManager:
    """Manages audio input devices, streams, and real-time level metering."""

    def __init__(self):
        self._stream = None
        self._audio_queue = queue.Queue()
        self._level_queue = queue.Queue(maxsize=1)  # Latest RMS level only
        self._is_streaming = False
        self._selected_device = None
        self._sample_rate = 16000
        self._block_size = 8000
        self._gate_level = 0.0
        self._lock = threading.Lock()

    # --- Device Enumeration ---

    def list_input_devices(self):
        """Return a list of dicts: {index, name, channels, default}."""
        devices = sd.query_devices()
        default_input = sd.default.device[0] if isinstance(sd.default.device, tuple) else sd.default.device
        input_devices = []
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                input_devices.append({
                    'index': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels'],
                    'default': (i == default_input),
                    'samplerate': dev['default_samplerate']
                })
        return input_devices

    def get_default_device_index(self):
        """Return the system default input device index."""
        default = sd.default.device
        return default[0] if isinstance(default, tuple) else default

    def select_device(self, device_index):
        """Select a specific input device. Restarts the stream if currently active."""
        with self._lock:
            was_streaming = self._is_streaming
            if was_streaming:
                self._stop_stream_internal()
            self._selected_device = device_index
            if was_streaming:
                self._start_stream_internal()

    # --- Stream Lifecycle ---

    def start_stream(self):
        """Start the audio input stream."""
        with self._lock:
            self._start_stream_internal()

    def stop_stream(self):
        """Stop the audio input stream."""
        with self._lock:
            self._stop_stream_internal()

    def _start_stream_internal(self):
        """Internal: start stream (must hold lock)."""
        if self._is_streaming:
            return
        try:
            device = self._selected_device or self.get_default_device_index()
            self._stream = sd.RawInputStream(
                samplerate=self._sample_rate,
                blocksize=self._block_size,
                dtype='int16',
                channels=1,
                device=device,
                callback=self._audio_callback
            )
            self._stream.start()
            self._is_streaming = True
        except Exception as e:
            self._is_streaming = False
            raise e

    def _stop_stream_internal(self):
        """Internal: stop stream (must hold lock)."""
        self._is_streaming = False
        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Raw audio callback — feeds data queue and computes RMS level."""
        if not self._is_streaming:
            return
        raw_bytes = bytes(indata)
        self._audio_queue.put(raw_bytes)

        # Compute RMS for the visualizer
        try:
            audio_data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
            rms = np.sqrt(np.mean(audio_data ** 2)) / 32768.0  # Normalize to 0..1
            level = min(rms * 3.0, 1.0)  # Amplify for visibility
            gated_level = level if level >= self._gate_level else 0.0
            # Replace old level (non-blocking)
            try:
                self._level_queue.get_nowait()
            except queue.Empty:
                pass
            self._level_queue.put_nowait(gated_level)
        except Exception:
            pass

    # --- Data Access ---

    def get_audio_data(self, timeout=0.5):
        """Get the next chunk of raw audio bytes. Returns None on timeout."""
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def get_audio_level(self):
        """Get the latest RMS audio level (0.0 to 1.0). Returns 0.0 if unavailable."""
        try:
            return self._level_queue.get_nowait()
        except queue.Empty:
            return 0.0

    def drain_queue(self):
        """Clear any buffered audio data."""
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

    @property
    def is_streaming(self):
        return self._is_streaming

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def gate_level(self):
        return self._gate_level

    @gate_level.setter
    def gate_level(self, value):
        self._gate_level = max(0.0, min(1.0, float(value)))

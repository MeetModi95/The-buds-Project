"""
SONIC VOICE STUDIO — Voice Recognition Engine
Wraps Vosk speech recognition with thread-safe start/stop,
dynamic grammar updates, and callback-based result delivery.
"""

import os
import json
import threading
from vosk import Model, KaldiRecognizer


class VoiceEngine:
    """
    Offline voice recognition engine powered by Vosk.
    
    Usage:
        engine = VoiceEngine(audio_manager)
        engine.load_model("model")
        engine.set_grammar('[\"play music\", \"[unk]\"]')
        engine.on_result = lambda text: print(f"Heard: {text}")
        engine.on_error = lambda err: print(f"Error: {err}")
        engine.on_status = lambda msg: print(msg)
        engine.start()
        ...
        engine.stop()
    """

    def __init__(self, audio_manager):
        self._audio_manager = audio_manager
        self._model = None
        self._recognizer = None
        self._is_running = False
        self._thread = None
        self._lock = threading.Lock()
        self._confidence_threshold = 0.5
        self._grammar = None

        # Callbacks
        self.on_result = None    # Called with recognized text (str)
        self.on_error = None     # Called with error message (str)
        self.on_status = None    # Called with status messages (str)

    # --- Model Loading ---

    @property
    def model_loaded(self):
        return self._model is not None

    @property
    def is_running(self):
        return self._is_running

    @property
    def confidence_threshold(self):
        return self._confidence_threshold

    @confidence_threshold.setter
    def confidence_threshold(self, value):
        self._confidence_threshold = max(0.0, min(1.0, float(value)))

    def load_model(self, model_path):
        """
        Load the Vosk model from disk.
        Returns True on success, False on failure.
        """
        self._emit_status("Initializing voice engine...")
        
        if not os.path.exists(model_path):
            self._emit_error(f"Model folder not found: '{model_path}'")
            return False

        try:
            self._model = Model(model_path)
            self._emit_status("ML Engine loaded successfully.")
            # Build recognizer with current grammar if set
            self._rebuild_recognizer()
            return True
        except Exception as e:
            self._model = None
            self._emit_error(f"Model load failed: {str(e)}")
            return False

    def set_grammar(self, grammar_json):
        """
        Set the recognition grammar (JSON array string).
        Rebuilds the recognizer with the new grammar.
        """
        self._grammar = grammar_json
        if self._model:
            self._rebuild_recognizer()

    def _rebuild_recognizer(self):
        """Rebuild the KaldiRecognizer with current model + grammar."""
        if not self._model:
            return
        try:
            if self._grammar:
                self._recognizer = KaldiRecognizer(
                    self._model,
                    self._audio_manager.sample_rate,
                    self._grammar
                )
            else:
                self._recognizer = KaldiRecognizer(
                    self._model,
                    self._audio_manager.sample_rate
                )
        except Exception as e:
            self._emit_error(f"Recognizer build failed: {str(e)}")

    # --- Engine Lifecycle ---

    def start(self):
        """Start the voice recognition loop in a background thread."""
        with self._lock:
            if self._is_running:
                return True
            if not self._model or not self._recognizer:
                self._emit_error("Cannot start: engine not loaded.")
                return False
            self._is_running = True

        try:
            self._audio_manager.start_stream()
        except Exception as e:
            with self._lock:
                self._is_running = False
            self._emit_error(f"Cannot start audio input: {str(e)}")
            return False

        self._thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self._thread.start()
        self._emit_status("Voice engine started — listening.")
        return True

    def stop(self):
        """Stop the recognition loop and audio stream."""
        with self._lock:
            if not self._is_running:
                return
            self._is_running = False

        self._audio_manager.stop_stream()
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._audio_manager.drain_queue()
        self._emit_status("Voice engine stopped.")

    def _recognition_loop(self):
        """Main loop: pull audio chunks and feed to recognizer."""
        while self._is_running:
            data = self._audio_manager.get_audio_data(timeout=0.5)
            if data is None:
                continue

            try:
                if self._recognizer.AcceptWaveform(data):
                    result = json.loads(self._recognizer.Result())
                    phrase = result.get("text", "").strip()
                    if phrase and phrase != "[unk]":
                        if self.on_result:
                            self.on_result(phrase)
            except Exception as e:
                self._emit_error(f"Recognition error: {str(e)}")

    # --- Helpers ---

    def _emit_status(self, msg):
        if self.on_status:
            self.on_status(msg)

    def _emit_error(self, msg):
        if self.on_error:
            self.on_error(msg)

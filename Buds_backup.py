import os
import sys
import threading
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from pynput.keyboard import Key, Controller
import customtkinter as ctk

# --- App Styling Configuration ---
ctk.set_appearance_mode("Dark")             
ctk.set_default_color_theme("dark-blue")    

class EarbudControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("SONIC VOICE STUDIO I")
        self.geometry("750x480")
        self.resizable(False, False)

        # Core Engine Backend Variables
        self.keyboard = Controller()
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.listener_thread = None
        self.stream = None
        self.confidence_threshold = 0.5  
        self.model_loaded = False  # Track model safety status

        # UI State Variables
        self.active_profile = "Gaming"

        # Build UI Construction
        self.create_header()
        self.create_main_panel()
        
        # Load model AFTER the UI text logs are drawn
        self.load_voice_model()

    def create_header(self):
        header_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color="#121212")
        header_frame.pack(fill="x", side="top")

        title_label = ctk.CTkLabel(header_frame, text="SONIC VOICE", font=ctk.CTkFont(size=18, weight="bold"), text_color="#E03030")
        title_label.pack(side="left", padx=30, pady=15)

        self.profile_btn = ctk.CTkButton(header_frame, text=f"Profile: {self.active_profile}", width=120, fg_color="#222", hover_color="#333")
        self.profile_btn.pack(side="right", padx=20, pady=15)

    def create_main_panel(self):
        control_frame = ctk.CTkFrame(self, width=220, fg_color="#181818", corner_radius=8)
        control_frame.pack(side="left", fill="y", padx=15, pady=15)

        lbl = ctk.CTkLabel(control_frame, text="SYSTEM VOICE ENGINE", font=ctk.CTkFont(size=12, weight="bold"))
        lbl.pack(pady=(20, 10), padx=20)

        # Master Switch
        self.switch_var = ctk.StringVar(value="off")
        self.master_switch = ctk.CTkSwitch(control_frame, text="Engine Offline", command=self.toggle_engine,
                                            variable=self.switch_var, onvalue="on", offvalue="off",
                                            progress_color="#E03030", button_color="#FF4D4D")
        self.master_switch.pack(pady=20, padx=20)

        # Text Feed Box
        self.status_log = ctk.CTkTextbox(control_frame, width=180, height=220, fg_color="#0D0D0D", text_color="#A0A0A0")
        self.status_log.pack(pady=10, padx=15)

        # Tuning Sliders Panel
        sliders_frame = ctk.CTkFrame(self, fg_color="#181818", corner_radius=8)
        sliders_frame.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)

        right_title = ctk.CTkLabel(sliders_frame, text="EFFECT TUNING & SENSITIVITY", font=ctk.CTkFont(size=13, weight="bold"))
        right_title.pack(anchor="w", padx=25, pady=(20, 15))

        self.create_slider_row(sliders_frame, "Microphone Gate Level", 0.8, lambda v: None)
        self.create_slider_row(sliders_frame, "Keyword Filter Matching", 0.5, self.update_confidence)
        self.create_slider_row(sliders_frame, "Command Cool-down", 0.2, lambda v: None)

    def create_slider_row(self, parent, label_text, default_val, callback):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=25, pady=12)
        
        lbl = ctk.CTkLabel(row, text=label_text, width=150, anchor="w", text_color="#C0C0C0")
        lbl.pack(side="left")

        slider = ctk.CTkSlider(row, from_=0, to=1, number_of_steps=100, 
                               progress_color="#E03030", button_color="#E03030", 
                               button_hover_color="#FF4D4D", command=callback)
        slider.set(default_val)
        slider.pack(side="right", fill="x", expand=True, padx=(10, 0))

    def log_message(self, text):
        self.status_log.insert("end", f"\n{text}")
        self.status_log.see("end")

    def update_confidence(self, value):
        self.confidence_threshold = float(value)

    def load_voice_model(self):
        """Initializes the Vosk components with path safety checks"""
        self.log_message("System Initialized.\nChecking files...")
        
        if not os.path.exists("model"):
            self.log_message("[-] Error: 'model' folder missing!\nPut the Vosk folder here.")
            self.model_loaded = False
            return

        try:
            self.model = Model("model")
            target_grammar = '["play music", "stop music", "next song", "previous song", "volume up", "volume down", "[unk]"]'
            self.recognizer = KaldiRecognizer(self.model, 16000, target_grammar)
            self.log_message("[+] ML Engine Loaded Successfully.")
            self.model_loaded = True
        except Exception as e:
            self.log_message(f"[-] Load failed: {str(e)}")
            self.model_loaded = False

    def toggle_engine(self):
        # Defend against running if the model engine files are missing
        if not self.model_loaded:
            self.log_message("[-] Cannot start: Engine not loaded.")
            self.switch_var.set("off")
            self.master_switch.configure(text="Engine Offline")
            return

        if self.switch_var.get() == "on":
            self.master_switch.configure(text="Engine Active")
            self.is_listening = True
            self.log_message("[*] Audio Pipeline: Link ON")
            
            self.listener_thread = threading.Thread(target=self.start_audio_listening, daemon=True)
            self.listener_thread.start()
        else:
            self.master_switch.configure(text="Engine Offline")
            self.is_listening = False
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.log_message("[-] Audio Pipeline: Closed")

    def audio_callback(self, indata, frames, time, status):
        if self.is_listening:
            self.audio_queue.put(bytes(indata))

    def start_audio_listening(self):
        try:
            self.stream = sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                           channels=1, callback=self.audio_callback)
            with self.stream:
                while self.is_listening:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue

                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        phrase = result.get("text", "")
                        if phrase:
                            self.after(0, self.log_message, f"Heard: {phrase}")
                            self.after(0, self.process_voice_command, phrase)
        except Exception as e:
            self.after(0, self.log_message, f"Error: {str(e)}")

    def process_voice_command(self, text):
        cleaned = text.strip().lower()
        if "play music" in cleaned or "stop music" in cleaned:
            self.keyboard.press(Key.media_play_pause)
            self.keyboard.release(Key.media_play_pause)
        elif "next song" in cleaned:
            self.keyboard.press(Key.media_next)
            self.keyboard.release(Key.media_next)
        elif "volume up" in cleaned:
            self.keyboard.press(Key.media_volume_up)
            self.keyboard.release(Key.media_volume_up)
        elif "volume down" in cleaned:
            self.keyboard.press(Key.media_volume_down)
            self.keyboard.release(Key.media_volume_down)

if __name__ == "__main__":
    app = EarbudControlApp()
    app.mainloop()
"""
SONIC VOICE STUDIO — Audio Page
Input device selection, sensitivity tuning, and audio configuration.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Sizes
from app.components.slider_row import SliderRow
from app.components.audio_visualizer import AudioVisualizer


class AudioPage(ctk.CTkFrame):
    """Audio configuration page — device picker, gate, sensitivity sliders."""

    def __init__(self, parent, app_state, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._app = app_state
        self._current_device_index = None
        self._build()

    def _build(self):
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_LG, Sizes.PAD_SM))

        title = ctk.CTkLabel(header, text="AUDIO",
                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TITLE_SIZE, weight="bold"),
                              text_color=Colors.TEXT_PRIMARY)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Input device & sensitivity configuration",
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                 text_color=Colors.TEXT_SECONDARY)
        subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        # --- Input Device Section ---
        device_section = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                                      border_width=1, border_color=Colors.BORDER)
        device_section.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_SM, Sizes.PAD_MD))

        device_title = ctk.CTkLabel(device_section, text="INPUT DEVICE",
                                     font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                     text_color=Colors.TEXT_DISABLED, anchor="w")
        device_title.pack(fill="x", padx=20, pady=(16, 8))

        device_row = ctk.CTkFrame(device_section, fg_color="transparent")
        device_row.pack(fill="x", padx=20, pady=(0, 16))

        self._device_var = ctk.StringVar(value="Default Device")
        self._device_dropdown = ctk.CTkOptionMenu(device_row,
                                                    variable=self._device_var,
                                                    values=["Loading devices..."],
                                                    width=400, height=36,
                                                    fg_color=Colors.BG_INPUT,
                                                    button_color=Colors.BORDER_SUBTLE,
                                                    button_hover_color=Colors.BG_HOVER,
                                                    text_color=Colors.TEXT_PRIMARY,
                                                    dropdown_fg_color=Colors.BG_CARD,
                                                    dropdown_hover_color=Colors.BG_HOVER,
                                                    dropdown_text_color=Colors.TEXT_PRIMARY,
                                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                                    corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                                    command=self._on_device_change)
        self._device_dropdown.pack(side="left")

        self._refresh_btn = ctk.CTkButton(device_row, text="⟳  Refresh", width=100, height=36,
                                           fg_color=Colors.BG_INPUT,
                                           hover_color=Colors.BG_HOVER,
                                           text_color=Colors.TEXT_SECONDARY,
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                           corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                           command=self._refresh_devices)
        self._refresh_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

        # --- Live Monitor ---
        monitor_section = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                                       border_width=1, border_color=Colors.BORDER)
        monitor_section.pack(fill="x", padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_MD))

        monitor_title = ctk.CTkLabel(monitor_section, text="LIVE INPUT MONITOR",
                                      font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                      text_color=Colors.TEXT_DISABLED, anchor="w")
        monitor_title.pack(fill="x", padx=20, pady=(16, 8))

        self._visualizer = AudioVisualizer(monitor_section, width=600, height=70,
                                            get_level_func=self._get_audio_level)
        self._visualizer.pack(fill="x", padx=20, pady=(0, 16))

        # --- Sensitivity Sliders Section ---
        sliders_section = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                                       border_width=1, border_color=Colors.BORDER)
        sliders_section.pack(fill="both", expand=True, padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_LG))

        sliders_title = ctk.CTkLabel(sliders_section, text="TUNING & SENSITIVITY",
                                      font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                      text_color=Colors.TEXT_DISABLED, anchor="w")
        sliders_title.pack(fill="x", padx=20, pady=(16, 12))

        self._gate_slider = SliderRow(sliders_section, "Microphone Gate Level",
                                       min_val=0.0, max_val=1.0, default_val=0.8,
                                       command=self._on_gate_change)
        self._gate_slider.pack(fill="x", padx=20, pady=8)

        self._confidence_slider = SliderRow(sliders_section, "Keyword Confidence Threshold",
                                             min_val=0.0, max_val=1.0, default_val=0.5,
                                             command=self._on_confidence_change)
        self._confidence_slider.pack(fill="x", padx=20, pady=8)

        self._cooldown_slider = SliderRow(sliders_section, "Command Cooldown",
                                           min_val=0.0, max_val=3.0, default_val=0.5,
                                           steps=30, suffix="s",
                                           command=self._on_cooldown_change)
        self._cooldown_slider.pack(fill="x", padx=20, pady=(8, 20))

    # --- Device Management ---

    def _refresh_devices(self):
        """Refresh the input device list from the audio manager."""
        try:
            devices = self._app.audio_manager.list_input_devices()
            self._device_map = {}  # display_name → device_index
            display_names = []
            default_name = None

            for dev in devices:
                name = f"{dev['name']} (Ch: {dev['channels']})"
                if dev['default']:
                    name = f"★ {name}"
                    default_name = name
                display_names.append(name)
                self._device_map[name] = dev['index']

            if display_names:
                self._device_dropdown.configure(values=display_names)
                if default_name:
                    self._device_var.set(default_name)
                    self._current_device_index = self._device_map[default_name]
                else:
                    self._device_var.set(display_names[0])
                    self._current_device_index = self._device_map[display_names[0]]
            else:
                self._device_dropdown.configure(values=["No devices found"])
                self._device_var.set("No devices found")
        except Exception as e:
            self._device_dropdown.configure(values=[f"Error: {str(e)}"])

    def _on_device_change(self, device_name):
        """Handle device selection change."""
        if hasattr(self, '_device_map') and device_name in self._device_map:
            device_index = self._device_map[device_name]
            try:
                self._app.audio_manager.select_device(device_index)
                self._current_device_index = device_index
            except Exception:
                pass

    def load_settings(self, audio_settings):
        """Load audio settings from a profile dict."""
        if audio_settings:
            try:
                self._app.audio_manager.gate_level = audio_settings.get('gate_level', 0.8)
            except Exception:
                pass
            self._gate_slider.set(audio_settings.get('gate_level', 0.8))
            self._confidence_slider.set(audio_settings.get('confidence_threshold', 0.5))
            self._cooldown_slider.set(audio_settings.get('cooldown_seconds', 0.5))

    def get_settings(self):
        """Get current audio settings as a dict."""
        return {
            'gate_level': self._gate_slider.get(),
            'confidence_threshold': self._confidence_slider.get(),
            'cooldown_seconds': self._cooldown_slider.get(),
            'input_device': getattr(self, '_current_device_index', None)
        }

    def set_engine_active(self, active):
        """Start/stop the visualizer based on engine state."""
        if active:
            self._visualizer.start()
        else:
            self._visualizer.stop()

    # --- Slider Callbacks ---

    def _on_gate_change(self, value):
        try:
            self._app.audio_manager.gate_level = float(value)
        except Exception:
            pass

    def _on_confidence_change(self, value):
        try:
            self._app.voice_engine.confidence_threshold = float(value)
        except Exception:
            pass

    def _on_cooldown_change(self, value):
        try:
            self._app.command_processor.cooldown = float(value)
        except Exception:
            pass

    def _get_audio_level(self):
        try:
            return self._app.audio_manager.get_audio_level()
        except Exception:
            return 0.0

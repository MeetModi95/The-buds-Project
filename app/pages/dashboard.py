"""
SONIC VOICE STUDIO — Dashboard Page
Overview page with engine status, live audio visualizer,
quick stats, and recent command activity feed.
"""

import customtkinter as ctk
import time
from app.theme import Colors, Fonts, Sizes
from app.components.audio_visualizer import AudioVisualizer
from app.components.status_indicator import StatusIndicator


class DashboardPage(ctk.CTkFrame):
    """Main dashboard page — the landing/home view."""

    def __init__(self, parent, app_state, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._app = app_state  # Reference to main app for engine/audio data
        self._command_count = 0
        self._start_time = time.time()
        self._activity_items = []

        self._build()

    def _build(self):
        # --- Page Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_LG, Sizes.PAD_SM))

        title = ctk.CTkLabel(header, text="DASHBOARD",
                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TITLE_SIZE, weight="bold"),
                              text_color=Colors.TEXT_PRIMARY)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="System Overview",
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                 text_color=Colors.TEXT_SECONDARY)
        subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        # --- Top Row: Status Cards ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_SM, Sizes.PAD_MD))

        # Engine Status Card
        self._engine_card = self._create_stat_card(cards_frame, "ENGINE STATUS", "OFFLINE", Colors.STATUS_OFFLINE)
        self._engine_card.pack(side="left", fill="both", expand=True, padx=(0, Sizes.PAD_SM))

        # Active Profile Card
        self._profile_card = self._create_stat_card(cards_frame, "ACTIVE PROFILE", "Default", Colors.ACCENT)
        self._profile_card.pack(side="left", fill="both", expand=True, padx=Sizes.PAD_SM)

        # Commands Today Card
        self._commands_card = self._create_stat_card(cards_frame, "COMMANDS EXECUTED", "0", Colors.ACCENT)
        self._commands_card.pack(side="left", fill="both", expand=True, padx=Sizes.PAD_SM)

        # Uptime Card
        self._uptime_card = self._create_stat_card(cards_frame, "SESSION UPTIME", "00:00:00", Colors.TEXT_SECONDARY)
        self._uptime_card.pack(side="left", fill="both", expand=True, padx=(Sizes.PAD_SM, 0))

        # --- Audio Visualizer Section ---
        viz_header = ctk.CTkLabel(self, text="AUDIO INPUT MONITOR",
                                   font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                   text_color=Colors.TEXT_DISABLED, anchor="w")
        viz_header.pack(fill="x", padx=Sizes.PAD_LG + 4, pady=(Sizes.PAD_SM, 4))

        self._visualizer = AudioVisualizer(self, width=600, height=90,
                                            get_level_func=self._get_audio_level)
        self._visualizer.pack(fill="x", padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_MD))

        # --- Activity Feed ---
        feed_header = ctk.CTkLabel(self, text="RECENT ACTIVITY",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                    text_color=Colors.TEXT_DISABLED, anchor="w")
        feed_header.pack(fill="x", padx=Sizes.PAD_LG + 4, pady=(0, 4))

        # Textbox wrapper card for glass border
        feed_container = ctk.CTkFrame(self, fg_color=Colors.BG_CARD,
                                      corner_radius=Sizes.CARD_CORNER_RADIUS,
                                      border_width=1, border_color=Colors.BORDER)
        feed_container.pack(fill="both", expand=True, padx=Sizes.PAD_LG, pady=(0, Sizes.PAD_LG))

        self._activity_feed = ctk.CTkTextbox(feed_container,
                                              fg_color="transparent",
                                              text_color=Colors.TEXT_SECONDARY,
                                              corner_radius=0,
                                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                              state="disabled")
        self._activity_feed.pack(fill="both", expand=True, padx=8, pady=8)

        # Start uptime ticker
        self._tick_uptime()

    def _create_stat_card(self, parent, title, value, value_color):
        """Create a small stats card."""
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                             border_width=1, border_color=Colors.BORDER,
                             height=90)
        card.pack_propagate(False)

        title_lbl = ctk.CTkLabel(card, text=title,
                                  font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TINY_SIZE, weight="bold"),
                                  text_color=Colors.TEXT_DISABLED, anchor="w")
        title_lbl.pack(fill="x", padx=16, pady=(14, 2))

        value_lbl = ctk.CTkLabel(card, text=value,
                                  font=ctk.CTkFont(family=Fonts.FAMILY, size=24, weight="bold"),
                                  text_color=value_color, anchor="w")
        value_lbl.pack(fill="x", padx=16, pady=(0, 14))

        # Store reference for updates
        card._value_label = value_lbl
        card._title_label = title_lbl
        return card

    # --- Public Methods ---

    def set_engine_status(self, is_active: bool):
        """Update the engine status card."""
        if is_active:
            self._engine_card._value_label.configure(text="ACTIVE", text_color=Colors.STATUS_ONLINE)
            self._visualizer.start()
        else:
            self._engine_card._value_label.configure(text="OFFLINE", text_color=Colors.STATUS_OFFLINE)
            self._visualizer.stop()

    def set_profile_name(self, name: str):
        """Update the active profile card."""
        self._profile_card._value_label.configure(text=name)

    def log_command(self, phrase, action):
        """Add a command execution to the activity feed."""
        self._command_count += 1
        self._commands_card._value_label.configure(text=str(self._command_count))

        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}]  \"{phrase}\" → {action}"
        self._activity_items.insert(0, entry)
        self._activity_items = self._activity_items[:50]  # Keep last 50

        self._activity_feed.configure(state="normal")
        self._activity_feed.delete("1.0", "end")
        self._activity_feed.insert("1.0", "\n".join(self._activity_items))
        self._activity_feed.configure(state="disabled")

    def log_status(self, message):
        """Add a status message to the activity feed."""
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}]  ⚡ {message}"
        self._activity_items.insert(0, entry)
        self._activity_items = self._activity_items[:50]

        self._activity_feed.configure(state="normal")
        self._activity_feed.delete("1.0", "end")
        self._activity_feed.insert("1.0", "\n".join(self._activity_items))
        self._activity_feed.configure(state="disabled")

    def _get_audio_level(self):
        """Get the current audio level from the audio manager."""
        try:
            return self._app.audio_manager.get_audio_level()
        except Exception:
            return 0.0

    def _tick_uptime(self):
        """Update the uptime display every second."""
        elapsed = int(time.time() - self._start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        self._uptime_card._value_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        self.after(1000, self._tick_uptime)

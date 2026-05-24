"""
SONIC VOICE STUDIO — Settings Page
Application preferences: model path, startup behavior, theme, tray settings.
"""

import customtkinter as ctk
import os
from app.theme import Colors, Fonts, Sizes, AppConfig


class SettingsPage(ctk.CTkFrame):
    """Application settings and preferences page."""

    def __init__(self, parent, app_state, **kwargs):
        super().__init__(parent, fg_color="transparent", corner_radius=0, **kwargs)
        self._app = app_state
        self._build()

    def _build(self):
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", padx=Sizes.PAD_LG, pady=(Sizes.PAD_LG, Sizes.PAD_SM))

        title = ctk.CTkLabel(header, text="SETTINGS",
                              font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TITLE_SIZE, weight="bold"),
                              text_color=Colors.TEXT_PRIMARY)
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Application preferences",
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                 text_color=Colors.TEXT_SECONDARY)
        subtitle.pack(side="left", padx=(12, 0), pady=(6, 0))

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                          scrollbar_button_color=Colors.BORDER_SUBTLE,
                                          scrollbar_button_hover_color=Colors.ACCENT_DIM)
        scroll.pack(fill="both", expand=True, padx=Sizes.PAD_LG, pady=(Sizes.PAD_SM, Sizes.PAD_LG))

        # --- Voice Model Section ---
        self._create_section_card(scroll, "VOICE MODEL", [
            self._build_model_path_row,
        ])

        # --- Behavior Section ---
        self._create_section_card(scroll, "BEHAVIOR", [
            self._build_minimize_tray_row,
            self._build_auto_start_engine_row,
        ])

        # --- Appearance Section ---
        self._create_section_card(scroll, "APPEARANCE", [
            self._build_accent_color_row,
        ])

        # --- About Section ---
        about_card = ctk.CTkFrame(scroll, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                                  border_width=1, border_color=Colors.BORDER)
        about_card.pack(fill="x", pady=(0, Sizes.PAD_MD))

        about_title = ctk.CTkLabel(about_card, text="ABOUT",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                    text_color=Colors.TEXT_DISABLED, anchor="w")
        about_title.pack(fill="x", padx=20, pady=(16, 8))

        info_frame = ctk.CTkFrame(about_card, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 16))

        app_name = ctk.CTkLabel(info_frame, text=AppConfig.APP_NAME,
                                 font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.HEADING_SIZE, weight="bold"),
                                 text_color=Colors.ACCENT, anchor="w")
        app_name.pack(fill="x")

        version_lbl = ctk.CTkLabel(info_frame, text=f"Version {AppConfig.APP_VERSION}  ·  {AppConfig.APP_AUTHOR}",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                    text_color=Colors.TEXT_SECONDARY, anchor="w")
        version_lbl.pack(fill="x", pady=(2, 0))

        desc = ctk.CTkLabel(info_frame,
                             text="Offline voice command engine powered by Vosk ML.\nControl your media and system with voice commands through your earbuds.",
                             font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                             text_color=Colors.TEXT_DISABLED, anchor="w", justify="left",
                             wraplength=500)
        desc.pack(fill="x", pady=(8, 0))

    def _create_section_card(self, parent, title, builder_funcs):
        """Create a settings section card with rows."""
        card = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=Sizes.CARD_CORNER_RADIUS,
                            border_width=1, border_color=Colors.BORDER)
        card.pack(fill="x", pady=(0, Sizes.PAD_MD))

        title_lbl = ctk.CTkLabel(card, text=title,
                                  font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.CAPTION_SIZE, weight="bold"),
                                  text_color=Colors.TEXT_DISABLED, anchor="w")
        title_lbl.pack(fill="x", padx=20, pady=(16, 8))

        for builder in builder_funcs:
            builder(card)

        return card

    # --- Setting Rows ---

    def _build_model_path_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))

        lbl = ctk.CTkLabel(row, text="Model Directory",
                            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                            text_color=Colors.TEXT_SECONDARY, anchor="w")
        lbl.pack(fill="x")

        path_frame = ctk.CTkFrame(row, fg_color="transparent")
        path_frame.pack(fill="x", pady=(4, 0))

        self._model_path_entry = ctk.CTkEntry(path_frame, height=34,
                                                fg_color=Colors.BG_INPUT,
                                                text_color=Colors.TEXT_PRIMARY,
                                                border_color=Colors.BORDER,
                                                border_width=1,
                                                corner_radius=Sizes.INPUT_CORNER_RADIUS,
                                                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE))
        # Resolve the default model path (works in both source and frozen mode)
        import sys as _sys
        if getattr(_sys, 'frozen', False) and hasattr(_sys, '_MEIPASS'):
            _default_model = os.path.join(_sys._MEIPASS, "model")
        else:
            _default_model = os.path.abspath("model")
        self._model_path_entry.insert(0, _default_model)
        self._model_path_entry.pack(side="left", fill="x", expand=True)

        browse_btn = ctk.CTkButton(path_frame, text="Browse...", width=80, height=34,
                                    fg_color=Colors.BG_INPUT,
                                    hover_color=Colors.BG_HOVER,
                                    text_color=Colors.TEXT_SECONDARY,
                                    border_width=1, border_color=Colors.BORDER,
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                    corner_radius=Sizes.BUTTON_CORNER_RADIUS,
                                    command=self._browse_model)
        browse_btn.pack(side="left", padx=(Sizes.PAD_SM, 0))

    def _build_minimize_tray_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))

        lbl = ctk.CTkLabel(row, text="Minimize to System Tray",
                            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                            text_color=Colors.TEXT_SECONDARY, anchor="w")
        lbl.pack(side="left")

        self._tray_var = ctk.StringVar(value="on")
        tray_switch = ctk.CTkSwitch(row, text="", variable=self._tray_var,
                                     onvalue="on", offvalue="off",
                                     progress_color=Colors.ACCENT,
                                     button_color=Colors.ACCENT_HOVER,
                                     fg_color=Colors.BORDER_SUBTLE)
        tray_switch.pack(side="right")

    def _build_auto_start_engine_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))

        lbl = ctk.CTkLabel(row, text="Auto-start Engine on Launch",
                            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                            text_color=Colors.TEXT_SECONDARY, anchor="w")
        lbl.pack(side="left")

        self._auto_start_var = ctk.StringVar(value="off")
        auto_switch = ctk.CTkSwitch(row, text="", variable=self._auto_start_var,
                                     onvalue="on", offvalue="off",
                                     progress_color=Colors.ACCENT,
                                     button_color=Colors.ACCENT_HOVER,
                                     fg_color=Colors.BORDER_SUBTLE)
        auto_switch.pack(side="right")

    def _build_accent_color_row(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))

        lbl = ctk.CTkLabel(row, text="Accent Color",
                            font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                            text_color=Colors.TEXT_SECONDARY, anchor="w")
        lbl.pack(side="left")

        # Color swatches
        colors_frame = ctk.CTkFrame(row, fg_color="transparent")
        colors_frame.pack(side="right")
        self._accent_swatches = []

        color_options = [
            ("#A855F7", "Purple"),
            ("#D946EF", "Fuchsia"),
            ("#F472B6", "Pink"),
            ("#34D399", "Mint"),
            ("#818CF8", "Indigo"),
        ]

        for hex_color, name in color_options:
            swatch = ctk.CTkButton(colors_frame, text="", width=28, height=28,
                                    fg_color=hex_color, hover_color=hex_color,
                                    corner_radius=14,
                                    border_width=2,
                                    border_color=Colors.BORDER,
                                    command=lambda c=hex_color: self._select_color(c))
            swatch.pack(side="left", padx=3)
            self._accent_swatches.append((hex_color, swatch))

    # --- Actions ---

    def _browse_model(self):
        from tkinter import filedialog
        path = filedialog.askdirectory(title="Select Vosk Model Directory")
        if path:
            self._model_path_entry.delete(0, "end")
            self._model_path_entry.insert(0, path)

    def _select_color(self, hex_color):
        """Handle accent color selection for current and future controls."""
        Colors.ACCENT = hex_color
        Colors.TEXT_ACCENT = hex_color
        for color, swatch in getattr(self, "_accent_swatches", []):
            swatch.configure(border_color=Colors.TEXT_PRIMARY if color == hex_color else Colors.BORDER_SUBTLE)

    def get_model_path(self):
        return self._model_path_entry.get()

    def get_settings(self):
        return {
            'model_path': self._model_path_entry.get(),
            'minimize_to_tray': self._tray_var.get() == "on",
            'auto_start_engine': self._auto_start_var.get() == "on",
        }

"""
SONIC VOICE STUDIO — Styled Slider Row Component
A label + slider + value display row for settings panels.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts


class SliderRow(ctk.CTkFrame):
    """
    A reusable row containing a label, slider, and current value display.
    """

    def __init__(self, parent, label_text, min_val=0.0, max_val=1.0,
                 default_val=0.5, steps=100, suffix="", command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._command = command
        self._suffix = suffix
        self._min_val = min_val
        self._max_val = max_val

        # Label
        self._label = ctk.CTkLabel(self, text=label_text, width=180, anchor="w",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                    text_color=Colors.TEXT_SECONDARY)
        self._label.pack(side="left", padx=(0, 8))

        # Value display
        self._value_label = ctk.CTkLabel(self, text=self._format_value(default_val),
                                          width=50, anchor="e",
                                          font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                          text_color=Colors.ACCENT)
        self._value_label.pack(side="right", padx=(8, 0))

        # Slider
        self._slider = ctk.CTkSlider(self, from_=min_val, to=max_val,
                                      number_of_steps=steps,
                                      progress_color=Colors.ACCENT,
                                      button_color=Colors.ACCENT,
                                      button_hover_color=Colors.ACCENT_HOVER,
                                      fg_color=Colors.BORDER_SUBTLE,
                                      command=self._on_change)
        self._slider.set(default_val)
        self._slider.pack(side="right", fill="x", expand=True, padx=(0, 4))

    def _format_value(self, val):
        display = f"{val:.2f}" if self._max_val <= 1.0 else f"{val:.0f}"
        return f"{display}{self._suffix}"

    def _on_change(self, value):
        self._value_label.configure(text=self._format_value(value))
        if self._command:
            self._command(value)

    def get(self):
        return self._slider.get()

    def set(self, value):
        self._slider.set(value)
        self._value_label.configure(text=self._format_value(value))

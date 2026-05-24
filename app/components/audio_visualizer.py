"""
SONIC VOICE STUDIO — Audio Visualizer Component
Canvas-based real-time audio level meter with smooth bar animation.
"""

import customtkinter as ctk
from app.theme import Colors
import math


class AudioVisualizer(ctk.CTkFrame):
    """
    A horizontal bar-graph audio level visualizer.
    Shows multiple bars that react to real-time audio levels.
    """

    NUM_BARS = 32
    BAR_GAP = 3
    UPDATE_INTERVAL_MS = 50

    def __init__(self, parent, width=500, height=80, get_level_func=None, **kwargs):
        from app.theme import Sizes
        super().__init__(parent, fg_color=Colors.BG_INPUT, corner_radius=Sizes.INPUT_CORNER_RADIUS,
                         border_width=1, border_color=Colors.BORDER, **kwargs)
        self._get_level = get_level_func
        self._target_level = 0.0
        self._current_level = 0.0
        self._bar_levels = [0.0] * self.NUM_BARS  # per-bar smoothed heights
        self._is_active = False

        self._canvas = ctk.CTkCanvas(self, width=width, height=height,
                                      highlightthickness=0, bg=Colors.BG_INPUT)
        self._canvas.pack(fill="both", expand=True, padx=8, pady=8)

        self._canvas_width = width
        self._canvas_height = height
        self._bars = []

        self._draw_bars()

    def _draw_bars(self):
        """Initialize the bar rectangles on the canvas."""
        self._canvas.delete("all")
        self._bars = []
        usable_width = self._canvas_width - 12
        bar_width = max(2, (usable_width - (self.NUM_BARS - 1) * self.BAR_GAP) // self.NUM_BARS)

        for i in range(self.NUM_BARS):
            x = 6 + i * (bar_width + self.BAR_GAP)
            # Draw from bottom up
            bar = self._canvas.create_rectangle(
                x, self._canvas_height - 4,
                x + bar_width, self._canvas_height - 4,
                fill=Colors.ACCENT_DIM, outline="", width=0
            )
            self._bars.append(bar)

    def start(self):
        """Start the visualizer animation loop."""
        if self._is_active:
            return
        self._is_active = True
        self._animate()

    def stop(self):
        """Stop the animation and reset bars."""
        self._is_active = False
        self._target_level = 0.0

    def _animate(self):
        """Main animation loop — updates bar heights based on audio level."""
        if not self._is_active:
            # Fade out
            self._target_level = 0.0
            self._smooth_update()
            if any(l > 0.01 for l in self._bar_levels):
                self.after(self.UPDATE_INTERVAL_MS, self._animate)
            return

        # Get fresh level
        if self._get_level:
            try:
                self._target_level = self._get_level()
            except Exception:
                self._target_level = 0.0

        self._smooth_update()
        self.after(self.UPDATE_INTERVAL_MS, self._animate)

    def _smooth_update(self):
        """Smoothly interpolate bar levels and redraw."""
        # Smooth the overall level
        smoothing = 0.3
        self._current_level += (self._target_level - self._current_level) * smoothing

        usable_width = self._canvas_width - 12
        bar_width = max(2, (usable_width - (self.NUM_BARS - 1) * self.BAR_GAP) // self.NUM_BARS)
        max_height = self._canvas_height - 12

        for i in range(self.NUM_BARS):
            # Create a natural-looking frequency distribution
            # Center bars are taller, edges fall off
            center = self.NUM_BARS / 2
            distance = abs(i - center) / center
            freq_weight = 1.0 - (distance * 0.6)

            # Add some variety with a sine pattern
            wave = 0.5 + 0.5 * math.sin(i * 0.8 + self._current_level * 20)

            target_height = self._current_level * freq_weight * wave * max_height
            target_height = max(3, min(target_height, max_height))

            # Smooth each bar independently
            self._bar_levels[i] += (target_height - self._bar_levels[i]) * 0.4

            h = self._bar_levels[i]
            x = 6 + i * (bar_width + self.BAR_GAP)

            # Color gradient: horizontal blend from Deep Purple (#7C3AED) to Fuchsia (#D946EF)
            idx_ratio = i / (self.NUM_BARS - 1)
            # Interpolate Deep Purple (124, 58, 237) -> Fuchsia (217, 70, 239)
            r_c = int(124 + (217 - 124) * idx_ratio)
            g_c = int(58 + (70 - 58) * idx_ratio)
            b_c = int(237 + (239 - 237) * idx_ratio)
            color = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

            try:
                self._canvas.coords(
                    self._bars[i],
                    x, self._canvas_height - 4 - h,
                    x + bar_width, self._canvas_height - 4
                )
                self._canvas.itemconfig(self._bars[i], fill=color)
            except Exception:
                pass

    def set_level(self, level):
        """Manually set the level (0.0 to 1.0) if not using a callback."""
        self._target_level = max(0.0, min(1.0, level))

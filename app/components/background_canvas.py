"""
SONIC VOICE STUDIO - Liquid Glass Background Canvas
Draws a vivid abstract Apple Music–style backdrop with deep purple
and fuchsia gradients that give the glass panels something colorful
to refract.
"""

import customtkinter as ctk


class BackgroundCanvas(ctk.CTkCanvas):
    """
    Full-window liquid gradient backdrop.

    Tk widgets cannot sample and blur pixels behind them, so this component
    paints the high-chroma "behind the glass" layer directly.
    """

    TOP = (13, 11, 26)
    MID = (30, 18, 58)
    BOTTOM = (10, 8, 22)

    def __init__(self, parent, **kwargs):
        self.bg_root = "#0D0B1A"
        super().__init__(parent, highlightthickness=0, bg=self.bg_root, **kwargs)
        self.bind("<Configure>", self._on_resize)
        self._draw_scheduled = False

    def _on_resize(self, event):
        """Debounce redraws during resize."""
        if not self._draw_scheduled:
            self._draw_scheduled = True
            self.after(16, self._draw)

    @staticmethod
    def _mix(a, b, t):
        return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

    @staticmethod
    def _hex(rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def _vertical_gradient(self, w, h):
        steps = 96
        for i in range(steps):
            t = i / max(steps - 1, 1)
            if t < 0.55:
                color = self._mix(self.TOP, self.MID, t / 0.55)
            else:
                color = self._mix(self.MID, self.BOTTOM, (t - 0.55) / 0.45)
            y1 = int(h * i / steps)
            y2 = int(h * (i + 1) / steps) + 1
            self.create_rectangle(0, y1, w, y2, fill=self._hex(color), outline="")

    def _ribbon(self, points, palette, layers=11):
        """Draw a broad feathered ribbon using nested smooth polygons."""
        for i in range(layers, 0, -1):
            t = i / layers
            inset = (1.0 - t) * 24
            fill = self._mix(palette[0], palette[1], 1.0 - t)
            shifted = []
            for x, y in points:
                shifted.extend((x + inset, y + inset * 0.35))
            self.create_polygon(
                shifted,
                fill=self._hex(fill),
                outline="",
                smooth=True,
                splinesteps=28,
            )

    def _draw(self):
        self._draw_scheduled = False
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1 or h <= 1:
            return

        self.delete("all")
        self._vertical_gradient(w, h)

        # Broad, fluid bands — deep purple / fuchsia / magenta tones.
        # Primary ribbon: purple → fuchsia (top-left flowing right)
        self._ribbon(
            [
                (-180, h * 0.12),
                (w * 0.22, -80),
                (w * 0.58, h * 0.18),
                (w + 180, h * 0.02),
                (w + 120, h * 0.22),
                (w * 0.52, h * 0.38),
                (w * 0.18, h * 0.18),
                (-160, h * 0.36),
            ],
            ((124, 58, 237), (217, 70, 239)),  # violet → fuchsia
        )
        # Secondary ribbon: deep indigo → electric violet (bottom)
        self._ribbon(
            [
                (-160, h * 0.72),
                (w * 0.22, h * 0.46),
                (w * 0.48, h * 0.62),
                (w + 160, h * 0.42),
                (w + 120, h * 0.78),
                (w * 0.58, h + 90),
                (w * 0.18, h * 0.84),
                (-160, h + 40),
            ],
            ((76, 29, 149), (168, 85, 247)),  # deep purple → bright purple
        )
        # Tertiary ribbon: magenta → hot pink (center accent)
        self._ribbon(
            [
                (w * 0.38, -120),
                (w * 0.68, h * 0.06),
                (w * 0.92, h * 0.34),
                (w * 0.74, h * 0.58),
                (w * 0.46, h * 0.34),
                (w * 0.28, h * 0.08),
            ],
            ((192, 38, 211), (244, 114, 182)),  # magenta → pink
            layers=8,
        )

        # Subtle dark veil to keep white text crisp — purple-black tint.
        for i in range(18):
            t = i / 17
            color = self._mix((13, 11, 26), (10, 8, 22), t)
            self.create_rectangle(0, int(h * t), w, int(h * (t + 1 / 18)) + 1,
                                  fill=self._hex(color), outline="", stipple="gray50")

        # Specular glass-like streaks — violet / lilac / pink.
        for y_ratio, color in ((0.18, "#D8B4FE"), (0.52, "#E9D5FF"), (0.78, "#F0ABFC")):
            y = h * y_ratio
            self.create_line(
                -40, y,
                w * 0.25, y - h * 0.08,
                w * 0.62, y + h * 0.04,
                w + 60, y - h * 0.03,
                fill=color,
                width=1,
                smooth=True,
                splinesteps=24,
                stipple="gray75",
            )

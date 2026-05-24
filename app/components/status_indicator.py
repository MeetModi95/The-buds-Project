"""
SONIC VOICE STUDIO — Status Indicator Component
Animated pulsing dot that shows engine/connection state.
"""

import customtkinter as ctk
from app.theme import Colors


class StatusIndicator(ctk.CTkCanvas):
    """
    A small animated status indicator (pulsing dot).
    States: 'online', 'offline', 'error', 'listening'
    """

    STATE_COLORS = {
        'online': Colors.STATUS_ONLINE,
        'offline': Colors.STATUS_OFFLINE,
        'error': Colors.STATUS_ERROR,
        'listening': Colors.STATUS_LISTENING,
    }

    def __init__(self, parent, size=16, state='offline', **kwargs):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bg=parent.cget("fg_color") if hasattr(parent, 'cget') else Colors.BG_PANEL,
                         **kwargs)
        self._size = size
        self._state = state
        self._pulse_alpha = 0.0
        self._pulse_growing = True
        self._animating = False
        self._glow_ring = None
        self._core_dot = None
        self._draw()

    def _draw(self):
        self.delete("all")
        color = self.STATE_COLORS.get(self._state, Colors.STATUS_OFFLINE)
        cx, cy = self._size // 2, self._size // 2
        r = self._size // 2 - 2

        # Outer glow ring (subtle)
        self._glow_ring = self.create_oval(cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                                            fill="", outline=color, width=1)

        # Core dot
        self._core_dot = self.create_oval(cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1,
                                           fill=color, outline="")

    def set_state(self, state: str):
        """Change the indicator state."""
        self._state = state
        self._draw()
        if state in ('online', 'listening'):
            self._start_pulse()
        else:
            self._stop_pulse()

    def _start_pulse(self):
        if self._animating:
            return
        self._animating = True
        self._pulse_step()

    def _stop_pulse(self):
        self._animating = False

    def _pulse_step(self):
        if not self._animating:
            return
        # Simple alpha-based glow pulse by toggling outline width
        if self._pulse_growing:
            self._pulse_alpha += 0.1
            if self._pulse_alpha >= 1.0:
                self._pulse_growing = False
        else:
            self._pulse_alpha -= 0.1
            if self._pulse_alpha <= 0.0:
                self._pulse_growing = True

        width = 1 + int(self._pulse_alpha * 2)
        color = self.STATE_COLORS.get(self._state, Colors.STATUS_OFFLINE)
        try:
            self.itemconfig(self._glow_ring, width=width, outline=color)
        except Exception:
            pass

        self.after(100, self._pulse_step)

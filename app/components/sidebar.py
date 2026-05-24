"""
SONIC VOICE STUDIO — Sidebar Navigation Component
Razer Synapse–inspired sidebar with icon labels, active state indicator,
hover effects, and engine status toggle at the bottom.
"""

import customtkinter as ctk
from app.theme import Colors, Fonts, Sizes


class SidebarItem(ctk.CTkFrame):
    """A single clickable sidebar navigation item."""

    def __init__(self, parent, icon_text, label_text, command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", height=Sizes.SIDEBAR_ITEM_HEIGHT,
                         cursor="hand2", corner_radius=10, **kwargs)
        self.pack_propagate(False)
        self._command = command
        self._is_active = False
        self._label_text = label_text

        # Icon
        self._icon_label = ctk.CTkLabel(self, text=icon_text, width=30,
                                         font=ctk.CTkFont(size=16),
                                         text_color=Colors.TEXT_SECONDARY)
        self._icon_label.pack(side="left", padx=(14, 4))

        # Text label
        self._text_label = ctk.CTkLabel(self, text=label_text,
                                         font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE),
                                         text_color=Colors.TEXT_SECONDARY, anchor="w")
        self._text_label.pack(side="left", padx=(6, 14), fill="x", expand=True)

        # Bind clicks to all child widgets
        for widget in [self, self._icon_label, self._text_label]:
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _on_click(self, event=None):
        if self._command:
            self._command()

    def _on_enter(self, event=None):
        if not self._is_active:
            self.configure(fg_color=Colors.BG_HOVER)

    def _on_leave(self, event=None):
        if not self._is_active:
            self.configure(fg_color="transparent")

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=Colors.SIDEBAR_ACTIVE_BG, border_width=1, border_color=Colors.BORDER)
            self._icon_label.configure(text_color=Colors.ACCENT)
            self._text_label.configure(text_color=Colors.TEXT_PRIMARY, font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="bold"))
        else:
            self.configure(fg_color="transparent", border_width=0)
            self._icon_label.configure(text_color=Colors.TEXT_SECONDARY)
            self._text_label.configure(text_color=Colors.TEXT_SECONDARY, font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.BODY_SIZE, weight="normal"))


class Sidebar(ctk.CTkFrame):
    """
    Full sidebar component with navigation items and engine status section.
    """

    # Navigation structure: (icon, label, page_key)
    NAV_ITEMS = [
        ("⌂", "Dashboard", "dashboard"),
        ("⎈", "Commands", "commands"),
        ("♪", "Audio", "audio"),
        ("☰", "Profiles", "profiles"),
        ("⚙", "Settings", "settings"),
    ]

    def __init__(self, parent, on_navigate=None, on_engine_toggle=None, **kwargs):
        super().__init__(parent, width=Sizes.SIDEBAR_WIDTH,
                         fg_color="transparent", corner_radius=0,
                         border_width=0, **kwargs)
        self.pack_propagate(False)
        self._on_navigate = on_navigate
        self._on_engine_toggle = on_engine_toggle
        self._items = {}
        self._active_page = None

        self._build()

    def _build(self):
        # --- Top Brand ---
        brand_frame = ctk.CTkFrame(self, fg_color="transparent", height=70)
        brand_frame.pack(fill="x", side="top")
        brand_frame.pack_propagate(False)

        brand_title = ctk.CTkLabel(brand_frame, text="SONIC",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=22, weight="bold"),
                                    text_color=Colors.ACCENT_GLOW)
        brand_title.pack(side="left", padx=(20, 2), pady=(20, 10))

        brand_sub = ctk.CTkLabel(brand_frame, text="VOICE",
                                  font=ctk.CTkFont(family=Fonts.FAMILY, size=22, weight="bold"),
                                  text_color=Colors.TEXT_PRIMARY)
        brand_sub.pack(side="left", padx=(0, 10), pady=(20, 10))

        # Section label
        section_lbl = ctk.CTkLabel(self, text="NAVIGATION",
                                    font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TINY_SIZE, weight="bold"),
                                    text_color=Colors.TEXT_DISABLED, anchor="w")
        section_lbl.pack(fill="x", padx=20, pady=(8, 4))

        # --- Nav Items ---
        for icon, label, page_key in self.NAV_ITEMS:
            item = SidebarItem(self, icon_text=icon, label_text=label,
                               command=lambda pk=page_key: self._handle_nav(pk))
            item.pack(fill="x", padx=12, pady=3)
            self._items[page_key] = item

        # --- Bottom Section: Engine Toggle ---
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        engine_frame = ctk.CTkFrame(self, fg_color=Colors.BG_CARD, height=56,
                                    corner_radius=16, border_width=1, border_color=Colors.BORDER)
        engine_frame.pack(fill="x", side="bottom", padx=12, pady=(0, 12))
        engine_frame.pack_propagate(False)

        # Status dot
        self._status_dot = ctk.CTkLabel(engine_frame, text="●", width=16,
                                         font=ctk.CTkFont(size=14),
                                         text_color=Colors.STATUS_OFFLINE)
        self._status_dot.pack(side="left", padx=(10, 4), pady=16)

        self._status_label = ctk.CTkLabel(engine_frame, text="OFFLINE",
                                           font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TINY_SIZE, weight="bold"),
                                           text_color=Colors.TEXT_DISABLED, anchor="w")
        self._status_label.pack(side="left", padx=(0, 4), pady=16)

        self._engine_switch_var = ctk.StringVar(value="off")
        self._engine_switch = ctk.CTkSwitch(engine_frame, text="",
                                             variable=self._engine_switch_var,
                                             onvalue="on", offvalue="off",
                                             command=self._handle_engine_toggle,
                                             width=36,
                                             progress_color=Colors.ACCENT,
                                             button_color=Colors.ACCENT_HOVER,
                                             button_hover_color=Colors.ACCENT_HOVER,
                                             fg_color=Colors.BORDER_SUBTLE)
        self._engine_switch.pack(side="right", padx=(0, 10), pady=16)

        # Version label at very bottom
        ver_lbl = ctk.CTkLabel(self, text="v2.0.0",
                                font=ctk.CTkFont(family=Fonts.FAMILY, size=Fonts.TINY_SIZE),
                                text_color=Colors.TEXT_DISABLED)
        ver_lbl.pack(side="bottom", pady=(0, 8))

    def _handle_nav(self, page_key):
        if page_key == self._active_page:
            return
        self._active_page = page_key
        for key, item in self._items.items():
            item.set_active(key == page_key)
        if self._on_navigate:
            self._on_navigate(page_key)

    def _handle_engine_toggle(self):
        if self._on_engine_toggle:
            self._on_engine_toggle(self._engine_switch_var.get() == "on")

    def set_active_page(self, page_key):
        """Programmatically set the active page."""
        self._active_page = page_key
        for key, item in self._items.items():
            item.set_active(key == page_key)

    def set_engine_status(self, is_active: bool, model_loaded: bool = True):
        """Update the engine status display."""
        if is_active:
            self._status_dot.configure(text_color=Colors.STATUS_ONLINE)
            self._status_label.configure(text="ENGINE ACTIVE", text_color=Colors.ACCENT)
            self._engine_switch_var.set("on")
        elif not model_loaded:
            self._status_dot.configure(text_color=Colors.STATUS_ERROR)
            self._status_label.configure(text="MODEL ERROR", text_color=Colors.DANGER)
            self._engine_switch_var.set("off")
        else:
            self._status_dot.configure(text_color=Colors.STATUS_OFFLINE)
            self._status_label.configure(text="ENGINE OFFLINE", text_color=Colors.TEXT_DISABLED)
            self._engine_switch_var.set("off")
